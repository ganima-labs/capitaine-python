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
  if (current.lesson) {
    displayLocalizedLesson(current.lesson);
  }
}

// Fonction pour obtenir une valeur localisée
function getLocalizedValue(value) {
  if (typeof value === 'string') return value;
  if (typeof value === 'object' && value[currentLanguage]) return value[currentLanguage];
  if (typeof value === 'object' && value.fr) return value.fr; // Fallback français
  return value; // Valeur par défaut
}

// Fonction pour afficher une leçon localisée
function displayLocalizedLesson(lesson) {
  const lessonSection = document.getElementById("lesson-section");
  const lessonTitle = document.getElementById("lesson-title");
  const lessonDuration = document.getElementById("lesson-duration");
  const lessonContent = document.getElementById("lesson-content");
  const lessonToggleIcon = document.getElementById("lesson-toggle-icon");

  if (!lesson) {
    lessonSection.classList.add("hidden");
    return;
  }

  const localizedTitle = getLocalizedValue(lesson.title);
  const localizedContent = getLocalizedValue(lesson.content);
  const localizedDuration = getLocalizedValue(lesson.duration);

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

  // Formater le contenu avec Markdown-like parsing
  let formattedContent = localizedContent
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
    if (ex.lesson) {
      displayLocalizedLesson(ex.lesson);
    } else {
      displayLesson(ex.lesson); // Fallback pour l'ancien système
    }

    // Commencer avec un éditeur vide
    document.getElementById("editor").value = "";
    document.getElementById("output").textContent = "—";
    document.getElementById("hint").textContent = "—";

    // Cacher les explications
    document.getElementById("explanation").classList.add("hidden");
    document.getElementById("explanation-content").textContent = "—";

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
      if (ex.lesson) {
        displayLocalizedLesson(ex.lesson);
      } else {
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
  const out = await api("/api/run",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({code})});

  // Garantir l'existence de l'élément output et afficher le résultat
  const outputElement = ensureOutputElement();
  if (outputElement) {
    outputElement.textContent = (out.run && out.run.stdout) || (out.run && out.run.stderr) || JSON.stringify(out,null,2);
  } else {
    console.error("❌ Impossible de créer ou trouver l'élément output");
  }
};

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

document.getElementById("solutionBtn").onclick = async ()=>{
  if(!current) return alert(t('messages.choose_exercise'));

  // Afficher la solution dans l'éditeur
  document.getElementById("editor").value = starter;

  // Afficher les explications (avec localisation)
  const explanation = getLocalizedValue(current.solution_explanation) || `Solution : ${starter}`;
  document.getElementById("explanation").classList.remove("hidden");
  document.getElementById("explanation-content").textContent = explanation;

  // Animation d'apparition des explications
  const explanationDiv = document.getElementById("explanation");
  explanationDiv.classList.remove("hidden");
  explanationDiv.classList.add("animate-fade-in");

  // Faire défiler jusqu'aux explications
  setTimeout(() => {
    explanationDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, 100);
};

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
});

// Initialisation de l'application
async function initApp() {
  console.log("🚀 Initialisation de l'application avec i18n...");

  // Charger les traductions d'abord
  await loadTranslations();

  // Détecter la langue du navigateur
  const savedLanguage = localStorage.getItem('preferredLanguage');
  const detectedLang = savedLanguage || detectLanguage();
  changeLanguage(detectedLang);

  // Mettre à jour le sélecteur de langue
  const languageSelector = document.getElementById('language-selector');
  if (languageSelector) {
    languageSelector.value = currentLanguage;
  }

  // Charger les cours
  loadCourses();
}

// Initialisation immédiate avec backup
console.log("🚀 Script chargé, initialisation...");

// Essayer de charger les cours immédiatement
initApp();

// Essayer aussi quand le DOM est prêt (backup)
document.addEventListener('DOMContentLoaded', function() {
  console.log("📄 DOM chargé, deuxième tentative d'initialisation...");
  initApp();
});

window.addEventListener('load', function() {
  console.log("🖼️ Page entièrement chargée, troisième tentative...");
  setTimeout(initApp, 100);
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
