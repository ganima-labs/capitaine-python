// Version simplifiée pour debugging
console.log("🚀 Script simplifié chargé");

// Variables globales
let current = null;
let starter = "";
let currentCourseId = null;
let currentLanguage = "fr";
let translations = {};

// Fonction API simple
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

    console.log(`📡 Réponse API: ${response.status}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(`✅ Données reçues:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Erreur API:`, error);
    throw error;
  }
}

// Fonction pour obtenir une valeur localisée
function getLocalizedValue(value) {
  if (typeof value === 'string') return value;
  if (typeof value === 'object' && value[currentLanguage]) return value[currentLanguage];
  if (typeof value === 'object' && value.fr) return value.fr;
  return value;
}

// Fonction loadCourses simplifiée
async function loadCourses() {
  console.log("🚀 Début du chargement des cours...");

  try {
    const courses = await api("/api/courses");
    console.log("✅ Cours reçus:", courses);

    const courseListEl = document.getElementById("course-list");
    if (!courseListEl) {
      console.error("❌ Élément course-list non trouvé!");
      return;
    }

    if (!courses || courses.length === 0) {
      console.warn("⚠️ Aucun cours trouvé");
      courseListEl.innerHTML = "<p class='text-gray-400'>Aucun cours disponible</p>";
      return;
    }

    console.log(`🎨 Génération de l'interface pour ${courses.length} cours`);

    // Générer le HTML pour les cours
    courseListEl.innerHTML = courses.map(course => {
      const localizedTitle = getLocalizedValue(course.title);
      const localizedDescription = getLocalizedValue(course.description);

      console.log(`📚 Cours: ${course.id} - ${localizedTitle}`);

      return `
      <div class="course-card bg-gray-700 hover:bg-gray-600 border-2 border-transparent hover:border-blue-500 rounded-lg p-4 cursor-pointer transition-all duration-200" data-course-id="${course.id}">
        <div class="flex items-start justify-between mb-3">
          <div class="flex items-center gap-2">
            ${course.icon ? `<img src="${course.icon}" alt="${localizedTitle}" class="w-6 h-6 rounded" />` : '<span class="text-xl">📚</span>'}
            <h3 class="font-bold text-white">${localizedTitle}</h3>
          </div>
          <span class="px-2 py-1 bg-blue-600 text-white text-xs rounded-full">${course.level}</span>
        </div>
        <p class="text-gray-300 text-sm mb-3">${localizedDescription}</p>
        <div class="flex flex-wrap gap-2 text-xs">
          <span class="px-2 py-1 bg-gray-600 text-gray-200 rounded">
            ${course.exercise_count} exercices
          </span>
          <span class="px-2 py-1 bg-amber-600/20 text-amber-300 rounded">
            ${course.total_stars} ⭐
          </span>
        </div>
      </div>
    `;
    }).join("");

    console.log("✅ Interface des cours générée");

    // Ajouter les écouteurs d'événements
    courseListEl.querySelectorAll(".course-card").forEach(card => {
      card.onclick = () => {
        console.log("🖱️ Clique sur le cours:", card.dataset.courseId);
        selectCourse(card.dataset.courseId);
      };
    });

    console.log("✅ Écouteurs d'événements ajoutés");

    // Sélectionner le premier cours par défaut
    if (courses.length > 0) {
      console.log("🎯 Sélection du premier cours:", courses[0].id);
      selectCourse(courses[0].id);
    }

  } catch (error) {
    console.error("❌ Erreur lors du chargement des cours:", error);
    const courseListEl = document.getElementById("course-list");
    if (courseListEl) {
      courseListEl.innerHTML = `<p class="text-red-400">Erreur: ${error.message}</p>`;
    }
  }
}

// Fonction selectCourse simplifiée
async function selectCourse(courseId) {
  console.log("🎯 Sélection du cours:", courseId);
  try {
    currentCourseId = courseId;

    // Mettre à jour l'interface de sélection
    document.querySelectorAll(".course-card").forEach(card => {
      const isSelected = card.dataset.courseId === courseId;
      if (isSelected) {
        card.classList.add("border-blue-500", "bg-blue-900/30");
      } else {
        card.classList.remove("border-blue-500", "bg-blue-900/30");
      }
    });

    // Charger les exercices du cours
    console.log("📚 Chargement des exercices...");
    const exercises = await api(`/api/courses/${courseId}/exercises`);
    console.log("✅ Exercices reçus:", exercises);

    // Afficher les exercices
    const exercisesContainer = document.getElementById("exercises-container");
    const exListEl = document.getElementById("ex-list");

    if (exercisesContainer && exListEl) {
      exercisesContainer.style.display = "block";
      exListEl.innerHTML = exercises.map(ex => {
        const localizedTitle = getLocalizedValue(ex.title);
        return `
        <div class="mb-2">
          <a href="#" data-course-id="${courseId}" data-id="${ex.id}"
             class="block px-4 py-3 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
            <div class="flex items-center justify-between">
              <span class="text-white font-medium">🧩 ${localizedTitle}</span>
              <span class="text-yellow-400">${"★".repeat(ex.stars)}</span>
            </div>
          </a>
        </div>`;
      }).join("");

      console.log(`✅ ${exercises.length} exercices affichés`);
    }

  } catch (error) {
    console.error("❌ Erreur lors de la sélection du cours:", error);
  }
}

// Initialisation
console.log("🚀 Initialisation simplifiée...");

// Attendre que le DOM soit prêt
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadCourses);
} else {
  loadCourses();
}

console.log("✅ Script simplifié initialisé");