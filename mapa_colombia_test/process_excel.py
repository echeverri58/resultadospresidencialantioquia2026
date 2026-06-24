import pandas as pd
import json
import re

df = pd.read_excel('Representantes_Camara_Colombia_Organizado.xlsx', sheet_name='Listado Completo', header=2)
df.columns = ['Departamento', 'Nombre del Representante', 'Partido o Coalición']
df = df.dropna(subset=['Departamento', 'Nombre del Representante'])

deps = {}
for index, row in df.iterrows():
    dep_name = str(row['Departamento']).strip()
    rep_name = str(row['Nombre del Representante']).strip()
    partido = str(row['Partido o Coalición']).strip() if pd.notna(row['Partido o Coalición']) else 'Independiente'
    
    if dep_name not in deps:
        deps[dep_name] = []
    deps[dep_name].append({
        'nombre': rep_name,
        'partido': partido
    })

js_code = """// Función para obtener datos de prueba/reales por cada departamento.
window.datosReales = %s;

function obtenerPoliticos(departamento) {
    const depName = departamento;
    const depKey = departamento.replace(/\s+/g, '_').toLowerCase();
    
    // Normalizar texto (quitar tildes y pasar a minusculas)
    const normalizar = (texto) => texto.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
    const depNormalizado = normalizar(departamento);
    
    // Ajustar casos especiales como "Bogotá, D.C." en el geojson vs "Bogotá" en Excel
    let depMatch = Object.keys(window.datosReales).find(k => {
        let excelDep = normalizar(k);
        return excelDep === depNormalizado || 
               (depNormalizado.includes("bogota") && excelDep.includes("bogota")) ||
               (depNormalizado.includes("san andres") && excelDep.includes("san andres")) ||
               (depNormalizado.includes("valle") && excelDep.includes("valle"));
    });
    
    let repsReales = [];
    if (depMatch) {
        repsReales = window.datosReales[depMatch].map((rep, index) => {
            return {
                id: "rep_" + (index + 1) + "_" + depKey,
                nombre: rep.nombre,
                partido: rep.partido,
                votos: "N/A", // No está en el excel
                foto_path: "fotos_politicos/rep_" + (index + 1) + "_" + depKey + "/foto.svg"
            };
        });
    } else {
        // Fallback si no hay datos
        repsReales = [
            {
                id: "rep_1_" + depKey,
                nombre: "No hay datos (" + departamento + ")",
                partido: "N/A",
                votos: "N/A",
                foto_path: "fotos_politicos/rep_1_" + depKey + "/foto.svg"
            }
        ];
    }
    
    return {
        senadores: [
            {
                id: "senador_1_" + depKey,
                nombre: "Juan Pérez (" + departamento + ")",
                partido: "Partido Liberal",
                votos: "125,000",
                foto_path: "fotos_politicos/senador_1_" + depKey + "/foto.svg"
            },
            {
                id: "senador_2_" + depKey,
                nombre: "María Rodríguez (" + departamento + ")",
                partido: "Partido Conservador",
                votos: "98,500",
                foto_path: "fotos_politicos/senador_2_" + depKey + "/foto.svg"
            }
        ],
        representantes: repsReales
    };
}
""" % json.dumps(deps, ensure_ascii=False, indent=4)

with open('datos_politicos.js', 'w', encoding='utf-8') as f:
    f.write(js_code)
