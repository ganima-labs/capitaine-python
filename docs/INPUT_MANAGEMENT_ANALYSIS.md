# Analyse de la Gestion des Inputs Clavier - Capitaine Python

## 🎯 Problème Principal

La fonction `input()` est bloquée par le système de sécurité, ce qui empêche les exercices interactifs de fonctionner correctement.

## 📊 État Actuel

### ✅ Ce qui fonctionne :
- **Tests automatisés** : `run_with_input()` simule correctement les inputs dans les tests
- **Exercices existants** : L'exercice "03-conditions" est bien défini avec des tests d'inputs

### ❌ Ce qui ne fonctionne pas :
- **Exécution interactive** : L'utilisateur ne peut pas tester son code avec `input()` directement
- **Feedback immédiat** : Pas de possibilité d'essayer le code avec des vrais inputs
- **Mode apprentissage** : L'expérience utilisateur est limitée pour les exercices interactifs

### ⚠️ Problème identifié :
```python
# Dans security.py - Lignes 13, 25
DANGEROUS_MODULES = {
    'input', 'raw_input',  # ← input() est considéré comme dangereux
    # ...
}

DANGEROUS_FUNCTIONS = {
    'input', 'raw_input',  # ← input() est bloqué à l'exécution
    # ...
}
```

## 🏗️ Architecture Actuelle

### 1. Système de Tests (fonctionnel)
```python
# Dans grader.py
def run_with_input(input_data=""):
    backup_stdin = sys.stdin
    backup_stdout = sys.stdout
    sys.stdin = io.StringIO(input_data)
    buf = io.StringIO()
    sys.stdout = buf
    try:
        exec(student_code, {})
        return buf.getvalue()
    finally:
        sys.stdin = backup_stdin
        sys.stdout = backup_stdout
```

### 2. Exemple d'exercice avec input (lignes 33-43 dans exercises.py)
```python
{
  "id": "03-conditions",
  "title": "Feu rouge/vert",
  "stars": 2,
  "prompt": "Lis un mot (rouge/vert) et affiche 'STOP' si rouge, 'GO' si vert.",
  "starter": 'couleur = input()\nif couleur == "rouge":\n    print("STOP")\nelif couleur == "vert":\n    print("GO")',
  "tests": [
    "out1 = run_with_input('rouge\n')",
    "out2 = run_with_input('vert\n')",
    "assert out1.strip() == 'STOP'",
    "assert out2.strip() == 'GO'"
  ]
}
```

## 🛠️ Solutions Proposées

### Solution 1: Input Sécurisé avec Interface Spéciale ⭐ **Recommandée**

**Avantages :**
- Permet les vrais inputs utilisateur
- Maintient la sécurité
- Expérience utilisateur optimale

**Implémentation :**
1. Détecter les exercices avec `input()` dans le code
2. Afficher une interface de saisie dans le frontend
3. Exécuter le code avec les inputs fournis
4. Modifier le validateur de sécurité pour autoriser `input()` uniquement dans ce contexte

### Solution 2: Mode "Test Interactif" ⭐ **Alternative**

**Avantages :**
- Simple à implémenter
- Moins de risques de sécurité
- Utilise l'infrastructure existante

**Implémentation :**
1. Ajouter un bouton "Tester avec des inputs"
2. Ouvrir une modale pour saisir les inputs
3. Exécuter via une API spécialisée `/api/run-with-inputs`

### Solution 3: Simulation d'Inputs ⭐ **Simple**

**Avantages :**
- Aucun changement de sécurité nécessaire
- Compatible avec le système existant

**Inconvénients :**
- Moins interactif pour l'utilisateur
- Pédagogiquement moins efficace

## 🚀 Plan d'Action Recommandé

### Phase 1: Analyse Complète (✅ Fait)
- [x] Identifier le problème de sécurité
- [x] Analyser l'architecture existante
- [x] Documenter les solutions possibles

### Phase 2: Implémentation Solution 1
- [ ] Créer un détecteur d'exercices avec input
- [ ] Modifier le validateur de sécurité pour les exercices interactifs
- [ ] Implémenter l'interface de saisie d'inputs
- [ ] Créer l'endpoint `/api/run-with-inputs`

### Phase 3: Tests et Validation
- [ ] Tester avec l'exercice "03-conditions"
- [ ] Créer de nouveaux exercices avec inputs
- [ ] Validation sécurité complète
- [ ] Documentation utilisateur

## 📋 Exercices Impactés

### Exercices existants avec inputs :
1. **"03-conditions"** : Feu rouge/vert
   - Input : "rouge" ou "vert"
   - Tests existants : ✅ fonctionnels

### Potentiels nouveaux exercices :
1. **Calculatrice simple** : Opérations mathématiques avec inputs
2. **Devine le nombre** : Jeu avec input utilisateur
3. **Formulaire de contact** : Collecte et affiche des informations
4. **Quiz interactif** : Pose questions et vérifie les réponses

## 🔒 Considérations de Sécurité

### Risques identifiés :
- Injection de code via les inputs
- Boucles infinies avec input
- Fuites d'information via les outputs

### Mesures de sécurité nécessaires :
1. **Validation des inputs** : Limiter la taille et le contenu
2. **Timeout étendu** : Permettre les interactions utilisateur
3. **Sanitization** : Nettoyer les inputs et outputs
4. **Monitoring** : Logger toutes les exécutions avec inputs

## 🎯 Recommandation Finale

La **Solution 1 (Input Sécurisé avec Interface Spéciale)** est recommandée car :

1. **Pédagogiquement optimale** : Les utilisateurs apprennent véritablement l'interaction
2. **Techniquement robuste** : Maintient la sécurité tout en permettant l'interactivité
3. **Scalable** : Permet de créer facilement de nouveaux exercices interactifs
4. **Utilisateur-friendly** : Expérience intuitive et engageante

Cette solution transformera complètement l'expérience d'apprentissage pour les exercices interactifs tout en maintenant les standards de sécurité élevés de Capitaine Python.