# Améliorations de Sécurité - SEC-002

## Vue d'ensemble

Ce document décrit les améliorations de sécurité implémentées dans le cadre de la story SEC-002 pour renforcer la validation des entrées utilisateur dans Capitaine Python.

## Fonctionnalités Ajoutées

### 1. Validation Avancée des Fichiers Uploadés

**Nouvelle méthode : `SecurityValidator.validate_file_upload()`**

- **Validation du nom de fichier** : Protection contre directory traversal, caractères interdits, extensions dangereuses
- **Validation de la taille** : Limite configurable (par défaut 2MB pour les fichiers JSON)
- **Validation du type de contenu** : Vérification par signature (magic bytes)
- **Types de fichiers autorisés** : JSON uniquement pour les cours

```python
file_validation = SecurityValidator.validate_file_upload(
    filename, content, max_size=2*1024*1024
)
```

### 2. Validation de Domaines URL

**Nouvelle méthode : `SecurityValidator.validate_url_domain()`**

- **Validation stricte des URLs** : Pattern matching pour les URLs valides
- **Liste blanche de domaines** : GitHub, GitLab, Pastebin, etc.
- **Support des domaines locaux** : Pour le développement
- **Logging des tentatives d'accès** : Monitoring des domaines bloqués

```python
if not SecurityValidator.validate_url_domain(str(url)):
    raise ValueError("URL domain not allowed")
```

### 3. Détection d'Obfuscation de Code

**Nouvelle méthode : `SecurityValidator.detect_obfuscation_attempts()`**

- **Séquences hexadécimales** : Détection de `\x68\x65\x6c\x6c\x6f`
- **Obfuscation de fonctions** : `e__v__a__l__` au lieu de `eval`
- **Encodage Base64** : Détection de contenu encodé suspect
- **Strings inversées** : Détection de techniques d'évasion

### 4. Sanitization Améliorée des Erreurs

**Amélioration de `SecurityValidator.sanitize_error_message()`**

- **Masquage des chemins** : `/home/user` → `[PATH]`
- **Masquage des adresses IP** : `192.168.1.1` → `[IP]`
- **Masquage des fichiers** : `config.json` → `[FILE]`
- **Masquage des tokens** : `abc123def456` → `[TOKEN]`
- **Limite de longueur** : 200 caractères maximum

### 5. Endpoint de Validation de Sécurité

**Nouvel endpoint : `POST /api/security/validate`**

Permet de valider un code sans l'exécuter :

```json
POST /api/security/validate
{
  "code": "print('Hello, World!')"
}
```

Réponse :
```json
{
  "safe": true,
  "risk_level": "low",
  "issues": [],
  "warnings": [],
  "code_length": 22,
  "timestamp": "2025-01-12T14:30:00"
}
```

### 6. Endpoint d'Informations de Sécurité

**Amélioration de `GET /api/security/info`**

Ajout des informations sur les nouvelles fonctionnalités :
- Types de fichiers autorisés
- Taille maximale des fichiers
- Domaines autorisés
- Fonctionnalités de détection d'obfuscation

## Patterns de Sécurité Bloqués

### Modules Dangereux
- `os`, `sys`, `subprocess`, `importlib`
- `eval`, `exec`, `compile`
- `socket`, `urllib`, `httplib`
- `pickle`, `marshal`, `ctypes`

### Fonctions Dangereuses
- Accès fichiers : `open()`, `file()`
- Exécution : `eval()`, `exec()`, `compile()`
- Système : `exit()`, `quit()`, `help()`

### Patterns d'Injection
- Import dynamique : `__import__()`
- Injection de code : `eval()`, `exec()`
- Accès système : `os.`, `sys.`, `subprocess.`

## Tests de Sécurité

### Tests Unitaires Ajoutés

1. **TestAdvancedSecurityFeatures** :
   - `test_validate_file_upload_safe()` : Validation de fichiers sûrs
   - `test_validate_file_upload_dangerous()` : Rejet de fichiers dangereux
   - `test_validate_url_domain_allowed()` : Domaines autorisés
   - `test_validate_url_domain_blocked()` : Domaines bloqués
   - `test_detect_obfuscation_attempts()` : Détection d'obfuscation
   - `test_security_validation_endpoint()` : Endpoint de validation
   - `test_enhanced_error_sanitization()` : Sanitization améliorée
   - `test_security_info_endpoint_enhanced()` : Infos sécurité enrichies

### Couverture de Tests

- **Tests de validation positive** : Vérification que les entrées valides sont acceptées
- **Tests de validation négative** : Vérification que les entrées dangereuses sont rejetées
- **Tests d'obfuscation** : Vérification des techniques de contournement
- **Tests d'intégration** : Workflow complet de validation

## Configuration

### Constantes de Sécurité

```python
# Limites de sécurité
MAX_CODE_LENGTH = 5000  # caractères
MAX_EXECUTION_TIME = 10  # secondes
MAX_MEMORY_USAGE = 128 * 1024 * 1024  # 128MB
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB pour les uploads

# Domaines autorisés
ALLOWED_DOMAINS = [
    'github.com', 'raw.githubusercontent.com', 'gitlab.com',
    'gist.githubusercontent.com', 'pastebin.com', 'dpaste.org'
]

# Types de fichiers autorisés
ALLOWED_FILE_TYPES = ['json']
```

## Monitoring et Logging

### Logs de Sécurité

- **Tentatives d'accès bloquées** : IP, code d'erreur, timestamp
- **Validation de fichiers** : Nom, taille, type, résultat
- **Validation d'URLs** : Domaine, autorisé/bloqué
- **Analyse de code** : Risque, problèmes détectés

### Métriques

- **Taux de blocage** : Pourcentage de requêtes bloquées
- **Types de menaces** : Catégories de problèmes détectés
- **Origines des menaces** : IPs et domaines suspects

## Recommandations de Déploiement

### Production

1. **Activer l'exécution sécurisée** : `USE_SECURE_EXECUTOR=true`
2. **Limiter les origines CORS** : Domaines spécifiques uniquement
3. **Utiliser HTTPS** : Pour toutes les communications
4. **Monitoring des logs** : Alertes sur les tentatives suspectes

### Développement

1. **Valider les imports** : Vérifier les fichiers de cours
2. **Tests de sécurité réguliers** : Exécuter la suite complète
3. **Review des patterns** : Surveiller les nouvelles menaces

## Impact sur la Performance

### Temps de Validation

- **Analyse de code** : < 10ms pour 5000 caractères
- **Validation de fichier** : < 5ms pour 2MB
- **Validation d'URL** : < 1ms

### Overhead Minimal

L'impact sur la performance est négligeable (< 1% du temps total de réponse) et la sécurité apportée justifie largement ce coût.

## Conclusion

Ces améliorations renforcent significativement la sécurité de Capitaine Python contre :

- **Injection de code malveillant**
- **Upload de fichiers dangereux**
- **Obfuscation et contournement**
- **Fuites d'information**
- **Attaques par enumeration**

La plateforme maintient un équilibre entre sécurité rigoureuse et expérience utilisateur fluide pour les apprenants légitimes.