import pandas as pd
import sys
import numpy as np

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

file_1v = 'MMV_XXX_01_000_XXX_XX_XX_XXX_1000.csv'
file_2v = 'MMV_XXX_01_000_XXX_XX_XX_XXX_1000 2v ant.csv'

print("Cargando datos...")
df_1v = pd.read_csv(file_1v, sep=';', encoding='latin1')
df_2v = pd.read_csv(file_2v, sep=';', encoding='latin1')

df_1v['VOTOS'] = pd.to_numeric(df_1v['VOTOS'], errors='coerce').fillna(0)
df_2v['VOTOS'] = pd.to_numeric(df_2v['VOTOS'], errors='coerce').fillna(0)

# Asegurar que ambos df tengan las mismas comunas y puestos para la comparación real
# Ya sabemos que 2da vuelta solo tiene Medellín, vamos a filtrar 1ra vuelta para Medellín
df_1v = df_1v[df_1v['MUNNOMBRE'].str.contains('MEDELLIN', case=False, na=False)]

group_cols = ['MUNNOMBRE', 'ZONA', 'PUESTO', 'PUESNOMBRE']

def agg_puesto(df):
    return df.groupby(group_cols + ['CANNOMBRE'])['VOTOS'].sum().unstack(fill_value=0).reset_index()

puestos_1v = agg_puesto(df_1v)
puestos_2v = agg_puesto(df_2v)

puestos_1v = puestos_1v.add_suffix('_1v')
puestos_2v = puestos_2v.add_suffix('_2v')

puestos_1v = puestos_1v.rename(columns={'MUNNOMBRE_1v': 'MUNNOMBRE', 'ZONA_1v': 'ZONA', 'PUESTO_1v': 'PUESTO', 'PUESNOMBRE_1v': 'PUESNOMBRE'})
puestos_2v = puestos_2v.rename(columns={'MUNNOMBRE_2v': 'MUNNOMBRE', 'ZONA_2v': 'ZONA', 'PUESTO_2v': 'PUESTO', 'PUESNOMBRE_2v': 'PUESNOMBRE'})

df_cruce = pd.merge(puestos_1v, puestos_2v, on=['MUNNOMBRE', 'ZONA', 'PUESTO', 'PUESNOMBRE'], how='inner').fillna(0)

candidatos_1v = [c for c in puestos_1v.columns if c not in group_cols]
candidatos_2v = [c for c in puestos_2v.columns if c not in group_cols]

df_cruce['TOTAL_VOTOS_1v'] = df_cruce[candidatos_1v].sum(axis=1)
df_cruce['TOTAL_VOTOS_2v'] = df_cruce[candidatos_2v].sum(axis=1)
df_cruce['DIF_PARTICIPACION'] = df_cruce['TOTAL_VOTOS_2v'] - df_cruce['TOTAL_VOTOS_1v']

finalistas = [c for c in candidatos_2v if 'VOTOS' not in c]
finalistas_clean = [f.replace('_2v', '') for f in finalistas]
otros_cand_1v = [c for c in candidatos_1v if c.replace('_1v', '') not in finalistas_clean and 'VOTOS' not in c]

df_cruce['BOLSA_HUERFANOS_1v'] = df_cruce[otros_cand_1v].sum(axis=1)

for f in finalistas:
    f_clean = f.replace('_2v', '')
    if f_clean + '_1v' in df_cruce.columns:
        df_cruce[f'CRECIMIENTO_{f_clean}'] = df_cruce[f] - df_cruce[f_clean + '_1v']

print(f"\n=== RESUMEN GLOBAL (SOLO MUNICIPIOS EN COMÚN, EJ. MEDELLÍN) ===")
print(f"Total Votos 1ra Vuelta: {df_cruce['TOTAL_VOTOS_1v'].sum():,.0f}")
print(f"Total Votos 2da Vuelta: {df_cruce['TOTAL_VOTOS_2v'].sum():,.0f}")
print(f"Diferencia de Participación: {df_cruce['DIF_PARTICIPACION'].sum():,.0f}")
print(f"Bolsa de Votos Huérfanos (1ra Vuelta): {df_cruce['BOLSA_HUERFANOS_1v'].sum():,.0f}")

