# 🔧 Plan de Refactoring - app.js

**Date**: 2026-01-05
**Fichier cible**: `app/frontend/app.js`
**Taille actuelle**: 2200 lignes
**Objectif**: Modulaire, maintenable, performant

---

## 📊 État Actuel

### Problèmes Identifiés

1. **Fichier monolithique** : 2200 lignes dans un seul fichier
2. **Responsabilités mélangées** : API, UI, routing, i18n dans le même fichier
3. **Duplication de code** : `loadCourses()` vs `loadCoursesSimple()`, `selectCourse()` vs `selectCourseSimple()`
4. **Variables globales** : `current`, `starter`, `currentCourseId`, `currentLanguage`, etc.
5. **Pas de séparation des préoccupations** : Logique métier mélangée avec manipulation DOM
6. **Console.log en production** : Logs de debug partout
7. **Pas de gestion d'erreur centralisée** : try/catch dispersés

### Métriques Actuelles

```
Total lignes:              2200
Fonctions:                 ~50
Variables globales:        ~15
Duplication estimée:       ~20%
Complexité cyclomatique:   Élevée (non mesurée)
Maintenabilité:            Faible
```

---

## 🎯 Architecture Cible

### Structure Modulaire Proposée

```
app/frontend/
├── index.html
├── main.js                      # Point d'entrée (50 lignes)
├── config/
│   └── constants.js             # Configuration (30 lignes)
├── api/
│   ├── apiClient.js             # Client API générique (80 lignes)
│   ├── coursesApi.js            # API cours (60 lignes)
│   └── exercisesApi.js          # API exercices (80 lignes)
├── services/
│   ├── courseManager.js         # Gestion cours (100 lignes)
│   ├── exerciseManager.js       # Gestion exercices (150 lignes)
│   ├── progressTracker.js       # Suivi progression (80 lignes)
│   └── themeManager.js          # Gestion thèmes (70 lignes)
├── ui/
│   ├── courseList.js            # Affichage liste cours (120 lignes)
│   ├── exerciseList.js          # Affichage liste exercices (100 lignes)
│   ├── codeEditor.js            # Éditeur de code (150 lignes)
│   ├── exerciseDisplay.js       # Affichage exercice (120 lignes)
│   ├── outputConsole.js         # Console sortie (80 lignes)
│   ├── progressDisplay.js       # Affichage progression (70 lignes)
│   └── notifications.js         # Système de notifications (60 lignes)
├── i18n/
│   ├── translator.js            # Système i18n (100 lignes)
│   └── translations.json        # Fichier de traductions
├── utils/
│   ├── logger.js                # Logging conditionnel (40 lignes)
│   ├── validators.js            # Validations (50 lignes)
│   └── dom.js                   # Helpers DOM (40 lignes)
└── features/
    ├── interactiveInputs.js     # Gestion inputs interactifs (150 lignes)
    ├── courseImport.js          # Import de cours (100 lignes)
    └── lessonDisplay.js         # Affichage leçons (120 lignes)
```

### Taille Estimée par Module

| Module | Lignes | Pourcentage |
|--------|--------|-------------|
| api/ | 220 | 11% |
| services/ | 400 | 20% |
| ui/ | 700 | 35% |
| features/ | 370 | 18% |
| i18n/ | 100 | 5% |
| utils/ | 130 | 6% |
| main.js | 50 | 2.5% |
| config/ | 30 | 1.5% |
| **TOTAL** | **~2000** | **100%** |

**Réduction**: -200 lignes grâce à l'élimination de duplication

---

## 📋 Plan d'Exécution Détaillé

### Phase 1 - Infrastructure de Base (2-3h)

#### Étape 1.1 : Créer la structure de dossiers
```bash
mkdir -p app/frontend/{api,services,ui,i18n,utils,features,config}
```

#### Étape 1.2 : Créer le système de logging
**Fichier**: `app/frontend/utils/logger.js`
```javascript
// logger.js
const DEBUG = window.location.hostname === 'localhost' ||
              window.location.search.includes('debug=true');

export const logger = {
  log: (...args) => DEBUG && console.log(...args),
  error: (...args) => console.error(...args),
  warn: (...args) => DEBUG && console.warn(...args),
  info: (...args) => DEBUG && console.info(...args)
};
```

