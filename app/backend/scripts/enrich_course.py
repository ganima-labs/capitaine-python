#!/usr/bin/env python3
"""
Script pour enrichir un fichier de cours JSON avec des images encodées en base64.
Génère des icônes et bannières SVG et les injecte dans le fichier de cours.
"""

import json
import base64
import argparse
from pathlib import Path
from typing import Dict, Any


def generate_icon_svg(theme: str = "python", color: str = "#3776ab") -> str:
    """Génère une icône SVG pour le cours"""
    if theme == "python":
        return f'''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="pythonGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
            <stop offset="100%" style="stop-color:#FFD43B;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="32" cy="32" r="30" fill="url(#pythonGradient)" stroke="#333" stroke-width="2"/>
    <text x="32" y="24" font-family="Arial, sans-serif" font-size="8" font-weight="bold" text-anchor="middle" fill="white">Py</text>
    <text x="32" y="36" font-family="Arial, sans-serif" font-size="10" font-weight="bold" text-anchor="middle" fill="white">Expert</text>
    <path d="M15 40 Q32 48 49 40" stroke="white" stroke-width="2" fill="none"/>
    <circle cx="20" cy="42" r="2" fill="white"/>
    <circle cx="44" cy="42" r="2" fill="white"/>
</svg>'''
    elif theme == "adventure":
        return f'''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="advGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#FF6B35;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#F7931E;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect x="2" y="2" width="60" height="60" rx="8" fill="url(#advGradient)" stroke="#333" stroke-width="2"/>
    <text x="32" y="20" font-family="Arial, sans-serif" font-size="10" font-weight="bold" text-anchor="middle" fill="white">Aventure</text>
    <text x="32" y="32" font-family="Arial, sans-serif" font-size="8" text-anchor="middle" fill="white">Python</text>
    <path d="M20 40 L28 48 L36 40 L44 48" stroke="white" stroke-width="3" fill="none" stroke-linecap="round"/>
    <circle cx="20" cy="38" r="2" fill="white"/>
    <circle cx="32" cy="38" r="2" fill="white"/>
    <circle cx="44" cy="38" r="2" fill="white"/>
</svg>'''
    elif theme == "basics":
        return f'''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="basicsGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#4CAF50;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#8BC34A;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="32" cy="32" r="30" fill="url(#basicsGradient)" stroke="#333" stroke-width="2"/>
    <text x="32" y="24" font-family="Arial, sans-serif" font-size="10" font-weight="bold" text-anchor="middle" fill="white">Python</text>
    <text x="32" y="36" font-family="Arial, sans-serif" font-size="8" text-anchor="middle" fill="white">Bases</text>
    <rect x="18" y="42" width="28" height="4" rx="2" fill="white"/>
    <rect x="23" y="48" width="18" height="4" rx="2" fill="white"/>
</svg>'''
    else:
        # Icône générique
        return f'''<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="genericGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667EEA;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764BA2;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect x="2" y="2" width="60" height="60" rx="12" fill="url(#genericGradient)" stroke="#333" stroke-width="2"/>
    <text x="32" y="30" font-family="Arial, sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="white">Code</text>
    <path d="M15 40 L25 35 L35 45 L45 40 L50 50" stroke="white" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="25" cy="35" r="2" fill="white"/>
    <circle cx="35" cy="45" r="2" fill="white"/>
</svg>'''


