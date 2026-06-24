import pandas as pd
import numpy as np

# Rutas de los archivos
file_1v = 'MMV_XXX_01_000_XXX_XX_XX_XXX_1000.csv'
file_2v = 'MMV_XXX_01_000_XXX_XX_XX_XXX_1000 2v ant.csv'
potencial_file = 'Potencial.xlsx'

print("Cargando datos de 1ra y 2da vuelta...")
df_1v = pd.read_csv(file_1v, sep=';', encoding='latin1')
df_2v = pd.read_csv(file_2v, sep=';', encoding='latin1')

# Convertir VOTOS a numérico (por si hay problemas de formato)
df_1v['VOTOS'] = pd.to_numeric(df_1v['VOTOS'], errors='coerce').fillna(0)
df_2v['VOTOS'] = pd.to_numeric(df_2v['VOTOS'], errors='coerce').fillna(0)

# Agrupar a nivel de Puesto
group_cols = ['MUNNOMBRE', 'ZONA', 'PUESTO', 'PUESNOMBRE']

def agg_puesto(df):
    return df.groupby(group_cols + ['CANNOMBRE'])['VOTOS'].sum().unstack(fill_value=0).reset_index()

puestos_1v = agg_puesto(df_1v)
puestos_2v = agg_puesto(df_2v)

# Añadir sufijos para poder cruzar
puestos_1v = puestos_1v.add_suffix('_1v')
puestos_2v = puestos_2v.add_suffix('_2v')

# Renombrar columnas base para el cruce
puestos_1v = puestos_1v.rename(columns={'MUNNOMBRE_1v': 'MUNNOMBRE', 'ZONA_1v': 'ZONA', 'PUESTO_1v': 'PUESTO', 'PUESNOMBRE_1v': 'PUESNOMBRE'})
puestos_2v = puestos_2v.rename(columns={'MUNNOMBRE_2v': 'MUNNOMBRE', 'ZONA_2v': 'ZONA', 'PUESTO_2v': 'PUESTO', 'PUESNOMBRE_2v': 'PUESNOMBRE'})

# Cruzar los DataFrames
print("Cruzando datos por Puesto de Votación...")
df_cruce = pd.merge(puestos_1v, puestos_2v, on=['MUNNOMBRE', 'ZONA', 'PUESTO', 'PUESNOMBRE'], how='outer').fillna(0)

# Calcular Totales de Participación
candidatos_1v = [c for c in puestos_1v.columns if c not in group_cols]
candidatos_2v = [c for c in puestos_2v.columns if c not in group_cols]

df_cruce['TOTAL_VOTOS_1v'] = df_cruce[candidatos_1v].sum(axis=1)
df_cruce['TOTAL_VOTOS_2v'] = df_cruce[candidatos_2v].sum(axis=1)
df_cruce['DIF_PARTICIPACION'] = df_cruce['TOTAL_VOTOS_2v'] - df_cruce['TOTAL_VOTOS_1v']

# Nombres de los finalistas (buscar los reales basándonos en los datos)
finalistas = [c for c in candidatos_2v if 'VOTOS' not in c]
print("Finalistas detectados en 2da vuelta:", finalistas)

for f in finalistas:
    f_clean = f.replace('_2v', '')
    if f_clean + '_1v' in df_cruce.columns:
        df_cruce[f'CRECIMIENTO_{f_clean}'] = df_cruce[f] - df_cruce[f_clean + '_1v']

# Identificar Votos Huérfanos
finalistas_clean = [f.replace('_2v', '') for f in finalistas]
otros_cand_1v = [c for c in candidatos_1v if c.replace('_1v', '') not in finalistas_clean and 'VOTOS' not in c]
df_cruce['BOLSA_HUERFANOS_1v'] = df_cruce[otros_cand_1v].sum(axis=1)

# Guardar resultados consolidados a nivel puesto
output_file = 'Analisis_Cruzado_Puestos_2026.csv'
df_cruce.to_csv(output_file, index=False, encoding='latin1')
print(f"Resultados exportados a {output_file}")

# Generar un resumen a nivel municipal
# Solo tomar las columnas numericas
cols_numericas = df_cruce.select_dtypes(include=[np.number]).columns.tolist()
resumen_mun = df_cruce.groupby('MUNNOMBRE')[cols_numericas].sum().reset_index()
resumen_mun_file = 'Analisis_Cruzado_Municipios_2026.csv'
resumen_mun.to_csv(resumen_mun_file, index=False, encoding='latin1')
print(f"Resumen por municipio exportado a {resumen_mun_file}")

# Imprimir métricas clave a nivel global
print("\n=== RESUMEN GLOBAL ===")
print(f"Total Votos 1ra Vuelta: {df_cruce['TOTAL_VOTOS_1v'].sum():,.0f}")
print(f"Total Votos 2da Vuelta: {df_cruce['TOTAL_VOTOS_2v'].sum():,.0f}")
print(f"Diferencia de Participación: {df_cruce['DIF_PARTICIPACION'].sum():,.0f}")
print(f"Bolsa de Votos Huérfanos (1ra Vuelta): {df_cruce['BOLSA_HUERFANOS_1v'].sum():,.0f}")

for f in finalistas:
    f_clean = f.replace('_2v', '')
    if f_clean + '_1v' in df_cruce.columns:
        crec = df_cruce[f'CRECIMIENTO_{f_clean}'].sum()
        votos_1v = df_cruce[f_clean + '_1v'].sum()
        votos_2v = df_cruce[f].sum()
        pct_crec = (crec / votos_1v) * 100 if votos_1v > 0 else 0
        print(f"{f_clean}: 1v={votos_1v:,.0f} | 2v={votos_2v:,.0f} | Crecimiento={crec:,.0f} (+{pct_crec:.1f}%)")

