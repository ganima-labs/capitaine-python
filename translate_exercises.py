#!/usr/bin/env python3
"""
Script pour traduire automatiquement les exercices python-basics.json
"""
import json
import sys

def translate_exercises():
    """Traduire tous les exercices en format multi-langue"""

    # Dictionnaires de traduction
    translations = {
        "03-conditions": {
            "title": {
                "fr": "Feu rouge/vert",
                "en": "Red/green light",
                "es": "Luz roja/verde",
                "de": "Rot/Grün Licht"
            },
            "prompt": {
                "fr": "Lis un mot (rouge/vert) et affiche 'STOP' si rouge, 'GO' si vert.",
                "en": "Read a word (red/green) and display 'STOP' if red, 'GO' if green.",
                "es": "Lee una palabra (rojo/verde) y muestra 'STOP' si es rojo, 'GO' si es verde.",
                "de": "Lies ein Wort (rot/grün) und zeige 'STOP' bei rot, 'GO' bei grün."
            },
            "explanation": {
                "fr": "input() lit ce que l'utilisateur tape. Le if/elif permet de faire des choix : si la couleur est 'rouge', on affiche 'STOP', sinon si c'est 'vert', on affiche 'GO'. Les conditions permettent à ton programme de réagir différemment selon la situation.",
                "en": "input() reads what the user types. The if/elif allows making choices: if the color is 'red', we display 'STOP', else if it's 'green', we display 'GO'. Conditions allow your program to react differently according to the situation.",
                "es": "input() lee lo que el usuario escribe. El if/elif permite hacer elecciones: si el color es 'rojo', mostramos 'STOP', si no, si es 'verde', mostramos 'GO'. Las condiciones permiten que tu programa reaccione diferente según la situación.",
                "de": "input() liest, was der Benutzer eingibt. Das if/elif ermöglicht Entscheidungen: Wenn die Farbe 'rot' ist, zeigen wir 'STOP', sonst wenn sie 'grün' ist, zeigen wir 'GO'. Bedingungen ermöglichen es Ihrem Programm, je nach Situation unterschiedlich zu reagieren."
            },
            "hints": {
                "fr": ["if couleur == 'rouge': print('STOP')", "elif couleur == 'vert': print('GO')"],
                "en": ["if color == 'red': print('STOP')", "elif color == 'green': print('GO')"],
                "es": ["if color == 'rojo': print('STOP')", "elif color == 'verde': print('GO')"],
                "de": ["if farbe == 'rot': print('STOP')", "elif farbe == 'grün': print('GO')"]
            }
        },
        "04-boucle-for": {
            "title": {
                "fr": "Compte 1 à 5",
                "en": "Count 1 to 5",
                "es": "Cuenta 1 a 5",
                "de": "Zähle 1 bis 5"
            },
            "prompt": {
                "fr": "Affiche les nombres de 1 à 5 chacun sur sa ligne.",
                "en": "Display numbers 1 to 5 each on its own line.",
                "es": "Muestra los números 1 a 5 cada uno en su línea.",
                "de": "Zeige die Zahlen 1 bis 5 jeweils in einer eigenen Zeile an."
            },
            "explanation": {
                "fr": "La boucle for répète des actions. range(1,6) génère les nombres 1,2,3,4,5. Pour chaque nombre, la boucle l'affiche avec print(i). C'est parfait pour répéter une tâche plusieurs fois !",
                "en": "The for loop repeats actions. range(1,6) generates numbers 1,2,3,4,5. For each number, the loop displays it with print(i). It's perfect for repeating a task multiple times!",
                "es": "El bucle for repite acciones. range(1,6) genera los números 1,2,3,4,5. Para cada número, el bucle lo muestra con print(i). ¡Es perfecto para repetir una tarea varias veces!",
                "de": "Die for-Schleife wiederholt Aktionen. range(1,6) erzeugt die Zahlen 1,2,3,4,5. Für jede Zahl zeigt die Schleife sie mit print(i) an. Es ist perfekt, um eine Aufgabe mehrmals zu wiederholen!"
            },
            "hints": {
                "fr": ["range(1,6) va de 1 à 5", "print(i) dans la boucle"],
                "en": ["range(1,6) goes from 1 to 5", "print(i) in the loop"],
                "es": ["range(1,6) va de 1 a 5", "print(i) en el bucle"],
                "de": ["range(1,6) geht von 1 bis 5", "print(i) in der Schleife"]
            }
        },
        "05-fonction-bonjour": {
            "title": {
                "fr": "Dis Bonjour",
                "en": "Say Hello",
                "es": "Di Hola",
                "de": "Sag Hallo"
            },
            "prompt": {
                "fr": "Écris une fonction bonjour(nom) qui renvoie 'Bonjour <nom>' (sans l'afficher).",
                "en": "Write a function hello(name) that returns 'Hello <name>' (without displaying it).",
                "es": "Escribe una función hola(nombre) que devuelve 'Hola <nombre>' (sin mostrarlo).",
                "de": "Schreibe eine Funktion hallo(name), die 'Hallo <name>' zurückgibt (ohne sie anzuzeigen)."
            },
            "explanation": {
                "fr": "Une fonction est un bloc de code réutilisable. def bonjour(nom): crée la fonction. return renvoie une valeur sans l'afficher. On peut l'utiliser plusieurs fois avec différents noms. C'est comme une recette de cuisine !",
                "en": "A function is a reusable code block. def hello(name): creates the function. return returns a value without displaying it. We can use it multiple times with different names. It's like a cooking recipe!",
                "es": "Una función es un bloque de código reutilizable. def hola(nombre): crea la función. return devuelve un valor sin mostrarlo. Podemos usarla varias veces con diferentes nombres. ¡Es como una receta de cocina!",
                "de": "Eine Funktion ist ein wiederverwendbarer Codeblock. def hallo(name): erstellt die Funktion. return gibt einen Wert zurück, ohne ihn anzuzeigen. Wir können ihn mehrmals mit verschiedenen Namen verwenden. Es ist wie ein Kochrezept!"
            },
            "hints": {
                "fr": ["def bonjour(nom):", "return 'Bonjour ' + nom"],
                "en": ["def hello(name):", "return 'Hello ' + name"],
                "es": ["def hola(nombre):", "return 'Hola ' + nombre"],
                "de": ["def hallo(name):", "return 'Hallo ' + name"]
            }
        },
        "06-somme-1-a-n": {
            "title": {
                "fr": "Addition magique",
                "en": "Magic addition",
                "es": "Adición mágica",
                "de": "Magische Addition"
            },
            "prompt": {
                "fr": "Écris une fonction somme(n) qui renvoie 1 + 2 + ... + n.",
                "en": "Write a function sum(n) that returns 1 + 2 + ... + n.",
                "es": "Escribe una función suma(n) que devuelve 1 + 2 + ... + n.",
                "de": "Schreibe eine Funktion summe(n), die 1 + 2 + ... + n zurückgibt."
            },
            "explanation": {
                "fr": "On utilise une variable 'total' qui commence à 0. La boucle ajoute chaque nombre de 1 à n. total += i signifie total = total + i. À la fin, on retourne le total. C'est comme compter dans un pot !",
                "en": "We use a 'total' variable that starts at 0. The loop adds each number from 1 to n. total += i means total = total + i. At the end, we return the total. It's like counting in a pot!",
                "es": "Usamos una variable 'total' que comienza en 0. El bucle agrega cada número de 1 a n. total += i significa total = total + i. Al final, devolvemos el total. ¡Es como contar en una olla!",
                "de": "Wir verwenden eine 'total'-Variable, die bei 0 beginnt. Die Schleife fügt jede Zahl von 1 bis n hinzu. total += i bedeutet total = total + i. Am Ende geben wir das total zurück. Es ist wie das Zählen in einem Topf!"
            },
            "hints": {
                "fr": ["Commence à 0", "Boucle de 1 à n", "Ajoute i à total", "Retourne total"],
                "en": ["Start at 0", "Loop from 1 to n", "Add i to total", "Return total"],
                "es": ["Comienza en 0", "Bucle de 1 a n", "Agrega i a total", "Devuelve total"],
                "de": ["Starte bei 0", "Schleife von 1 bis n", "Füge i zu total hinzu", "Gib total zurück"]
            }
        },
        "07-fizzbuzz": {
            "title": {
                "fr": "FizzBuzz rigolo",
                "en": "Funny FizzBuzz",
                "es": "FizzBuzz divertido",
                "de": "Lustiger FizzBuzz"
            },
            "prompt": {
                "fr": "Écris une fonction fizzbuzz(n) qui renvoie une liste de 1..n en remplaçant multiples de 3 par 'Fizz', de 5 par 'Buzz', et de 3 et 5 par 'FizzBuzz'.",
                "en": "Write a function fizzbuzz(n) that returns a list 1..n replacing multiples of 3 with 'Fizz', of 5 with 'Buzz', and of 3 and 5 with 'FizzBuzz'.",
                "es": "Escribe una función fizzbuzz(n) que devuelve una lista 1..n reemplazando múltiplos de 3 con 'Fizz', de 5 con 'Buzz', y de 3 y 5 con 'FizzBuzz'.",
                "de": "Schreibe eine Funktion fizzbuzz(n), die eine Liste 1..n zurückgibt, wobei Vielfache von 3 durch 'Fizz', von 5 durch 'Buzz' und von 3 und 5 durch 'FizzBuzz' ersetzt werden."
            },
            "explanation": {
                "fr": "Le modulo (%) donne le reste d'une division. Si i % 3 == 0, i est multiple de 3. On construit une chaîne vide et on y ajoute 'Fizz' et/ou 'Buzz'. s or i retourne i si s est vide. C'est un jeu de logique !",
                "en": "The modulo (%) gives the remainder of a division. If i % 3 == 0, i is a multiple of 3. We build an empty string and add 'Fizz' and/or 'Buzz' to it. s or i returns i if s is empty. It's a logic game!",
                "es": "El módulo (%) da el resto de una división. Si i % 3 == 0, i es múltiplo de 3. Construimos una cadena vacía y le agregamos 'Fizz' y/o 'Buzz'. s o i devuelve i si s está vacío. ¡Es un juego de lógica!",
                "de": "Der Modulo (%) gibt den Rest einer Division. Wenn i % 3 == 0, ist i ein Vielfaches von 3. Wir bauen einen leeren String und fügen 'Fizz' und/oder 'Buzz' hinzu. s or i gibt i zurück, wenn s leer ist. Es ist ein Logikspiel!"
            },
            "hints": {
                "fr": ["Utilise % (modulo)", "Ajoute 'Fizz' si multiple de 3, 'Buzz' si multiple de 5"],
                "en": ["Use % (modulo)", "Add 'Fizz' if multiple of 3, 'Buzz' if multiple of 5"],
                "es": ["Usa % (módulo)", "Agrega 'Fizz' si es múltiplo de 3, 'Buzz' si es múltiplo de 5"],
                "de": ["Verwende % (Modulo)", "Füge 'Fizz' hinzu bei Vielfachem von 3, 'Buzz' bei Vielfachem von 5"]
            }
        },
        "08-max-de-trois": {
            "title": {
                "fr": "Le plus grand",
                "en": "The biggest",
                "es": "El más grande",
                "de": "Der größte"
            },
            "prompt": {
                "fr": "Écris une fonction max_de_trois(a,b,c) qui renvoie le plus grand sans utiliser max().",
                "en": "Write a function max_of_three(a,b,c) that returns the biggest without using max().",
                "es": "Escribe una función max_de_tres(a,b,c) que devuelve el más grande sin usar max().",
                "de": "Schreibe eine Funktion max_von_drei(a,b,c), die den größten zurückgibt, ohne max() zu verwenden."
            },
            "explanation": {
                "fr": "On commence avec m = a comme plus grand provisoire. Ensuite on compare avec b et c. Si on trouve un plus grand, on met à jour m. C'est comme une compétition où le vainqueur change si quelqu'un de plus grand arrive !",
                "en": "We start with m = a as the provisional biggest. Then we compare with b and c. If we find a bigger one, we update m. It's like a competition where the winner changes if someone bigger arrives!",
                "es": "Comenzamos con m = a como el más grande provisional. Luego comparamos con b y c. Si encontramos uno más grande, actualizamos m. ¡Es como una competencia donde el ganador cambia si llega alguien más grande!",
                "de": "Wir beginnen mit m = a als vorläufig größtem. Dann vergleichen wir mit b und c. Wenn wir einen größeren finden, aktualisieren wir m. Es ist wie ein Wettbewerb, bei dem der Gewinner wechselt, wenn jemand Größeres ankommt!"
            },
            "hints": {
                "fr": ["Garde une variable m", "Compare b puis c"],
                "en": ["Keep a variable m", "Compare b then c"],
                "es": ["Mantén una variable m", "Compara b luego c"],
                "de": ["Behalte eine Variable m", "Vergleiche b dann c"]
            }
        }
    }

    # Lire le fichier actuel
    with open('/Users/vgadreau/Downloads/capitaine-python/app/backend/courses/python-basics.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Mettre à jour chaque exercice
    for exercise in data['exercises']:
        exercise_id = exercise['id']
        if exercise_id in translations:
            trans = translations[exercise_id]

            # Mettre à jour le titre
            if 'title' in trans:
                exercise['title'] = trans['title']

            # Mettre à jour le prompt
            if 'prompt' in trans:
                exercise['prompt'] = trans['prompt']

            # Mettre à jour l'explication
            if 'explanation' in trans:
                exercise['solution_explanation'] = trans['explanation']

            # Mettre à jour les indices
            if 'hints' in trans:
                exercise['hints'] = trans['hints']

    # Sauvegarder le fichier mis à jour
    with open('/Users/vgadreau/Downloads/capitaine-python/app/backend/courses/python-basics.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Traductions appliquées avec succès à python-basics.json")
    print(f"📝 {len([ex for ex in data['exercises'] if ex['id'] in translations])} exercices traduits")

if __name__ == "__main__":
    translate_exercises()