#### Étape 1.3 : Créer les constantes
**Fichier**: `app/frontend/config/constants.js`
```javascript
// constants.js
export const API_BASE_URL = window.location.origin;
export const DEFAULT_LANGUAGE = 'fr';
export const SUPPORTED_LANGUAGES = ['fr', 'en', 'es', 'de'];
export const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
export const MAX_INPUTS = 10;
export const DEFAULT_TIMEOUT = 30;
```

#### Étape 1.4 : Créer le client API générique
**Fichier**: `app/frontend/api/apiClient.js`
```javascript
// apiClient.js
import { logger } from '../utils/logger.js';
import { API_BASE_URL } from '../config/constants.js';

class ApiClient {
  constructor(baseUrl = API_BASE_URL) {
    this.baseUrl = baseUrl;
    this.cache = new Map();
  }

  async fetch(url, options = {}) {
    const fullUrl = `${this.baseUrl}${url}`;
    logger.log(`📡 API call: ${fullUrl}`);

    try {
      const response = await fetch(fullUrl, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      logger.log(`✅ API response from ${url}`, data);
      return data;
    } catch (error) {
      logger.error(`❌ API error for ${url}:`, error);
      throw error;
    }
  }

  async get(url, useCache = false) {
    if (useCache && this.cache.has(url)) {
      const cached = this.cache.get(url);
      if (Date.now() - cached.timestamp < CACHE_DURATION) {
        logger.log(`💾 Cache hit: ${url}`);
        return cached.data;
      }
    }

    const data = await this.fetch(url);

    if (useCache) {
      this.cache.set(url, { data, timestamp: Date.now() });
    }

    return data;
  }

  async post(url, body) {
    return this.fetch(url, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }

  clearCache() {
    this.cache.clear();
  }
}

export const apiClient = new ApiClient();
```

---

### Phase 2 - Extraction des APIs (2-3h)

#### Étape 2.1 : API Cours
**Fichier**: `app/frontend/api/coursesApi.js`
```javascript
// coursesApi.js
import { apiClient } from './apiClient.js';

export const coursesApi = {
  async getAllCourses() {
    return apiClient.get('/api/courses', true);
  },

  async getCourse(courseId) {
    return apiClient.get(`/api/courses/${courseId}`, true);
  },

  async getTheme(courseId) {
    return apiClient.get(`/api/courses/${courseId}/theme`, true);
  },

  async selectCourse(courseId) {
    return apiClient.post(`/api/courses/${courseId}/select`);
  },

  async importCourse(url, courseId = null, overwrite = true) {
    return apiClient.post('/api/courses/import', {
      url,
      course_id: courseId,
      overwrite
    });
  },

  async deleteCourse(courseId) {
    return apiClient.fetch(`/api/courses/${courseId}`, {
      method: 'DELETE'
    });
  }
};
```

#### Étape 2.2 : API Exercices
**Fichier**: `app/frontend/api/exercisesApi.js`
```javascript
// exercisesApi.js
import { apiClient } from './apiClient.js';

export const exercisesApi = {
  async getExercises(courseId) {
    return apiClient.get(`/api/courses/${courseId}/exercises`, true);
  },

  async getExercise(courseId, exerciseId) {
    return apiClient.get(`/api/courses/${courseId}/exercises/${exerciseId}`);
  },

  async runCode(code, courseId = 'python-basics') {
    return apiClient.post('/api/run', { code, course_id: courseId });
  },

  async runWithInputs(code, inputs, courseId = 'python-basics', timeout = 30) {
    return apiClient.post('/api/run-with-inputs', {
      code,
      inputs,
      course_id: courseId,
      timeout
    });
  },

  async gradeCode(code, courseId, exerciseId, learner = 'Hugo') {
    return apiClient.post('/api/grade', {
      code,
      course_id: courseId,
      exercise_id: exerciseId,
      learner
    });
  },

  async getProgress(learner = 'Hugo') {
    return apiClient.get(`/api/progress?learner=${learner}`);
  }
};
```

---

### Phase 3 - Services Métier (3-4h)

