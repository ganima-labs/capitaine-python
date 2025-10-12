import json
import os
from pathlib import Path
from typing import Dict, List, Optional

class CourseManager:
    def __init__(self, courses_dir: str = None):
        self.courses_dir = courses_dir or os.path.join(os.path.dirname(__file__), "courses")
        self.courses: Dict[str, Dict] = {}
        self.current_course_id: Optional[str] = None
        self.load_all_courses()

    def load_all_courses(self):
        """Charge tous les fichiers JSON de cours du dossier courses"""
        courses_path = Path(self.courses_dir)
        if not courses_path.exists():
            print(f"⚠️ Dossier des cours introuvable: {self.courses_dir}")
            return

        for course_file in courses_path.glob("*.json"):
            try:
                with open(course_file, 'r', encoding='utf-8') as f:
                    course_data = json.load(f)
                    course_id = course_data.get("meta", {}).get("id")
                    if course_id:
                        self.courses[course_id] = course_data
                        print(f"✅ Cours chargé: {course_id}")
                    else:
                        print(f"⚠️ Fichier de cours sans ID: {course_file}")
            except Exception as e:
                print(f"❌ Erreur lors du chargement du cours {course_file}: {e}")

    def get_course_list(self) -> List[Dict]:
        """Retourne la liste des cours disponibles avec métadonnées"""
        return [
            {
                "id": course_id,
                "title": course.get("meta", {}).get("title", "Sans titre"),
                "description": course.get("meta", {}).get("description", ""),
                "level": course.get("meta", {}).get("level", "Non spécifié"),
                "estimated_hours": course.get("meta", {}).get("estimated_hours", 0),
                "exercise_count": len(course.get("exercises", [])),
                "total_stars": sum(ex.get("stars", 0) for ex in course.get("exercises", [])),
                "theme_name": course.get("theme", {}).get("name", "default"),
                "icon": course.get("meta", {}).get("icon", None)
            }
            for course_id, course in self.courses.items()
        ]

    def get_course(self, course_id: str) -> Optional[Dict]:
        """Retourne les données complètes d'un cours"""
        return self.courses.get(course_id)

    def get_course_exercises(self, course_id: str) -> List[Dict]:
        """Retourne la liste des exercices d'un cours avec toutes les données nécessaires"""
        course = self.get_course(course_id)
        if not course:
            return []

        return [
            {
                "id": ex.get("id"),
                "title": ex.get("title"),
                "stars": ex.get("stars", 0),
                "prompt": ex.get("prompt", {}),
                "starter": ex.get("starter", {}),
                "theory": ex.get("theory"),
                "hints": ex.get("hints", []),
                "tests": ex.get("tests", [])
            }
            for ex in course.get("exercises", [])
        ]

    def get_exercise(self, course_id: str, exercise_id: str) -> Optional[Dict]:
        """Retourne les données d'un exercice spécifique"""
        course = self.get_course(course_id)
        if not course:
            return None

        for exercise in course.get("exercises", []):
            if exercise.get("id") == exercise_id:
                return exercise

        return None

    def get_course_theme(self, course_id: str) -> Dict:
        """Retourne le thème d'un cours ou un thème par défaut"""
        course = self.get_course(course_id)
        if not course:
            return self.get_default_theme()

        return course.get("theme", self.get_default_theme())

    def get_default_theme(self) -> Dict:
        """Retourne le thème par défaut"""
        return {
            "name": "default",
            "primary_color": "#0077be",
            "secondary_color": "#00a8cc",
            "background_color": "#0a1929",
            "surface_color": "#1e3a5f",
            "text_color": "#ffffff",
            "accent_color": "#00d4aa",
            "gradient_start": "#0a1929",
            "gradient_end": "#1e3a5f",
            "font_family": "system-ui, -apple-system, sans-serif"
        }

    def set_current_course(self, course_id: str) -> bool:
        """Définit le cours actuel"""
        if course_id in self.courses:
            self.current_course_id = course_id
            return True
        return False

    def get_current_course(self) -> Optional[str]:
        """Retourne l'ID du cours actuel"""
        return self.current_course_id

    def get_star_map(self, course_id: str) -> Dict[str, int]:
        """Retourne un mapping des étoiles par exercice pour un cours"""
        exercises = self.get_course_exercises(course_id)
        return {ex["id"]: ex["stars"] for ex in exercises}

# Instance globale du gestionnaire de cours
course_manager = CourseManager()