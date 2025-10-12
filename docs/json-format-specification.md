# Spécification du Format JSON des Cours

Ce document décrit en détail le format JSON utilisé pour structurer les cours pédagogiques dans Capitaine Python.

## 📋 Vue d'Ensemble

Les cours sont stockés dans des fichiers JSON situés dans `app/backend/courses/`. Chaque fichier contient un cours complet avec métadonnées, thème visuel et exercices progressifs.

## 🏗️ Structure JSON Complète

```json
{
  "meta": {
    "id": "python-basics",
    "title": {
      "fr": "Python les Bases - Édition Enrichie",
      "en": "Python Basics - Enhanced Edition",
      "es": "Python Básicos - Edición Enriquecida",
      "de": "Python Grundlagen - Erweiterte Ausgabe"
    },
    "level": "débutant",
    "estimated_hours": 12,
    "prerequisites": [
      {
        "fr": "Aucun prérequis, idéal pour les débutants complets",
        "en": "No prerequisites, perfect for complete beginners"
      }
    ],
    "learning_objectives": [
      {
        "fr": "Maîtriser les concepts fondamentaux de Python",
        "en": "Master fundamental Python concepts"
      }
    ],
    "tags": ["python", "basics", "beginner", "programming"],
    "author": "Capitaine Python",
    "version": "2.0",
    "created_at": "2024-01-01",
    "updated_at": "2024-10-12"
  },
  "theme": {
    "name": "ocean",
    "primary_color": "#0077be",
    "secondary_color": "#00a8cc",
    "background_color": "#0a1929",
    "text_color": "#ffffff",
    "accent_color": "#ff6b6b",
    "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
  },
  "exercises": [
    {
      "id": "01-print",
      "title": {
        "fr": "Fais parler l'ordinateur",
        "en": "Make the computer speak"
      },
      "stars": 1,
      "estimated_minutes": 15,
      "tags": ["print", "strings", "output"],
      "prompt": {
        "fr": "Écris un programme qui affiche 'Bonjour le monde!'",
        "en": "Write a program that displays 'Hello world!'"
      },
      "starter": {
        "fr": "# Écris ton code ici\nprint(\"Bonjour le monde!\")",
        "en": "# Write your code here\nprint(\"Hello world!\")"
      },
      "theory": {
        "fr": {
          "concept": "La fonction print()",
          "explanation": "...",
          "examples": ["...", "..."],
          "best_practices": ["...", "..."],
          "common_mistakes": ["...", "..."]
        },
        "en": {
          "concept": "The print() function",
          "explanation": "...",
          "examples": ["...", "..."],
          "best_practices": ["...", "..."],
          "common_mistakes": ["...", "..."]
        }
      },
      "solution_explanation": {
        "fr": "La fonction print() affiche du texte à l'écran...",
        "en": "The print() function displays text on screen..."
      },
      "why_important": {
        "fr": "C'est votre premier pas dans la programmation...",
        "en": "This is your first step in programming..."
      },
      "further_exploration": {
        "fr": [
          "Essaie d'afficher ton prénom",
          "Essaie d'afficher plusieurs lignes"
        ],
        "en": [
          "Try displaying your first name",
          "Try displaying multiple lines"
        ]
      },
      "cultural_note": {
        "fr": "\"Hello, World!\" est traditionnellement le premier programme...",
        "en": "\"Hello, World!\" is traditionally the first program..."
      },
      "tests": [
        {
          "description": "Test affichage simple",
          "code": "print(\"Bonjour le monde!\")",
          "expected_output": "Bonjour le monde!",
          "points": 1
        }
      ],
      "hints": [
        {
          "level": 1,
          "text": {
            "fr": "Utilise la fonction print()",
            "en": "Use the print() function"
          }
        },
        {
          "level": 2,
          "text": {
            "fr": "print(\"texte à afficher\")",
            "en": "print(\"text to display\")"
          }
        }
      ],
      "validation_rules": {
        "required_functions": [],
        "forbidden_imports": ["os", "sys"],
        "max_lines": 10,
        "timeout_seconds": 5
      }
    }
  ]
}
```

