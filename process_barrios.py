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
            
            posts_records.append({
                'post_id': post_id,
                'name': post_data.get('name'),
                'geometry': Point(lon, lat),
                'votes': post_votes
            })

print(f"Found {len(posts_records)} valid posts with coordinates in Medellin")
gdf_posts = gpd.GeoDataFrame(posts_records, crs="EPSG:4326")

# 3. Spatial join
print("Performing spatial join...")
# Assign each post to the barrio it falls into
joined = gpd.sjoin(gdf_posts, gdf_barrios, how="inner", predicate="within")

print(f"Matched {len(joined)} posts to barrios")

# 4. Aggregate votes per barrio
barrio_results = {} # index -> [votes]

for idx, row in joined.iterrows():
    barrio_idx = row['index_right']
    if barrio_idx not in barrio_results:
        barrio_results[barrio_idx] = [0] * len(candidates)
    
    for i in range(len(candidates)):
        barrio_results[barrio_idx][i] += row['votes'][i]

# 5. Populate geojson properties
print("Populating properties...")
# Add default columns to GeoDataFrame
def get_winner_info(barrio_idx):
    if barrio_idx not in barrio_results:
        return json.dumps({"winner": "Sin Datos", "results": [], "total_votes": 0})
    
    votes = barrio_results[barrio_idx]
    total_votes = sum(votes)
    if total_votes == 0:
        return json.dumps({"winner": "Sin Datos", "results": [], "total_votes": 0})
    
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
        "total_votes": total_votes
    })

gdf_barrios['electoral_json'] = gdf_barrios.index.map(get_winner_info)

# Convert stringified json back to object during save is tricky in fiona, 
# but we can save it to geojson directly using the underlying json dictionary representation 
# after using pandas to_dict
print("Saving to barrios_resultados.geojson...")
geojson_dict = json.loads(gdf_barrios.to_json())
for feature in geojson_dict['features']:
    props = feature['properties']
    if 'electoral_json' in props:
        electoral_info = json.loads(props['electoral_json'])
        props['winner'] = electoral_info['winner']
        props['results'] = electoral_info['results']
        props['total_votes'] = electoral_info['total_votes']
        del props['electoral_json']

with open('barrios_resultados.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson_dict, f, ensure_ascii=False)

print("Done!")
