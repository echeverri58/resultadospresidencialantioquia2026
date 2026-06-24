import json
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import re

print("Loading geojson...")
gdf_barrios = gpd.read_file('barrios_y_veredas_mr.geojson')
gdf_barrios = gdf_barrios.to_crs(epsg=4326)

print("Loading electoral data...")
with open('electoral_data.json', 'r', encoding='utf-8') as f:
    electoral_data = json.load(f)

# Leer analisis cruzado
df_cruce = pd.read_csv('Analisis_Cruzado_Puestos_2026.csv', encoding='latin1')

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

hierarchy = electoral_data['hierarchy']
medellin_data = hierarchy.get("MEDELLIN", {})

# Construir diccionario de coordenadas de puestos
post_coords = {}
for zone_id, posts in medellin_data.items():
    for post_id, post_data in posts.items():
        lat = post_data.get('lat')
        lon = post_data.get('lon')
        if lat is not None and lon is not None:
            post_name_norm = normalize_text(post_data.get('name', ''))
            post_coords[post_name_norm] = Point(lon, lat)

posts_records = []
for idx, row in df_cruce.iterrows():
    if 'MEDELLIN' in str(row['MUNNOMBRE']).upper():
        post_name = str(row['PUESNOMBRE'])
        post_name_norm = normalize_text(post_name)
        
        # Buscar coordenadas
        point = None
        if post_name_norm in post_coords:
            point = post_coords[post_name_norm]
        else:
            # fuzzy o fallback?
            for k, v in post_coords.items():
                if k in post_name_norm or post_name_norm in k:
                    point = v
                    break
        
        cepeda_1v_col = [col for col in row.index if 'CEPEDA' in col and '_1v' in col]
        cepeda_1v_col = cepeda_1v_col[0] if cepeda_1v_col else None
        
        cepeda_2v_col = [col for col in row.index if 'CEPEDA' in col and '_1v' not in col and 'CRECIMIENTO' not in col]
        cepeda_2v_col = cepeda_2v_col[0] if cepeda_2v_col else None
        
        cepeda_crec_col = [col for col in row.index if 'CEPEDA' in col and 'CRECIMIENTO' in col]
        cepeda_crec_col = cepeda_crec_col[0] if cepeda_crec_col else None
        
        if point:
            posts_records.append({
                'name': post_name,
                'geometry': point,
                'votos_1v_abelardo': row.get('ABELARDO DE LA ESPRIELLA_1v', 0),
                'votos_2v_abelardo': row.get('ABELARDO DE LA ESPRIELLA_2v', 0),
                'crecimiento_abelardo': row.get('CRECIMIENTO_ABELARDO DE LA ESPRIELLA', 0),
                'votos_1v_cepeda': row.get(cepeda_1v_col, 0) if cepeda_1v_col else 0,
                'votos_2v_cepeda': row.get(cepeda_2v_col, 0) if cepeda_2v_col else 0,
                'crecimiento_cepeda': row.get(cepeda_crec_col, 0) if cepeda_crec_col else 0,
                'total_1v': row.get('TOTAL_VOTOS_1v', 0),
                'total_2v': row.get('TOTAL_VOTOS_2v', 0),
            })
        else:
            print(f"Post without coordinates: {post_name}")

print(f"Matched {len(posts_records)} posts from CSV to coordinates")
gdf_posts = gpd.GeoDataFrame(posts_records, crs="EPSG:4326")

print("Performing spatial join...")
joined = gpd.sjoin(gdf_posts, gdf_barrios, how="inner", predicate="within")

barrio_metrics = {}
for idx, row in joined.iterrows():
    b_idx = row['index_right']
    if b_idx not in barrio_metrics:
        barrio_metrics[b_idx] = {
            'votos_1v_abelardo': 0, 'votos_2v_abelardo': 0, 'crecimiento_abelardo': 0,
            'votos_1v_cepeda': 0, 'votos_2v_cepeda': 0, 'crecimiento_cepeda': 0,
            'total_1v': 0, 'total_2v': 0,
            'posts_details': []
        }
    
    # Need to handle exact column names from the CSV if there are typos/encoding issues.
    # The script generated these so we will aggregate what we found:
    for k in barrio_metrics[b_idx].keys():
        if k != 'posts_details':
            barrio_metrics[b_idx][k] += row[k]
            
    barrio_metrics[b_idx]['posts_details'].append({
        'name': row.get('name', 'Puesto Desconocido'),
        'a_1v': row.get('votos_1v_abelardo', 0),
        'a_2v': row.get('votos_2v_abelardo', 0),
        'a_c': row.get('crecimiento_abelardo', 0),
        'c_1v': row.get('votos_1v_cepeda', 0),
        'c_2v': row.get('votos_2v_cepeda', 0),
        'c_c': row.get('crecimiento_cepeda', 0),
    })

print("Updating barrios_resultados.geojson...")
with open('barrios_resultados.geojson', 'r', encoding='utf-8') as f:
    geojson_data = json.load(f)

for feature in geojson_data['features']:
    b_idx = int(feature['id']) if 'id' in feature else None
    if b_idx is not None and b_idx in barrio_metrics:
        m = barrio_metrics[b_idx]
        feature['properties']['crecimiento_abelardo'] = m['crecimiento_abelardo']
        feature['properties']['crecimiento_cepeda'] = m['crecimiento_cepeda']
        feature['properties']['votos_1v_abelardo'] = m['votos_1v_abelardo']
        feature['properties']['votos_2v_abelardo'] = m['votos_2v_abelardo']
        feature['properties']['votos_1v_cepeda'] = m['votos_1v_cepeda']
        feature['properties']['votos_2v_cepeda'] = m['votos_2v_cepeda']
        feature['properties']['total_1v'] = m['total_1v']
        feature['properties']['total_2v'] = m['total_2v']
        feature['properties']['posts_details'] = m['posts_details']
        
        if m['crecimiento_abelardo'] > m['crecimiento_cepeda']:
            feature['properties']['winner_crecimiento'] = 'ABELARDO DE LA ESPRIELLA'
        elif m['crecimiento_cepeda'] > m['crecimiento_abelardo']:
            feature['properties']['winner_crecimiento'] = 'IVÁN CEPEDA CASTRO'
        else:
            feature['properties']['winner_crecimiento'] = 'EMPATE'
    else:
        feature['properties']['winner_crecimiento'] = 'Sin Datos'
        feature['properties']['crecimiento_abelardo'] = 0
        feature['properties']['crecimiento_cepeda'] = 0

with open('barrios_resultados.geojson', 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f, ensure_ascii=False)

print("Done! barrios_resultados.geojson updated with 2v data.")