#### Étape 3.1 : Gestionnaire de Cours
**Fichier**: `app/frontend/services/courseManager.js`
```javascript
// courseManager.js
import { coursesApi } from '../api/coursesApi.js';
import { logger } from '../utils/logger.js';

class CourseManager {
  constructor() {
    this.courses = [];
    this.currentCourseId = null;
  }

  async loadCourses() {
    try {
      logger.log("📚 Chargement des cours...");
      this.courses = await coursesApi.getAllCourses();
      logger.log(`✅ ${this.courses.length} cours chargés`);
      return this.courses;
    } catch (error) {
      logger.error("❌ Erreur lors du chargement des cours:", error);
      throw error;
    }
  }

  async getCourse(courseId) {
    try {
      return await coursesApi.getCourse(courseId);
    } catch (error) {
      logger.error(`❌ Erreur lors du chargement du cours ${courseId}:`, error);
      throw error;
    }
  }

  async selectCourse(courseId) {
    try {
      logger.log(`🎯 Sélection du cours: ${courseId}`);
      await coursesApi.selectCourse(courseId);
      this.currentCourseId = courseId;
      return courseId;
    } catch (error) {
      logger.error(`❌ Erreur lors de la sélection du cours:`, error);
      throw error;
    }
  }

  getCurrentCourse() {
    return this.currentCourseId;
  }

  async importCourse(url, courseId = null, overwrite = true) {
    try {
      const response = await coursesApi.importCourse(url, courseId, overwrite);
      if (response.success) {
        await this.loadCourses(); // Recharger les cours
      }
      return response;
    } catch (error) {
      logger.error("❌ Erreur lors de l'import:", error);
      throw error;
    }
  }
}

export const courseManager = new CourseManager();
```

#### Étape 3.2 : Gestionnaire d'Exercices
**Fichier**: `app/frontend/services/exerciseManager.js`
```javascript
// exerciseManager.js
import { exercisesApi } from '../api/exercisesApi.js';
import { logger } from '../utils/logger.js';

class ExerciseManager {
  constructor() {
    this.currentExercise = null;
    this.exercises = [];
  }

  async loadExercises(courseId) {
    try {
      logger.log(`📝 Chargement des exercices du cours ${courseId}...`);
      this.exercises = await exercisesApi.getExercises(courseId);
      logger.log(`✅ ${this.exercises.length} exercices chargés`);
      return this.exercises;
    } catch (error) {
      logger.error("❌ Erreur lors du chargement des exercices:", error);
      throw error;
    }
  }

  async selectExercise(courseId, exerciseId) {
    try {
      logger.log(`🎯 Sélection de l'exercice: ${exerciseId}`);
      this.currentExercise = await exercisesApi.getExercise(courseId, exerciseId);
      return this.currentExercise;
    } catch (error) {
      logger.error(`❌ Erreur lors de la sélection de l'exercice:`, error);
      throw error;
    }
  }

  getCurrentExercise() {
    return this.currentExercise;
  }

  async runCode(code, courseId) {
    return exercisesApi.runCode(code, courseId);
  }

  async runWithInputs(code, inputs, courseId, timeout) {
    return exercisesApi.runWithInputs(code, inputs, courseId, timeout);
  }

  async gradeCode(code, courseId, exerciseId, learner) {
    return exercisesApi.gradeCode(code, courseId, exerciseId, learner);
  }
}

export const exerciseManager = new ExerciseManager();
```

#### Étape 3.3 : Gestionnaire de Progression
**Fichier**: `app/frontend/services/progressTracker.js`
```javascript
// progressTracker.js
import { exercisesApi } from '../api/exercisesApi.js';
import { logger } from '../utils/logger.js';

class ProgressTracker {
  constructor() {
    this.progress = { completed: [], stars: 0 };
  }

  async loadProgress(learner = 'Hugo') {
    try {
      this.progress = await exercisesApi.getProgress(learner);
      return this.progress;
    } catch (error) {
      logger.error("❌ Erreur lors du chargement de la progression:", error);
      return { completed: [], stars: 0 };
    }
  }

  isCompleted(courseId, exerciseId) {
    const fullId = `${courseId}_${exerciseId}`;
    return this.progress.completed.includes(fullId);
  }

  getStars() {
    return this.progress.stars;
  }

  getCompletedCount() {
    return this.progress.completed.length;
  }
}

export const progressTracker = new ProgressTracker();
```

---

### Phase 4 - Composants UI (4-5h)

#### Étape 4.1 : Liste des Cours
**Fichier**: `app/frontend/ui/courseList.js`
```javascript
// courseList.js
import { courseManager } from '../services/courseManager.js';
import { translator } from '../i18n/translator.js';
import { logger } from '../utils/logger.js';

