// Version DEBUG ULTRA-SIMPLIFIÉE pour diagnostiquer le problème
console.log("🚀 app_debug.js DEBUG version chargée");

// Variables globales
let current = null;
let currentCourseId = null;
let language = 'fr';

// Fonction utilitaire simple
function getLocalizedValue(obj) {
  if (!obj) return '';
  return obj[language] || obj.fr || obj.en || '';
}

// Fonction ultra-simple de chargement de cours
async function loadCoursesDebug() {
  console.log("🔍 Début chargement des cours DEBUG");

  try {
    // Test 1: Vérifier l'élément DOM
    const courseListEl = document.getElementById("course-list");
    console.log("📋 Élément course-list trouvé:", !!courseListEl);

    if (!courseListEl) {
      console.error("❌ Élément course-list non trouvé dans le DOM!");
      console.log("🔍 Éléments disponibles:", document.querySelectorAll('[id*="course"]'));
      return;
    }

    // Test 2: Appel API
    console.log("🌐 Appel API /api/courses...");
    const response = await fetch('/api/courses');
    console.log("📡 Response status:", response.status);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const courses = await response.json();
    console.log("✅ Cours reçus:", courses.length, courses);

    // Test 3: Vider le conteneur
    courseListEl.innerHTML = '';
    console.log("🗑️ Conteneur vidé");

    // Test 4: Créer les cartes de cours
    courses.forEach((course, index) => {
      console.log(`🎨 Création carte ${index}:`, course.id);

      const courseCard = document.createElement('div');
      courseCard.className = 'course-card flex-shrink-0 w-48 bg-gray-700 rounded-lg p-4 border-2 border-transparent hover:border-blue-500 transition-all duration-200 cursor-pointer';
      courseCard.dataset.courseId = course.id;

      const title = getLocalizedValue(course.title);
      const description = getLocalizedValue(course.description);
      const exerciseCount = course.exercise_count || 0;
      const totalStars = course.total_stars || 0;
      const level = course.level || '🎯';

      courseCard.innerHTML = `
        <div class="text-lg font-bold text-white mb-2">${title}</div>
        <div class="text-sm text-gray-300 mb-3">${description}</div>
        <div class="flex items-center justify-between text-xs text-gray-400">
          <span>${level}</span>
          <span>${exerciseCount} exercices</span>
        </div>
        <div class="mt-2">
          ${'⭐'.repeat(Math.min(totalStars, 5))}
        </div>
      `;

      courseListEl.appendChild(courseCard);
      console.log(`✅ Carte ${index} ajoutée`);
    });

    console.log("🎉 Cours affichés avec succès!");

    // Test 5: Ajouter les écouteurs d'événements
    document.querySelectorAll('.course-card').forEach(card => {
      card.addEventListener('click', function() {
        const courseId = this.dataset.courseId;
        console.log("🖱️ Cours cliqué:", courseId);
        selectCourseDebug(courseId);
      });
    });

    // Test 6: Sélectionner automatiquement le premier cours
    if (courses.length > 0) {
      console.log("🎯 Sélection automatique du premier cours");
      selectCourseDebug(courses[0].id);
    }

  } catch (error) {
    console.error("❌ ERREUR dans loadCoursesDebug:", error);
    console.error("Stack trace:", error.stack);
  }
}

// Fonction ultra-simple de sélection de cours
async function selectCourseDebug(courseId) {
  console.log("🎯 Sélection du cours DEBUG:", courseId);

  try {
    currentCourseId = courseId;

    // Mettre à jour les classes CSS
    document.querySelectorAll('.course-card').forEach(card => {
      const isSelected = card.dataset.courseId === courseId;
      if (isSelected) {
        card.classList.remove('border-transparent', 'hover:border-blue-500');
        card.classList.add('border-blue-500', 'bg-blue-900/30');
      } else {
        card.classList.add('border-transparent', 'hover:border-blue-500');
        card.classList.remove('border-blue-500', 'bg-blue-900/30');
      }
    });

    // Afficher le conteneur d'exercices
    const exercisesContainer = document.getElementById('exercises-container');
    if (exercisesContainer) {
      exercisesContainer.style.display = 'flex';
      console.log("📋 Conteneur exercices affiché");
    }

    // Charger les exercices
    const response = await fetch(`/api/courses/${courseId}/exercises`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const exercises = await response.json();
    console.log("✅ Exercices chargés:", exercises.length);

    // Afficher les exercices
    const exList = document.getElementById('ex-list');
    if (exList) {
      exList.innerHTML = '';
      exercises.forEach(exercise => {
        const exLink = document.createElement('a');
        exLink.href = '#';
        exLink.className = 'block p-3 bg-gray-700 rounded hover:bg-gray-600 transition-colors mb-2';
        exLink.innerHTML = `
          <div class="font-medium">${getLocalizedValue(exercise.title)}</div>
          <div class="text-sm text-gray-400">${'⭐'.repeat(exercise.stars || 1)}</div>
        `;
        exLink.addEventListener('click', (e) => {
          e.preventDefault();
          loadExerciseDebug(exercise.id);
        });
        exList.appendChild(exLink);
      });
      console.log("🎯 Exercices affichés");
    }

  } catch (error) {
    console.error("❌ ERREUR dans selectCourseDebug:", error);
  }
}

// Fonction ultra-simple de chargement d'exercice
async function loadExerciseDebug(exerciseId) {
  console.log("📖 Chargement exercice DEBUG:", exerciseId);

  try {
    const response = await fetch(`/api/exercises/${exerciseId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const exercise = await response.json();
    console.log("✅ Exercice chargé:", exercise);
    current = exercise;

    // Mettre à jour l'interface
    document.getElementById('ex-title').textContent = getLocalizedValue(exercise.title);
    document.getElementById('ex-prompt').textContent = getLocalizedValue(exercise.prompt);
    document.getElementById('editor').value = getLocalizedValue(exercise.starter);

    // Afficher les étoiles
    const starsContainer = document.getElementById('ex-stars');
    if (starsContainer) {
      starsContainer.innerHTML = '⭐'.repeat(exercise.stars || 1);
    }

    console.log("🎉 Exercice affiché avec succès");

  } catch (error) {
    console.error("❌ ERREUR dans loadExerciseDebug:", error);
  }
}

// Démarrage
console.log("🚀 Démarrage version DEBUG...");

// Essai immédiat
loadCoursesDebug();

// Backup après DOM chargé
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    console.log("📄 DOM chargé, deuxième tentative...");
    setTimeout(loadCoursesDebug, 100);
  });
} else {
  console.log("📄 DOM déjà chargé, deuxième tentative immédiate...");
  setTimeout(loadCoursesDebug, 100);
}

// Backup final après chargement complet
window.addEventListener('load', () => {
  console.log("🖼️ Page chargée, troisième tentative...");
  setTimeout(loadCoursesDebug, 500);
});

// Fonctions vides pour éviter les erreurs
function resetExerciseInterface() {}
function showNotification(message, type) { console.log(`[${type}] ${message}`); }
function showCodeEditor() {}
function showSolutionView() {}

console.log("🎯 Version DEBUG initialisée");