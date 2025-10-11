import sqlite3, os, json
DB = os.getenv("DB_PATH", "./progress.db")

def _conn(): return sqlite3.connect(DB)

def init_db():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS progress(user TEXT, exercise TEXT, ok INTEGER, raw TEXT, ts DATETIME DEFAULT CURRENT_TIMESTAMP)")
        c.commit()

def save_result(user, ex, res):
    with _conn() as c:
        c.execute("INSERT INTO progress(user, exercise, ok, raw) VALUES(?,?,?,?)",(user, ex, 1 if res.get('ok') else 0, json.dumps(res)))
        c.commit()

def get_progress(user):
    with _conn() as c:
        cur = c.execute("SELECT exercise, MAX(ok) FROM progress WHERE user=? GROUP BY exercise", (user,))
        done = {row[0]: row[1] for row in cur.fetchall()}

    # Import dynamique pour éviter la dépendance circulaire
    try:
        from .course_manager import course_manager

        # Calculer les étoiles en fonction de tous les cours disponibles
        total_stars = 0
        completed_exercises = []

        for course_id in course_manager.courses.keys():
            star_map = course_manager.get_star_map(course_id)
            for exercise_key, stars in star_map.items():
                # Les exercices sont stockés avec le format "courseId_exerciseId"
                full_exercise_id = f"{course_id}_{exercise_key}"
                if done.get(full_exercise_id) == 1:
                    total_stars += stars
                    completed_exercises.append(full_exercise_id)

        return {"completed": completed_exercises, "stars": total_stars}
    except ImportError:
        # Fallback si course_manager n'est pas disponible
        return {"completed": [k for k,v in done.items() if v==1], "stars": 0}
