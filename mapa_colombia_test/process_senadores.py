import pandas as pd
import os
import shutil
import re
import difflib
import json
import unicodedata

def normalize(s):
    if pd.isna(s): return ""
    s = str(s)
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return s.upper().strip()

# Leer CSV
df = pd.read_csv('Lista de senadores.csv')

# Listar fotos
fotos_dir = r'C:\Users\ASUS vivobook\Desktop\Elecciones presidenciales\fotos_pdf_senadores'
fotos_files = [f for f in os.listdir(fotos_dir) if f.endswith(('.jpeg', '.jpg', '.png'))]

# Crear carpeta de destino
dest_dir = 'fotos_senadores'
os.makedirs(dest_dir, exist_ok=True)

senadores_list = []

for idx, row in df.iterrows():
    nombre = row['NOMBRE DEL SENADOR']
    partido = row['PARTIDO O COALICION'] if pd.notna(row['PARTIDO O COALICION']) else 'Independiente'
    
    norm_nombre = normalize(nombre)
    
    # Intentar buscar foto por coincidencia
    mejor_coincidencia = None
    mejor_score = 0
    
    parts = norm_nombre.split()
    
    for f in fotos_files:
        norm_f = normalize(os.path.splitext(f)[0])
        
        # heuristica simple: contar cuantas palabras coinciden
        f_parts = norm_f.split()
        coincidencias = sum(1 for p in f_parts if p in parts and len(p) > 2)
        score = coincidencias / max(len(f_parts), 1)
        
        if score > mejor_score:
            mejor_score = score
            mejor_coincidencia = f

    # Si no es muy bueno el score, probar difflib
    if mejor_score < 0.5:
        nombres_fotos = [os.path.splitext(f)[0] for f in fotos_files]
        norm_nombres_fotos = [normalize(n) for n in nombres_fotos]
        matches = difflib.get_close_matches(norm_nombre, norm_nombres_fotos, n=1, cutoff=0.4)
        if matches:
            idx_match = norm_nombres_fotos.index(matches[0])
            mejor_coincidencia = fotos_files[idx_match]
            mejor_score = 0.5 # Aprobado por fallback

    id_senador = f"senador_nal_{idx}"
    foto_path = "https://via.placeholder.com/400x400.png?text=Sin+Foto"
    
    if mejor_coincidencia and mejor_score >= 0.5:
        ext = os.path.splitext(mejor_coincidencia)[1]
        new_filename = f"{id_senador}{ext}"
        src_path = os.path.join(fotos_dir, mejor_coincidencia)
        dst_path = os.path.join(dest_dir, new_filename)
        shutil.copy2(src_path, dst_path)
        foto_path = f"fotos_senadores/{new_filename}"
        
        # Eliminar la foto usada para que no se asigne a varios si no es necesario (opcional, mejor no para no dañar)
        
    senadores_list.append({
        "id": id_senador,
        "nombre": nombre,
        "partido": partido,
        "votos": "N/A",
        "foto_path": foto_path
    })

# Inyectar en datos_politicos.js
with open('datos_politicos.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

match = re.search(r'window\.datosReales = (\{.*?\});', js_content, re.DOTALL)
datos_reales_str = match.group(1) if match else "{}"

new_js = f"""// Función para obtener datos de prueba/reales por cada departamento.
window.datosReales = {datos_reales_str};
window.senadoresReales = {json.dumps(senadores_list, ensure_ascii=False, indent=4)};

function obtenerPoliticos(departamento) {{
    const depKey = departamento.replace(/\\s+/g, '_').toLowerCase();
    
    const normalizar = (texto) => texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
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
    
    return {{
        senadores: window.senadoresReales,
        representantes: repsReales
    }};
}}
"""

with open('datos_politicos.js', 'w', encoding='utf-8') as f:
    f.write(new_js)

print("Procesamiento completado.")
