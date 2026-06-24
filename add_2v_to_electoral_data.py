import json
import csv
import sys
import re

print("Loading electoral_data.json...")
with open("electoral_data.json", "r", encoding="utf-8") as f:
    electoral_data = json.load(f)

csv_path = "MMV_XXX_01_000_XXX_XX_XX_XXX_1000 2v ant.csv"
print(f"Reading {csv_path}...")

def normalize_text(text):
    if not text:
        return ""
    text = str(text).upper().strip()
    text = text.replace('?', 'A').replace('Á', 'A')
    text = text.replace('?', 'E').replace('É', 'E')
    text = text.replace('?', 'I').replace('Í', 'I')
    text = text.replace('"', 'O').replace('Ó', 'O')
    text = text.replace('s', 'U').replace('Ú', 'U')
    text = text.replace("'", 'N').replace('Ñ', 'N')
    text = text.replace('?', 'A') # Fallback for Ivan Cepeda and others that get ? instead of Á/Í
    return text

with open(csv_path, mode='r', encoding='latin1') as f:
    reader = csv.DictReader(f, delimiter=';')
    count = 0
    for row in reader:
        try:
            votos = int(row['VOTOS'])
        except ValueError:
            votos = 0
            
        muni = normalize_text(row['MUNNOMBRE'])
        zona = 'Zona ' + str(int(row['ZONA']))
        puesto = str(row['PUESTO']).zfill(2)
        mesa = str(row['MESA']).zfill(3)
        cand = normalize_text(row['CANNOMBRE'])
        
        # fix cand name
        if 'ABELARDO' in cand: cand = 'ABELARDO DE LA ESPRIELLA'
        elif 'CEPEDA' in cand: cand = 'IVAN CEPEDA CASTRO'
        elif 'BLANCO' in cand: cand = 'VOTOS EN BLANCO'
        elif 'NO MARCADOS' in cand: cand = 'VOTOS NO MARCADOS'
        elif 'NULOS' in cand: cand = 'VOTOS NULOS'
        else: continue
        
        if muni in electoral_data['hierarchy']:
            if zona in electoral_data['hierarchy'][muni]:
                if puesto in electoral_data['hierarchy'][muni][zona]:
                    p_info = electoral_data['hierarchy'][muni][zona][puesto]
                    if 'tables_2v' not in p_info:
                        p_info['tables_2v'] = {}
                    if mesa not in p_info['tables_2v']:
                        p_info['tables_2v'][mesa] = {
                            'ABELARDO DE LA ESPRIELLA': 0,
                            'IVAN CEPEDA CASTRO': 0,
                            'VOTOS EN BLANCO': 0,
                            'VOTOS NO MARCADOS': 0,
                            'VOTOS NULOS': 0
                        }
                    p_info['tables_2v'][mesa][cand] += votos
        count += 1
        if count % 100000 == 0:
            print(f"Processed {count} rows")

print("Saving electoral_data.json...")
with open("electoral_data.json", "w", encoding="utf-8") as f:
    json.dump(electoral_data, f, ensure_ascii=False)

print("Done!")
