# Règles de Sécurité - Aide-Mémoire Capitaine Python

## 🚨 RÈGLES DE SÉCURITÉ - POINTS BLOQUANTS

### ❌ FONCTIONS INTERDITES (jamais utiliser)
```python
exec()          # Exécution de code arbitraire
eval()          # Évaluation d'expressions arbitraires
__import__()     # Import dynamique
globals()       # Accès variables globales
locals()        # Accès variables locales
vars()          # Accès attributs objet
```

### ❌ MODULES INTERDITS (jamais importer)
```python
os              # Accès système fichiers
sys             # Accès système Python
subprocess      # Exécution commandes
shutil          # Opérations fichiers
socket          # Réseau
threading       # Concurrence
multiprocessing # Parallélisme
pickle          # Sérialisation
marshal         # Sérialisation bas niveau
```

### ❌ PATTERNS SYSTÈME INTERDITS
```python
os.system()     # Exécuter commandes système
open('/')        # Accès fichiers système
subprocess.call() # Lancer processus
socket.socket()  # Connexions réseau
```

---

## ✅ PATTERNS AUTORISÉS ET RECOMMANDÉS

### 🎯 Types de base
```python
# Variables
nombre = 42
texte = "Bonjour"
liste = [1, 2, 3]
dictionnaire = {"cle": "valeur"}

# Conditions
if condition:
    # code
elif autre:
    # code
else:
    # code

# Boucles
for element in liste:
    pass

while condition:
    pass

# Fonctions
def ma_fonction(param1, param2="defaut"):
    return resultat
```

### 🔄 Gestion inputs utilisateur
```python
# ✅ AVEC input() - utiliser run_with_input()
def deviner():
    essai = int(input("Nombre : "))
    if essai == 42:
        print("Gagné!")

# Test correspondant
out = run_with_input('42\n')
assert 'Gagné' in out

# ✅ SANS input() - utiliser execute_code()
def saluer():
    print("Bonjour!")

# Test correspondant
out = execute_code()
assert 'Bonjour' in out
```

---

## 📋 STRUCTURE OBLIGATOIRE

### JSON minimum requis
```json
{
  "id": "01-nom-exercice",
  "title": {"fr": "Titre"},
  "stars": 1,
  "prompt": {"fr": "Consigne avec verbe d'action"},
  "starter": "code de départ",
  "tests": ["tests cohérents"]
}
```

### Règles de nommage
- **ID** : `01-nom-exercice` (kebab-case, préfixe numérique)
- **Titre** : Multilingue obligatoire
- **Étoiles** : 1 (débutant), 2 (intermédiaire), 3 (avancé)

---

## 🧪 RÈGLES DE TESTS

### Patterns obligatoires
```python
# ✅ Exercice SANS input()
tests = [
    "out = execute_code()",
    "assert 'résultat attendu' in out"
]

# ✅ Exercice AVEC input()
tests = [
    "out = run_with_input('valeur\\n')",
    "assert 'résultat attendu' in out"
]

# ✅ Exercice avec fonction
tests = [
    "assert ns.get('ma_fonction'), 'La fonction doit exister'",
    "assert ns['ma_fonction'](param) == resultat"
]
```

### ❌ Erreurs à éviter
```python
# ❌ INCOHÉRENT - input() sans run_with_input
starter = "print('hello')"  # Pas de input()
tests = ["out = run_with_input('test')"]  # ❌ MAUVAIS

# ❌ INCOHÉRENT - run_with_input sans input()
starter = "name = input()"  # Avec input()
tests = ["out = execute_code()"]  # ❌ MAUVAIS
```

---

## 🔍 VALIDATION AUTOMATIQUE

### Commandes essentielles
```bash
# Valider un exercice
python3 validate_integration.py python-basics 01-print

# Valider tous les exercices
python3 validate_integration.py

# API validation
curl -X POST http://localhost:8080/api/validate/exercise \
  -H "Content-Type: application/json" \
  -d '{"exercise": {...}}'
```

### Scores de qualité
- **90-100** : ✅ Excellent (prêt)
- **80-89** : ✅ Bon (corrections mineures)
- **70-79** : ⚠️ Moyen (corrections importantes)
- **< 70** : ❌ Insuffisant (refonte nécessaire)

---

## 🚨 CHECKLIST SÉCURITÉ (5 points)

Avant de soumettre un exercice, vérifier :

1. **[ ] Pas de exec()/eval()** dans starter ou tests
2. **[ ] Pas de import os/sys/subprocess** dans starter ou tests
3. **[ ] Tests cohérents** (execute_code ↔ run_with_input)
4. **[ ] Pas d'accès fichiers/réseau** dans starter ou tests
5. **[ ] Validation automatique** ≥ 80/100

---

## 📞 URGENCE - EN CAS DE DOUTE

### Qui contacter ?
- **Sécurité** : Équipe technique immédiatement
- **Validation** : Documentation validateur
- **Patterns** : Guide complet EXERCISE_PATTERNS_GUIDE.md

### Outils de diagnostic
```bash
# Analyse complète
python3 validate_integration.py

# Test sécurité
python3 test_validator.py

# Détection incohérences
python3 analyze_run_with_input.py
```

---

**RAPPEL** : La sécurité est non négociable. En cas de doute, ne pas intégrer et demander de l'aide.

*Document de référence - Version 1.0*