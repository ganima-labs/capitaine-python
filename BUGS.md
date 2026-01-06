# 🐛 BUGS.md - Bugs Identifiés et Corrections

**Date de revue**: 2026-01-05
**Version**: 2.2.6
**Statut**: 🔴 Corrections critiques requises

---

## 🔴 Bugs Critiques (À corriger immédiatement)

### BUG #1: Fonction dupliquée dans main.py
**Fichier**: `app/backend/main.py`
**Lignes**: 580-586 et 598-605
**Sévérité**: 🔴 CRITIQUE

**Description**:
Deux fonctions avec le même nom `get_exercise` dans le même module. La deuxième définition (ligne 598) écrase la première (ligne 580), rendant l'endpoint `/api/courses/{course_id}/exercises/{exercise_id}` inaccessible.

**Code problématique**:
```python
# Ligne 580
@app.get("/api/courses/{course_id}/exercises/{exercise_id}")
def get_exercise(course_id: str, exercise_id: str):
    """Retourne les détails d'un exercice"""
    ...

# Ligne 598 - ÉCRASE LA PREMIÈRE!
@app.get("/api/exercises/{eid}")
def get_exercise(eid: str):  # ⚠️ MÊME NOM
    """API legacy - cherche l'exercice dans tous les cours"""
    ...
```

**Impact**:
- L'endpoint moderne `/api/courses/{course_id}/exercises/{exercise_id}` ne fonctionne pas
- Erreurs silencieuses dans l'application
- Mauvaise expérience utilisateur

**Correction**:
```python
@app.get("/api/exercises/{eid}")
def get_exercise_legacy(eid: str):  # Renommer
    """API legacy - cherche l'exercice dans tous les cours"""
    ...
```

**Statut**: ⏳ En cours de correction

---

### BUG #2: Configuration de sécurité incohérente
**Fichier**: `app/backend/security.py`
**Lignes**: 10-48
**Sévérité**: 🔴 CRITIQUE

**Description**:
Le `SecurityValidator` bloque `input()`, les définitions de fonctions (`def`), et les lambdas, alors que les exercices officiels dans `exercises.py` utilisent ces constructions légitimes.

**Code problématique**:
```python
# security.py
DANGEROUS_MODULES = {
    'input', 'raw_input',  # ⚠️ Bloqué
}

DANGEROUS_PATTERNS = [
    r'def\s+\w+\s*\([^)]*\)\s*:',  # ⚠️ Bloque TOUTES les fonctions
    r'lambda\s+',  # ⚠️ Bloque les lambdas
]
```

Mais dans `exercises.py`:
```python
{
    "id": "03-conditions",
    "starter": 'couleur = input()\nif couleur == "rouge":\n...'
},
{
    "id": "05-fonction-bonjour",
    "starter": "def bonjour(nom):\n    return 'Bonjour ' + nom"
}
```

**Impact**:
- Les exercices officiels échouent à la validation de sécurité
- Utilisateurs ne peuvent pas compléter les exercices légitimes
- Incohérence entre design et implémentation

**Correction**:
Implémenter un système de permissions contextuelles :
- `allow_input=True` pour les exercices qui nécessitent input()
- `allow_functions=True` pour les exercices de fonctions
- Blacklist seulement pour import/exec/eval/os/sys

**Statut**: ⏳ En cours de correction

---

### BUG #3: Sandbox désactivé par défaut
**Fichier**: `docker-compose.yml`
**Ligne**: 13
**Sévérité**: 🔴 CRITIQUE

**Description**:
Le système d'exécution sécurisé (`secure_grader.py`) existe mais est désactivé par défaut dans la configuration Docker.

**Code problématique**:
```yaml
# docker-compose.yml
environment:
  - USE_SECURE_EXECUTOR=false  # ⚠️ Désactivé!
```

Alors que `secure_grader.py` implémente:
- Limites de ressources (CPU, mémoire)
- Timeout d'exécution
- Sandbox avec restrictions

**Impact**:
- Code utilisateur exécuté sans protection renforcée
- Risque de déni de service (boucles infinies)
- Risque d'épuisement de ressources

**Correction**:
```yaml
environment:
  - USE_SECURE_EXECUTOR=true  # Activer par défaut
```

**Statut**: ⏳ En cours de correction

---

## 🟡 Bugs Majeurs (À corriger cette semaine)

### BUG #4: Initialisation multiple de l'application
**Fichier**: `app/frontend/app.js`
**Lignes**: 1625-1653
**Sévérité**: 🟡 MAJEUR

**Description**:
L'application s'initialise 3 fois au chargement de la page.

**Code problématique**:
```javascript
initApp();  // Ligne 1642 - Appel immédiat

document.addEventListener('DOMContentLoaded', function() {
  initApp();  // Ligne 1647 - Au chargement DOM
});

window.addEventListener('load', function() {
  setTimeout(initApp, 100);  // Ligne 1652 - Après chargement complet
});
```

