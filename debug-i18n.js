// Script de diagnostic pour la localisation
console.log("🔍 Script de diagnostic i18n chargé");

// Vérifier l'état actuel
function diagnostic() {
    console.log("=== DIAGNOSTIC i18n ===");

    // 1. Vérifier la langue actuelle
    console.log("🌍 Langue actuelle:", window.currentLanguage || "Non définie");

    // 2. Vérifier les traductions
    if (typeof translations !== 'undefined') {
        console.log("📚 Traductions chargées:", Object.keys(translations));
        console.log("Traductions FR:", translations.fr);
        console.log("Traductions EN:", translations.en);
    } else {
        console.log("❌ Traductions non chargées");
    }

    // 3. Vérifier les éléments DOM
    const languageSelector = document.getElementById('language-selector');
    console.log("🎛️ Sélecteur de langue:", languageSelector ? "Trouvé" : "Non trouvé");

    if (languageSelector) {
        console.log("📋 Valeur actuelle du sélecteur:", languageSelector.value);
    }

    // 4. Vérifier les cours
    const courseCards = document.querySelectorAll('.course-card h3');
    console.log("📚 Nombre de cartes de cours:", courseCards.length);

    courseCards.forEach((card, index) => {
        console.log(`  Cours ${index + 1}: "${card.textContent.trim()}"`);
    });

    // 5. Vérifier la fonction getLocalizedValue
    if (typeof getLocalizedValue !== 'undefined') {
        console.log("✅ Fonction getLocalizedValue disponible");

        // Test avec un objet multi-langue
        const testValue = {
            fr: "Test français",
            en: "Test anglais",
            es: "Test español",
            de: "Test deutsch"
        };

        console.log("🧪 Test getLocalizedValue:");
        console.log("  FR:", getLocalizedValue(testValue, 'fr'));
        console.log("  EN:", getLocalizedValue(testValue, 'en'));
        console.log("  ES:", getLocalizedValue(testValue, 'es'));
        console.log("  DE:", getLocalizedValue(testValue, 'de'));
    } else {
        console.log("❌ Fonction getLocalizedValue non disponible");
    }

    console.log("=== FIN DU DIAGNOSTIC ===");
}

// Test manuel du changement de langue
async function testManuelChangementLangue() {
    console.log("🔄 Test manuel du changement de langue");

    const languageSelector = document.getElementById('language-selector');
    if (!languageSelector) {
        console.error("❌ Sélecteur de langue non trouvé");
        return;
    }

    console.log("📋 Langue avant:", languageSelector.value);

    // Changer vers anglais
    languageSelector.value = 'en';
    console.log("📋 Langue changée pour: EN");

    // Déclencher l'événement
    const event = new Event('change', { bubbles: true });
    languageSelector.dispatchEvent(event);

    // Attendre un peu
    await new Promise(resolve => setTimeout(resolve, 500));

    // Vérifier les résultats
    console.log("📚 Titres après changement de langue:");
    const courseCards = document.querySelectorAll('.course-card h3');
    courseCards.forEach((card, index) => {
        console.log(`  Cours ${index + 1}: "${card.textContent.trim()}"`);
    });

    console.log("✅ Test terminé");
}

// Fonction pour exécuter un appel API direct
async function testAPIDirect() {
    try {
        console.log("📡 Test API direct...");
        const response = await fetch('/api/courses');
        const courses = await response.json();

        console.log("✅ Cours reçus de l'API:");
        courses.forEach((course, index) => {
            console.log(`  ${index + 1}. ${course.id}:`);
            console.log(`     Titre FR: ${course.title.fr || course.title}`);
            console.log(`     Titre EN: ${course.title.en || 'N/A'}`);
            console.log(`     Titre ES: ${course.title.es || 'N/A'}`);
            console.log(`     Titre DE: ${course.title.de || 'N/A'}`);
        });
    } catch (error) {
        console.error("❌ Erreur API:", error);
    }
}

// Ajouter les fonctions au scope global
window.diagnostic = diagnostic;
window.testManuelChangementLangue = testManuelChangementLangue;
window.testAPIDirect = testAPIDirect;

// Diagnostic automatique après 2 secondes
setTimeout(() => {
    diagnostic();
}, 2000);

console.log("🔍 Fonctions de diagnostic ajoutées. Utilisez diagnostic(), testManuelChangementLangue() ou testAPIDirect() dans la console.");