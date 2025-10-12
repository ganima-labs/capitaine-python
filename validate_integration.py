#!/usr/bin/env python3
"""
Script d'intégration pour valider tous les exercices du système
"""

import requests
import json
import sys
from pathlib import Path

def validate_local_course(file_path: str):
    """Valide un fichier JSON de cours local"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            course_data = json.load(f)

        response = requests.post("http://localhost:8080/api/validate/course", json={"course": course_data})
        result = response.json()

        return result
    except Exception as e:
        return {"error": str(e), "valid": False}

def validate_all_courses():
    """Valide tous les cours disponibles dans le système"""
    try:
        response = requests.get("http://localhost:8080/api/validate/stats")
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def generate_quality_report():
    """Génère un rapport de qualité complet"""
    print("🎯 RAPPORT DE QUALITÉ - CAPITAINE PYTHON")
    print("=" * 60)

    # Statistiques globales
    stats = validate_all_courses()
    if 'error' in stats:
        print(f"❌ Erreur: {stats['error']}")
        return

    summary = stats['summary']
    health = stats['health_status']

    print(f"📚 Cours analysés: {summary['total_courses']}")
    print(f"📝 Exercices analysés: {summary['total_exercises']}")
    print(f"✅ Exercices valides: {summary['valid_exercises']}")
    print(f"📊 Taux de qualité: {summary['overall_quality_percent']:.1f}%")
    print(f"⭐ Score moyen: {summary['average_score']:.1f}/100")
    print(f"🏥 État de santé: {health['status'].upper()}")
    print()

    # Détails par cours
    print("📋 DÉTAILS PAR COURS:")
    print("-" * 40)

    for course in stats['courses']:
        status_icon = "✅" if course['valid'] else "❌"
        print(f"{status_icon} {course['course_id']}: {course['exercises']} exercices, score {course['average_score']:.1f}/100")

        if course['error_count'] > 0 or course['warning_count'] > 0:
            print(f"   ⚠️  {course['error_count']} erreurs, {course['warning_count']} avertissements")
        print()

    # Validation du cours python-basics en détail
    print("🔍 ANALYSE DÉTAILLÉE - COURS PYTHON-BASICS")
    print("-" * 50)

    basics_validation = validate_local_course("app/backend/courses/python-basics.json")
    if 'error' in basics_validation:
        print(f"❌ Erreur: {basics_validation['error']}")
        return

    print(f"✅ Cours valide: {basics_validation['valid']}")
    print(f"📊 Résumé: {basics_validation['summary']}")

    # Top 5 des exercices avec le meilleur score
    exercises = basics_validation['exercises']
    exercises.sort(key=lambda x: x['score'], reverse=True)

    print("\n🏆 TOP 5 DES EXERCICES (par score):")
    for i, ex in enumerate(exercises[:5], 1):
        print(f"{i}. {ex['exercise_id']}: {ex['score']}/100 ({'valide' if ex['valid'] else 'invalide'})")

    # Top 5 des exercices avec le plus d'issues
    exercises.sort(key=lambda x: x['error_count'] + x['warning_count'], reverse=True)

    print("\n🚨 TOP 5 DES EXERCICES À AMÉLIORER:")
    for i, ex in enumerate(exercises[:5], 1):
        total_issues = ex['error_count'] + ex['warning_count']
        if total_issues > 0:
            print(f"{i}. {ex['exercise_id']}: {total_issues} issues ({ex['error_count']} erreurs, {ex['warning_count']} avertissements)")

    print("\n💡 RECOMMANDATIONS GLOBALES:")
    print("-" * 30)

    if summary['overall_quality_percent'] >= 90:
        print("🎉 Qualité excellente ! Le système est prêt pour la production.")
    elif summary['overall_quality_percent'] >= 80:
        print("✅ Bonne qualité globale. Quelques améliorations possibles.")
    elif summary['overall_quality_percent'] >= 70:
        print("⚠️  Qualité moyenne. Des améliorations sont recommandées.")
    else:
        print("❌ Qualité insuffisante. Des corrections sont nécessaires.")

    # Recommandations spécifiques
    if summary['error_count'] > 0:
        print(f"🔧 Corriger les {summary['error_count']} erreurs bloquantes avant tout déploiement.")

    if summary['warning_count'] > 10:
        print("💡 Envisager de corriger les avertissements pour améliorer l'expérience utilisateur.")

    print("\n📊 MÉTRIQUES DE QUALITÉ:")
    print("-" * 25)
    print(f"• Taux de validation: {summary['valid_exercises']}/{summary['total_exercises']} ({summary['overall_quality_percent']:.1f}%)")
    print(f"• Score de qualité moyen: {summary['average_score']:.1f}/100")
    print(f"• Densité d'issues: {(summary['error_count'] + summary['warning_count'])/summary['total_exercises']:.1f} issues/exercice")

def validate_specific_exercise(course_id: str, exercise_id: str):
    """Valide un exercice spécifique"""
    try:
        response = requests.get(f"http://localhost:8080/api/validate/exercises/{course_id}/{exercise_id}")
        result = response.json()

        print(f"🔍 Validation de {course_id}/{exercise_id}")
        print("=" * 40)
        print(f"✅ Valide: {result['valid']}")
        print(f"⭐ Score: {result['score']}/100")
        print(f"📊 {result['summary']}")

        if result['issues']:
            print("\n🚨 Issues détectées:")
            for issue in result['issues']:
                level_icon = {'error': '❌', 'warning': '⚠️', 'info': '💡'}
                icon = level_icon.get(issue['level'], '📝')
                print(f"  {icon} [{issue['category']}] {issue['message']}")
                if issue.get('suggestion'):
                    print(f"     💡 {issue['suggestion']}")

        if result['recommendations']:
            print("\n💡 Recommandations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")

        return result
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Rapport complet
        generate_quality_report()
    elif len(sys.argv) == 3:
        # Validation d'un exercice spécifique
        course_id, exercise_id = sys.argv[1], sys.argv[2]
        validate_specific_exercise(course_id, exercise_id)
    else:
        print("Usage:")
        print("  python3 validate_integration.py                    # Rapport complet")
        print("  python3 validate_integration.py <course> <exercise> # Exercice spécifique")
        print("\nExemples:")
        print("  python3 validate_integration.py python-basics 01-print")