print("\n--- DESEMPEÑO FINALISTAS ---")
for f in finalistas:
    f_clean = f.replace('_2v', '')
    if f_clean + '_1v' in df_cruce.columns:
        crec = df_cruce[f'CRECIMIENTO_{f_clean}'].sum()
        votos_1v = df_cruce[f_clean + '_1v'].sum()
        votos_2v = df_cruce[f].sum()
        pct_crec = (crec / votos_1v) * 100 if votos_1v > 0 else 0
        print(f"{f_clean}: 1v={votos_1v:,.0f} | 2v={votos_2v:,.0f} | Crecimiento={crec:,.0f} (+{pct_crec:.1f}%)")

# Generar archivo Markdown como Walkthrough
with open('resultados_analisis.md', 'w', encoding='utf-8') as md:
    md.write("# Análisis de Resultados: Primera vs Segunda Vuelta (Medellín 2026)\n\n")
    md.write("Este análisis cruza los datos de los puestos de votación de la ciudad de Medellín para observar el comportamiento entre la primera y la segunda vuelta.\n\n")
    md.write("## 1. Métricas Globales de Participación\n\n")
    md.write(f"- **Votos 1ra Vuelta:** {df_cruce['TOTAL_VOTOS_1v'].sum():,.0f}\n")
    md.write(f"- **Votos 2da Vuelta:** {df_cruce['TOTAL_VOTOS_2v'].sum():,.0f}\n")
    md.write(f"- **Diferencia de Participación:** {df_cruce['DIF_PARTICIPACION'].sum():,.0f} votos\n")
    md.write(f"- **Votos Huérfanos (candidatos eliminados):** {df_cruce['BOLSA_HUERFANOS_1v'].sum():,.0f} votos disponibles para ser captados.\n\n")
    
    md.write("## 2. Crecimiento de los Finalistas\n\n")
    md.write("| Candidato | Votos 1ra Vuelta | Votos 2da Vuelta | Crecimiento Absoluto | % Crecimiento |\n")
    md.write("|---|---|---|---|---|\n")
    for f in finalistas:
        f_clean = f.replace('_2v', '')
        if f_clean + '_1v' in df_cruce.columns:
            crec = df_cruce[f'CRECIMIENTO_{f_clean}'].sum()
            votos_1v = df_cruce[f_clean + '_1v'].sum()
            votos_2v = df_cruce[f].sum()
            pct_crec = (crec / votos_1v) * 100 if votos_1v > 0 else 0
            md.write(f"| {f_clean} | {votos_1v:,.0f} | {votos_2v:,.0f} | {crec:,.0f} | {pct_crec:.1f}% |\n")
    
    md.write("\n## 3. Matriz de Correlación (Transferencia Inferida)\n\n")
    md.write("Correlación de Pearson entre los votos obtenidos por los candidatos eliminados en 1ra vuelta y el crecimiento de los finalistas en 2da vuelta (a nivel de puesto de votación). Una correlación más cercana a 1 sugiere una fuerte transferencia de votos.\n\n")
    
    correlations = []
    for cand_out in otros_cand_1v:
        if df_cruce[cand_out].sum() > 5000: # solo candidatos relevantes
            row = {'Candidato 1ra Vuelta': cand_out.replace('_1v', '')}
            for f in finalistas:
                f_clean = f.replace('_2v', '')
                if f_clean + '_1v' in df_cruce.columns:
                    # Correlación entre (votos candidato eliminado) vs (crecimiento candidato finalista)
                    corr = df_cruce[cand_out].corr(df_cruce[f'CRECIMIENTO_{f_clean}'])
                    row[f_clean] = corr
            correlations.append(row)
    
    corr_df = pd.DataFrame(correlations)
    md.write(corr_df.to_markdown(index=False))

print("Markdown generado exitosamente en 'resultados_analisis.md'.")
