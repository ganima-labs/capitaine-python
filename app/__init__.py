"""
Package principal pour l'application Capitaine Python
"""

__version__ = "1.0.0"
__title__ = "Capitaine Python"
__description__ = "Plateforme d'apprentissage interactif pour Python"

# Re-export backend submodules so legacy `app.<mod>` paths resolve.
from .backend import (  # noqa: F401
    config,
    course_manager,
    db,
    exercises,
    grader,
    main,
    secure_grader,
    security,
)