**Impact**:
- Appels API triplés (gaspillage bande passante)
- Performance dégradée
- Logs dupliqués dans la console

**Correction**:
```javascript
let isInitialized = false;

async function initApp() {
  if (isInitialized) return;
  isInitialized = true;

  console.log("🚀 Initialisation...");
  await loadCourses();
}

// Utiliser seulement DOMContentLoaded
document.addEventListener('DOMContentLoaded', initApp);
```

**Statut**: ⏳ En cours de correction

---

### BUG #5: Logs de debug en production
**Fichier**: `app/frontend/app.js`
**Lignes**: Multiple (484, 488, 533, 539, etc.)
**Sévérité**: 🟡 MAJEUR

**Description**:
Des dizaines de `console.log()` dans le code production.

**Code problématique**:
```javascript
console.log("🚀 Début du chargement des cours...");
console.log("✅ Cours reçus:", courses);
console.log("🎨 Interface des cours générée");
console.log("🖱️ Écouteurs d'événements ajoutés");
// ... 50+ console.log
```

**Impact**:
- Pollution de la console
- Fuite potentielle d'informations
- Performance légèrement dégradée

**Correction**:
```javascript
const DEBUG = process.env.NODE_ENV === 'development';

function log(...args) {
  if (DEBUG) console.log(...args);
}

// Utiliser log() au lieu de console.log()
log("🚀 Début du chargement des cours...");
```

**Statut**: ⏳ En cours de correction

---

### BUG #6: Duplication de code grader
**Fichiers**: `app/backend/grader.py` et `app/backend/secure_grader.py`
**Sévérité**: 🟡 MAJEUR

**Description**:
Deux implémentations différentes de la même logique de validation sans abstraction commune.

**Impact**:
- Maintenance difficile
- Risque de désynchronisation
- ~30% de code dupliqué

**Correction**:
Créer une classe abstraite `BaseGrader` avec:
- Méthode abstraite `execute(code, tests)`
- Méthode commune `validate_security(code)`
- Implémentations: `PistonGrader` et `SecureLocalGrader`

**Statut**: 📋 Planifié

---

## 🟢 Bugs Mineurs (Amélioration continue)

### BUG #7: Pas de migrations de base de données
**Fichier**: `app/backend/db.py`
**Sévérité**: 🟢 MINEUR

**Description**:
Utilisation de `CREATE TABLE IF NOT EXISTS` sans système de migrations.

**Impact**:
- Difficile de faire évoluer le schéma
- Pas de versioning de la DB
- Risque de corruption lors de changements

**Correction**:
Implémenter Alembic pour les migrations.

**Statut**: 📋 Planifié

---

### BUG #8: Frontend sans build process
**Fichier**: `app/frontend/`
**Sévérité**: 🟢 MINEUR

**Description**:
- Pas de bundler (Webpack/Vite/Rollup)
- Tailwind chargé depuis CDN (lent)
- Pas de minification
- Pas de tree-shaking

**Impact**:
- Performance sous-optimale
- Taille des fichiers plus grande
- Pas de modules ES6

**Correction**:
Mettre en place Vite avec:
- Build optimisé
- Tailwind compilé
- Modules ES6
- Hot Module Replacement

**Statut**: 📋 Planifié

---

## 📊 Statistiques

```
Bugs critiques:     3
Bugs majeurs:       3
Bugs mineurs:       2
Total:              8

Corrigés:           0/8 (0%)
En cours:           4/8 (50%)
Planifiés:          4/8 (50%)
```

---

## 🎯 Plan de Correction

### Phase 1 - Critique (Aujourd'hui)
- [ ] BUG #1: Renommer fonction dupliquée
- [ ] BUG #2: Corriger validation sécurité
- [ ] BUG #3: Activer sandbox

### Phase 2 - Majeur (Cette semaine)
- [ ] BUG #4: Implémenter garde initialisation
- [ ] BUG #5: Système de logging conditionnel
- [ ] BUG #6: Refactoring grader

### Phase 3 - Mineur (Ce mois)
- [ ] BUG #7: Migrations Alembic
- [ ] BUG #8: Build process frontend

---

## 📝 Notes

### Bugs non listés mais observés:
- Nommage inconsistant des tests (`_complete` suffix)
- Pas de gestion des erreurs réseau dans le frontend
- Pas de retry logic pour les appels API
- XSS potentiel dans `displayLocalizedLesson()` (innerHTML sans sanitization complète)

### Recommandations additionnelles:
1. Ajouter pre-commit hooks pour linting
2. Implémenter CI/CD avec tests automatiques
3. Ajouter monitoring en production (Sentry)
4. Documentation d'architecture (ADR)

---

**Dernière mise à jour**: 2026-01-05
**Prochaine révision**: Après correction bugs critiques
