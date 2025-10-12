# Story QUAL-007 - Nettoyer les tests incohérents (run_with_input inutile)

## Résumé

✅ **Story terminée avec succès** - Correction des incohérences dans l'utilisation de `run_with_input('')`

## Problème identifié

Des exercices utilisaient `run_with_input('')` dans leurs tests alors que leur code de départ ne contenait aucune fonction `input()`. C'était inutile et incohérent :

- **run_with_input('')** : Simule des inputs utilisateur (nécessaire seulement si le code utilise `input()`)
- **execute_code()** : Exécute simple sans inputs (approprié pour les codes sans `input()`)

## Analyse effectuée

### Fichiers analysés
1. `/app/backend/exercises.py` - Ancien système (non utilisé)
2. `/app/backend/courses/python-basics.json` - Système actuel (13 exercices)

### Incohérences trouvées
- **exercises.py** : 3 exercices avec `run_with_input('')` inutile
- **python-basics.json** : 6 exercices avec `run_with_input('')` inutile

**Total** : 9 corrections nécessaires

## Corrections apportées

### 1. Amélioration du grader.py
Ajout de la fonction `execute_code()` dans le harness de test :

```python
def execute_code():
    backup_stdout = sys.stdout
    buf = io.StringIO()
    sys.stdout = buf
    try:
        exec(student_code, {})
        return buf.getvalue()
    finally:
        sys.stdout = backup_stdout
```

### 2. Corrections dans exercises.py
3 exercices corrigés :
- **01-print** : `run_with_input('')` → `execute_code()`
- **02-variables** : `run_with_input('')` → `execute_code()`
- **04-boucle-for** : `run_with_input('')` → `execute_code()`

### 3. Corrections dans python-basics.json
6 exercices corrigés avec 7 remplacements au total (certains exercices avaient plusieurs tests avec `run_with_input('')`)

Exemples de corrections :
```javascript
// Avant
"tests": ["out = run_with_input('')", "assert out.strip() == 'Salut Capitaine Python !'"]

// Après
"tests": ["out = execute_code()", "assert out.strip() == 'Salut Capitaine Python !'"]
```

## Scripts créés

### analyze_run_with_input.py
Script d'analyse pour détecter les incohérences `run_with_input` vs `input()`.

### fix_json_exercises.py
Script de correction automatique qui :
- Détecte les incohérences dans les fichiers JSON
- Remplace `run_with_input('')` par `execute_code()`
- Vérifie qu'aucune incohérence ne subsiste

## Vérification finale

✅ **Zéro incohérence restante** - Tous les exercices utilisent maintenant la bonne méthode :
- **1 exercice** utilise `run_with_input()` (exercice 03-conditions qui contient `input()`)
- **12 exercices** utilisent `execute_code()` (exercices sans `input()`)

## Impact

- **Qualité** : Tests plus cohérents et logiques
- **Performance** : Exécution plus rapide (pas de simulation d'inputs inutile)
- **Maintenabilité** : Code plus clair et standardisé
- **Pédagogie** : Meilleure distinction entre exercices interactifs et non-interactifs

## Prochaines étapes

Continuer avec les stories restantes :
- **QUAL-008** : Créer un validateur d'exercices automatisé
- **QUAL-009** : Documenter les patterns autorisés/interdits