let current = null, starter = "";
let currentCourseId = null;
let currentLanguage = "fr"; // Langue par défaut
let translations = {}; // Stockage des traductions

// Système de localisation i18n
async function loadTranslations() {
  try {
    const response = await fetch('/static/i18n.json');
    translations = await response.json();
    console.log("🌍 Traductions chargées:", Object.keys(translations));
  } catch (error) {
    console.error("❌ Erreur lors du chargement des traductions:", error);
    // Fallback : traductions minimales
    translations = {
      fr: { title: "Capitaine Python", subtitle: "Entraîneur de Héros" },
      en: { title: "Captain Python", subtitle: "Hero Trainer" }
    };
  }
}

// Fonction pour obtenir le texte traduit
function t(key, params = {}) {
  // Si les traductions ne sont pas encore chargées, retourner la clé
  if (Object.keys(translations).length === 0) {
    return key;
  }

  const keys = key.split('.');
  let value = translations[currentLanguage];

  for (const k of keys) {
    value = value?.[k];
  }

  if (!value) {
    // Fallback vers le français si disponible
    value = translations.fr;
    for (const k of keys) {
      value = value?.[k];
    }
  }

  if (!value) {
    // Si la clé n'existe pas, essayer de deviner un message approprié
    if (key.includes('success')) {
      return currentLanguage === 'en' ? '🎉 Success!' :
             currentLanguage === 'es' ? '🎉 ¡Éxito!' :
             currentLanguage === 'de' ? '🎉 Erfolg!' : '🎉 Réussi !';
    }
    if (key.includes('try_again')) {
      return currentLanguage === 'en' ? 'Try again!' :
             currentLanguage === 'es' ? '¡Intenta de nuevo!' :
             currentLanguage === 'de' ? 'Versuche es erneut!' : 'Essaie encore !';
    }
    if (key.includes('choose_exercise')) {
      return currentLanguage === 'en' ? 'Choose an exercise first!' :
             currentLanguage === 'es' ? '¡Elige un ejercicio primero!' :
             currentLanguage === 'de' ? 'Wähle zuerst eine Übung!' : 'Choisis un exercice d\'abord !';
    }
    // Fallback générique pour les messages d'erreur
    if (key.includes('hint') || key.includes('error')) {
      return currentLanguage === 'en' ? 'Try again or check the hints!' :
             currentLanguage === 'es' ? '¡Intenta de nuevo o revisa las pistas!' :
             currentLanguage === 'de' ? 'Versuche es erneut oder überprüfe die Hinweise!' : 'Essaie encore ou vérifie les indices !';
    }

    // Fallback final : retourner la clé mais nettoyée
    return key;
  }

  // Remplacer les paramètres dans le texte
  return Object.keys(params).reduce((str, param) => {
    return str.replace(`{${param}}`, params[param]);
  }, value);
}

// Fonction pour détecter la langue du navigateur
function detectLanguage() {
  const browserLang = navigator.language || navigator.userLanguage;
  const langCode = browserLang.split('-')[0]; // Extraire le code de langue principal

  // Liste des langues supportées
  const supportedLanguages = ['fr', 'en', 'es', 'de'];

  // Vérifier si la langue est supportée
  if (supportedLanguages.includes(langCode)) {
    return langCode;
  }

  // Fallback vers le français
  return "fr";
}

// Fonction pour changer la langue
async function changeLanguage(lang) {
  const supportedLanguages = ['fr', 'en', 'es', 'de'];
  if (!supportedLanguages.includes(lang)) {
    console.warn(`⚠️ Langue non supportée: ${lang}`);
    return;
  }

  currentLanguage = lang;
  localStorage.setItem('preferredLanguage', lang);
  console.log(`🌍 Langue changée pour: ${lang}`);

  // Mettre à jour l'interface (seulement si les traductions sont chargées)
  if (Object.keys(translations).length > 0) {
    updateInterfaceLanguage();
  }

  // Recharger les cours avec la nouvelle langue
  await loadCourses();
}

// Fonction pour mettre à jour l'interface avec la nouvelle langue
function updateInterfaceLanguage() {
  // Mettre à jour les éléments statiques
  updateStaticTexts();

  // Mettre à jour l'exercice courant si existant
  if (current) {
    updateExerciseDisplay();
  }
}

// Fonction pour mettre à jour les textes statiques
function updateStaticTexts() {
  // Header
  const titleElement = document.querySelector('h1 span:nth-child(2)');
  const subtitleElement = document.querySelector('h1 span:nth-child(3)');
  if (titleElement) titleElement.textContent = t('title');
  if (subtitleElement) subtitleElement.textContent = t('subtitle');

  // Sections
  updateElementText('h2 span:nth-child(2)', t('courses.title'));
  updateElementText('#exercises-container h3 span:nth-child(2)', t('courses.exercises'));

  // Exercise section
  updateElementText('#ex-title', t('exercise.select'));
  updateElementText('label[for="editor"]', t('exercise.code_editor'));
  updateElementText('#editor', t('exercise.placeholder'), true);
  updateElementText('#runBtn span:last-child', t('exercise.run'));
  updateElementText('#gradeBtn span:last-child', t('exercise.validate'));
  updateElementText('#solutionBtn span:last-child', t('exercise.solution'));

  // Results section - s'assurer que les éléments existent avant d'y accéder
  const outputElement = ensureOutputElement();
  const hintElement = document.getElementById("hint");

  if (outputElement && outputElement.parentElement) {
    const outputHeader = outputElement.parentElement.previousElementSibling;
    if (outputHeader) outputHeader.textContent = `🖥 ${t('exercise.output')}`;
  }

  if (hintElement && hintElement.parentElement) {
    const hintsHeader = hintElement.parentElement.previousElementSibling;
    if (hintsHeader) hintsHeader.textContent = `🧭 ${t('exercise.hints')}`;
  }

  // Explanation section
  const explanationHeader = document.querySelector('#explanation h3 span:nth-child(2)');
  if (explanationHeader) explanationHeader.textContent = t('exercise.explanations');

  // Progress section - gérer les éléments manquants
  const progressElement = document.getElementById("progress");
  if (progressElement && progressElement.parentElement) {
    const progressHeader = progressElement.parentElement.previousElementSibling;
    if (progressHeader) progressHeader.textContent = `⭐ ${t('exercise.progress')}`;
  }
}

// Fonction utilitaire pour mettre à jour le texte d'un élément
function updateElementText(selector, text, isPlaceholder = false) {
  const element = document.querySelector(selector);
  if (element) {
    if (isPlaceholder) {
      element.placeholder = text;
    } else {
      element.textContent = text;
    }
  }
}

// Fonction utilitaire pour garantir l'existence de l'élément output
function ensureOutputElement() {
  let outputElement = document.getElementById("output");
  if (!outputElement) {
    console.log("⚠️ Élément output manquant, création automatique...");
    const resultsGrid = document.querySelector('.grid.grid-cols-1.md\\:grid-cols-2.gap-4');
    if (resultsGrid) {
      const outputColumn = document.createElement('div');
      outputColumn.className = 'bg-gray-900 rounded-lg p-4 border border-gray-700';
      outputColumn.innerHTML = `
        <h3 class="text-sm font-semibold text-gray-400 mb-2 flex items-center gap-2">
          <span>🖥</span>
          <span>Sortie</span>
        </h3>
        <pre id="output" class="text-xs font-mono text-gray-300 whitespace-pre-wrap min-h-[100px]">—</pre>
      `;

      // Insérer au début de la grille
      resultsGrid.insertBefore(outputColumn, resultsGrid.firstChild);
      outputElement = document.getElementById("output");
      console.log("✅ Élément output créé automatiquement");
    }
  }
  return outputElement;
}

// Fonction pour mettre à jour l'affichage de l'exercice avec la localisation
function updateExerciseDisplay() {
  if (!current) return;

  // Mettre à jour le titre de l'exercice
  const localizedTitle = getLocalizedValue(current.title);
  document.getElementById("ex-title").textContent = "🧩 " + localizedTitle;

  // Mettre à jour le prompt
  const localizedPrompt = getLocalizedValue(current.prompt);
  document.getElementById("ex-prompt").textContent = localizedPrompt;

  // Mettre à jour les étoiles
  document.getElementById("ex-stars").innerHTML =
    Array.from({length: current.stars}, (_, i) =>
      `<span class="text-yellow-400 text-lg">★</span>`
    ).join('');

  // Mettre à jour la leçon si elle existe
  if (current.theory) {
    displayLocalizedLesson(current.theory);
  }
}

// Fonction pour obtenir une valeur localisée
function getLocalizedValue(value) {
  if (typeof value === 'string') return value;
  if (typeof value === 'object' && value[currentLanguage]) return value[currentLanguage];
  if (typeof value === 'object' && value.fr) return value.fr; // Fallback français
  return value; // Valeur par défaut
}

