# Guide des Patterns d'Exercices - Capitaine Python

## Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Patterns de sécurité](#patterns-de-sécurité)
3. [Patterns de code autorisés](#patterns-de-code-autorisés)
4. [Patterns de code interdits](#patterns-de-code-interdits)
5. [Patterns de tests](#patterns-de-tests)
6. [Patterns pédagogiques](#patterns-pédagogiques)
7. [Formats et structures](#formats-et-structures)
8. [Exemples complets](#exemples-complets)
9. [Checklist de validation](#checklist-de-validation)
10. [Outils et ressources](#outils-et-ressources)

---

## Vue d'ensemble

Ce guide définit les standards de qualité et de sécurité pour la création d'exercices dans la plateforme Capitaine Python. L'objectif est de garantir un environnement d'apprentissage sûr, cohérent et pédagogiquement efficace.

### Principes directeurs

- **🔒 Sécurité avant tout** : Aucun compromis sur la sécurité des apprenants
- **📚 Pédagogie centrée** : Clarté, progression et accompagnement
- **✅ Cohérence totale** : Alignement entre énoncé, code starter et tests
- **🎯 Simplicité efficace** : Éviter la complexité inutile
- **🌍 Accessibilité** : Support multilingue et adapté aux débutants

---

## Patterns de sécurité

### 🔴 Patterns DANGEREUX (INTERDITS)

#### Fonctions Python interdites

| Fonction | Risque | Alternative | Exemple |
|----------|--------|--------------|---------|
| `exec()` | Exécution de code arbitraire | ✅ **Aucune** | ❌ `exec(code)` |
| `eval()` | Exécution de code arbitraire | ✅ **Aucune** | ❌ `eval(expression)` |
| `__import__()` | Import dynamique non contrôlé | ✅ Import direct | ❌ `__import__('os')` |
| `globals()` | Accès à l'espace de nommage global | ✅ **Aucune** | ❌ `globals()['module']` |
| `locals()` | Accès aux variables locales | ✅ **Aucune** | ❌ `locals()['var']` |
| `vars()` | Accès aux attributs d'objet | ✅ **Aucune** | ❌ `vars(obj)` |

#### Modules Python interdits

| Module | Risque | Alternative | Exemple |
|--------|--------|--------------|---------|
| `os` | Accès système de fichiers | ✅ **Aucune** | ❌ `import os` |
| `sys` | Accès système Python | ✅ **Aucune** | ❌ `import sys` |
| `subprocess` | Exécution de commandes système | ✅ **Aucune** | ❌ `import subprocess` |
| `shutil` | Opérations fichiers | ✅ **Aucune** | ❌ `import shutil` |
| `socket` | Réseau | ✅ **Aucune** | ❌ `import socket` |
| `threading` | Concurrence | ✅ **Aucune** | ❌ `import threading` |
| `multiprocessing` | Parallélisme | ✅ **Aucune** | ❌ `import multiprocessing` |
| `pickle` | Sérialisation (risques sécurité) | ✅ **Aucune** | ❌ `import pickle` |
| `marshal` | Sérialisation bas niveau | ✅ **Aucune** | ❌ `import marshal` |

#### Patterns système interdits

```python
# ❌ INTERDIT - Accès fichiers
os.system('ls')
open('/etc/passwd', 'r')
os.listdir('/')

# ❌ INTERDIT - Réseau
import socket
socket.socket()

# ❌ INTERDIT - Processus
subprocess.call(['ls'])
subprocess.Popen(['python'])

# ❌ INTERDIT - Code dynamique
exec(user_input)
eval('2 + 2')
compile(source, '<string>', 'exec')
```

### 🟡 Patterns SURVEILLÉS (AUTORISÉS AVEC VÉRIFICATION)

#### Fonctions nécessitant validation

| Fonction | Conditions d'utilisation | Validation requise |
|----------|------------------------|-------------------|
| `input()` | ✅ Autorisé avec `run_with_input()` | Vérifier cohérence tests |
| `print()` | ✅ Autorisé | Vérifier contenu approprié |
| `open()` | ❌ Généralement interdit | Seulement si absolument nécessaire |
| `getattr()` | ❌ Généralement interdit | Validation stricte requise |
| `setattr()` | ❌ Généralement interdit | Validation stricte requise |

---

## Patterns de code autorisés

### ✅ Patterns RECOMMANDÉS

#### Types de données de base

```python
# ✅ Types simples
nombre = 42
texte = "Bonjour"
decimal = 3.14
boolean = True
liste = [1, 2, 3]
dictionnaire = {"cle": "valeur"}

# ✅ Structures conditionnelles
if condition:
    # code
elif autre_condition:
    # code
else:
    # code

# ✅ Boucles
for element in liste:
    # traitement element

for i in range(5):
    # traitement i

while condition:
    # code

# ✅ Fonctions
def ma_fonction(parametre1, parametre2="valeur_par_defaut"):
    """Documentation de la fonction"""
    return resultat

# ✅ Classes simples
class Personne:
    def __init__(self, nom, age):
        self.nom = nom
        self.age = age

    def se_presenter(self):
        return f"Je m'appelle {self.nom}"
```

#### Patterns algorithmiques

```python
# ✅ Calculs mathématiques
def factorielle(n):
    if n <= 1:
        return 1
    return n * factorielle(n - 1)

# ✅ Manipulation de chaînes
def inverser_texte(texte):
    return texte[::-1]

# ✅ Algorithmes de tri
def trouver_maximum(liste):
    maximum = liste[0]
    for element in liste:
        if element > maximum:
            maximum = element
    return maximum

# ✅ Gestion d'erreurs
def division_securisee(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "Division par zéro impossible"
```

#### Patterns avec inputs utilisateur

```python
# ✅ Exercice interactif (avec input)
def deviner_nombre():
    nombre_secret = 42
    essai = int(input("Devinez le nombre : "))
    if essai == nombre_secret:
        print("Bravo !")
    else:
        print("Essaye encore !")

# Test correspondant
out = run_with_input('42\n')
assert 'Bravo' in out
```

### 📏 Standards de qualité du code

#### Longueur et complexité

- **Maximum 20 lignes** pour le code starter
- **Complexité cyclomatique < 10**
- **Indentation cohérente** (espaces ou tabulations, pas les deux)
- **Noms de variables explicites** en français

#### Style recommandé

```python
# ✅ BONS exemples
def calculer_surface_rectangle(longueur, largeur):
    """Calcule la surface d'un rectangle"""
    return longueur * largeur

# Noms de variables clairs
prix_total = prix_unitaire * quantite
est_majeur = age >= 18

# Commentaires utiles
# Vérifier si le nombre est pair
if nombre % 2 == 0:
    print("Le nombre est pair")

# ❌ MAUVAIS exemples
def f(x, y):  # Noms peu clairs
    return x * y

a = 5  # Variable mal nommée
if a % 2 == 0:
    print("pair")  # Commentaire inutile
```

---

## Patterns de tests

### ✅ Patterns de tests AUTORISÉS

#### Structure générale des tests

```python
# Pattern 1: Exercice sans input()
# Tests avec execute_code()
tests = [
    "out = execute_code()",
    "assert 'résultat attendu' in out",
    "assert len(out.strip().splitlines()) == nombre_lignes_attendu"
]

# Pattern 2: Exercice avec input()
# Tests avec run_with_input()
tests = [
    "out1 = run_with_input('valeur1\\n')",
    "out2 = run_with_input('valeur2\\n')",
    "assert 'résultat1' in out1",
    "assert 'résultat2' in out2"
]

# Pattern 3: Exercice avec fonctions
# Tests avec ns['nom_fonction']
tests = [
    "assert ns.get('ma_fonction'), 'La fonction ma_fonction doit exister'",
    "resultat = ns['ma_fonction'](parametre_test)",
    "assert resultat == resultat_attendu",
    "assert isinstance(resultat, type_attendu)"
]
```

#### Assertions recommandées

```python
# ✅ Assertions sur les valeurs
assert resultat == 42
assert len(liste) == 5
assert texte.startswith("Bonjour")
assert nombre in range(1, 101)

# ✅ Assertions sur les types
assert isinstance(resultat, int)
assert type(nom) == str

# ✅ Assertions sur les structures
assert 'clé' in dictionnaire
assert element in liste
assert not liste_vide

# ✅ Messages d'erreur personnalisés
assert condition, "Message d'erreur explicatif"
```

### ❌ Patterns de tests INTERDITS

```python
# ❌ Tests sans sortie
# Mauvais : pas de print() ou return
def fonction_silencieuse():
    x = 1 + 1
# Test invalide car aucune sortie à vérifier

# ❌ Tests incohérents
# Code sans input() mais test avec run_with_input()
starter = "print('Hello')"
tests = ["out = run_with_input('test')"]  # ❌ INCOHÉRENT

# ❌ Tests dangereux
# Utilisation de fonctions interdites dans les tests
tests = ["exec('print(test)')"]  # ❌ DANGEREUX
```

---

## Patterns pédagogiques

### ✅ Standards de contenu

#### Structure d'un exercice

```json
{
  "id": "identifiant-unique",
  "title": {
    "fr": "Titre en français",
    "en": "English title",
    "es": "Título en español",
    "de": "Deutscher Titel"
  },
  "stars": 1,
  "prompt": {
    "fr": "Consigne claire avec verbe d'action",
    "en": "Clear instruction with action verb",
    "es": "Instrucción clara con verbo de acción",
    "de": "Klare Anweisung mit Aktionsverb"
  },
  "starter": "code de départ guidé",
  "tests": ["tests cohérents"],
  "hints": {
    "fr": ["indice 1", "indice 2", "indice 3"],
    "en": ["hint 1", "hint 2", "hint 3"]
  },
  "solution_explanation": "explication pédagogique"
}
```

#### Qualité des prompts

```python
# ✅ BONS prompts - verbes d'action clairs
"Écris une fonction qui calcule la somme de deux nombres"
"Crée une liste contenant les nombres pairs de 1 à 10"
"Définis une classe Personne avec nom et âge"
"Affiche 'Bonjour' suivi du nom de l'utilisateur"

# ❌ MAUVAIS prompts - vagues ou sans verbe d'action
"Fonction somme"  # Trop court
"Calcul de somme"  # Pas de verbe d'action
"Faites quelque chose avec des nombres"  # Trop vague
"Code pour l'addition"  # Pas assez précis
```

#### Indices de qualité

```python
# ✅ BONS indices - progressifs et utiles
hints = [
    "Utilise une boucle for pour parcourir la liste",
    "Pense à utiliser range(1, 11) pour générer les nombres",
    "N'oublie pas d'ajouter chaque élément à une variable de somme"
]

# ❌ MAUVAIS indices - trop vagues ou inutiles
hints = [
    "Réfléchissez bien",  # Trop vague
    "Demandez de l'aide",  # Inutile
    "Le code est simple",  # Pas une aide
    "Utilise Python"  # Évident
]
```

### 📚 Progression pédagogique

#### Difficulté par étoiles

- **⭐ (1 étoile)** : Concepts de base, une seule notion
  - Variables, print(), types simples
  - Conditions simples, boucles de base
  - Fonctions avec un seul paramètre

- **⭐⭐ (2 étoiles)** : Concepts intermédiaires
  - Combinaison de plusieurs notions
  - Fonctions avec plusieurs paramètres
  - Structures de données simples

- **⭐⭐⭐ (3 étoiles)** : Concepts avancés
  - Algorithmes complexes
  - Classes et objets simples
  - Gestion d'erreurs

---

## Formats et structures

### 📋 Structure JSON requise

#### Champs obligatoires

```json
{
  "id": "string",           // Identifiant unique (kebab-case)
  "title": "object",        // Titre multilingue
  "stars": "number",        // 1, 2 ou 3
  "prompt": "object",       // Consigne multilingue
  "starter": "string",      // Code de départ
  "tests": "array"          // Tests de validation
}
```

#### Champs recommandés

```json
{
  "hints": "object",                    // Indices multilingues
  "solution_explanation": "string",     // Explication solution
  "theory": "object",                  // Contenu théorique (optionnel)
  "prerequisites": "array",             // Prérequis (optionnel)
  "learning_objectives": "array"        // Objectifs (optionnel)
}
```

### 🔍 Conventions de nommage

#### Identifiants d'exercices

```python
# ✅ Format kebab-case avec préfixe numérique
"01-print"
"02-variables"
"03-conditions"
"04-boucle-for"
"05-fonction-bonjour"
"06-somme-1-a-n"
"07-fizzbuzz"
"08-max-de-trois"

# ❌ Formats incorrects
"print_exercise"      # snake_case
"PrintExercise"       # camelCase
"1 print"             # espace
"print"               // pas de préfixe numérique
```

#### Titres multilingues

```python
# ✅ Titres cohérents
title = {
  "fr": "Trésor dans une variable",
  "en": "Treasure in a variable",
  "es": "Tesoro en una variable",
  "de": "Schatz in einer Variable"
}

# ❌ Titres incohérents
title = {
  "fr": "Variables",
  "en": "Using Variables in Python Programming",  # Trop long
  "es": "variables",  # Pas de majuscule
  "de": "Variablen"   # Pas de traduction complète
}
```

---

## Exemples complets

### 🌟 Exemple d'exercice PARFAIT

```json
{
  "id": "05-fonction-bonjour",
  "title": {
    "fr": "Dis Bonjour",
    "en": "Say Hello",
    "es": "Di Hola",
    "de": "Sag Hallo"
  },
  "stars": 2,
  "prompt": {
    "fr": "Écris une fonction bonjour(nom) qui renvoie 'Bonjour <nom>' (sans l'afficher).",
    "en": "Write a function hello(name) that returns 'Hello <name>' (without printing).",
    "es": "Escribe una función hola(nombre) que devuelva 'Hola <nombre>' (sin mostrarlo).",
    "de": "Schreibe eine Funktion hallo(name), die 'Hallo <name>' zurückgibt (ohne auszugeben)."
  },
  "starter": "def bonjour(nom):\n    return 'Bonjour ' + nom",
  "solution_explanation": "Une fonction est un bloc de code réutilisable. def bonjour(nom): crée la fonction. return renvoie une valeur sans l'afficher. On peut l'utiliser plusieurs fois avec différents noms.",
  "tests": [
    "assert ns.get('bonjour'), 'La fonction bonjour(nom) doit exister'",
    "assert ns['bonjour']('Hugo') == 'Bonjour Hugo'",
    "assert ns['bonjour']('Ava') == 'Bonjour Ava'",
    "assert isinstance(ns['bonjour']('Test'), str), 'La fonction doit retourner une chaîne'"
  ],
  "hints": {
    "fr": [
      "def bonjour(nom):",
      "return 'Bonjour ' + nom"
    ],
    "en": [
      "def hello(name):",
      "return 'Hello ' + name"
    ],
    "es": [
      "def hola(nombre):",
      "return 'Hola ' + nombre"
    ],
    "de": [
      "def hallo(name):",
      "return 'Hallo ' + name"
    ]
  }
}
```

**Score de validation : 95/100 ✅**

### ❌ Exemple d'exercice PROBLÉMATIQUE

```json
{
  "id": "dangerous-system",
  "title": "System Explorer",
  "stars": 3,
  "prompt": "Explore system files and directories",
  "starter": "import os\nfiles = os.listdir('/')\nfor file in files[:5]:\n    print(file)",
  "tests": [
    "out = execute_code()",
    "assert len(out.strip().splitlines()) > 0"
  ],
  "hints": ["Use os.listdir()"]
}
```

**Problèmes détectés :**
- ❌ Import du module `os` (interdit)
- ❌ Accès au système de fichiers
- ❌ Pas de version multilingue
- ❌ Titre en anglais uniquement
- ❌ Pas de verbe d'action clair

**Score de validation : 15/100 ❌**

### ✅ Exemple d'exercice INTERACTIF

```json
{
  "id": "03-conditions",
  "title": {
    "fr": "Feu rouge/vert",
    "en": "Traffic Light",
    "es": "Semáforo rojo/verde",
    "de": "Ampel rot/grün"
  },
  "stars": 2,
  "prompt": {
    "fr": "Lis un mot (rouge/vert) et affiche 'STOP' si rouge, 'GO' si vert.",
    "en": "Read a word (red/green) and display 'STOP' for red, 'GO' for green.",
    "es": "Lee una palabra (rojo/verde) y muestra 'STOP' si es rojo, 'GO' si es verde.",
    "de": "Lies ein Wort (rot/grün) und zeige 'STOP' bei rot, 'GO' bei grün."
  },
  "starter": "couleur = input()\nif couleur == \"rouge\":\n    print(\"STOP\")\nelif couleur == \"vert\":\n    print(\"GO\")",
  "tests": [
    "out1 = run_with_input('rouge\\n')",
    "out2 = run_with_input('vert\\n')",
    "assert out1.strip() == 'STOP'",
    "assert out2.strip() == 'GO'"
  ],
  "hints": {
    "fr": [
      "if couleur == 'rouge': print('STOP')",
      "elif couleur == 'vert': print('GO')"
    ]
  }
}
```

**Score de validation : 90/100 ✅**

---

## Checklist de validation

### 🔍 Avant de soumettre un exercice

#### ✅ Sécurité
- [ ] Pas de fonctions dangereuses (`exec`, `eval`, etc.)
- [ ] Pas de modules interdits (`os`, `sys`, `subprocess`, etc.)
- [ ] Code safe dans starter ET tests
- [ ] Pas d'accès système de fichiers ou réseau

#### ✅ Structure
- [ ] ID unique en kebab-case avec préfixe numérique
- [ ] Titre multilingue (fr, en, es, de recommandé)
- [ ] Nombre d'étoiles approprié (1-3)
- [ ] Prompt avec verbe d'action clair
- [ ] Code starter (< 20 lignes)
- [ ] Tests cohérents avec le starter

#### ✅ Tests
- [ ] Tests fonctionnels et valides
- [ ] `execute_code()` pour exercices sans input()
- [ ] `run_with_input()` pour exercices avec input()
- [ ] Assertions claires avec messages d'erreur
- [ ] Couverture des cas principaux

#### ✅ Pédagogie
- [ ] Indices progressifs et utiles (2-3 minimum)
- [ ] Explication de solution claire
- [ ] Difficulté appropriée au nombre d'étoiles
- [ ] Consigne compréhensible pour débutants

#### ✅ Qualité
- [ ] Code lisible et bien commenté
- [ ] Noms de variables explicites
- [ ] Indentation cohérente
- [ ] Pas de code mort ou inutile

### 🚀 Validation automatique

```bash
# Valider un exercice spécifique
python3 validate_integration.py python-basics 01-print

# Valider tous les exercices d'un cours
python3 validate_integration.py

# Validation via API
curl -X POST http://localhost:8080/api/validate/exercise \
  -H "Content-Type: application/json" \
  -d '{"exercise": {...}}'
```

### 📊 Critères de validation

| Score | Qualité | Action requise |
|-------|---------|----------------|
| 90-100 | ✅ Excellente | Prêt pour intégration |
| 80-89 | ✅ Bonne | Corrections mineures suggérées |
| 70-79 | ⚠️ Moyenne | Corrections importantes requises |
| < 70 | ❌ Insuffisante | Refonte nécessaire |

---

## Outils et ressources

### 🛠️ Outils de développement

#### Validation locale
```bash
# Script de validation complet
python3 validate_integration.py

# Test du validateur
python3 test_validator.py

# Analyse des incohérences
python3 analyze_run_with_input.py
```

#### Éditeurs recommandés
- **VS Code** avec extension Python
- **PyCharm** Community Edition
- **Thonny** (pour débutants)

### 📚 Ressources d'apprentissage

#### Documentation Python
- [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/)
- [W3Schools Python](https://www.w3schools.com/python/)

#### Meilleures pratiques
- [PEP 8 -- Style Guide](https://peps.python.org/pep-0008/)
- [Python Code Quality Tools](https://realpython.com/python-code-quality/)
- [Clean Code Python](https://github.com/zedshaw/clean-code-python)

### 🤖 Support et communauté

#### Obtenir de l'aide
- **Issues GitHub** pour rapports de bugs
- **Documentation** du validateur
- **Exemples** dans le dépôt du projet

#### Contribuer
- **Fork** du projet
- **Branch** `feature/nom-exercice`
- **Validation** avant PR
- **Review** par l'équipe

---

## Conclusion

Ce guide établit les standards de qualité et de sécurité pour la création d'exercices Capitaine Python. En suivant ces patterns, vous contribuerez à offrir une expérience d'apprentissage sécurisée, cohérente et pédagogiquement efficace.

**Rappel des points clés :**
- 🔒 **Sécurité avant tout** : jamais de compromis sur la sécurité
- 📚 **Pédagogie centrée** : clarté et progression
- ✅ **Cohérence totale** : alignement énoncé/code/tests
- 🎯 **Qualité vérifiée** : validation automatique obligatoire

Pour toute question ou clarification, n'hésitez pas à consulter l'équipe ou la documentation technique.

---

*Ce document est maintenu par l'équipe Capitaine Python et mis à jour régulièrement.*