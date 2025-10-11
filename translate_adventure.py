#!/usr/bin/env python3
"""
Script pour traduire automatiquement les exercices python-adventure.json
"""
import json

def translate_adventure():
    """Traduire tous les exercices restants en format multi-langue"""

    # Traductions pour les exercices manquants
    translations = {
        "02-aventure-variable": {
            "lesson_title": {
                "fr": "📚 Leçon : Les Variables",
                "en": "📚 Lesson: Variables",
                "es": "📚 Lección: Variables",
                "de": "📚 Lektion: Variablen"
            },
            "title": {
                "fr": "Le Sac à Dos Magique",
                "en": "The Magic Backpack",
                "es": "La Mochila Mágica",
                "de": "Der magische Rucksack"
            },
            "prompt": {
                "fr": "Stocke 'Potion de vie' dans un sac (variable) nommé inventaire et affiche son contenu.",
                "en": "Store 'Life Potion' in a bag (variable) named inventory and display its contents.",
                "es": "Almacena 'Poción de vida' en una bolsa (variable) llamada inventario y muestra su contenido.",
                "de": "Speichere 'Lebenstrank' in einer Tasche (Variable) namens inventar und zeige ihren Inhalt an."
            },
            "hints": {
                "fr": ["inventaire = 'Potion de vie'", "print(inventaire) montre ce que contient ton sac"],
                "en": ["inventory = 'Life Potion'", "print(inventory) shows what's in your bag"],
                "es": ["inventario = 'Poción de vida'", "print(inventario) muestra lo que contiene tu bolsa"],
                "de": ["inventar = 'Lebenstrank'", "print(inventar) zeigt, was in deiner Tasche ist"]
            }
        },
        "03-aventure-conditions": {
            "lesson_title": {
                "fr": "📚 Leçon : Les Conditions (if/elif/else)",
                "en": "📚 Lesson: Conditions (if/elif/else)",
                "es": "📚 Lección: Condiciones (if/elif/else)",
                "de": "📚 Lektion: Bedingungen (if/elif/else)"
            },
            "title": {
                "fr": "Le Choix du Chemin",
                "en": "The Path Choice",
                "es": "La Elección del Camino",
                "de": "Der Wegewahl"
            },
            "prompt": {
                "fr": "Demande à l'aventurier son choix (foret/montagne) et affiche 'Tu explores la forêt' ou 'Tu gravis la montagne'.",
                "en": "Ask the adventurer for their choice (forest/mountain) and display 'You explore the forest' or 'You climb the mountain'.",
                "es": "Pregunta al aventurero su elección (bosque/montaña) y muestra 'Exploras el bosque' o 'Escalas la montaña'.",
                "de": "Frage den Abenteurer nach seiner Wahl (Wald/Berg) und zeige 'Du erforschst den Wald' oder 'Du besteigst den Berg' an."
            },
            "hints": {
                "fr": ["if choix == 'foret':", "elif choix == 'montagne':"],
                "en": ["if choice == 'forest':", "elif choice == 'mountain':"],
                "es": ["if eleccion == 'bosque':", "elif eleccion == 'montaña':"],
                "de": ["if wahl == 'wald':", "elif wahl == 'berg':"]
            }
        },
        "04-aventure-boucle": {
            "lesson_title": {
                "fr": "📚 Leçon : Les Boucles (for)",
                "en": "📚 Lesson: Loops (for)",
                "es": "📚 Lección: Bucles (for)",
                "de": "📚 Lektion: Schleifen (for)"
            },
            "title": {
                "fr": "Les Pas du Voyageur",
                "en": "The Traveler's Steps",
                "es": "Los Pasos del Viajero",
                "de": "Die Schritte des Reisenden"
            },
            "prompt": {
                "fr": "Compte tes pas de 1 à 3 comme si tu marchais vers l'aventure.",
                "en": "Count your steps from 1 to 3 as if you were walking towards adventure.",
                "es": "Cuenta tus pasos de 1 a 3 como si caminaras hacia la aventura.",
                "de": "Zähle deine Schritte von 1 bis 3, als ob du zum Abenteuer gehst."
            },
            "hints": {
                "fr": ["for pas in range(1, 4):", "print(f\"Pas {pas}\")"],
                "en": ["for step in range(1, 4):", "print(f\"Step {step}\")"],
                "es": ["for paso in range(1, 4):", "print(f\"Paso {paso}\")"],
                "de": ["for schritt in range(1, 4):", "print(f\"Schritt {schritt}\")"]
            }
        },
        "05-aventure-fonction": {
            "lesson_title": {
                "fr": "📚 Leçon : Les Fonctions",
                "en": "📚 Lesson: Functions",
                "es": "📚 Lección: Funciones",
                "de": "📚 Lektion: Funktionen"
            },
            "title": {
                "fr": "L'Arme du Héros",
                "en": "The Hero's Weapon",
                "es": "El Arma del Héroe",
                "de": "Die Waffe des Helden"
            },
            "prompt": {
                "fr": "Crée une fonction attaque(nom) qui renvoie '[nom] lance une attaque !' (sans l'afficher).",
                "en": "Create a function attack(name) that returns '[name] launches an attack!' (without displaying it).",
                "es": "Crea una función ataque(nombre) que devuelve '[nombre] lanza un ataque!' (sin mostrarlo).",
                "de": "Erstelle eine Funktion angriff(name), die '[name] startet einen Angriff!' zurückgibt (ohne ihn anzuzeigen)."
            },
            "hints": {
                "fr": ["def attaque(nom):", "return f\"{nom} lance une attaque !\""],
                "en": ["def attack(name):", "return f\"{name} launches an attack!\""],
                "es": ["def ataque(nombre):", "return f\"{nombre} lanza un ataque!\""],
                "de": ["def angriff(name):", "return f\"{name} startet einen Angriff!\""]
            }
        }
    }

    # Lire le fichier actuel
    with open('/Users/vgadreau/Downloads/capitaine-python/app/backend/courses/python-adventure.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Mettre à jour chaque exercice
    for exercise in data['exercises']:
        exercise_id = exercise['id']
        if exercise_id in translations:
            trans = translations[exercise_id]

            # Mettre à jour le titre
            if 'title' in trans:
                exercise['title'] = trans['title']

            # Mettre à jour le titre de leçon
            if 'lesson_title' in trans:
                exercise['lesson']['title'] = trans['lesson_title']

            # Mettre à jour le prompt
            if 'prompt' in trans:
                exercise['prompt'] = trans['prompt']

            # Mettre à jour les indices
            if 'hints' in trans:
                exercise['hints'] = trans['hints']

    # Sauvegarder le fichier mis à jour
    with open('/Users/vgadreau/Downloads/capitaine-python/app/backend/courses/python-adventure.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ Traductions appliquées avec succès à python-adventure.json")
    print(f"📝 {len([ex for ex in data['exercises'] if ex['id'] in translations])} exercices mis à jour")

if __name__ == "__main__":
    translate_adventure()