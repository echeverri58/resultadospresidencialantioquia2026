import fitz
import os
import re

pdf_path = r"C:\Users\ASUS vivobook\Desktop\Elecciones presidenciales\mapa_colombia_test\6 Senado 2026 solo para Diego.pdf"
output_dir = r"C:\Users\ASUS vivobook\Desktop\Elecciones presidenciales\fotos_pdf_senadores"

os.makedirs(output_dir, exist_ok=True)

# Nombres a buscar en caso de no poder extraer por posicion
senators = [
    "Diana Carolina Corcho Mejía", "Pedro Hernando Flórez Porras", "Carmen Patricia Caicedo Omar",
    "Wilson Néber Arias Castillo", "Laura Cristina Ahumada García", "Walter Alfonso Rodríguez Chaparro",
    "Aída Yolanda Avella Esquivel", "Ferney Silva Idrobo", "Yuly Esmeralda Hernández Silva",
    "Carlos Alberto Benavides Mora", "Sandra Claudia Chindoy Jamioy", "Jorge Alejandro Ocampo Giraldo",
    "María Eugenia Londoño Ocampo", "Alex Xavier Flórez Hernández", "Kamelia Edith Zuluaga Navarro",
    "Agmeth José Escaf Tijerino", "Yaini Isabel Contreras Jiménez", "Cristian Kevin Gómez Paz",
    "Isabel Cristina Zuleta López", "Martín Alonso Caicedo Carabalí", "Deisy Johana Osorio Márquez",
    "David Ricardo Racero Mayorca", "Deyci Alejandra Omaña Ortiz", "Orlando Miguel De La Hoz García",
    "Mary Jurado Palomino", "Andrés Eduardo Forero Molina", "Rafael Nieto Loaiza",
    "Claudia Margarita Zuleta Murgas", "Hernán Darío Cadavid Márquez", "Julia Correa Nuttin",
    "Carlos Manuel Meisel Vergara", "Christian Munir Garcés Aljure", "María Clara Posada Caicedo",
    "Honorio Miguel Henríquez Pinedo", "Josué Alirio Barrera Rodríguez", "Esteban Quintero Cardona",
    "Enrique Cabrales Baquero", "Óscar Leonardo Villamizar Meneses", "Juan Fernando Espinal Ramírez",
    "María Angélica Guerra López", "Juan Fernando Caicedo Callejas", "Zandra María Bernal Rincón",
    "Lidio Arturo García Turbay", "Yessid Enrique Pulgar Daza", "María Eugenia Lopera Monsalve",
    "Alix Yirley Vargas Torrado", "Gersson Vargas Valdeleón", "Camilo Andrés Torres Villalba",
    "Leonardo de Jesús Gallego Arroyave", "Óscar Hernán Sánchez León", "Héctor Olimpo Espinosa Oliver",
    "Fabio Raúl Amín Saleme", "Santiago Montoya Montoya", "Álvaro Henry Monedero Rivera",
    "Laura Ester Fortich Sánchez", "Jonathan Ferney Pulido Hernández", "Luis Carlos Rúa Sánchez",
    "Andrea Padilla Villarraga", "John Edickson Amaya Rodríguez", "Ariel Fernando Ávila Martínez",
    "Gustavo Adolfo Moreno Hurtado", "José Gutemberg Macea Gómez", "Duvalier Sánchez Arango",
    "Wilder Iberson Escobar Ortiz", "Luis Alfonso Mejía Núñez", "Carlos Eduardo Enríquez Caicedo",
    "Nadya Georgette Blel Scaff", "Wadith Alberto Manzur Imbett", "Daniel Restrepo Carmona",
    "David Alejandro Barguil Assis", "Miguel Ángel Barreto Castillo", "Diela Liliana Benavides Solarte",
    "Marcos Daniel Pineda García", "Luis Eduardo Díaz Mateus", "Juan Carlos García Gómez",
    "Santiago Barreto Triana", "Norma Hurtado Sánchez", "Juan Carlos Garcés Rojas",
    "Wilmer Ramiro Carrillo Mendoza", "Alfredo Rafael Deluque Zuleta", "John Moisés Besaile Fayad",
    "Ana Paola García Soto", "María Irma Noreña Arboleda", "Antonio José Correa Jiménez",
    "José Alfredo Gnecco Zuleta", "Edgardo Miguel Espitia Cabrales", "José Nicolás Gómez Medina",
    "Selmen David Arana Cano", "Didier Lobo Chinchilla", "Gonzalo Dimas Baute González",
    "Carlos Mario Farelo Daza", "Nelson Javier López Rodríguez", "Ana Paola Agudelo García",
    "Manuel Antonio Vírguez Piraquive", "Carlos Eduardo Guevara Villabón", "Jennifer Dalley Pedraza Sandoval",
    "María Lucía Villalba Gómez", "Enrique Gómez Martínez", "Sara Jimena Castellanos Rodríguez",
    "Germán Andrés Rodríguez Prieto", "John Alejandro Bermeo Rodríguez", "Martha Isabel Peralta Epieyú",
    "José Wilman Tumbo Chepe"
]

doc = fitz.open(pdf_path)
image_count = 0

def clean_name(name):
    name = re.sub(r'[\\/*?:"<>|\n]', "", name)
    return name.strip()

for page_num in range(len(doc)):
    page = doc[page_num]
    text_blocks = page.get_text("blocks")
    
    # bloques de texto
    text_blocks = [b for b in text_blocks if b[6] == 0 and b[4].strip()]
    
    images = page.get_images(full=True)
    
    for img_index, img in enumerate(images):
        xref = img[0]
        rects = page.get_image_rects(xref)
        if not rects:
            continue
        rect = rects[0]
        
        best_dist = float('inf')
        best_text = f"pagina_{page_num+1}_img_{img_index+1}"
        
        for b in text_blocks:
            bx0, by0, bx1, by1, text, _, _ = b
            
            # Buscar el texto que esté justo debajo de la imagen
            if by0 >= rect.y1 - 20: 
                dist = by0 - rect.y1
                # Check overlap horizontal
                if max(rect.x0, bx0) <= min(rect.x1, bx1) or abs((rect.x0+rect.x1)/2 - (bx0+bx1)/2) < 100:
                    if dist < best_dist:
                        best_dist = dist
                        best_text = text.split('\n')[0]
                        
        # Si el texto extraído no es un senador, intentar buscar el nombre del senador en todo el texto del bloque
        filename_found = False
        if best_text != f"pagina_{page_num+1}_img_{img_index+1}":
            for sen in senators:
                if sen.lower() in best_text.lower():
                    best_text = sen
                    filename_found = True
                    break
                    
        base_image = doc.extract_image(xref)
        image_bytes = base_image["image"]
        image_ext = base_image["ext"]
        
        filename = clean_name(best_text)
        if not filename:
            filename = f"pagina_{page_num+1}_img_{img_index+1}"
            
        filepath = os.path.join(output_dir, f"{filename}.{image_ext}")
        
        counter = 1
        while os.path.exists(filepath):
            filepath = os.path.join(output_dir, f"{filename}_{counter}.{image_ext}")
            counter += 1
            
        with open(filepath, "wb") as f:
            f.write(image_bytes)
        image_count += 1
        print(f"Extraída: {filepath}")

print(f"\nExtracción completada. {image_count} imágenes guardadas en {output_dir}")
