import pandas as pd
import json
import os
import re
import unicodedata

def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', '', text)
    return text

# Load Excel
df = pd.read_excel('mapa_colombia_test/Representantes_Camara_Colombia_Organizado.xlsx', sheet_name='Listado Completo', header=2)
col_dep = df.columns[0]
col_nom = df.columns[1]
col_par = df.columns[2]
df = df.dropna(subset=[col_dep, col_nom])

# Get image files
img_dir = 'mapa_colombia_test/fotos_extraidas_representantes'
img_files = os.listdir(img_dir)
img_map = {}
for f in img_files:
    if f.endswith(('.png', '.jpg', '.jpeg')):
        name_part = os.path.splitext(f)[0]
        norm_name = normalize_text(name_part)
        img_map[norm_name] = f

# Process data
deps = {}
for index, row in df.iterrows():
    dep_name = str(row[col_dep]).strip()
    rep_name = str(row[col_nom]).strip()
    partido = str(row[col_par]).strip() if pd.notna(row[col_par]) else 'Independiente'
    
    norm_rep = normalize_text(rep_name)
    foto_path = ""
    
    # Try exact match first
    if norm_rep in img_map:
        foto_path = f"fotos_extraidas_representantes/{img_map[norm_rep]}"
    else:
        # Try partial match
        best_match = None
        best_len = 0
        for norm_img, original_file in img_map.items():
            if norm_rep in norm_img or norm_img in norm_rep:
                if len(norm_img) > best_len:
                    best_len = len(norm_img)
                    best_match = original_file
        if best_match:
            foto_path = f"fotos_extraidas_representantes/{best_match}"

    if dep_name not in deps:
        deps[dep_name] = []
        
    rep_obj = {
        'nombre': rep_name,
        'partido': partido
    }
    if foto_path:
        rep_obj['foto_path'] = foto_path
        
    deps[dep_name].append(rep_obj)

# Update JS file
js_path = 'mapa_colombia_test/datos_politicos.js'
with open(js_path, 'r', encoding='utf-8') as f:
    js_content = f.read()

# Replace window.datosReales
json_str = json.dumps(deps, ensure_ascii=False, indent=4)
pattern = re.compile(r'(window\.datosReales\s*=\s*)\{.*?\};(\s*window\.senadoresPorDepartamento\s*=)', re.DOTALL)
js_content = pattern.sub(r'\1' + json_str + r';\2', js_content)

# Update obtenerPoliticos if needed
old_foto_line = r'foto_path:\s*"fotos_politicos/rep_"\s*\+\s*\(index\s*\+\s*1\)\s*\+\s*"_"\s*\+\s*depKey\s*\+\s*"/foto\.svg"'
new_foto_line = r'foto_path: rep.foto_path || ("fotos_politicos/rep_" + (index + 1) + "_" + depKey + "/foto.svg")'

if "rep.foto_path ||" not in js_content:
    js_content = re.sub(old_foto_line, new_foto_line, js_content)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Actualización completada!")
