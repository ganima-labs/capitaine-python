# Makefile pour Capitaine Python - Tests et Qualité

.PHONY: help install install-dev test test-coverage test-watch test-all lint format security-check

# Default target
help:
	@echo "Capitaine Python - Commandes de test et qualité"
	@echo ""
	@echo "Installation:"
	@echo "  install     - Installe les dépendances de production"
	@echo "  install-dev - Installe les dépendances de développement et tests"
	@echo ""
	@echo "Tests:"
	@echo "  test        - Exécute tous les tests avec couverture"
	@echo "  test-fast   - Exécute les tests sans couverture (rapide)"
	@echo "  test-watch  - Exécute les tests en continu (watch mode)"
	@echo "  test-unit   - Exécute uniquement les tests unitaires"
	@echo "  test-integration - Exécute uniquement les tests d'intégration"
	@echo "  test-security - Exécute uniquement les tests de sécurité"
	@echo ""
	@echo "Couverture:"
	@echo "  coverage    - Génère le rapport de couverture HTML"
	@echo "  coverage-open - Ouvre le rapport de couverture dans le navigateur"
	@echo ""
	@echo "Qualité:"
	@echo "  lint        - Analyse statique du code"
	@echo "  format      - Formate le code Python"
	@echo "  security-check - Vérification de sécurité complète"
	@echo ""
	@echo "Docker:"
	@echo "  docker-test - Exécute les tests dans Docker"
	@echo "  build       - Build Docker image"
	@echo "  run         - Lance l'application Docker"

# Installation
install:
	pip install -r requirements-test.txt

install-dev:
	pip install -r requirements-test.txt
	pip install black flake8 mypy bandit safety pre-commit

# Tests
test:
	pytest --cov=app.backend --cov-report=html --cov-report=term-missing --cov-fail-under=100

test-fast:
	pytest -x --tb=short

test-watch:
	pytest -f --tb=short

test-unit:
	pytest -m "unit" --cov=app.backend --cov-report=term-missing

test-integration:
	pytest -m "integration" --cov=app.backend --cov-report=term-missing

test-security:
	pytest -m "security" --cov=app.backend --cov-report=term-missing

test-all: test lint security-check

# Couverture
coverage:
	pytest --cov=app.backend --cov-report=html --cov-report=term-missing --cov-fail-under=100
	@echo "Rapport de couverture généré dans htmlcov/"

coverage-open: coverage
	open htmlcov/index.html

# Qualité
lint:
	flake8 app/backend/ --max-line-length=88 --extend-ignore=E203,W503
	mypy app/backend/ --ignore-missing-imports

format:
	black app/backend/ --line-length=88

security-check:
	bandit -r app/backend/ -f json -o bandit-report.json
	safety check --json --output safety-report.json
	@echo "Rapports de sécurité générés : bandit-report.json, safety-report.json"

# Docker
docker-test:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

build:
	docker-compose build

run:
	docker-compose up -d

# Nettoyage
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ bandit-report.json safety-report.json

# CI/CD helpers
ci-install:
	pip install --upgrade pip
	pip install -r requirements-test.txt

ci-test:
	pytest --cov=app.backend --cov-report=xml --cov-report=term-missing --cov-fail-under=100 --junitxml=test-results.xml

ci-security:
	bandit -r app/backend/ -f json -o bandit-report.json
	safety check --json --output safety-report.json