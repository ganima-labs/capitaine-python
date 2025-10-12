import re
import html
import json
from typing import Dict, Any, List

class SecurityValidator:
    """Classe de validation et sanitization pour la sécurité du code"""

    # Modules Python dangereux à bloquer
    DANGEROUS_MODULES = {
        'os', 'sys', 'subprocess', 'importlib', 'imp', 'compile',
        'eval', 'exec', 'execfile', '__import__', 'open', 'file',
        'input', 'raw_input', 'reload', 'vars', 'globals', 'locals',
        'dir', 'hasattr', 'getattr', 'setattr', 'delattr',
        'exit', 'quit', 'help', 'copyright', 'credits', 'license',
        'shutil', 'tempfile', 'threading', 'multiprocessing',
        'socket', 'urllib', 'httplib', 'ftplib', 'smtplib',
        'pickle', 'marshal', 'ctypes', 'inspect', 'ast',
        'platform', 'sysconfig', 'distutils', 'pkgutil'
    }

    # Fonctions dangereuses à bloquer
    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'reload',
        'open', 'file', 'input', 'raw_input', 'exit', 'quit',
        'help', 'copyright', 'credits', 'license'
    }

    # Patterns d'injection dangereux
    DANGEROUS_PATTERNS = [
        r'__import__\s*\(',
        r'eval\s*\(',
        r'exec\s*\(',
        r'compile\s*\(',
        r'open\s*\(',
        r'file\s*\(',
        r'subprocess\.',
        r'os\.',
        r'sys\.',
        r'import\s+',
        r'from\s+.*\s+import',
        r'class\s+\w+\s*\(',
        r'def\s+\w+\s*\([^)]*\)\s*:',
        r'lambda\s+',
        r'@\w+',  # Decorators
        r'global\s+',
        r'nonlocal\s+',
    ]

    # Limites pour la sécurité
    MAX_CODE_LENGTH = 5000  # caractères
    MAX_EXECUTION_TIME = 10  # secondes
    MAX_MEMORY_USAGE = 128 * 1024 * 1024  # 128MB

    @classmethod
    def sanitize_string(cls, input_str: str, max_length: int = 1000) -> str:
        """Sanitize une chaîne de caractères"""
        if not isinstance(input_str, str):
            raise ValueError("Input must be a string")

        # Limiter la longueur
        if len(input_str) > max_length:
            raise ValueError(f"Input too long (max {max_length} characters)")

        # HTML encoding pour prévenir XSS
        sanitized = html.escape(input_str)

        # Supprimer les caractères de contrôle sauf newline et tab
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)

        return sanitized.strip()

    @classmethod
    def validate_course_id(cls, course_id: str) -> str:
        """Valide et sanitize un ID de cours"""
        if not isinstance(course_id, str):
            raise ValueError("Course ID must be a string")

        # Pattern alphanumeric avec tirets et underscores seulement
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, course_id):
            raise ValueError("Invalid course ID format")

        if len(course_id) > 50:
            raise ValueError("Course ID too long")

        return course_id.lower()

    @classmethod
    def validate_exercise_id(cls, exercise_id: str) -> str:
        """Valide et sanitize un ID d'exercice"""
        if not isinstance(exercise_id, str):
            raise ValueError("Exercise ID must be a string")

        # Pattern alphanumeric avec tirets et underscores seulement
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not re.match(pattern, exercise_id):
            raise ValueError("Invalid exercise ID format")

        if len(exercise_id) > 50:
            raise ValueError("Exercise ID too long")

        return exercise_id.lower()

    @classmethod
    def validate_learner_name(cls, learner: str) -> str:
        """Valide et sanitize un nom d'apprenant"""
        if not isinstance(learner, str):
            raise ValueError("Learner name must be a string")

        # Nettoyer et limiter
        sanitized = cls.sanitize_string(learner, 50)

        # Pattern alphanumeric avec espaces et tirets
        pattern = r'^[a-zA-Z0-9\s_-]+$'
        if not re.match(pattern, sanitized):
            raise ValueError("Invalid learner name format")

        return sanitized.strip()

    @classmethod
    def analyze_code_security(cls, code: str, allow_input: bool = False) -> Dict[str, Any]:
        """Analyse un code Python pour détecter les menaces de sécurité"""
        if not isinstance(code, str):
            raise ValueError("Code must be a string")

        if len(code) > cls.MAX_CODE_LENGTH:
            raise ValueError(f"Code too long (max {cls.MAX_CODE_LENGTH} characters)")

        issues = []
        warnings = []

        # Détecter si le code utilise input()
        has_input = re.search(rf'\b{"input"}\s*\(', code)

        # Vérifier les modules dangereux
        for module in cls.DANGEROUS_MODULES:
            # Skip input check if allowed and this is the input module/function
            if allow_input and module in ['input', 'raw_input'] and has_input:
                continue
            if re.search(rf'\b{re.escape(module)}\b', code):
                issues.append(f"Dangerous module detected: {module}")

        # Vérifier les fonctions dangereuses
        for func in cls.DANGEROUS_FUNCTIONS:
            # Skip input check if allowed and this is the input function
            if allow_input and func in ['input', 'raw_input'] and has_input:
                continue
            if re.search(rf'\b{re.escape(func)}\s*\(', code):
                issues.append(f"Dangerous function detected: {func}")

        # Vérifier les patterns dangereux
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, code):
                issues.append(f"Dangerous pattern detected: {pattern}")

        # Vérifications supplémentaires
        if '__' in code and 'import' in code:
            issues.append("Potential dunder import detected")

        if code.count('(') > 50 or code.count('[') > 50:
            warnings.append("Complex code structure detected")

        # Détection d'obfuscation
        obfuscation_issues = cls.detect_obfuscation_attempts(code)
        issues.extend(obfuscation_issues)

        # Avertissement spécial pour les exercices avec input
        if has_input and allow_input:
            warnings.append("This code contains input() - interactive execution required")
        elif has_input and not allow_input:
            issues.append("input() function detected but not allowed in this context")

        return {
            'safe': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'risk_level': 'low' if len(issues) == 0 else 'high' if len(issues) > 3 else 'medium',
            'has_input': has_input,
            'requires_interactive_mode': has_input and allow_input
        }

    @classmethod
    def create_safe_execution_context(cls) -> Dict[str, Any]:
        """Crée un contexte d'exécution sécurisé pour eval/exec"""
        # Builtins sécurisés
        safe_builtins = {
            'abs': abs,
            'all': all,
            'any': any,
            'bin': bin,
            'bool': bool,
            'chr': chr,
            'dict': dict,
            'divmod': divmod,
            'enumerate': enumerate,
            'float': float,
            'hex': hex,
            'int': int,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'oct': oct,
            'ord': ord,
            'pow': pow,
            'range': range,
            'reversed': reversed,
            'round': round,
            'set': set,
            'slice': slice,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'type': type,
            'zip': zip,
            'print': print,
        }

        # Modules sécurisés
        safe_modules = {
            'math': __import__('math'),
            'random': __import__('random'),
            'datetime': __import__('datetime'),
            'itertools': __import__('itertools'),
            'collections': __import__('collections'),
            'string': __import__('string'),
        }

        return {**safe_builtins, **safe_modules}

    @classmethod
    def validate_json_data(cls, data: Any, max_size: int = 1024 * 1024) -> Dict[str, Any]:
        """Valide les données JSON entrantes"""
        if isinstance(data, str):
            # Si c'est une chaîne, la parser
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format")
        elif isinstance(data, dict):
            parsed = data
        else:
            raise ValueError("Data must be JSON string or dict")

        # Vérifier la taille
        json_str = json.dumps(parsed)
        if len(json_str) > max_size:
            raise ValueError(f"JSON data too large (max {max_size} bytes)")

        return parsed

    @classmethod
    def sanitize_error_message(cls, error_msg: str) -> str:
        """Sanitize les messages d'erreur pour éviter les fuites d'information"""
        if not isinstance(error_msg, str):
            return "An error occurred"

        # Masquer les chemins du système de fichiers
        sanitized = re.sub(r'/[a-zA-Z0-9_/-]+', '[PATH]', error_msg)

        # Masquer les adresses IP
        sanitized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP]', sanitized)

        # Masquer les noms de fichiers et extensions sensibles
        sanitized = re.sub(r'\b\w+\.(json|py|txt|log|db|sql)\b', '[FILE]', sanitized)

        # Masquer les clés API et tokens (pattern plus précis)
        sanitized = re.sub(r'\b[a-zA-Z0-9_-]{32,}\b', '[TOKEN]', sanitized)

        # Limiter la longueur
        if len(sanitized) > 200:
            sanitized = sanitized[:200] + "..."

        return sanitized

    @classmethod
    def validate_file_upload(cls, filename: str, content: bytes, max_size: int = 5*1024*1024) -> Dict[str, Any]:
        """Validation de sécurité pour les fichiers uploadés"""
        if not isinstance(filename, str):
            raise ValueError("Filename must be a string")

        if not isinstance(content, bytes):
            raise ValueError("Content must be bytes")

        # Vérifier la taille
        if len(content) > max_size:
            raise ValueError(f"File too large (max {max_size} bytes)")

        # Vérifier le nom de fichier
        if len(filename) > 255:
            raise ValueError("Filename too long")

        # Patterns dangereux dans les noms de fichiers
        dangerous_patterns = [
            r'\.\.',  # Directory traversal
            r'[<>:"|?*]',  # Caractères interdits
            r'\.(exe|bat|cmd|sh|ps1|vbs|jar)$',  # Exécutables
            r'\.(php|jsp|asp|aspx)$',  # Scripts web
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                raise ValueError(f"Dangerous filename pattern detected: {pattern}")

        # Vérifier le type de contenu par signature
        allowed_signatures = {
            b'{': 'json',  # JSON files start with {
            b'[': 'json',  # ou [
        }

        content_type = 'unknown'
        for signature, file_type in allowed_signatures.items():
            if content.startswith(signature):
                content_type = file_type
                break

        if content_type not in ['json']:
            raise ValueError(f"File type {content_type} not allowed")

        return {
            'safe': True,
            'filename': cls.sanitize_string(filename, 255),
            'content_type': content_type,
            'size': len(content)
        }

    @classmethod
    def validate_url_domain(cls, url: str, allowed_domains: List[str] = None) -> bool:
        """Validation de sécurité des URLs"""
        if not isinstance(url, str):
            return False

        # Pattern de base pour URL
        url_pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*$'
        if not re.match(url_pattern, url):
            return False

        # Extraire le domaine
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Domaines par défaut autorisés
        default_allowed = [
            'github.com', 'raw.githubusercontent.com', 'gitlab.com',
            'gist.githubusercontent.com', 'pastebin.com', 'dpaste.org'
        ]

        allowed = allowed_domains or default_allowed

        # Vérifier que le domaine est dans la liste autorisée
        for allowed_domain in allowed:
            if allowed_domain in domain:
                return True

        # Autoriser localhost en dev (inclure les ports)
        if domain.startswith('localhost') or domain.startswith('127.0.0.1'):
            return True

        # Vérifier les sous-domaines localhost avec ports
        if 'localhost' in domain or '127.0.0.1' in domain:
            return True

        return False

    @classmethod
    def detect_obfuscation_attempts(cls, code: str) -> List[str]:
        """Détection de tentatives d'obfuscation de code"""
        issues = []

        # Encodages suspects
        if re.search(r'\\[x0-9a-fA-F]{2,}', code):
            issues.append("Hex escape sequences detected")

        # Obfuscation par strings inversées (simplifié pour éviter les erreurs regex)
        if '][::-1]' in code:
            issues.append("String reversal obfuscation detected")

        # Tentatives de contourner les filtres par variations
        if re.search(r"(e|E)\+(v|V)+(a|A)+(l|L)", code):
            issues.append("Eval function obfuscation detected")

        # Base64 ou autres encodages
        import base64
        try:
            # Tenter de décoder du base64 dans le code
            base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
            matches = re.findall(base64_pattern, code)
            for match in matches[:3]:  # Limiter pour éviter le DoS
                base64.b64decode(match, validate=True)
                issues.append("Base64 encoded content detected")
        except:
            pass

        return issues