// Configuration des sections de contenu théorique
const THEORY_SECTION_CONFIG = {
  concept: {
    icon: '📚',
    titleClass: 'text-lg font-semibold text-blue-300 mb-3',
    isTitle: true
  },
  details: {
    icon: '📖',
    titleKey: 'theory.details',
    titleClass: 'text-sm font-medium text-gray-300 mb-2',
    containerClass: 'mb-4',
    listClass: 'list-disc list-inside space-y-1 text-sm text-gray-300 ml-4',
    type: 'list'
  },
  examples: {
    icon: '💡',
    titleKey: 'theory.examples',
    titleClass: 'text-sm font-medium text-green-300 mb-2',
    containerClass: 'mb-4',
    itemClass: 'bg-gray-900 p-3 rounded border border-gray-700',
    codeClass: 'text-sm font-mono text-green-400',
    type: 'code'
  },
  best_practices: {
    icon: '⭐',
    titleKey: 'theory.best_practices',
    titleClass: 'text-sm font-medium text-amber-300 mb-2',
    containerClass: 'mb-4',
    listClass: 'list-disc list-inside space-y-1 text-sm text-amber-200 ml-4',
    type: 'list'
  }
};

/**
 * Crée un titre HTML pour une section
 */
function createSectionTitle(text, config) {
  if (!text || !config) return '';

  if (config.isTitle) {
    return `<h4 class="${config.titleClass}">${escapeHtml(text)}</h4>`;
  }

  const titleText = config.titleKey ? t(config.titleKey) : text;
  return `<h5 class="${config.titleClass}">${config.icon} ${titleText} :</h5>`;
}

/**
 * Crée une liste HTML à partir d'un tableau d'éléments
 */
function createListContent(items, config) {
  if (!Array.isArray(items) || items.length === 0 || !config) return '';

  const itemsHtml = items
    .map(item => `<li>${escapeHtml(item)}</li>`)
    .join('');

  return `<ul class="${config.listClass}">${itemsHtml}</ul>`;
}

/**
 * Crée des blocs de code HTML à partir d'un tableau d'exemples
 */
function createCodeBlocks(items, config) {
  if (!Array.isArray(items) || items.length === 0 || !config) return '';

  const blocksHtml = items
    .map(item => `
      <div class="${config.itemClass}">
        <code class="${config.codeClass}">${escapeHtml(item)}</code>
      </div>
    `)
    .join('');

  return `<div class="space-y-2">${blocksHtml}</div>`;
}

/**
 * Crée un conteneur HTML pour une section de contenu
 */
function createSectionContainer(content, config) {
  if (!content || !config || !config.containerClass) return content;

  return `<div class="${config.containerClass}">${content}</div>`;
}

/**
 * Échappe les caractères HTML spéciaux pour éviter les injections
 */