export class CourseList {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.onCourseSelect = null;
  }

  render(courses) {
    if (!this.container) {
      logger.error("❌ Container non trouvé pour CourseList");
      return;
    }

    this.container.innerHTML = courses.map(course => this.renderCourseCard(course)).join('');
    this.attachEventListeners();
  }

  renderCourseCard(course) {
    const title = translator.getLocalizedValue(course.title);
    const description = translator.getLocalizedValue(course.description);

    return `
      <div class="course-card" data-course-id="${course.id}">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-2">
            ${course.icon ? `<img src="${course.icon}" alt="${title}" class="w-6 h-6 rounded" />` : '<span class="text-xl">📚</span>'}
            <h3 class="font-bold text-white">${title}</h3>
          </div>
          <span class="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">${course.level}</span>
        </div>
        <p class="text-gray-300 text-sm mb-3">${description}</p>
        <div class="flex flex-wrap gap-2 text-xs">
          <span class="px-2 py-1 bg-gray-600 text-gray-200 rounded">
            ${course.exercise_count} ${translator.t('courses.exercises')}
          </span>
          <span class="px-2 py-1 bg-amber-600/20 text-amber-300 rounded">
            ${course.total_stars} ⭐
          </span>
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    this.container.querySelectorAll('.course-card').forEach(card => {
      card.addEventListener('click', () => {
        const courseId = card.dataset.courseId;
        this.selectCourse(courseId);
      });
    });
  }

  async selectCourse(courseId) {
    this.highlightSelected(courseId);

    if (this.onCourseSelect) {
      await this.onCourseSelect(courseId);
    }
  }

  highlightSelected(courseId) {
    this.container.querySelectorAll('.course-card').forEach(card => {
      const isSelected = card.dataset.courseId === courseId;

      if (isSelected) {
        card.classList.add('border-blue-500', 'bg-blue-900/30');
        card.classList.remove('border-transparent');
      } else {
        card.classList.remove('border-blue-500', 'bg-blue-900/30');
        card.classList.add('border-transparent');
      }
    });
  }
}
```

#### Étape 4.2 : Console de Sortie
**Fichier**: `app/frontend/ui/outputConsole.js`
```javascript
// outputConsole.js
import { logger } from '../utils/logger.js';

export class OutputConsole {
  constructor(outputId, statusId = null, overlayId = null, statsId = null) {
    this.outputEl = document.getElementById(outputId);
    this.statusEl = statusId ? document.getElementById(statusId) : null;
    this.overlayEl = overlayId ? document.getElementById(overlayId) : null;
    this.statsEl = statsId ? document.getElementById(statsId) : null;
  }

  showStatus(message = "En cours...") {
    if (this.statusEl) {
      this.statusEl.classList.remove('hidden');
      this.statusEl.textContent = message;
    }
    if (this.outputEl) {
      this.outputEl.textContent = `⏳ ${message}`;
    }
  }

  hideStatus() {
    if (this.statusEl) {
      this.statusEl.classList.add('hidden');
    }
  }

  displaySuccess(output, executionTime = null) {
    this.hideStatus();

    if (this.outputEl) {
      this.outputEl.textContent = output || "Exécution terminée sans sortie";
      this.outputEl.parentElement.classList.add('border-green-500/50', 'bg-green-950/10');

      setTimeout(() => {
        this.outputEl.parentElement.classList.remove('border-green-500/50', 'bg-green-950/10');
      }, 3000);
    }

    if (this.overlayEl && executionTime !== null) {
      this.showSuccessOverlay(executionTime);
    }
  }

  displayError(errorMessage) {
    this.hideStatus();

    if (this.outputEl) {
      this.outputEl.innerHTML = `<span class="text-red-400">❌ Erreur :</span>\n${errorMessage}`;
      this.outputEl.parentElement.classList.add('border-red-500/50', 'bg-red-950/10');

      setTimeout(() => {
        this.outputEl.parentElement.classList.remove('border-red-500/50', 'bg-red-950/10');
      }, 3000);
    }
  }

  showSuccessOverlay(executionTime) {
    if (!this.overlayEl) return;

    this.overlayEl.classList.remove('hidden');

    if (this.statsEl) {
      this.displayStats(executionTime, true);
    }

    setTimeout(() => {
      this.overlayEl.classList.add('hidden');
    }, 2000);
  }

  displayStats(timeMs, success) {
    if (!this.statsEl) return;

    const timeEl = this.statsEl.querySelector('#execution-time');
    const barEl = this.statsEl.querySelector('#performance-bar');

    this.statsEl.classList.remove('hidden');

    // Calculer performance
    let performance = 100;
    if (timeMs > 1000) performance = 20;
    else if (timeMs > 500) performance = 40;
    else if (timeMs > 200) performance = 60;
    else if (timeMs > 100) performance = 80;

    // Couleur selon succès
    let colorClass = success ? 'bg-green-500' : 'bg-red-500';
    if (success && performance < 50) colorClass = 'bg-yellow-500';
    else if (success && performance < 80) colorClass = 'bg-blue-500';

    barEl.className = `${colorClass} h-1 rounded-full transition-all duration-500`;
    barEl.style.width = `${performance}%`;

    // Message
    if (success) {
      if (timeMs < 50) timeEl.textContent = `${timeMs}ms ⚡ Ultra rapide !`;
      else if (timeMs < 100) timeEl.textContent = `${timeMs}ms 🚀 Très performant !`;
      else if (timeMs < 200) timeEl.textContent = `${timeMs}ms 👍 Bonne performance !`;
      else timeEl.textContent = `${timeMs}ms 💪 Code fonctionnel !`;
    } else {
      timeEl.textContent = `${timeMs}ms`;
    }
  }

  clear() {
    if (this.outputEl) {
      this.outputEl.textContent = "—";
    }
  }
}
```

---

### Phase 5 - Intégration et Point d'Entrée (2h)

#### Étape 5.1 : Point d'entrée principal
**Fichier**: `app/frontend/main.js`
```javascript
// main.js
import { courseManager } from './services/courseManager.js';
import { exerciseManager } from './services/exerciseManager.js';
import { progressTracker } from './services/progressTracker.js';
import { themeManager } from './services/themeManager.js';
import { CourseList } from './ui/courseList.js';
import { ExerciseList } from './ui/exerciseList.js';
import { CodeEditor } from './ui/codeEditor.js';
import { OutputConsole } from './ui/outputConsole.js';
import { translator } from './i18n/translator.js';
import { logger } from './utils/logger.js';

// État de l'application
let isInitialized = false;

// Composants UI
let courseListUI;
let exerciseListUI;
let codeEditor;
let outputConsole;

// Initialisation de l'application
async function initApp() {
  if (isInitialized) {
    logger.log("⏭️ Application déjà initialisée");
    return;
  }

  isInitialized = true;
  logger.log("🚀 Initialisation de l'application...");

  try {
    // 1. Charger les traductions
    await translator.loadTranslations();

    // 2. Initialiser les composants UI
    initializeUIComponents();

    // 3. Charger les cours
    const courses = await courseManager.loadCourses();

    // 4. Afficher les cours
    courseListUI.render(courses);

    // 5. Sélectionner le premier cours
    if (courses.length > 0) {
      await selectCourse(courses[0].id);
    }

    logger.log("✅ Application initialisée");
  } catch (error) {
    logger.error("❌ Erreur lors de l'initialisation:", error);
  }
}

function initializeUIComponents() {
  // Initialiser les composants UI
  courseListUI = new CourseList('course-list');
  exerciseListUI = new ExerciseList('ex-list');
  codeEditor = new CodeEditor('editor');
  outputConsole = new OutputConsole('output', 'execution-status', 'success-overlay', 'execution-stats');

  // Connecter les événements
  courseListUI.onCourseSelect = selectCourse;
  exerciseListUI.onExerciseSelect = selectExercise;
  codeEditor.onRun = runCode;
  codeEditor.onGrade = gradeCode;
}

async function selectCourse(courseId) {
  await courseManager.selectCourse(courseId);
  await themeManager.loadTheme(courseId);

  const exercises = await exerciseManager.loadExercises(courseId);
  exerciseListUI.render(exercises, courseId);

  const progress = await progressTracker.loadProgress();
  exerciseListUI.updateCompletion(progress.completed);
}

async function selectExercise(courseId, exerciseId) {
  const exercise = await exerciseManager.selectExercise(courseId, exerciseId);
  codeEditor.loadExercise(exercise);
  outputConsole.clear();
}

async function runCode(code, courseId) {
  const startTime = performance.now();
  outputConsole.showStatus("Lancement du programme...");

  try {
    const result = await exerciseManager.runCode(code, courseId);
    const executionTime = Math.round(performance.now() - startTime);

    if (result.run && !result.run.stderr) {
      outputConsole.displaySuccess(result.run.stdout, executionTime);
    } else {
      outputConsole.displayError(result.run.stderr);
    }
  } catch (error) {
    outputConsole.displayError(error.message);
  }
}

async function gradeCode(code, courseId, exerciseId, learner) {
  try {
    const result = await exerciseManager.gradeCode(code, courseId, exerciseId, learner);

    // Afficher le résultat
    // ... (logique d'affichage)

    // Recharger la progression
    const progress = await progressTracker.loadProgress();
    exerciseListUI.updateCompletion(progress.completed);
  } catch (error) {
    logger.error("❌ Erreur lors de la validation:", error);
  }
}

// Démarrer l'application au chargement du DOM
document.addEventListener('DOMContentLoaded', initApp);
```

---

## ⚙️ Modifications HTML Requises

### Mise à jour de index.html

```html
<!-- Remplacer -->
<script src="/static/app.js?v=2.2.6"></script>

<!-- Par -->
<script type="module" src="/static/main.js?v=3.0.0"></script>
```

---

## 🧪 Plan de Test

### Tests Unitaires

```javascript
// tests/frontend/api/apiClient.test.js
import { apiClient } from '../../../app/frontend/api/apiClient.js';

describe('ApiClient', () => {
  test('should fetch data successfully', async () => {
    const data = await apiClient.get('/api/courses');
    expect(data).toBeDefined();
  });

  test('should cache responses when enabled', async () => {
    const data1 = await apiClient.get('/api/courses', true);
    const data2 = await apiClient.get('/api/courses', true);
    // Vérifier que le deuxième appel utilise le cache
  });
});
```

### Tests d'Intégration

```javascript
// tests/frontend/integration/courseFlow.test.js
describe('Course Selection Flow', () => {
  test('should load and select a course', async () => {
    await courseManager.loadCourses();
    await courseManager.selectCourse('python-basics');
    expect(courseManager.getCurrentCourse()).toBe('python-basics');
  });
});
```

---

## 📊 Métriques de Succès

| Métrique | Avant | Après | Objectif |
|----------|-------|-------|----------|
| Taille fichier principal | 2200 lignes | ~50 lignes | ✅ <100 lignes |
| Nombre de fichiers | 1 | ~20 | ✅ Modulaire |
| Fonctions par fichier | ~50 | ~5-10 | ✅ <15 |
| Duplication de code | ~20% | ~5% | ✅ <10% |
| Console.log en prod | ~50 | 0 | ✅ 0 |
| Maintenabilité | Faible | Élevée | ✅ |
| Performance | Moyenne | Élevée | ✅ |

---

## 🚀 Exécution

### Ordre d'Implémentation

1. **Jour 1** : Phase 1 + Phase 2 (Infrastructure + APIs)
2. **Jour 2** : Phase 3 (Services)
3. **Jour 3** : Phase 4 (UI Components)
4. **Jour 4** : Phase 5 (Intégration + Tests)
5. **Jour 5** : Tests, bugs fixes, optimisations

### Commandes

```bash
# Démarrer le refactoring
git checkout -b refactor/modular-frontend

# Créer la structure
mkdir -p app/frontend/{api,services,ui,i18n,utils,features,config}

# Après chaque phase, tester
docker-compose up --build
# Vérifier dans le navigateur

# Commit réguliers
git add .
git commit -m "refactor: Phase 1 - Infrastructure de base"
```

---

## ⚠️ Points d'Attention

1. **Compatibilité navigateur** : Utiliser des modules ES6 (vérifier support)
2. **Gestion des dépendances** : Pas de bundler initialement (peut être ajouté plus tard)
3. **État partagé** : Utiliser des singletons pour les managers
4. **Retrocompatibilité** : Tester avec les anciens endpoints legacy
5. **Performance** : Monitoring du temps de chargement initial

---

## 🔄 Migration Progressive

### Option 1 : Big Bang (Recommandé pour ce cas)
- Tout refactorer d'un coup
- Plus rapide mais risqué
- Nécessite tests exhaustifs

### Option 2 : Incrémentale
- Migrer module par module
- Garder app.js comme fallback
- Plus long mais moins risqué

**Choix recommandé** : Big Bang car le projet est petit et bien testé

---

## 📝 Checklist de Validation

### Avant le Merge

- [ ] Tous les modules créés et testés
- [ ] Aucune duplication de code
- [ ] Pas de console.log en production
- [ ] Tests unitaires passent (>80% coverage)
- [ ] Tests d'intégration passent
- [ ] Performance comparable ou meilleure
- [ ] Pas de régression fonctionnelle
- [ ] Code review effectuée
- [ ] Documentation à jour
- [ ] Build process testé

---

**Date de début prévue** : À définir
**Durée estimée** : 4-5 jours (1 développeur)
**Statut** : 📋 Planifié

---

**Dernière mise à jour** : 2026-01-05