def generate_banner_svg(course_title: str, theme: str = "python", color: str = "#3776ab") -> str:
    """Génère une bannière SVG pour le cours"""
    # Nettoyer le titre pour l'affichage
    display_title = course_title.replace("Python Expert - ", "")

    if theme == "python":
        return f'''<svg width="800" height="200" viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bannerGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
            <stop offset="50%" style="stop-color:#3498db;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2ECC71;stop-opacity:1" />
        </linearGradient>
        <pattern id="codePattern" x="0" y="0" width="40" height="20" patternUnits="userSpaceOnUse">
            <text x="2" y="15" font-family="monospace" font-size="8" fill="#ffffff20">def</text>
            <text x="20" y="15" font-family="monospace" font-size="8" fill="#ffffff20">()</text>
        </pattern>
    </defs>
    <rect width="800" height="200" fill="url(#bannerGradient)"/>
    <rect width="800" height="200" fill="url(#codePattern)"/>
    <text x="400" y="60" font-family="Arial, sans-serif" font-size="28" font-weight="bold" text-anchor="middle" fill="white">{display_title}</text>
    <text x="400" y="90" font-family="Arial, sans-serif" font-size="16" text-anchor="middle" fill="#ffffffee">Maîtrisez les concepts avancés de la programmation</text>

    <g transform="translate(50, 120)">
        <rect x="0" y="0" width="120" height="60" rx="8" fill="#ffffff20" stroke="white" stroke-width="1"/>
        <text x="60" y="25" font-family="monospace" font-size="10" text-anchor="middle" fill="white">@decorator</text>
        <text x="60" y="40" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">meta</text>
        <text x="60" y="52" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">async</text>
    </g>

    <g transform="translate(200, 120)">
        <rect x="0" y="0" width="120" height="60" rx="8" fill="#ffffff20" stroke="white" stroke-width="1"/>
        <text x="60" y="25" font-family="monospace" font-size="10" text-anchor="middle" fill="white">class</text>
        <text x="60" y="40" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">OOP</text>
        <text x="60" y="52" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">inherit</text>
    </g>

    <g transform="translate(350, 120)">
        <rect x="0" y="0" width="120" height="60" rx="8" fill="#ffffff20" stroke="white" stroke-width="1"/>
        <text x="60" y="25" font-family="monospace" font-size="10" text-anchor="middle" fill="white">yield</text>
        <text x="60" y="40" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">gen</text>
        <text x="60" y="52" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">async</text>
    </g>

    <g transform="translate(500, 120)">
        <rect x="0" y="0" width="120" height="60" rx="8" fill="#ffffff20" stroke="white" stroke-width="1"/>
        <text x="60" y="25" font-family="monospace" font-size="10" text-anchor="middle" fill="white">with</text>
        <text x="60" y="40" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">context</text>
        <text x="60" y="52" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">manager</text>
    </g>

    <g transform="translate(650, 120)">
        <rect x="0" y="0" width="120" height="60" rx="8" fill="#ffffff20" stroke="white" stroke-width="1"/>
        <text x="60" y="25" font-family="monospace" font-size="10" text-anchor="middle" fill="white">__</text>
        <text x="60" y="40" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">meta</text>
        <text x="60" y="52" font-family="monospace" font-size="8" text-anchor="middle" fill="#ffffffcc">class</text>
    </g>
</svg>'''
    else:
        # Bannière générique
        return f'''<svg width="800" height="200" viewBox="0 0 800 200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="bannerGradientGeneric" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667EEA;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#764BA2;stop-opacity:1" />
        </linearGradient>
    </defs>
    <rect width="800" height="200" fill="url(#bannerGradientGeneric)"/>
    <text x="400" y="70" font-family="Arial, sans-serif" font-size="32" font-weight="bold" text-anchor="middle" fill="white">{display_title}</text>
    <text x="400" y="100" font-family="Arial, sans-serif" font-size="18" text-anchor="middle" fill="#ffffffee">Apprentissage interactif</text>
    <circle cx="200" cy="130" r="15" fill="#ffffff30"/>
    <circle cx="400" cy="130" r="15" fill="#ffffff30"/>
    <circle cx="600" cy="130" r="15" fill="#ffffff30"/>
</svg>'''


def svg_to_base64(svg_content: str) -> str:
    """Convertit SVG en base64"""
    svg_bytes = svg_content.encode('utf-8')
    base64_bytes = base64.b64encode(svg_bytes)
    return base64_bytes.decode('utf-8')


def determine_theme_from_course_id(course_id: str) -> str:
    """Détermine le thème graphique selon l'ID du cours"""
    if "expert" in course_id.lower():
        return "python"
    elif "adventure" in course_id.lower():
        return "adventure"
    elif "basics" in course_id.lower() or "base" in course_id.lower():
        return "basics"
    else:
        return "generic"