## 📝 Description Détaillée des Champs

### Section `meta` - Métadonnées du Cours

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `id` | string | ✅ | Identifiant unique du cours (format: kebab-case) |
| `title` | object | ✅ | Titre du cours en plusieurs langues |
| `level` | string | ✅ | Niveau de difficulté (débutant, intermédiaire, avancé) |
| `estimated_hours` | number | ✅ | Durée estimée en heures |
| `prerequisites` | array | ✅ | Liste des prérequis en plusieurs langues |
| `learning_objectives` | array | ✅ | Objectifs pédagogiques en plusieurs langues |
| `tags` | array | ❌ | Mots-clés pour la recherche et classification |
| `author` | string | ❌ | Auteur du cours |
| `version` | string | ❌ | Version du cours (format: semver) |
| `created_at` | string | ❌ | Date de création (format: YYYY-MM-DD) |
| `updated_at` | string | ❌ | Dernière mise à jour (format: YYYY-MM-DD) |

### Section `theme` - Thème Visuel

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `name` | string | ✅ | Nom du thème (ex: ocean, forest, desert) |
| `primary_color` | string | ✅ | Couleur principale (format: hex) |
| `secondary_color` | string | ❌ | Couleur secondaire (format: hex) |
| `background_color` | string | ✅ | Couleur de fond (format: hex) |
| `text_color` | string | ✅ | Couleur du texte (format: hex) |
| `accent_color` | string | ❌ | Couleur d'accentuation (format: hex) |
| `gradient` | string | ❌ | Dégradé CSS (format: css gradient) |

### Section `exercises` - Liste des Exercices

Chaque exercice contient les champs suivants :

#### Métadonnées de l'Exercice

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `id` | string | ✅ | Identifiant unique (format: NN-action) |
| `title` | object | ✅ | Titre en plusieurs langues |
| `stars` | number | ✅ | Difficulté (1: facile, 2: moyen, 3: difficile) |
| `estimated_minutes` | number | ❌ | Temps estimé en minutes |
| `tags` | array | ❌ | Mots-clés de l'exercice |

#### Contenu Pédagogique

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `prompt` | object | ✅ | Consigne pour l'apprenant en plusieurs langues |
| `starter` | object | ✅ | Code de départ en plusieurs langues |
| `theory` | object | ✅ | Section théorie complète (voir détail ci-dessous) |
| `solution_explanation` | object | ✅ | Explication de la solution |
| `why_important` | object | ✅ | Importance et contexte réel |
| `further_exploration` | object | ✅ | Pistes pour aller plus loin |
| `cultural_note` | object | ❌ | Note culturelle ou anecdote |

#### Tests et Validation

| Champ | Type | Obligatoire | Description |
|-------|------|-------------|-------------|
| `tests` | array | ✅ | Tests unitaires de validation |
| `hints` | array | ✅ | Indices progressifs |
| `validation_rules` | object | ❌ | Règles de validation spécifiques |

### Section `theory` - Structure Détaillée

```json
{
  "theory": {
    "fr": {
      "concept": "Titre du concept",
      "explanation": "Explication détaillée du concept",
      "examples": [
        "Exemple 1 avec explication",
        "Exemple 2 avec explication"
      ],
      "best_practices": [
        "Meilleure pratique 1",
        "Meilleure pratique 2"
      ],
      "common_mistakes": [
        "Erreur fréquente 1 et comment l'éviter",
        "Erreur fréquente 2 et comment l'éviter"
      ],
      "syntax": "structure_syntaxique_du_concept",
      "key_points": [
        "Point clé 1",
        "Point clé 2"
      ]
    },
    "en": {
      // Mêmes champs en anglais
    }
  }
}
```

### Section `tests` - Tests Unitaires

