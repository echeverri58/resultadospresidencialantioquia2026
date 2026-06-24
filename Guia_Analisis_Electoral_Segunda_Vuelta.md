# Guía Completa de Análisis Electoral: Segunda Vuelta Presidencial

Este documento recopila las metodologías y enfoques analíticos que se pueden aplicar al comparar los resultados de una primera y segunda vuelta presidencial, cruzando datos a nivel de puesto de votación, barrio, comuna o municipio.

---

## 1. Análisis Fundamentales y de Comportamiento

### A. Análisis de Migración y Transferencia de Votos (El destino de los "votos huérfanos")
Busca entender hacia dónde se fueron los votos de los candidatos que no pasaron a segunda vuelta.
*   **Matrices de Transición (Inferencia Ecológica):** Estimación estadística de qué porcentaje de los votantes de un candidato eliminado migraron hacia el Candidato A, el Candidato B, el voto en blanco o la abstención.
*   **Correlación en fortines políticos:** Filtrar los puestos de votación donde los candidatos eliminados eran fuertes (ej. >30% de votos en 1ra vuelta) y observar quién fue el mayor beneficiario en esos puntos exactos durante la 2da vuelta.

### B. Dinámica de la Abstención y Movilización (Los nuevos votantes)
Analizar si un candidato ganó convenciendo a indecisos o movilizando a personas que no habían votado antes.
*   **Caza de "Nuevos Votantes":** Identificar los puestos de votación donde la abstención se redujo. Al cruzar esto con el crecimiento de los finalistas, se infiere hacia qué campaña se fue ese "voto nuevo" activado a última hora.
*   **Abstención de Castigo:** Identificar puestos donde la participación cayó. Frecuente en zonas donde el candidato favorito local no pasó a segunda vuelta y sus votantes prefirieron no participar.

### C. Dinámica del Voto en Blanco y Votos Nulos
*   **Voto Refugio / Voto Protesta:** Identificar en qué regiones o estratos socioeconómicos creció más el voto en blanco respecto a la primera vuelta, señalando qué demografías se sintieron menos representadas por los dos finalistas.

### D. Techos Electorales y Consolidación de Territorios
*   **Análisis de Crecimiento:** Medir el crecimiento porcentual de cada candidato respecto a su propia votación de primera vuelta.
*   **Fidelización vs. Expansión:** Clasificar los puestos en "Fortines" (donde ya había ganado) y "Zonas de Expansión" (donde había perdido). Esto indica si el candidato ganó exprimiendo más votos de su base o penetrando territorios hostiles.

### E. Análisis Geoespacial y Sociodemográfico
Cruce de resultados electorales con datos censales o mapas (GeoJSON):
*   **Brecha Urbano/Rural:** Comparar el comportamiento de las grandes ciudades frente a las subregiones y periferias.
*   **Voto por Estrato/Nivel Socioeconómico:** Analizar si la transferencia de votos varió según el estrato (ej. si los estratos altos y bajos migraron hacia candidatos distintos en la segunda vuelta).

---

## 2. Análisis Avanzados y Estratégicos

### F. Análisis Forense y Detección de Anomalías (Antifraude)
Crucial para la vigilancia electoral el mismo día de las elecciones:
*   **Ley de Benford:** Aplicar este principio a la distribución de los primeros dígitos de los votos por mesa para detectar desviaciones estadísticas que sugieran manipulación de formularios (E-14).
*   **Mesas "Atípicas" (Outliers):** Detección de mesas con participación atípicamente alta (>90%), picos anormales de votos nulos, o mesas donde un candidato obtiene el 100% de los votos.

### G. Análisis de "Zonas Péndulo" (Swing Regions)
*   **Lugares Bisagra:** Identificar municipios o comunas históricamente divididos (ej. 50/50) y ver hacia qué lado se "rompió" el empate en la segunda vuelta. Estas zonas suelen decidir elecciones cerradas.
*   **Zonas de Volatilidad:** Lugares que cambiaron radicalmente su tendencia política entre elecciones pasadas y la actual, investigando los motivos de ese giro.

### H. Voto de Opinión vs. Voto de Maquinaria (Estructura)
*   Requiere cruzar los resultados de la 2da vuelta presidencial con las elecciones legislativas (Congreso) recientes. 
*   Mide qué tanto el resultado de un candidato dependió de los votos de los senadores/representantes aliados (maquinaria local) versus los votos obtenidos por encima de esa estructura (voto de opinión libre).

### I. Análisis del Ingreso de la Información (El factor "Tiempo")
*   **Curva de Boletines:** Analizar la brecha entre candidatos a medida que la Registraduría emite los boletines (del 1 al N).
*   Permite entender si el "voto tardío" (usualmente rural o de periferia) favoreció a un candidato específico y ayuda a detectar "saltos" atípicos en la tendencia a última hora.

### J. Elasticidad de la Participación
*   **Sensibilidad a la participación:** Un modelo estadístico para responder: por cada 1% que sube la participación general, ¿qué candidato crece más? Indica si un candidato depende de la alta movilización masiva para ganar o si tiene una base pequeña pero inamovible (le conviene la baja participación).

### K. Índice de Polarización Local
*   Calcular métricas para ver si los territorios se "homogeneizaron" (ej. el ganador arrasa con 80%) o si la mayoría de los lugares quedaron fuertemente divididos (55% a 45%), y cómo esto cambió respecto a la primera vuelta.

### L. Eficiencia de Campaña
*   Si se dispone de datos de inversión o agenda, se cruza el *crecimiento de votos en 2da vuelta* vs. *inversión en publicidad/número de visitas del candidato* por región, para calcular el Retorno de Inversión (ROI) electoral.