function escapeHtml(text) {
  if (typeof text !== 'string') return '';

  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Génère le contenu HTML pour un type de section spécifique
 */
function generateSectionContent(key, data, config) {
  const value = getLocalizedValue(data);

  if (!value || !config) return '';

  const title = createSectionTitle(
    config.isTitle ? value : (key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')),
    config
  );

  let content = '';
  if (config.type === 'list') {
    content = createListContent(value, config);
  } else if (config.type === 'code') {
    content = createCodeBlocks(value, config);
  }

  const section = title + content;
  return createSectionContainer(section, config);
}

/**
 * Formate et affiche le contenu théorique d'une leçon (version refactorisée)
 * @param {Object} theory - Objet contenant les données théoriques
 * @returns {string} Contenu HTML formaté
 */
function formatTheoryContent(theory) {
  const theoryData = getLocalizedValue(theory);

  if (!theoryData || typeof theoryData !== 'object') {
    console.warn('formatTheoryContent: Invalid theory data provided');
    return '';
  }

  try {
    const sections = [];

    // Générer chaque section dans l'ordre configuré
    for (const [key, config] of Object.entries(THEORY_SECTION_CONFIG)) {
      if (theoryData[key]) {
        const sectionHtml = generateSectionContent(key, theoryData[key], config);
        if (sectionHtml) {
          sections.push(sectionHtml);
        }
      }
    }

    return sections.join('');

  } catch (error) {
    console.error('formatTheoryContent: Error generating content:', error);
    return `<div class="text-red-400">${t('errors.theory_content')}</div>`;
  }
}

// Fonction pour afficher une leçon localisée
function displayLocalizedLesson(theory) {
  const lessonSection = document.getElementById("lesson-section");
  const lessonTitle = document.getElementById("lesson-title");
  const lessonDuration = document.getElementById("lesson-duration");
  const lessonContent = document.getElementById("lesson-content");
  const lessonToggleIcon = document.getElementById("lesson-toggle-icon");

  if (!theory) {
    lessonSection.classList.add("hidden");
    return;
  }

  const theoryData = getLocalizedValue(theory);
  const localizedTitle = theoryData?.concept || "Leçon théorique";
  const localizedContent = formatTheoryContent(theory);
  const localizedDuration = "5 min";

  // Afficher la section de leçon
  lessonSection.classList.remove("hidden");

  // Réinitialiser l'état de la leçon
  lessonContent.style.display = "block";
  lessonToggleIcon.textContent = "▼";
  lessonToggleIcon.style.transform = "rotate(0deg)";

  // Mettre à jour le titre
  lessonTitle.innerHTML = `
    <span>📚</span>
    <span>${localizedTitle}</span>
    <span id="lesson-toggle-icon" class="ml-2 text-sm transition-transform duration-200">▼</span>
  `;

  // Mettre à jour la durée
  if (localizedDuration) {
    lessonDuration.textContent = localizedDuration;
    lessonDuration.style.display = "inline-block";
  } else {
    lessonDuration.style.display = "none";
  }

  // Afficher le contenu formaté
  lessonContent.innerHTML = localizedContent;
}


// Fonction pour recharger les exercices du cours actuel
async function loadExercisesForCurrentCourse() {
  if (!currentCourseId) return;

  try {
    const exercises = await api(`/api/courses/${currentCourseId}/exercises`);
    loadExercises(exercises, currentCourseId);
  } catch (error) {
    console.error("❌ Erreur lors du rechargement des exercices:", error);
  }
}

// Fonction API plus robuste avec gestion d'erreur
async function api(url, options = {}) {
  try {
    console.log(`📡 Appel API: ${url}`);
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    console.log(`📡 Réponse API: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✅ Données reçues de ${url}:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Erreur API pour ${url}:`, error);
    throw error;
  }
}

async function loadCourses(){
  console.log("🚀 Début du chargement des cours...");

  try {
    const courses = await api("/api/courses");

    const courseListEl = document.getElementById("course-list");
    if (!courseListEl) {
      console.error("❌ Élément course-list non trouvé!");
      return;
    }

    if (!courses || courses.length === 0) {
      console.warn("⚠️ Aucun cours trouvé, fallback vers l'ancien système");
      loadLegacyExercises();
      return;
    }

    courseListEl.innerHTML = courses.map(course => {
      const localizedTitle = getLocalizedValue(course.title);
      const localizedDescription = getLocalizedValue(course.description);
      return `
      <div class="course-card bg-gray-700 hover:bg-gray-600 border-2 border-transparent hover:border-blue-500 rounded-lg p-4 cursor-pointer transition-all duration-200 transform hover:scale-105 flex-shrink-0 w-80" data-course-id="${course.id}">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-2">
            ${course.icon ? `<img src="${course.icon}" alt="${localizedTitle}" class="w-6 h-6 rounded" />` : '<span class="text-xl">📚</span>'}
            <h3 class="font-bold text-white">${localizedTitle}</h3>
          </div>
          <span class="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">${course.level}</span>
        </div>

        <p class="text-gray-300 text-sm mb-3 line-clamp-2">${localizedDescription}</p>

        <div class="flex flex-wrap gap-2 text-xs">
          <span class="px-2 py-1 bg-gray-600 text-gray-200 rounded">
            ${course.exercise_count} ${t('courses.exercises')}
          </span>
          <span class="px-2 py-1 bg-amber-600/20 text-amber-300 rounded">
            ${course.total_stars} ⭐
          </span>
          <span class="px-2 py-1 bg-green-600/20 text-green-300 rounded">
            ~${course.estimated_hours}h
          </span>
        </div>
      </div>
    `;
    }).join("");

    console.log("🎨 Interface des cours générée");

    // Ajouter les écouteurs d'événements
    courseListEl.querySelectorAll(".course-card").forEach(card => {
      card.onclick = () => selectCourse(card.dataset.courseId);
    });

    console.log("🖱️ Écouteurs d'événements ajoutés");

    // Sélectionner le premier cours par défaut
    if (courses.length > 0) {
      console.log("🎯 Sélection du premier cours:", courses[0].id);
      selectCourse(courses[0].id);
    }
  } catch (error) {
    console.error("❌ Erreur lors du chargement des cours:", error);
    console.log("🔄 Fallback vers l'ancien système");
    // Fallback vers l'ancien système
    loadLegacyExercises();
  }
}

async function selectCourse(courseId) {
  console.log("🎯 Sélection du cours:", courseId);
  try {
    currentCourseId = courseId;

    // Réinitialiser l'exercice courant pour éviter les conflits
    current = null;
    starter = "";
    console.log("🔄 Exercice courant réinitialisé");

    // Mettre à jour l'interface de sélection
    document.querySelectorAll(".course-card").forEach(card => {
      const isSelected = card.dataset.courseId === courseId;

      if (isSelected) {
        card.classList.remove("border-transparent", "hover:border-blue-500");
        card.classList.add("border-blue-500", "bg-blue-900/30", "shadow-lg", "shadow-blue-500/20");
      } else {
        card.classList.remove("border-blue-500", "bg-blue-900/30", "shadow-lg", "shadow-blue-500/20");
        card.classList.add("border-transparent", "hover:border-blue-500");
      }
    });
    console.log("✅ Interface de sélection mise à jour");

    // Réinitialiser l'interface d'exercice à l'état par défaut
    resetExerciseInterface();

    // Charger le thème du cours
    console.log("🎨 Chargement du thème...");
    await loadCourseTheme(courseId);
    console.log("✅ Thème chargé");

    // Charger les exercices du cours
    console.log("📚 Chargement des exercices...");
    const exercises = await api(`/api/courses/${courseId}/exercises`);
    console.log("✅ Exercices reçus:", exercises);
    loadExercises(exercises, courseId);
    console.log("✅ Exercices chargés");

    // Afficher la section des exercices
    const exercisesContainer = document.getElementById("exercises-container");
    if (exercisesContainer) {
      exercisesContainer.style.display = "block";
      console.log("✅ Section exercices affichée");
    } else {
      console.error("❌ Élément exercises-container non trouvé!");
    }

    // Sélectionner le cours dans le backend
    await api(`/api/courses/${courseId}/select`, {method: "POST"});
    console.log("✅ Cours sélectionné dans le backend");

  } catch (error) {
    console.error("❌ Erreur lors de la sélection du cours:", error);
  }
}

// Fonction pour réinitialiser l'interface d'exercice à l'état par défaut
function resetExerciseInterface() {
  console.log("🔄 Réinitialisation de l'interface d'exercice");

  // S'assurer que l'éditeur et les boutons sont visibles
  const editor = document.getElementById("editor");
  const runBtn = document.getElementById("runBtn");
  const gradeBtn = document.getElementById("gradeBtn");
  const solutionBtn = document.getElementById("solutionBtn");

  if (editor) editor.style.display = "block";
  if (runBtn) runBtn.style.display = "inline-flex";
  if (gradeBtn) gradeBtn.style.display = "inline-flex";
  if (solutionBtn) solutionBtn.style.display = "inline-flex";

  // Réinitialiser le contenu
  const exTitle = document.getElementById("ex-title");
  const exStars = document.getElementById("ex-stars");
  const exPrompt = document.getElementById("ex-prompt");
  const output = document.getElementById("output");
  const hint = document.getElementById("hint");

  if (exTitle) exTitle.textContent = t('exercise.select');
  if (exStars) exStars.innerHTML = "";
  if (exPrompt) exPrompt.textContent = "";
  if (editor) editor.value = "";
  if (output) output.textContent = "—";
  if (hint) hint.textContent = "—";

  // Cacher les explications
  const explanation = document.getElementById("explanation");
  const explanationContent = document.getElementById("explanation-content");

  if (explanation) explanation.classList.add("hidden");
  if (explanationContent) explanationContent.textContent = "—";

  // Cacher la zone de solution
  const solutionDisplay = document.getElementById("solution-display");
  if (solutionDisplay) solutionDisplay.classList.add("hidden");

  // S'assurer que l'éditeur est visible
  const editorContainer = editor.closest('.mb-6');
  if (editorContainer) editorContainer.classList.remove("hidden");

  // Réinitialiser le bouton solution
  if (solutionBtn) {
    solutionBtn.innerHTML = `
      <span>🎯</span>
      <span>Solution</span>
    `;
    solutionBtn.classList.remove("bg-blue-600", "hover:bg-blue-700");
    solutionBtn.classList.add("bg-purple-600", "hover:bg-purple-700");
  }

  // Réinitialiser l'état de la solution
  isShowingSolution = false;

  // Cacher la section leçon
  const lessonSection = document.getElementById("lesson-section");
  if (lessonSection) {
    lessonSection.classList.add("hidden");
  }

  // Réinitialiser la progression
  const progress = document.getElementById("progress");
  if (progress) {
    progress.textContent = "—";
  }

  console.log("✅ Interface d'exercice réinitialisée");
}

async function loadCourseTheme(courseId) {
  try {
    const theme = await api(`/api/courses/${courseId}/theme`);
    applyTheme(theme);
  } catch (error) {
    console.error("Erreur lors du chargement du thème:", error);
    // Utiliser le thème par défaut
    applyTheme(getDefaultTheme());
  }
}

function applyTheme(theme) {
  // Appliquer le thème personnalisé avec Tailwind
  const root = document.documentElement;

  // Créer des variables CSS personnalisées
  root.style.setProperty('--theme-primary', theme.primary_color || "#3b82f6");
  root.style.setProperty('--theme-secondary', theme.secondary_color || "#10b981");
  root.style.setProperty('--theme-accent', theme.accent_color || "#f59e0b");
  root.style.setProperty('--theme-surface', theme.surface_color || "#1f2937");
  root.style.setProperty('--theme-background', theme.background_color || "#111827");
  root.style.setProperty('--theme-text', theme.text_color || "#f3f4f6");

  // Appliquer le style au body
  const body = document.body;

  // Gérer l'image de fond si disponible
  if (theme.background_image) {
    body.style.background = `linear-gradient(135deg, rgba(0,0,0,0.4), rgba(0,0,0,0.6)), url('${theme.background_image}')`;
    body.style.backgroundSize = 'cover';
    body.style.backgroundPosition = 'center';
    body.style.backgroundAttachment = 'fixed';
  } else {
    body.style.background = `linear-gradient(135deg, ${theme.gradient_start || "#111827"}, ${theme.gradient_end || "#1f2937"})`;
  }

  body.style.fontFamily = theme.font_family || "system-ui, -apple-system, sans-serif";

  // Styles dynamiques personnalisés
  const customStyles = `
    :root {
      --theme-primary: ${theme.primary_color || "#3b82f6"};
      --theme-secondary: ${theme.secondary_color || "#10b981"};
      --theme-accent: ${theme.accent_color || "#f59e0b"};
      --theme-surface: ${theme.surface_color || "#1f2937"};
      --theme-background: ${theme.background_color || "#111827"};
      --theme-text: ${theme.text_color || "#f3f4f6"};
    }

    .theme-primary { color: var(--theme-primary) !important; }
    .theme-secondary { color: var(--theme-secondary) !important; }
    .theme-accent { color: var(--theme-accent) !important; }

    .bg-theme-primary { background-color: var(--theme-primary) !important; }
    .bg-theme-secondary { background-color: var(--theme-secondary) !important; }
    .bg-theme-accent { background-color: var(--theme-accent) !important; }
    .bg-theme-surface { background-color: var(--theme-surface) !important; }

    .border-theme-primary { border-color: var(--theme-primary) !important; }
    .border-theme-secondary { border-color: var(--theme-secondary) !important; }

    /* Personnalisation des boutons principaux */
    #runBtn {
      background: var(--theme-primary) !important;
    }
    #runBtn:hover {
      background: var(--theme-primary) !important;
      filter: brightness(0.9);
    }

    /* Personnalisation du bouton succès */
    #gradeBtn {
      background: var(--theme-accent) !important;
    }
    #gradeBtn:hover {
      background: var(--theme-accent) !important;
      filter: brightness(0.9);
    }

    /* Personnalisation du bouton solution */
    #solutionBtn {
      background: var(--theme-secondary) !important;
    }
    #solutionBtn:hover {
      background: var(--theme-secondary) !important;
      filter: brightness(0.9);
    }

    /* Animations personnalisées */
    .course-card {
      transition: all 0.3s ease;
    }

    .course-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
    }
  `;

  document.getElementById("theme-styles").textContent = customStyles;
}

function getDefaultTheme() {
  return {
    font_family: "system-ui, Arial",
    background_color: "#0b1220",
    text_color: "#ffffff",
    gradient_start: "#0b1220",
    gradient_end: "#13213d",
    surface_color: "#111b33",
    primary_color: "#4da3ff",
    secondary_color: "#9ecbff",
    accent_color: "#29c36a"
  };
}

// Fonction pour afficher la leçon d'un exercice
function displayLesson(lesson) {
  const lessonSection = document.getElementById("lesson-section");
  const lessonTitle = document.getElementById("lesson-title");
  const lessonDuration = document.getElementById("lesson-duration");
  const lessonContent = document.getElementById("lesson-content");
  const lessonToggleIcon = document.getElementById("lesson-toggle-icon");

  if (!lesson || !lesson.title || !lesson.content) {
    // Cacher la section si pas de leçon
    lessonSection.classList.add("hidden");
    return;
  }

  // Afficher la section de leçon
  lessonSection.classList.remove("hidden");

  // Réinitialiser l'état de la leçon (développée par défaut)
  lessonContent.style.display = "block";
  lessonToggleIcon.textContent = "▼";
  lessonToggleIcon.style.transform = "rotate(0deg)";

  // Mettre à jour le titre
  lessonTitle.innerHTML = `
    <span>📚</span>
    <span>${lesson.title}</span>
    <span id="lesson-toggle-icon" class="ml-2 text-sm transition-transform duration-200">▼</span>
  `;

  // Mettre à jour la durée si elle existe
  if (lesson.duration) {
    lessonDuration.textContent = lesson.duration;
    lessonDuration.style.display = "inline-block";
  } else {
    lessonDuration.style.display = "none";
  }

  // Formater le contenu avec Markdown-like parsing
  let formattedContent = lesson.content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // Gras
    .replace(/\*(.*?)\*/g, '<em>$1</em>')      // Italique
    .replace(/```python\n([\s\S]*?)```/g, '<pre class="bg-gray-800 p-3 rounded-lg overflow-x-auto text-xs"><code>$1</code></pre>')  // Blocs de code Python
    .replace(/`([^`]+)`/g, '<code class="bg-gray-800 px-1 py-0.5 rounded text-xs">$1</code>')  // Code inline
    .replace(/^### (.*$)/gim, '<h4 class="text-base font-semibold text-blue-300 mt-4 mb-2">$1</h4>')  // Sous-titres
    .replace(/^## (.*$)/gim, '<h3 class="text-lg font-semibold text-blue-200 mt-4 mb-3">$1</h3>')  // Titres
    .replace(/^# (.*$)/gim, '<h2 class="text-xl font-bold text-blue-100 mt-4 mb-4">$1</h2>')   // Gros titres
    .replace(/^\*\s(.*)$/gim, '<li class="ml-4">$1</li>')  // Listes
    .replace(/^-\s(.*)$/gim, '<li class="ml-8 text-gray-400">$1</li>')  // Sous-listes
    .replace(/(<li>.*<\/li>)/gs, '<ul class="list-disc list-inside space-y-1 my-2">$1</ul>')  // Entourer les listes
    .replace(/\n\n/g, '</p><p class="mb-3">')  // Paragraphes
    .replace(/^(?!<[hul<>])/gm, '<p>')  // Premier paragraphe
    .replace(/<p>$/, '</p>');  // Dernier paragraphe

  lessonContent.innerHTML = formattedContent;
}

function loadExercises(exercises, courseId) {
  const el = document.getElementById("ex-list");
  el.innerHTML = exercises.map(x => {
    const localizedTitle = getLocalizedValue(x.title);
    return `
    <div class="mb-2">
      <a href="#" data-course-id="${courseId}" data-id="${x.id}"
         class="block px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors duration-200 group">
        <div class="flex items-center justify-between">
          <span class="text-white font-medium group-hover:text-blue-300 transition-colors">
            🧩 ${localizedTitle}
          </span>
          <span class="text-yellow-400">
            ${"★".repeat(x.stars)}
          </span>
        </div>
      </a>
    </div>
  `;
  }).join("");

  el.querySelectorAll("a").forEach(a => a.onclick = async (e) => {
    e.preventDefault();
    const ex = await api(`/api/courses/${a.dataset.courseId}/exercises/${a.dataset.id}`);
    current = ex;
    starter = ex.starter || "";

    // S'assurer que l'éditeur et les boutons sont visibles
    document.getElementById("editor").style.display = "block";
    document.getElementById("runBtn").style.display = "inline-flex";
    document.getElementById("gradeBtn").style.display = "inline-flex";
    document.getElementById("solutionBtn").style.display = "inline-flex";

    // Mettre à jour l'interface de l'exercice avec localisation
    const localizedTitle = getLocalizedValue(ex.title);
    const localizedPrompt = getLocalizedValue(ex.prompt);

    document.getElementById("ex-title").textContent = "🧩 " + localizedTitle;
    document.getElementById("ex-stars").innerHTML =
      Array.from({length: ex.stars}, (_, i) =>
        `<span class="text-yellow-400 text-lg">★</span>`
      ).join('');

    document.getElementById("ex-prompt").textContent = localizedPrompt;

    // Afficher la leçon si elle existe (avec localisation)
    if (ex.theory) {
      displayLocalizedLesson(ex.theory);
    } else if (ex.lesson) {
      displayLesson(ex.lesson); // Fallback pour l'ancien système
    }

    // Commencer avec un éditeur vide
    document.getElementById("editor").value = "";
    document.getElementById("output").textContent = "—";
    document.getElementById("hint").textContent = "—";

    // Cacher les explications
    document.getElementById("explanation").classList.add("hidden");
    document.getElementById("explanation-content").textContent = "—";

    // S'assurer que l'éditeur est visible et le bouton solution est dans le bon état
    const editorContainer = document.getElementById("editor").closest('.mb-6');
    const solutionDisplay = document.getElementById("solution-display");
    const solutionBtn = document.getElementById("solutionBtn");

    if (editorContainer) editorContainer.classList.remove("hidden");
    if (solutionDisplay) solutionDisplay.classList.add("hidden");
    if (solutionBtn) {
      solutionBtn.innerHTML = `
        <span>🎯</span>
        <span>Solution</span>
      `;
      solutionBtn.classList.remove("bg-blue-600", "hover:bg-blue-700");
      solutionBtn.classList.add("bg-purple-600", "hover:bg-purple-700");
    }

    // Réinitialiser l'état
    isShowingSolution = false;

    // Vérifier si l'exercice contient des inputs et mettre à jour l'interface
    if (ex.starter && hasInputFunction(ex.starter)) {
      console.log("🔍 Exercice avec inputs détecté:", ex.id);
      // Pré-remplir l'éditeur avec le starter code pour activer la détection
      document.getElementById("editor").value = ex.starter;
      updateInteractiveInputsUI(ex.starter);
    } else {
      updateInteractiveInputsUI("");
    }

    // Mettre à jour la sélection visuelle
    updateSelectedExerciseInList(ex.id);
  });

  // Charger la progression actuelle pour mettre à jour l'état des exercices
  loadCurrentProgress();

  // Charger automatiquement le premier exercice non terminé
  loadFirstIncompleteExercise(courseId, exercises);
}

async function loadLegacyExercises() {
  // Fallback pour l'ancien système
  const xs = await api("/api/exercises");
  const el = document.getElementById("ex-list");
  el.innerHTML = xs.map(x => {
    const localizedTitle = getLocalizedValue(x.title);
    return `<div><a href="#" data-course-id="python-basics" data-id="${x.id}">🧩 ${localizedTitle} — ${"★".repeat(x.stars)}</a></div>`;
  }).join("");

  el.querySelectorAll("a").forEach(a=>a.onclick = async (e)=>{
    const ex = await api("/api/exercises/"+a.dataset.id);
    current = ex; starter = ex.starter || "";

    // Utiliser la localisation même pour le système legacy
    const localizedTitle = getLocalizedValue(ex.title);
    const localizedPrompt = getLocalizedValue(ex.prompt);

    document.getElementById("ex-title").textContent = "🧩 " + localizedTitle;
    document.getElementById("ex-stars").textContent = "★".repeat(ex.stars);
    document.getElementById("ex-prompt").textContent = localizedPrompt;
    document.getElementById("editor").value = "";
    document.getElementById("output").textContent = "—";
    document.getElementById("hint").textContent = "—";
    document.getElementById("explanation").style.display = "none";
    document.getElementById("explanation").textContent = "—";
  });

  // Charger la progression actuelle pour mettre à jour l'état des exercices
  loadCurrentProgress();
}

// Fonction pour charger la progression actuelle et mettre à jour l'affichage
window.loadCurrentProgress = async function() {
  try {
    const progress = await api("/api/progress?learner=Hugo");
    if (progress) {
      displayProgress(progress);
    }
  } catch (error) {
    console.log("Impossible de charger la progression:", error);
  }
};

// Fonction pour trouver le premier exercice non terminé dans un cours
async function findFirstIncompleteExercise(courseId, exercises) {
  try {
    // Charger la progression de l'utilisateur
    const progress = await api("/api/progress?learner=Hugo");
    if (!progress || !progress.completed) {
      // Si aucune progression, retourner le premier exercice
      return exercises.length > 0 ? exercises[0] : null;
    }

    const completedExercises = progress.completed;

    // Chercher le premier exercice non complété
    for (const exercise of exercises) {
      const fullExerciseId = `${courseId}_${exercise.id}`;
      if (!completedExercises.includes(fullExerciseId)) {
        console.log(`🎯 Premier exercice non terminé trouvé: ${exercise.id}`);
        return exercise;
      }
    }

    // Si tous les exercices sont complétés, retourner null
    console.log("🏆 Tous les exercices de ce cours sont terminés !");
    return null;

  } catch (error) {
    console.error("❌ Erreur lors de la recherche du premier exercice non terminé:", error);
    // En cas d'erreur, retourner le premier exercice
    return exercises.length > 0 ? exercises[0] : null;
  }
}

// Fonction pour charger automatiquement le premier exercice non terminé
async function loadFirstIncompleteExercise(courseId, exercises) {
  if (!exercises || exercises.length === 0) return;

  const firstIncomplete = await findFirstIncompleteExercise(courseId, exercises);

  if (firstIncomplete) {
    console.log(`🎯 Chargement automatique du premier exercice non terminé: ${firstIncomplete.id}`);

    // Charger l'exercice
    try {
      const ex = await api(`/api/courses/${courseId}/exercises/${firstIncomplete.id}`);
      current = ex;
      starter = ex.starter || "";

      // Mettre à jour l'interface de l'exercice avec localisation
      const localizedTitle = getLocalizedValue(ex.title);
      const localizedPrompt = getLocalizedValue(ex.prompt);

      const exTitle = document.getElementById("ex-title");
      const exStars = document.getElementById("ex-stars");
      const exPrompt = document.getElementById("ex-prompt");
      const editor = document.getElementById("editor");
      const output = document.getElementById("output");
      const hint = document.getElementById("hint");
      const explanation = document.getElementById("explanation");
      const explanationContent = document.getElementById("explanation-content");

      if (exTitle) exTitle.textContent = "🧩 " + localizedTitle;
      if (exStars) {
        exStars.innerHTML =
          Array.from({length: ex.stars}, (_, i) =>
            `<span class="text-yellow-400 text-lg">★</span>`
          ).join('');
      }
      if (exPrompt) exPrompt.textContent = localizedPrompt;

      // Afficher la leçon si elle existe (avec localisation)
      if (ex.theory) {
        displayLocalizedLesson(ex.theory);
      } else if (ex.lesson) {
        displayLesson(ex.lesson); // Fallback pour l'ancien système
      }

      // Commencer avec un éditeur vide
      if (editor) editor.value = "";
      if (output) output.textContent = "—";
      if (hint) hint.textContent = "—";

      // Cacher les explications
      if (explanation) explanation.classList.add("hidden");
      if (explanationContent) explanationContent.textContent = "—";

      // Mettre en évidence l'exercice sélectionné dans la liste
      updateSelectedExerciseInList(firstIncomplete.id);

    } catch (error) {
      console.error("❌ Erreur lors du chargement de l'exercice:", error);
    }
  } else {
    console.log("🏆 Tous les exercices sont terminés !");
    // Afficher un message de félicitations
    showCongratulationsMessage();
  }
}

// Fonction pour mettre en évidence l'exercice sélectionné dans la liste
function updateSelectedExerciseInList(selectedExerciseId) {
  const exerciseLinks = document.querySelectorAll("#ex-list a");

  exerciseLinks.forEach(link => {
    const exerciseId = link.dataset.id;
    const isSelected = exerciseId === selectedExerciseId;

    // Réinitialiser les classes de base
    link.classList.remove("bg-blue-700", "border-blue-500", "shadow-lg", "shadow-blue-500/20", "opacity-75", "line-through", "bg-green-900/30", "border-green-600/20");

    // Vérifier si l'exercice est complété
    const courseId = link.dataset.courseId;
    const fullExerciseId = `${courseId}_${exerciseId}`;
    const isCompleted = link.classList.contains("completed-exercise");

    if (isCompleted) {
      // Maintenir les classes de complétion
      link.classList.add("opacity-75", "line-through", "bg-green-900/30", "border-green-600/20");
    } else {
      // Classes par défaut pour les exercices non complétés
      link.classList.add("bg-gray-700", "hover:bg-gray-600");
    }

    if (isSelected) {
      // Ajouter les classes de sélection
      link.classList.add("bg-blue-700", "border-blue-500", "shadow-lg", "shadow-blue-500/20");
      link.classList.remove("bg-gray-700", "hover:bg-gray-600");
    }
  });
}

// Fonction pour afficher un message de félicitations
function showCongratulationsMessage() {
  const exerciseTitle = document.getElementById("ex-title");
  const exercisePrompt = document.getElementById("ex-prompt");
  const exerciseStars = document.getElementById("ex-stars");

  exerciseTitle.innerHTML = "🏆 " + t('messages.congratulations_title');
  exercisePrompt.textContent = t('messages.congratulations_message');
  exerciseStars.innerHTML = '<span class="text-yellow-400 text-2xl">🏆🎉⭐</span>';

  // Cacher l'éditeur et les boutons
  document.getElementById("editor").style.display = "none";
  document.getElementById("runBtn").style.display = "none";
  document.getElementById("gradeBtn").style.display = "none";
  document.getElementById("solutionBtn").style.display = "none";

  // Afficher un message encourageant
  const output = document.getElementById("output");
  output.innerHTML = `
    <div class="text-center text-green-300 text-lg font-bold mb-4">
      🎊 ${t('messages.course_completed')} 🎊
    </div>
    <div class="text-center text-blue-300">
      ${t('messages.ready_next_challenge')}
    </div>
  `;

  // Cacher la section leçon
  const lessonSection = document.getElementById("lesson-section");
  if (lessonSection) {
    lessonSection.classList.add("hidden");
  }
}

document.getElementById("runBtn").onclick = async ()=>{
  const code = document.getElementById("editor").value;

  // Vérifier si le code contient des inputs
  if (hasInputFunction(code)) {
    showNotification("Ce code contient des inputs(). Utilisez la section 'Inputs interactifs' ci-dessous.", "warning");
    return;
  }

  // Afficher le statut d'exécution
  const statusEl = document.getElementById("execution-status");
  const outputEl = document.getElementById("output");
  const successOverlay = document.getElementById("success-overlay");
  const statsEl = document.getElementById("execution-stats");

  // Réinitialiser les éléments
  statusEl.classList.remove("hidden");
  successOverlay.classList.add("hidden");
  statsEl.classList.add("hidden");
  outputEl.textContent = "⏳ Lancement de ton programme...";

  // Mesurer le temps d'exécution
  const startTime = performance.now();

  try {
    const out = await api("/api/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code})});

    const endTime = performance.now();
    const executionTime = Math.round(endTime - startTime);

    // Masquer le statut
    statusEl.classList.add("hidden");

    // Afficher le résultat avec mise en forme
    const result = (out.run && out.run.stdout) || (out.run && out.run.stderr) || "";

    if (result && !out.run.stderr) {
      // Succès : afficher le résultat et l'animation
      outputEl.textContent = result;

      // Afficher l'overlay de succès après un court délai
      setTimeout(() => {
        successOverlay.classList.remove("hidden");
        showExecutionStats(executionTime, true);

        // Masquer l'overlay après 2 secondes
        setTimeout(() => {
          successOverlay.classList.add("hidden");
        }, 2000);
      }, 300);

      // Ajouter une classe de succès à la console
      outputEl.parentElement.classList.add("border-green-500/50", "bg-green-950/10");
      setTimeout(() => {
        outputEl.parentElement.classList.remove("border-green-500/50", "bg-green-950/10");
      }, 3000);

    } else {
      // Erreur : afficher en rouge avec aide
      const errorMsg = out.run?.stderr || "Une erreur est survenue";
      outputEl.innerHTML = `<span class="text-red-400">❌ Erreur :</span>\n${errorMsg}`;

      // Afficher les stats d'erreur
      showExecutionStats(executionTime, false);

      // Ajouter une classe d'erreur
      outputEl.parentElement.classList.add("border-red-500/50", "bg-red-950/10");
      setTimeout(() => {
        outputEl.parentElement.classList.remove("border-red-500/50", "bg-red-950/10");
      }, 3000);
    }

  } catch (error) {
    const endTime = performance.now();
    const executionTime = Math.round(endTime - startTime);

    statusEl.classList.add("hidden");
    outputEl.innerHTML = `<span class="text-orange-400">⚠️ Problème de connexion :</span>\n${error.message}`;
    showExecutionStats(executionTime, false);

    outputEl.parentElement.classList.add("border-orange-500/50", "bg-orange-950/10");
    setTimeout(() => {
      outputEl.parentElement.classList.remove("border-orange-500/50", "bg-orange-950/10");
    }, 3000);
  }
};

// Fonction pour afficher les statistiques d'exécution
function showExecutionStats(timeMs, success) {
  const statsEl = document.getElementById("execution-stats");
  const timeEl = document.getElementById("execution-time");
  const barEl = document.getElementById("performance-bar");

  statsEl.classList.remove("hidden");
  timeEl.textContent = `${timeMs}ms`;

  // Calculer la performance (basé sur le temps)
  let performance = 100;
  if (timeMs > 1000) performance = 20;
  else if (timeMs > 500) performance = 40;
  else if (timeMs > 200) performance = 60;
  else if (timeMs > 100) performance = 80;

  // Couleur selon succès et performance
  let colorClass = "bg-green-500";
  if (!success) {
    colorClass = "bg-red-500";
    performance = 30; // Performance faible en cas d'erreur
  } else if (performance < 50) {
    colorClass = "bg-yellow-500";
  } else if (performance < 80) {
    colorClass = "bg-blue-500";
  }

  barEl.className = `${colorClass} h-1 rounded-full transition-all duration-500`;
  barEl.style.width = `${performance}%`;

  // Message de motivation
  if (success) {
    if (timeMs < 50) {
      timeEl.textContent = `${timeMs}ms ⚡ Ultra rapide !`;
    } else if (timeMs < 100) {
      timeEl.textContent = `${timeMs}ms 🚀 Très performant !`;
    } else if (timeMs < 200) {
      timeEl.textContent = `${timeMs}ms 👍 Bonne performance !`;
    } else {
      timeEl.textContent = `${timeMs}ms 💪 Code fonctionnel !`;
    }
  }
}

document.getElementById("gradeBtn").onclick = async ()=>{
  if(!current) return alert(t('messages.choose_exercise'));
  const code = document.getElementById("editor").value;
  const res = await api("/api/grade",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
    course_id: currentCourseId || "python-basics",
    exercise_id: current.id,
    code
  })});
  const ok = res.result && res.result.ok;
  document.getElementById("hint").textContent = ok ? t('messages.success') : (res.result.hint || t('messages.try_again'));
  displayProgress(res.progress);
};

// Fonction pour afficher la progression de manière visuelle et compacte
function displayProgress(progress) {
  const progressEl = document.getElementById("progress");
  if (!progressEl) return;

  const completedExercises = progress.completed || [];
  const totalStars = progress.stars || 0;

  // Créer une progression visuelle compacte
  let progressHTML = `
    <div class="progress-container text-xs">
      ${completedExercises.length > 0 ? `
        <div class="flex items-center justify-between mb-2">
          <span class="text-green-300 font-medium">🏆 ${totalStars}⭐</span>
          <span class="text-blue-300">${completedExercises.length}/${completedExercises.length}</span>
        </div>
        <div class="flex flex-wrap gap-1">
          ${completedExercises.map(exId => {
            const parts = exId.split('_');
            const exerciseId = parts.slice(1).join('-');
            return `<span class="px-1 py-0.5 bg-green-600/15 text-green-300 rounded text-xs border border-green-600/20">
              ✅ ${exerciseId}
            </span>`;
          }).join('')}
        </div>
      ` : `
        <div class="text-center text-gray-400">
          <span class="text-sm">🎯 Commence ton aventure !</span>
        </div>
      `}
    </div>
  `;

  progressEl.innerHTML = progressHTML;

  // Mettre à jour l'état des exercices dans la liste (barré + ✅)
  updateExerciseListCompletion(completedExercises);
}

// Fonction pour marquer les exercices complétés dans la liste
window.updateExerciseListCompletion = function(completedExercises) {
  const exerciseLinks = document.querySelectorAll("#ex-list a");

  exerciseLinks.forEach(link => {
    const courseId = link.dataset.courseId;
    const exerciseId = link.dataset.id;
    const fullExerciseId = `${courseId}_${exerciseId}`;

    const isCompleted = completedExercises.includes(fullExerciseId);

    // Marquer l'exercice comme complété/non complété avec une classe
    if (isCompleted) {
      link.classList.add("completed-exercise");
    } else {
      link.classList.remove("completed-exercise");
    }

    // Appliquer le style approprié
    if (isCompleted) {
      // Ajouter les classes de complétion
      link.classList.add("opacity-75", "line-through", "bg-green-900/30", "border-green-600/20");
      link.classList.remove("bg-gray-700", "hover:bg-gray-600");

      // Ajouter une coche verte devant le titre
      const titleSpan = link.querySelector("span:first-child");
      if (titleSpan && !titleSpan.textContent.includes("✅ ")) {
        titleSpan.textContent = "✅ " + titleSpan.textContent.replace("🧩 ", "");
        titleSpan.classList.add("text-green-300");
      }

      // Changer la couleur des étoiles
      const starsSpan = link.querySelector("span:last-child");
      if (starsSpan) {
        starsSpan.classList.add("text-green-400");
        starsSpan.classList.remove("text-yellow-400");
      }
    } else {
      // Retirer les classes de complétion si elles existent
      link.classList.remove("opacity-75", "line-through", "bg-green-900/30", "border-green-600/20");
      link.classList.add("bg-gray-700", "hover:bg-gray-600");

      // Retirer la coche si elle existe
      const titleSpan = link.querySelector("span:first-child");
      if (titleSpan && titleSpan.textContent.includes("✅ ")) {
        titleSpan.textContent = "🧩 " + titleSpan.textContent.replace("✅ ", "");
        titleSpan.classList.remove("text-green-300");
      }

      // Restaurer la couleur des étoiles
      const starsSpan = link.querySelector("span:last-child");
      if (starsSpan) {
        starsSpan.classList.remove("text-green-400");
        starsSpan.classList.add("text-yellow-400");
      }
    }
  });
}

// Gestionnaire pour le bouton d'indice
document.getElementById("hintBtn").onclick = ()=>{
  if(!current) {
    showNotification("Choisis un exercice d'abord !", "warning");
    return;
  }

  const hintSection = document.getElementById("hint-section");
  const hintContent = document.getElementById("hint-content");

  // Récupérer les indices localisés
  const hints = getLocalizedValue(current.hints) || [];
  if (hints.length === 0) {
    showNotification("Pas d'indices disponibles pour cet exercice", "info");
    return;
  }

  // Afficher le premier indice disponible
  const hintText = typeof hints[0] === 'string' ? hints[0] : "Pas d'indice disponible";

  // Afficher l'indice
  hintContent.textContent = hintText;
  hintSection.classList.remove("hidden");
  hintSection.classList.add("animate-slide-up");

  // Faire défiler jusqu'à l'indice
  setTimeout(() => {
    hintSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 100);

  showNotification("Indice affiché 💡", "success");
};

// Gestionnaire pour fermer l'indice
document.getElementById("close-hint").onclick = ()=>{
  const hintSection = document.getElementById("hint-section");
  hintSection.classList.add("hidden");
};

// Gestionnaire pour le bouton solution avec toggle
let isShowingSolution = false;

document.getElementById("solutionBtn").onclick = ()=>{
  if(!current) {
    showNotification("Choisis un exercice d'abord !", "warning");
    return;
  }

  if (isShowingSolution) {
    // Retourner à l'édition
    showCodeEditor();
  } else {
    // Afficher la solution
    showSolutionView();
  }
};

function showSolutionView() {
  const editor = document.getElementById("editor");
  const editorContainer = editor.closest('.mb-6');
  const solutionDisplay = document.getElementById("solution-display");
  const solutionCode = document.getElementById("solution-code");
  const explanationDiv = document.getElementById("explanation");
  const explanationContent = document.getElementById("explanation-content");
  const solutionBtn = document.getElementById("solutionBtn");

  // Sauvegarder le code actuel
  editor.dataset.originalCode = editor.value;

  // Masquer l'éditeur de code
  editorContainer.classList.add("hidden");

  // Afficher la solution
  solutionCode.textContent = starter;
  solutionDisplay.classList.remove("hidden");
  solutionDisplay.classList.add("animate-fade-in");

  // Afficher les explications
  const explanation = getLocalizedValue(current.solution_explanation) || `Solution : ${starter}`;
  explanationDiv.classList.remove("hidden");
  explanationContent.textContent = explanation;

  // Animation d'apparition
  explanationDiv.classList.add("animate-fade-in");

  // Changer le texte du bouton
  solutionBtn.innerHTML = `
    <span>✏️</span>
    <span>Coder</span>
  `;
  solutionBtn.classList.remove("bg-purple-600", "hover:bg-purple-700");
  solutionBtn.classList.add("bg-blue-600", "hover:bg-blue-700");

  // Mettre à jour l'état
  isShowingSolution = true;

  // Faire défiler jusqu'à la solution
  setTimeout(() => {
    solutionDisplay.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 100);

  showNotification("Solution affichée 🎯", "success");
}

function showCodeEditor() {
  const editor = document.getElementById("editor");
  const editorContainer = editor.closest('.mb-6');
  const solutionDisplay = document.getElementById("solution-display");
  const solutionBtn = document.getElementById("solutionBtn");

  // Masquer la solution
  solutionDisplay.classList.add("hidden");

  // Afficher l'éditeur de code
  editorContainer.classList.remove("hidden");

  // Restaurer le texte du bouton
  solutionBtn.innerHTML = `
    <span>🎯</span>
    <span>Solution</span>
  `;
  solutionBtn.classList.remove("bg-blue-600", "hover:bg-blue-700");
  solutionBtn.classList.add("bg-purple-600", "hover:bg-purple-700");

  // Mettre à jour l'état
  isShowingSolution = false;

  showNotification("Mode édition activé ✏️", "info");
}

// Fonction pour afficher les notifications
function showNotification(message, type = "info") {
  // Créer l'élément de notification
  const notification = document.createElement("div");
  notification.className = `fixed top-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 animate-slide-up text-sm font-medium`;

  // Style selon le type
  switch(type) {
    case "success":
      notification.classList.add("bg-green-600", "text-white");
      break;
    case "warning":
      notification.classList.add("bg-amber-600", "text-white");
      break;
    case "error":
      notification.classList.add("bg-red-600", "text-white");
      break;
    default:
      notification.classList.add("bg-blue-600", "text-white");
  }

  notification.textContent = message;
  document.body.appendChild(notification);

  // Supprimer après 3 secondes
  setTimeout(() => {
    notification.classList.add("animate-fade-out");
    setTimeout(() => {
      if (notification.parentElement) {
        notification.parentElement.removeChild(notification);
      }
    }, 300);
  }, 3000);
}

// Écouteur pour le changement de langue
document.addEventListener('DOMContentLoaded', function() {
  const languageSelector = document.getElementById('language-selector');
  if (languageSelector) {
    languageSelector.addEventListener('change', async (e) => {
      console.log("🌍 Changement de langue détecté:", e.target.value);
      changeLanguage(e.target.value);

      // Attendre un peu que la langue soit mise à jour
      await new Promise(resolve => setTimeout(resolve, 100));

      // Recharger les cours et l'exercice actuel si besoin
      console.log("🔄 Rechargement des cours...");
      await loadCourses();

      if (currentCourseId) {
        console.log("🔄 Rechargement des exercices pour le cours:", currentCourseId);
        await loadExercisesForCurrentCourse();
      }
    });
  }

  // Event listeners pour les inputs interactifs
  const runWithInputsBtn = document.getElementById('runWithInputsBtn');
  if (runWithInputsBtn) {
    runWithInputsBtn.addEventListener('click', runCodeWithInputs);
  }

  const addInputBtn = document.getElementById('addInputBtn');
  if (addInputBtn) {
    addInputBtn.addEventListener('click', () => addInputField());
  }

  const clearInputsBtn = document.getElementById('clearInputsBtn');
  if (clearInputsBtn) {
    clearInputsBtn.addEventListener('click', () => {
      clearAllInputs();
      showNotification("Inputs vidés", "info");
    });
  }

  // Écouter les changements dans l'éditeur pour détecter les inputs
  const editor = document.getElementById('editor');
  if (editor) {
    let inputDetectionTimeout;
    editor.addEventListener('input', (e) => {
      clearTimeout(inputDetectionTimeout);
      inputDetectionTimeout = setTimeout(() => {
        updateInteractiveInputsUI(e.target.value);
      }, 500); // Délai de 500ms pour éviter trop de détections
    });
  }
});

// Variable globale pour empêcher les initialisations multiples
let isAppInitialized = false;

// Initialisation de l'application simplifiée
async function initApp() {
  // Garde pour éviter les initialisations multiples
  if (isAppInitialized) {
    console.log("⏭️ Application déjà initialisée, ignorer...");
    return;
  }

  isAppInitialized = true;
  console.log("🚀 Initialisation de l'application...");

  // Charger les cours directement sans i18n
  try {
    await loadCoursesSimple();
  } catch (error) {
    console.error("❌ Erreur lors de l'initialisation:", error);
    // Fallback vers le système legacy
    loadLegacyExercises();
  }
}

// Initialisation UNIQUE au chargement du DOM
document.addEventListener('DOMContentLoaded', function() {
  console.log("📄 DOM chargé, démarrage de l'application...");
  initApp();
});

// Gestionnaire d'événements pour le toggle de la leçon
document.addEventListener('DOMContentLoaded', function() {
  const lessonToggle = document.getElementById("lesson-toggle");

  if (lessonToggle) {
    lessonToggle.addEventListener('click', function() {
      const lessonContent = document.getElementById("lesson-content");
      const lessonToggleIcon = document.getElementById("lesson-toggle-icon");

      if (!lessonContent || !lessonToggleIcon) return;

      // Vérifier l'état actuel et inverser
      const isHidden = lessonContent.style.display === "none";

      if (isHidden) {
        // Développer la leçon
        lessonContent.style.display = "block";
        lessonToggleIcon.textContent = "▼";
        lessonToggleIcon.style.transform = "rotate(0deg)";
      } else {
        // Réduire la leçon
        lessonContent.style.display = "none";
        lessonToggleIcon.textContent = "▶";
        lessonToggleIcon.style.transform = "rotate(0deg)";
      }
    });
  }
});

// ===== FONCTIONNALITÉ D'IMPORT DE COURS =====

// Gestionnaire simple pour l'icône d'import
document.addEventListener('DOMContentLoaded', function() {
  const importBtnHeader = document.getElementById('import-course-btn-header');
  const importBtn = document.getElementById('import-course-btn');

  // Fonction simple d'import
  const handleImport = () => {
    const url = prompt("Entrez l'URL du cours à importer (GitHub, GitLab, etc.) :");
    if (url && url.trim()) {
      importFromSimpleUrl(url.trim());
    }
  };

  // Attacher aux deux boutons d'import
  if (importBtnHeader) {
    importBtnHeader.addEventListener('click', handleImport);
  }
  if (importBtn) {
    importBtn.addEventListener('click', handleImport);
  }
});

// Fonction de chargement de cours simplifiée
async function loadCoursesSimple() {
  console.log("🚀 Chargement des cours (simplifié)...");

  try {
    const courses = await fetch('/api/courses').then(r => r.json());
    console.log("✅ Cours reçus:", courses);

    const courseListEl = document.getElementById("course-list");
    if (!courseListEl) {
      console.error("❌ Élément course-list non trouvé!");
      return;
    }

    if (!courses || courses.length === 0) {
      console.warn("⚠️ Aucun cours trouvé, fallback vers l'ancien système");
      loadLegacyExercises();
      return;
    }

    // Afficher les cours
    courseListEl.innerHTML = courses.map(course => {
      const title = course.title.fr || course.title.en || course.id;
      return `
      <div class="course-card bg-gray-700 hover:bg-gray-600 border-2 border-transparent hover:border-blue-500 rounded-lg p-4 cursor-pointer transition-all duration-200 flex-shrink-0 w-80" data-course-id="${course.id}">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">📚</span>
            <h3 class="font-bold text-white">${title}</h3>
          </div>
          <span class="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">${course.level || 'N/A'}</span>
        </div>

        <p class="text-gray-300 text-sm mb-3 line-clamp-2">
          ${course.description.fr || course.description.en || 'Description non disponible'}
        </p>

        <div class="flex flex-wrap gap-2 text-xs">
          <span class="px-2 py-1 bg-gray-600 text-gray-200 rounded">
            ${course.exercise_count || 0} exercices
          </span>
          <span class="px-2 py-1 bg-amber-600/20 text-amber-300 rounded">
            ${course.total_stars || 0} ⭐
          </span>
        </div>
      </div>
    `;
    }).join("");

    console.log("🎨 Interface des cours générée");

    // Ajouter les écouteurs d'événements
    courseListEl.querySelectorAll(".course-card").forEach(card => {
      card.onclick = () => selectCourseSimple(card.dataset.courseId);
    });

    console.log("🖱️ Écouteurs d'événements ajoutés");

    // Sélectionner le premier cours par défaut
    if (courses.length > 0) {
      console.log("🎯 Sélection du premier cours:", courses[0].id);
      selectCourseSimple(courses[0].id);
    }
  } catch (error) {
    console.error("❌ Erreur lors du chargement des cours:", error);
    console.log("🔄 Fallback vers l'ancien système");
    loadLegacyExercises();
  }
}

// Fonction de sélection de cours simplifiée
async function selectCourseSimple(courseId) {
  console.log("🎯 Sélection du cours:", courseId);
  try {
    currentCourseId = courseId;

    // Mettre à jour l'interface de sélection
    document.querySelectorAll(".course-card").forEach(card => {
      const isSelected = card.dataset.courseId === courseId;

      if (isSelected) {
        card.classList.remove("border-transparent", "hover:border-blue-500");
        card.classList.add("border-blue-500", "bg-blue-900/30");
      } else {
        card.classList.remove("border-blue-500", "bg-blue-900/30");
        card.classList.add("border-transparent", "hover:border-blue-500");
      }
    });

    // Charger les exercices du cours
    console.log("📚 Chargement des exercices...");
    const exercises = await fetch(`/api/courses/${courseId}/exercises`).then(r => r.json());
    console.log("✅ Exercices reçus:", exercises);
    loadExercisesSimple(exercises, courseId);
    console.log("✅ Exercices chargés");

    // Afficher la section des exercices
    const exercisesContainer = document.getElementById("exercises-container");
    if (exercisesContainer) {
      exercisesContainer.style.display = "block";
      console.log("✅ Section exercices affichée");
    } else {
      console.error("❌ Élément exercises-container non trouvé!");
    }

  } catch (error) {
    console.error("❌ Erreur lors de la sélection du cours:", error);
  }
}

// Fonction de chargement d'exercices simplifiée
function loadExercisesSimple(exercises, courseId) {
  const el = document.getElementById("ex-list");
  if (!el) {
    console.error("❌ Élément ex-list non trouvé!");
    return;
  }

  el.innerHTML = exercises.map(x => {
    const title = x.title.fr || x.title.en || x.id;
    return `
    <div class="mb-2">
      <a href="#" data-course-id="${courseId}" data-id="${x.id}"
         class="block px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors duration-200 group">
        <div class="flex items-center justify-between">
          <span class="text-white font-medium group-hover:text-blue-300 transition-colors">
            🧩 ${title}
          </span>
          <span class="text-yellow-400">
            ${"★".repeat(x.stars || 0)}
          </span>
        </div>
      </a>
    </div>
  `;
  }).join("");

  // Ajouter les écouteurs d'événements
  el.querySelectorAll("a").forEach(a => a.onclick = async (e) => {
    e.preventDefault();
    console.log("📝 Sélection de l'exercice:", a.dataset.id);

    try {
      const ex = await fetch(`/api/courses/${a.dataset.courseId}/exercises/${a.dataset.id}`).then(r => r.json());
      current = ex;
      starter = ex.starter || "";

      // Mettre à jour l'interface de l'exercice
      const title = ex.title.fr || ex.title.en || ex.id;
      const prompt = ex.prompt.fr || ex.prompt.en || 'Pas de description';

      document.getElementById("ex-title").textContent = "🧩 " + title;
      document.getElementById("ex-stars").innerHTML = "★".repeat(ex.stars || 0);
      document.getElementById("ex-prompt").textContent = prompt;

      // Vider l'éditeur et les sorties
      document.getElementById("editor").value = "";
      document.getElementById("output").textContent = "—";
      document.getElementById("hint").textContent = "—";

      // Cacher les explications
      document.getElementById("explanation").classList.add("hidden");

      // Afficher la leçon théorique si elle existe
      if (ex.theory) {
        console.log("📚 Affichage de la leçon théorique pour:", ex.id);
        displayLocalizedLesson(ex.theory);
      } else {
        console.log("ℹ️ Aucune leçon théorique pour:", ex.id);
        // Cacher la section leçon si pas de théorie
        const lessonSection = document.getElementById("lesson-section");
        if (lessonSection) {
          lessonSection.classList.add("hidden");
        }
      }

      // Vérifier si l'exercice contient des inputs et mettre à jour l'interface
      if (ex.starter && hasInputFunction(ex.starter)) {
        console.log("🔍 Exercice avec inputs détecté:", ex.id);
        // Pré-remplir l'éditeur avec le starter code pour activer la détection
        document.getElementById("editor").value = ex.starter;
        updateInteractiveInputsUI(ex.starter);
      } else {
        updateInteractiveInputsUI("");
      }

      console.log("✅ Exercice chargé");
    } catch (error) {
      console.error("❌ Erreur lors du chargement de l'exercice:", error);
    }
  });

  console.log("✅ Exercices affichés");
}

// Fonction d'import simple
async function importFromSimpleUrl(url) {
  showNotification("Importation en cours...", "info");

  try {
    const response = await api('/api/courses/import', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        url: url,
        course_id: null,
        overwrite: true
      })
    });

    if (response.success) {
      showNotification(`✅ ${response.message}`, "success");

      // Recharger les cours après un court délai
      setTimeout(() => {
        loadCoursesSimple();
      }, 1000);
    } else {
      showNotification(`❌ ${response.message}`, "error");
    }
  } catch (error) {
    console.error('Erreur lors de l\'import:', error);
    showNotification("Erreur lors de l'import: " + error.message, "error");
  }
}

// ===== FONCTIONNALITÉ D'INPUTS INTERACTIFS =====

// Variables globales pour la gestion des inputs
let inputFields = [];
let inputCounter = 0;

/**
 * Détecte si le code contient des fonctions input()
 * @param {string} code - Le code Python à analyser
 * @returns {boolean} - True si le code contient input()
 */
function hasInputFunction(code) {
  if (!code || typeof code !== 'string') return false;

  // Supprimer les commentaires pour éviter les faux positifs
  const codeWithoutComments = code.replace(/#.*$/gm, '');

  // Rechercher les appels à input() de manière robuste
  // Évite les faux positifs comme "def input_function" ou "# input() est dans un commentaire"
  return /\binput\s*\(/.test(codeWithoutComments);
}

/**
 * Affiche ou masque la section des inputs interactifs
 * @param {boolean} show - True pour afficher, false pour masquer
 */
function toggleInteractiveInputsSection(show) {
  const section = document.getElementById("interactive-inputs-section");
  if (!section) return;

  if (show) {
    section.classList.remove("hidden");
    section.classList.add("animate-slide-up");

    // Initialiser avec un premier input si vide
    if (inputFields.length === 0) {
      addInputField();
    }
  } else {
    section.classList.add("hidden");
  }
}

/**
 * Ajoute un champ d'input
 */
function addInputField(value = "") {
  inputCounter++;
  const inputId = `interactive-input-${inputCounter}`;

  const inputContainer = document.getElementById("inputs-container");
  if (!inputContainer) return;

  const inputField = {
    id: inputId,
    value: value
  };

  inputFields.push(inputField);

  const inputElement = document.createElement("div");
  inputElement.className = "flex items-center gap-2 animate-slide-up";
  inputElement.id = inputId;
  inputElement.innerHTML = `
    <label class="text-sm text-gray-300 min-w-[80px]">
      Input #${inputCounter}:
    </label>
    <input
      type="text"
      class="flex-1 px-3 py-2 bg-gray-800 text-gray-100 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
      placeholder="Entrez une valeur..."
      value="${escapeHtml(value)}"
      data-input-id="${inputId}"
    />
    <button
      class="px-2 py-1 bg-red-600/20 text-red-300 rounded hover:bg-red-600/30 transition-colors duration-200"
      onclick="removeInputField('${inputId}')"
      title="Supprimer cet input"
    >
      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>
  `;

  inputContainer.appendChild(inputElement);
}

/**
 * Supprime un champ d'input
 * @param {string} inputId - L'ID du champ à supprimer
 */
function removeInputField(inputId) {
  const index = inputFields.findIndex(field => field.id === inputId);
  if (index !== -1) {
    inputFields.splice(index, 1);
    const element = document.getElementById(inputId);
    if (element) {
      element.remove();
    }
  }
}

/**
 * Récupère les valeurs des inputs
 * @returns {string[]} - La liste des valeurs des inputs
 */
function getInputValues() {
  const values = [];
  inputFields.forEach(field => {
    const inputElement = document.querySelector(`[data-input-id="${field.id}"]`);
    if (inputElement) {
      values.push(inputElement.value);
    }
  });
  return values;
}

/**
 * Vide tous les champs d'input
 */
function clearAllInputs() {
  inputFields = [];
  inputCounter = 0;
  const container = document.getElementById("inputs-container");
  if (container) {
    container.innerHTML = "";
  }
}

/**
 * Exécute le code avec les inputs fournis
 */
async function runCodeWithInputs() {
  const code = document.getElementById("editor").value;
  const inputs = getInputValues();

  if (inputs.length === 0) {
    showNotification("Veuillez ajouter au moins un input", "warning");
    return;
  }

  // Afficher le statut d'exécution
  const statusEl = document.getElementById("execution-status");
  const outputEl = document.getElementById("output");
  const successOverlay = document.getElementById("success-overlay");
  const statsEl = document.getElementById("execution-stats");

  // Réinitialiser les éléments
  statusEl.classList.remove("hidden");
  successOverlay.classList.add("hidden");
  statsEl.classList.add("hidden");
  outputEl.textContent = "⏳ Lancement avec inputs interactifs...";

  // Mesurer le temps d'exécution
  const startTime = performance.now();

  try {
    const response = await api("/api/run-with-inputs", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        course_id: currentCourseId || "python-basics",
        code: code,
        inputs: inputs,
        timeout: 30
      })
    });

    const endTime = performance.now();
    const executionTime = Math.round(endTime - startTime);

    // Masquer le statut
    statusEl.classList.add("hidden");

    if (response.ok) {
      // Succès : afficher le résultat
      outputEl.textContent = response.output || "Exécution terminée sans sortie";

      // Afficher l'overlay de succès
      setTimeout(() => {
        successOverlay.classList.remove("hidden");
        showExecutionStats(executionTime, true);

        setTimeout(() => {
          successOverlay.classList.add("hidden");
        }, 2000);
      }, 300);

      // Ajouter une classe de succès
      outputEl.parentElement.classList.add("border-green-500/50", "bg-green-950/10");
      setTimeout(() => {
        outputEl.parentElement.classList.remove("border-green-500/50", "bg-green-950/10");
      }, 3000);

      showNotification("Exécution avec inputs réussie !", "success");
    } else {
      // Erreur : afficher en rouge
      const errorMsg = response.error || "Une erreur est survenue lors de l'exécution";
      outputEl.innerHTML = `<span class="text-red-400">❌ Erreur avec inputs :</span>\n${errorMsg}`;

      showExecutionStats(executionTime, false);
      outputEl.parentElement.classList.add("border-red-500/50", "bg-red-950/10");
      setTimeout(() => {
        outputEl.parentElement.classList.remove("border-red-500/50", "bg-red-950/10");
      }, 3000);

      showNotification("Erreur lors de l'exécution avec inputs", "error");
    }

  } catch (error) {
    const endTime = performance.now();
    const executionTime = Math.round(endTime - startTime);

    statusEl.classList.add("hidden");
    outputEl.innerHTML = `<span class="text-orange-400">⚠️ Problème de connexion avec inputs :</span>\n${error.message}`;
    showExecutionStats(executionTime, false);

    outputEl.parentElement.classList.add("border-orange-500/50", "bg-orange-950/10");
    setTimeout(() => {
      outputEl.parentElement.classList.remove("border-orange-500/50", "bg-orange-950/10");
    }, 3000);

    showNotification("Problème de connexion avec les inputs", "error");
  }
}

/**
 * Met à jour l'interface en fonction de la présence d'inputs dans le code
 * @param {string} code - Le code à analyser
 */
function updateInteractiveInputsUI(code) {
  const hasInputs = hasInputFunction(code);

  if (hasInputs) {
    toggleInteractiveInputsSection(true);

    // Modifier le bouton d'exécution principal
    const runBtn = document.getElementById("runBtn");
    if (runBtn) {
      runBtn.innerHTML = `
        <span>⚠️</span>
        <span>Exécuter (sans inputs)</span>
      `;
      runBtn.classList.remove("bg-blue-600", "hover:bg-blue-700");
      runBtn.classList.add("bg-orange-600", "hover:bg-orange-700");
    }

    showNotification("Cet exercice contient des inputs() ! Utilise la section inputs interactifs.", "info");
  } else {
    toggleInteractiveInputsSection(false);

    // Restaurer le bouton d'exécution normal
    const runBtn = document.getElementById("runBtn");
    if (runBtn) {
      runBtn.innerHTML = `
        <span>▶️</span>
        <span>Exécuter</span>
      `;
      runBtn.classList.remove("bg-orange-600", "hover:bg-orange-700");
      runBtn.classList.add("bg-blue-600", "hover:bg-blue-700");
    }

    clearAllInputs();
  }
}
