import json
import geopandas as gpd
from shapely.geometry import Point
import os

# 1. Load the geojson
print("Loading geojson...")
gdf_barrios = gpd.read_file('barrios_y_veredas_mr.geojson')

# Output original CRS
print(f"Original CRS: {gdf_barrios.crs}")

# Reproject to WGS84
print("Reprojecting to EPSG:4326...")
gdf_barrios = gdf_barrios.to_crs(epsg=4326)

# 2. Load electoral data
print("Loading electoral data...")
with open('electoral_data.json', 'r', encoding='utf-8') as f:
    electoral_data = json.load(f)

candidates = electoral_data['candidates']
hierarchy = electoral_data['hierarchy']

# Extract Medellin posts
medellin_data = hierarchy.get("MEDELLIN", {})

# Load zone potentials and compute total tables per zone
zone_potentials = electoral_data.get("zone_potentials", {})
zone_total_tables = {}
for zone_id, posts in medellin_data.items():
    total_tables = sum(len(post_data.get('tables', {})) for post_data in posts.values())
    zone_total_tables[zone_id] = total_tables

import re

def normalize_text(text):
    if not text:
        return ''
    text = text.upper()
    replacements = {'?':'A', '%':'E', '?':'I', '"':'O', 's':'U', '\'':'N', 'o':'U'}
    for k, v in replacements.items():
        text = text.replace(k, v)
    text = re.sub(r'\b(I\.?E\.?R?|C\.?E\.?R?|S\.?D|I\.?E\.?S\.?E\.?D?|E\.?U|I\.?E|COL\.?|COLLEGIO|COLEGIO|ESCUELA|CENTRO EDUCATIVO|INSTITUCION EDUCATIVA|SEDE)\b', '', text)
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text

# Load exact potentials
post_potentials = electoral_data.get("post_potentials", {})

posts_records = []
for zone_id, posts in medellin_data.items():
    for post_id, post_data in posts.items():
        lat = post_data.get('lat')
        lon = post_data.get('lon')
        if lat is not None and lon is not None:
            # Aggregate votes for this post
            post_votes = [0] * len(candidates)
            for table_id, table_votes in post_data.get('tables', {}).items():
                for i in range(len(candidates)):
                    post_votes[i] += table_votes[i]
            
            # Match exact potential using normalized name
            post_name = post_data.get('name', '')
            post_name_norm = normalize_text(post_name)
            
            pot_data = post_potentials.get(post_name_norm, {})
            if isinstance(pot_data, int):
                pot_data = {'total': pot_data, 'mujeres': 0, 'hombres': 0}
            if not pot_data:
                pot_data = post_potentials.get(post_name, {})
                if isinstance(pot_data, int):
                    pot_data = {'total': pot_data, 'mujeres': 0, 'hombres': 0}
                
            potencial_post = pot_data.get('total', 0)
                
            # Fallback if Divipole exact matching fails
            if potencial_post == 0:
                tables_post = len(post_data.get('tables', {}))
                potencial_zona = zone_potentials.get(zone_id, 0)
                mesas_zona = zone_total_tables.get(zone_id, 0)
                if mesas_zona > 0:
                    potencial_post = potencial_zona * (tables_post / mesas_zona)
                else:
                    potencial_post = 0
            
            posts_records.append({
                'post_id': post_id,
                'name': post_data.get('name'),
                'geometry': Point(lon, lat),
                'votes': post_votes,
                'potential': potencial_post,
                'zone_id': zone_id
            })

print(f"Found {len(posts_records)} valid posts with coordinates in Medellin")
gdf_posts = gpd.GeoDataFrame(posts_records, crs="EPSG:4326")

# 3. Spatial join
print("Performing spatial join...")
# Assign each post to the barrio it falls into
joined = gpd.sjoin(gdf_posts, gdf_barrios, how="inner", predicate="within")

print(f"Matched {len(joined)} posts to barrios")