def enrich_course_json(input_file: Path, output_file: Path = None, overwrite: bool = False) -> Dict[str, Any]:
    """
    Enrichit un fichier de cours JSON avec des images encodées en base64

    Args:
        input_file: Fichier JSON d'entrée
        output_file: Fichier JSON de sortie (si None, utilise le fichier d'entrée)
        overwrite: Si True, écrase le fichier d'entrée

    Returns:
        Le dictionnaire JSON enrichi
    """

    # Charger le fichier JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        course_data = json.load(f)

    # Déterminer le fichier de sortie
    if output_file is None:
        if overwrite:
            output_file = input_file
        else:
            # Créer un nouveau nom de fichier
            suffix = "_enriched"
            output_file = input_file.with_name(f"{input_file.stem}{suffix}.json")

    # Extraire les informations du cours
    course_id = course_data.get('metadata', {}).get('id', input_file.stem)
    title = course_data.get('metadata', {}).get('title', {}).get('fr', 'Cours Python')

    # Déterminer le thème
    theme = determine_theme_from_course_id(course_id)

    # Générer l'icône
    icon_svg = generate_icon_svg(theme)
    icon_base64 = svg_to_base64(icon_svg)

    # Générer la bannière
    banner_svg = generate_banner_svg(title, theme)
    banner_base64 = svg_to_base64(banner_svg)

    # Ajouter les images au fichier
    if 'images' not in course_data['metadata']:
        course_data['metadata']['images'] = {}

    course_data['metadata']['images']['icon'] = {
        'type': 'svg+xml',
        'encoding': 'base64',
        'data': icon_base64,
        'generated': True,
        'theme': theme
    }

    course_data['metadata']['images']['banner'] = {
        'type': 'svg+xml',
        'encoding': 'base64',
        'data': banner_base64,
        'generated': True,
        'theme': theme
    }

    # Mettre à jour les chemins d'images pour utiliser les données embarquées
    if 'icon_path' in course_data['metadata']:
        course_data['metadata']['icon_embedded'] = f"data:image/svg+xml;base64,{icon_base64}"

    if 'banner_path' in course_data['metadata']:
        course_data['metadata']['banner_embedded'] = f"data:image/svg+xml;base64,{banner_base64}"

    # Sauvegarder le fichier enrichi
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(course_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Cours enrichi sauvegardé dans: {output_file}")
    print(f"   Thème détecté: {theme}")
    print(f"   Icône: {len(icon_base64)} caractères (base64)")
    print(f"   Bannière: {len(banner_base64)} caractères (base64)")

    return course_data


def main():
    parser = argparse.ArgumentParser(description="Enrichit un fichier de cours JSON avec des images encodées en base64")
    parser.add_argument("input_file", help="Fichier JSON du cours à enrichir")
    parser.add_argument("-o", "--output", help="Fichier JSON de sortie (optionnel)")
    parser.add_argument("--overwrite", action="store_true", help="Écrase le fichier d'entrée")
    parser.add_argument("--verbose", "-v", action="store_true", help="Mode verbeux")

    args = parser.parse_args()

    input_path = Path(args.input_file)

    if not input_path.exists():
        print(f"❌ Erreur: Le fichier {input_path} n'existe pas.")
        return 1

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = None

    try:
        # Enrichir le cours
        enriched_data = enrich_course_json(
            input_path,
            output_path,
            args.overwrite
        )

        if args.verbose:
            print("\n📋 Métadonnées du cours enrichi:")
            metadata = enriched_data.get('metadata', {})
            print(f"   ID: {metadata.get('id', 'N/A')}")
            print(f"   Titre: {metadata.get('title', {}).get('fr', 'N/A')}")
            print(f"   Auteur: {metadata.get('author', {}).get('name', 'N/A')}")
            print(f"   Version: {metadata.get('version', 'N/A')}")
            print(f"   Images: {len(metadata.get('images', {}))} générées")

        return 0

    except Exception as e:
        print(f"❌ Erreur lors de l'enrichissement: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())