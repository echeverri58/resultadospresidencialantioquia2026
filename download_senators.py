import os
import time
import urllib.request
import json

try:
    from duckduckgo_search import DDGS
except ImportError:
    print("duckduckgo_search is not installed.")
    exit(1)

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

output_dir = "fotos_senadores"
os.makedirs(output_dir, exist_ok=True)

status = {}

with DDGS() as ddgs:
    for name in senators:
        filepath = os.path.join(output_dir, f"{name}.jpg")
        if os.path.exists(filepath):
            print(f"[X] {name} (Ya existe)")
            status[name] = True
            continue
            
        print(f"Buscando a {name}...")
        try:
            results = list(ddgs.images(f"{name} senador colombia", max_results=1))
            if results:
                image_url = results[0]['image']
                req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=10) as response, open(filepath, 'wb') as f:
                    f.write(response.read())
                print(f"[X] Descargado: {name}")
                status[name] = True
            else:
                print(f"[ ] No se encontró imagen para: {name}")
                status[name] = False
        except Exception as e:
            print(f"[ ] Error con {name}: {e}")
            status[name] = False
        time.sleep(1)

with open('download_status.json', 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

print("\nTerminado.")