# 4. Aggregate votes, potential, and other metrics per barrio
barrio_results = {} # index -> [votes]
barrio_potential = {} # index -> potential
barrio_posts_list = {} # index -> list of post names

for idx, row in joined.iterrows():
    barrio_idx = row['index_right']
    if barrio_idx not in barrio_results:
        barrio_results[barrio_idx] = [0] * len(candidates)
        barrio_potential[barrio_idx] = 0.0
        barrio_posts_list[barrio_idx] = []
    
    for i in range(len(candidates)):
        barrio_results[barrio_idx][i] += row['votes'][i]
        
    barrio_potential[barrio_idx] += row['potential']
    barrio_posts_list[barrio_idx].append(row['name'])

# 5. Populate geojson properties
print("Populating properties...")
# Add default columns to GeoDataFrame
def get_winner_info(barrio_idx):
    if barrio_idx not in barrio_results:
        return json.dumps({
            "winner": "Sin Datos", 
            "results": [], 
            "total_votes": 0, 
            "potential": 0, 
            "abstencion": 0, 
            "opportunity": 0, 
            "otros": 0
        })
    
    votes = barrio_results[barrio_idx]
    total_votes = sum(votes)
    potential = int(round(barrio_potential.get(barrio_idx, 0)))
    abstencion = max(0, potential - total_votes)
    
    # Calculate Right wing votes vs Cepeda votes
    fico_votes = 0
    cepeda_votes = 0
    
    for i, cand in enumerate(candidates):
        cand_upper = cand.upper()
        if "ESPRIELLA" in cand_upper or "PALOMA" in cand_upper:
            fico_votes += votes[i]
        elif "CEPEDA" in cand_upper:
            cepeda_votes += votes[i]
            
    otros = total_votes - fico_votes - cepeda_votes
    
    # Cepeda affinity
    pct_cepeda = (cepeda_votes / total_votes) if total_votes > 0 else 0
    
    # Opportunity formula: (Abstention * Cepeda affinity) + Otros
    opportunity = int(round((abstencion * pct_cepeda) + otros))
    
    if total_votes == 0:
        return json.dumps({
            "winner": "Sin Datos", 
            "results": [], 
            "total_votes": 0, 
            "potential": potential, 
            "abstencion": abstencion, 
            "opportunity": opportunity, 
            "otros": otros
        })
    
    results_list = []
    for i, cand in enumerate(candidates):
        results_list.append({
            "candidate": cand,
            "votes": votes[i],
            "pct": (votes[i] / total_votes * 100)
        })
    results_list.sort(key=lambda x: x["votes"], reverse=True)
    
    winner = results_list[0]["candidate"]
    
    return json.dumps({
        "winner": winner,
        "results": results_list,
        "total_votes": total_votes,
        "potential": potential,
        "abstencion": abstencion,
        "opportunity": opportunity,
        "otros": otros
    })

gdf_barrios['electoral_json'] = gdf_barrios.index.map(get_winner_info)

# Convert stringified json back to object during save
print("Saving to barrios_resultados.geojson...")
geojson_dict = json.loads(gdf_barrios.to_json())
for feature in geojson_dict['features']:
    props = feature['properties']
    if 'electoral_json' in props:
        electoral_info = json.loads(props['electoral_json'])
        props['winner'] = electoral_info['winner']
        props['results'] = electoral_info['results']
        props['total_votes'] = electoral_info['total_votes']
        props['potential'] = electoral_info.get('potential', 0)
        props['abstencion'] = electoral_info.get('abstencion', 0)
        props['opportunity'] = electoral_info.get('opportunity', 0)
        props['otros'] = electoral_info.get('otros', 0)
        
        # Add posts names list for display
        barrio_idx = int(feature['id']) if 'id' in feature else None
        if barrio_idx is not None and barrio_idx in barrio_posts_list:
            props['posts'] = list(set(barrio_posts_list[barrio_idx]))
        else:
            props['posts'] = []
            
        del props['electoral_json']

with open('barrios_resultados.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson_dict, f, ensure_ascii=False)

print("Done!")
