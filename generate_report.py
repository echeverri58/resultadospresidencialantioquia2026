# -*- coding: utf-8 -*-
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT

def main():
    with open('barrios_resultados.geojson', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Extract properties
    features = data.get('features', [])
    records = []
    for feat in features:
        props = feat.get('properties', {})
        name = props.get('nombre', 'Desconocido')
        opp = props.get('opportunity', 0)
        abst = props.get('abstencion', 0)
        otros = props.get('otros', 0)
        if opp > 0:
            records.append({'name': name, 'opportunity': opp, 'abstencion': abst, 'otros': otros})

    # Sort and get top 50
    records.sort(key=lambda x: x['opportunity'], reverse=True)
    top_50 = records[:50]

    # Create PDF
    pdf_filename = 'Informe_Inteligencia_Electoral_Ivan_Cepeda.pdf'
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Title'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#166534'),
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569'),
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    author_style = ParagraphStyle(
        'AuthorInfo',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#0f172a'),
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica-Oblique'
    )
    
    heading_style = ParagraphStyle(
        'Heading',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=15,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        spaceAfter=8
    )
    
    story = []
    
    # HEADER
    story.append(Paragraph("INFORME ESTRATÉGICO DE INTELIGENCIA ELECTORAL", title_style))
    story.append(Paragraph("Focalización Territorial y Análisis de Datos para la Recuperación y Captación de Votos: Campaña Iván Cepeda", subtitle_style))
    story.append(Paragraph("<b>Creado por John Alexander Echeverry Ocampo</b><br/>Politólogo y Analista de Datos<br/>Correo: echeverri58@gmail.com | WhatsApp: 3217466359", author_style))
    
    # SECTION 1
    story.append(Paragraph("1. Contexto Político y Estratégico", heading_style))
    story.append(Paragraph("El escenario electoral actual en Antioquia y Medellín exige una superación de la política tradicional basada únicamente en medios masivos. Como analista político, es evidente que el dominio hegemónico de las candidaturas de derecha en la región requiere una táctica de <i>micro-targeting</i> territorial. Este informe no busca persuadir a los votantes consolidados de la oposición, sino que aplica ciencia de datos para identificar los nichos donde existe un electorado 'latente', desencantado o periférico.", body_style))
    story.append(Paragraph("La estrategia central para la campaña de Iván Cepeda debe enfocarse en una recuperación quirúrgica de votos. En lugar de dispersar recursos de campaña por toda la geografía, el análisis de datos nos permite señalar exactamente qué barrios y veredas ofrecen la menor resistencia ideológica y el mayor potencial de crecimiento matemático.", body_style))
    
    # SECTION 2
    story.append(Paragraph("2. Metodología: La Construcción del Índice de 'Oportunidad'", heading_style))
    story.append(Paragraph("El ranking de los Top 50 lugares no es fortuito; es el resultado de un modelo matemático diseñado para maximizar el Retorno de Inversión (ROI) político. La métrica principal se calcula mediante la siguiente fórmula estructurada:", body_style))
    story.append(Paragraph("<b>Índice de Oportunidad = (Abstención Estimada × Afinidad hacia la Izquierda) + Votos 'Otros' (Blanco y Nulo)</b>", ParagraphStyle('Formula', parent=body_style, alignment=TA_CENTER, textColor=colors.HexColor('#047857'), fontName='Helvetica-Bold')))
    
    story.append(Paragraph("Desde la ciencia política, justificamos cada componente de este modelo así:", body_style))
    story.append(Paragraph("• <b>Abstención Ponderada (Afinidad a la Izquierda):</b> No toda abstención es igual. Movilizar a un abstencionista en un bastión conservador es ineficiente y costoso. Para este reporte, se ha implementado una mejora drástica: <b>el potencial electoral (y por ende la abstención) se calcula extrayendo el dato exacto mesa a mesa y puesto a puesto del censo de la primera vuelta presidencial 2026</b>, abandonando proyecciones genéricas por comuna. Al multiplicar la abstención real de la zona por el porcentaje histórico de votos progresistas, focalizamos nuestros esfuerzos de movilización exclusivamente en aquellos ciudadanos que simpatizan con el proyecto político, pero que no salieron a votar.", bullet_style))
    story.append(Paragraph("• <b>Voto en Blanco y Nulo ('Otros'):</b> Este es el electorado más valioso. Es un ciudadano que hizo el esfuerzo físico de salir a votar (venciendo la abstención), pero que rechazó visceralmente el establecimiento de derecha al no encontrar una alternativa que lo convenciera. Captar a este elector no requiere convencerlo del problema, sino presentarse como la solución viable y estructurada. Es un voto de castigo que Iván Cepeda puede capitalizar con un mensaje de firmeza institucional y paz.", bullet_style))
    
    # SECTION 3
    story.append(Paragraph("3. Rigurosidad y Fuentes de Datos", heading_style))
    story.append(Paragraph("Para garantizar que la operación en territorio tenga fundamentos empíricos sólidos, este análisis cruza bases de datos oficiales de alto volumen:", body_style))
    story.append(Paragraph("• <b>Censo y Potencial Electoral 2026:</b> Se extrajo el censo exacto por puesto de votación del archivo <i>Divipole Antioquia.xlsx (Primera vuelta presidencial 2026)</i>. Esto provee una precisión quirúrgica sobre cuántos votantes reales existen en cada barrio, mejorando radicalmente la métrica de abstención.", bullet_style))
    story.append(Paragraph("• <b>Registraduría Nacional del Estado Civil (RNEC):</b> Utilizamos el archivo crudo de resultados presidenciales (<i>MMV_ANTIOQUIA_2022_1v.csv</i> y <i>MMV_NACIONAL_PRESIDENTE_2022_1v.csv</i>), lo que nos da el comportamiento histórico y de afinidad ideológica en las urnas mesa a mesa, eliminando sesgos de encuestas.", bullet_style))
    story.append(Paragraph("• <b>Sistemas de Información Geográfica (GIS):</b> Mediante polígonos cartográficos (<i>barrios_resultados.geojson</i>), transformamos puestos abstractos de votación en realidades urbanas georreferenciadas. La campaña no hace proselitismo en un 'Puesto de Votación', lo hace en las calles de un 'Barrio'. Este cruce permite enviar a los equipos de base exactamente a la zona correcta.", bullet_style))
    
    story.append(PageBreak())
    
    # SECTION 4
    story.append(Paragraph("4. Ranking Operativo: Top 50 Zonas Estratégicas", heading_style))
    story.append(Paragraph("La siguiente tabla expone las 50 zonas con mayor volumen de votos recuperables (Oportunidad). Se recomienda asignar a los coordinadores territoriales más experimentados a los primeros 15 barrios de esta lista, ejecutando campañas de 'puerta a puerta' y reuniones comunitarias, pues albergan la masa crítica necesaria para inclinar la balanza.", body_style))
    story.append(Spacer(1, 10))
    
    table_data = [['Ranking', 'Nombre del Barrio / Vereda (Sector)', 'Volumen Recuperable\n(Votos Objetivo)']]
    for i, r in enumerate(top_50):
        table_data.append([str(i+1), r['name'], f"{r['opportunity']:,}"])
        
    t = Table(table_data, colWidths=[60, 300, 140], repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')])
    ]))
    
    story.append(t)
    
    # SECTION 5
    story.append(Spacer(1, 20))
    story.append(Paragraph("5. Conclusión y Ruta de Acción", heading_style))
    story.append(Paragraph("En conclusión, el éxito electoral no depende de gritar más fuerte en todas partes, sino de hablar con precisión donde matemáticamente se puede ganar. Movilizar a los abstencionistas afines e integrar a quienes votaron en blanco en estas 50 zonas constituye la maniobra más eficiente en relación costo-beneficio para la campaña de Iván Cepeda. La directriz política es clara: trasladar el esfuerzo logístico y discursivo prioritariamente a estos polígonos urbanos.", body_style))
    
    doc.build(story)
    print("PDF Generated successfully as Informe_Inteligencia_Electoral_Ivan_Cepeda.pdf")

if __name__ == '__main__':
    main()
