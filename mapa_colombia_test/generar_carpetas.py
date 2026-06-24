import json
import os
import re

# Ruta al geojson para extraer los nombres de los departamentos
geojson_path = 'colombia_departamentos.geojson'
fotos_base_dir = 'fotos_politicos'

if not os.path.exists(fotos_base_dir):
    os.makedirs(fotos_base_dir)

# SVG de una silueta humana simple para la foto genérica
svg_generico = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#bdc3c7">
  <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
</svg>"""

with open(geojson_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

departamentos = set()
for feature in data['features']:
    if 'DPTO_CNMBR' in feature['properties']:
        departamentos.add(feature['properties']['DPTO_CNMBR'])

carpetas_creadas = 0

for depto in departamentos:
    dep_key = re.sub(r'\s+', '_', depto).lower()
    
    # IDs basados en datos_politicos.js
    ids = [
        f"senador_1_{dep_key}",
        f"senador_2_{dep_key}",
        f"rep_1_{dep_key}",
        f"rep_2_{dep_key}"
    ]
    
    for politico_id in ids:
        dir_path = os.path.join(fotos_base_dir, politico_id)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            # Crear un archivo de foto genérica (.svg para que funcione en web directamente)
            # O guardar como foto.jpg simulada (el navegador puede renderizar SVG si se lo indicamos o usamos foto.svg)
            # Para coincidir con la URL, usaremos foto.svg (modificaré datos_politicos.js para .svg)
            # Aunque si el usuario quiere reemplazarla por un .jpg, es mejor dejar la extensión como .jpg o .png y decirle que la reemplace.
            # Por simplicidad, guardaré la silueta SVG pero nombrada .svg, y el usuario la reemplaza por su .jpg.
            pass

        # Vamos a escribir foto.svg para el placeholder inicial
        placeholder_path = os.path.join(dir_path, 'foto.svg')
        if not os.path.exists(placeholder_path):
            with open(placeholder_path, 'w', encoding='utf-8') as sf:
                sf.write(svg_generico)
            carpetas_creadas += 1

print(f"Estructura completada. Se crearon fotos genéricas para {carpetas_creadas} carpetas en {fotos_base_dir}/")