```json
{
  "tests": [
    {
      "description": "Description du test",
      "code": "code_de_test_à_exécuter",
      "expected_output": "sortie_attendue",
      "expected_exception": "exception_attendue_si_applicable",
      "points": 1,
      "test_type": "output|exception|function_call",
      "input_data": "données_entrée_si_besoin",
      "mock_calls": [
        {
          "function": "nom_fonction",
          "args": ["arg1", "arg2"],
          "return_value": "valeur_retour"
        }
      ]
    }
  ]
}
```

### Section `hints` - Indices Progressifs

```json
{
  "hints": [
    {
      "level": 1,
      "text": {
        "fr": "Premier indice subtil",
        "en": "First subtle hint"
      },
      "type": "concept|syntax|example"
    },
    {
      "level": 2,
      "text": {
        "fr": "Deuxième indice plus direct",
        "en": "Second more direct hint"
      },
      "type": "code_snippet",
      "code": "print(\"exemple\")"
    }
  ]
}
```

## 🔍 Règles de Validation

### Validation de Structure

1. **Champs obligatoires** : Tous les champs marqués ✅ doivent être présents
2. **Types de données** : Respect strict des types spécifiés
3. **Format des dates** : YYYY-MM-DD uniquement
4. **Format des couleurs** : Hexadecimal (#RRGGBB) uniquement
5. **Format des IDs** : kebab-case sans caractères spéciaux

### Validation de Contenu

1. **Multilinguisme** : Au minimum `fr` et `en` requis
2. **Longueur maximale** :
   - Titre : 100 caractères
   - Description : 500 caractères
   - Explication : 2000 caractères
3. **Tests obligatoires** : Au moins 1 test par exercice
4. **Indices progressifs** : 1-3 indices par exercice

### Validation Pédagogique

1. **Progression** : Difficulté croissante des exercices
2. **Équilibre** : Théorie et pratique équilibrées
3. **Clarté** : Explications compréhensibles pour le niveau visé
4. **Exemples** : Au moins 2 exemples par concept théorique

## 🛠️ Outils de Validation

### Script de Validation Python

```python
import json
import re
from pathlib import Path

def validate_course_json(file_path):
    """Validation complète d'un fichier de cours JSON"""

    with open(file_path, 'r', encoding='utf-8') as f:
        course = json.load(f)

    errors = []
    warnings = []

    # Validation structure
    validate_structure(course, errors, warnings)

    # Validation contenu
    validate_content(course, errors, warnings)

    # Validation pédagogique
    validate_pedagogy(course, errors, warnings)

    return errors, warnings
```

### Tests Automatisés

```bash
# Validation tous les cours
python -m pytest tests/test_course_validation.py

# Validation format JSON
python -c "import json; json.load(open('app/backend/courses/python-basics.json'))"
```

## 📚 Bonnes Pratiques

### Organisation

1. **Un cours par fichier** : Éviter les méga-fichiers
2. **Nommage cohérent** : Utiliser kebab-case
3. **Versionnement** : Incrémenter version lors modifications
4. **Backup** : Garder versions précédentes

### Rédaction

1. **Clarté** : Langage simple et direct
2. **Progressivité** : Complexité croissante
3. **Exemples** : Concrets et testés
4. **Feedback** : Messages d'erreur constructifs

### Maintenance

1. **Tests réguliers** : Valider tous les exercices
2. **Mise à jour** : Garder contenu actuel
3. **Documentation** : Commenter les changements
4. **Review** : Validation par pairs

## 🔄 Migration et Évolution

### Version 1.0 → 2.0

- Ajout sections `theory` complètes
- Support multilingue étendu
- Validation renforcée
- Tests automatisés

### Évolutions Futures

1. **Adaptatif** : Exercices basés sur progression
2. **Médias** : Images et vidéos intégrées
3. **Collaboratif** : Contributions communautaires
4. **IA** : Génération automatique d'exercices

Ce format structuré permet une gestion efficace des contenus pédagogiques tout en assurant qualité et cohérence dans l'expérience d'apprentissage.