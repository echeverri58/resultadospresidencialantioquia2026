import pandas as pd
import json
import re
import os
import difflib
import unicodedata

def normalize(s):
    if pd.isna(s): return ""
    s = str(s)
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.upper().strip()

def normalize_key(texto):
    if pd.isna(texto): return "n_a"
    texto = str(texto)
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto.lower().replace(' ', '_').strip()

# Leer CSV
df = pd.read_csv('Perfiles y Candidaturas para el Senado de Colombia - Table 1.csv')

# Listar fotos de la carpeta destino (ya que en la tarea anterior copié algunas, 
# pero quizá deba buscar en la original fotos_pdf_senadores por si acaso).
fotos_dir = r'C:\Users\ASUS vivobook\Desktop\Elecciones presidenciales\fotos_pdf_senadores'
fotos_files = [f for f in os.listdir(fotos_dir) if f.endswith(('.jpeg', '.jpg', '.png'))]
dest_dir = 'fotos_senadores'
os.makedirs(dest_dir, exist_ok=True)

senadores_por_dep = {}

for idx, row in df.iterrows():
    nombre = row['Nombre del Candidato']
    if pd.isna(nombre): continue
    
    departamento = str(row['Departamento']).strip()
    dep_key = normalize_key(departamento)
    if not dep_key or dep_key == "nan":
        dep_key = "nacional"
        
    partido = row['Partido Político'] if pd.notna(row['Partido Político']) else 'Independiente'
    profesion = row['Profesión / Formación'] if pd.notna(row['Profesión / Formación']) else ''
    trayectoria = row['Trayectoria y Perfil'] if pd.notna(row['Trayectoria y Perfil']) else ''
    estatus = row['Estatus de Candidatura'] if pd.notna(row['Estatus de Candidatura']) else ''
    
    norm_nombre = normalize(nombre)
    
    # Buscar foto
    mejor_coincidencia = None
    mejor_score = 0
    parts = norm_nombre.split()
    
    for f in fotos_files:
        norm_f = normalize(os.path.splitext(f)[0])
        f_parts = norm_f.split()
        coincidencias = sum(1 for p in f_parts if p in parts and len(p) > 2)
        score = coincidencias / max(len(f_parts), 1)
        if score > mejor_score:
            mejor_score = score
            mejor_coincidencia = f

    if mejor_score < 0.5:
        nombres_fotos = [os.path.splitext(f)[0] for f in fotos_files]
        norm_nombres_fotos = [normalize(n) for n in nombres_fotos]
        matches = difflib.get_close_matches(norm_nombre, norm_nombres_fotos, n=1, cutoff=0.4)
        if matches:
            idx_match = norm_nombres_fotos.index(matches[0])
            mejor_coincidencia = fotos_files[idx_match]
            mejor_score = 0.5

    id_senador = f"senador_perfil_{idx}"
    foto_path = "https://via.placeholder.com/400x400.png?text=Sin+Foto"
    
    if mejor_coincidencia and mejor_score >= 0.5:
        ext = os.path.splitext(mejor_coincidencia)[1]
        new_filename = f"{id_senador}{ext}"
        src_path = os.path.join(fotos_dir, mejor_coincidencia)
        dst_path = os.path.join(dest_dir, new_filename)
        import shutil
        shutil.copy2(src_path, dst_path)
        foto_path = f"fotos_senadores/{new_filename}"
        
    senador_obj = {
        "id": id_senador,
        "nombre": nombre,
        "partido": partido,
        "votos": "N/A", # Will hide in UI
        "foto_path": foto_path,
        "profesion": profesion,
        "trayectoria": trayectoria,
        "estatus": estatus
    }
    
    if dep_key not in senadores_por_dep:
        senadores_por_dep[dep_key] = []
    senadores_por_dep[dep_key].append(senador_obj)

# Inyectar en datos_politicos.js
with open('datos_politicos.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

match = re.search(r'window\.datosReales = (\{.*?\});', js_content, re.DOTALL)
datos_reales_str = match.group(1) if match else "{}"

# Rescribimos datos_politicos.js
new_js = f"""// Función para obtener datos de prueba/reales por cada departamento.
window.datosReales = {datos_reales_str};
window.senadoresPorDepartamento = {json.dumps(senadores_por_dep, ensure_ascii=False, indent=4)};

function obtenerPoliticos(departamento) {{
    const depKey = departamento.replace(/\\s+/g, '_').toLowerCase();
    
    const normalizar = (texto) => texto.normalize("NFD").replace(/[\\u0300-\\u036f]/g, "").toLowerCase();
    const depNormalizado = normalizar(departamento);
    
    let depMatch = Object.keys(window.datosReales).find(k => {{
        let excelDep = normalizar(k);
        return excelDep === depNormalizado || 
               (depNormalizado.includes("bogota") && excelDep.includes("bogota")) ||
               (depNormalizado.includes("san andres") && excelDep.includes("san andres")) ||
               (depNormalizado.includes("valle") && excelDep.includes("valle"));
    }});
    
    let repsReales = [];
    if (depMatch) {{
        repsReales = window.datosReales[depMatch].map((rep, index) => {{
            return {{
                id: "rep_" + (index + 1) + "_" + depKey,
                nombre: rep.nombre,
                partido: rep.partido,
                votos: "N/A",
                foto_path: "fotos_politicos/rep_" + (index + 1) + "_" + depKey + "/foto.svg"
            }};
        }});
    }} else {{
        repsReales = [
            {{
                id: "rep_1_" + depKey,
                nombre: "No hay datos (" + departamento + ")",
                partido: "N/A",
                votos: "N/A",
                foto_path: "fotos_politicos/rep_1_" + depKey + "/foto.svg"
            }}
        ];
    }}
    
    let sensReales = [];
    let depMatchSen = Object.keys(window.senadoresPorDepartamento).find(k => {{
        let excelDep = normalizar(k);
        return excelDep === depNormalizado || 
               (depNormalizado.includes("bogota") && excelDep.includes("bogota")) ||
               (depNormalizado.includes("san andres") && excelDep.includes("san andres")) ||
               (depNormalizado.includes("valle") && excelDep.includes("valle"));
    }});
    
    if (depMatchSen && window.senadoresPorDepartamento[depMatchSen]) {{
        sensReales = window.senadoresPorDepartamento[depMatchSen];
    }} else {{
        sensReales = window.senadoresPorDepartamento["nacional"] || [];
    }}
    
    return {{
        senadores: sensReales,
        representantes: repsReales
    }};
}}
"""

with open('datos_politicos.js', 'w', encoding='utf-8') as f:
    f.write(new_js)

print("Procesamiento completado.")
