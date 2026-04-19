/**
 * theme_toggle.js
 * Universal Theme Initialization & Toggle Logic.
 * Optimized for immediate execution to prevent "white flash".
 */

(function() {
    const themeStorageKey = 'theme';
    const body = document.body;
    const html = document.documentElement;

    // 1. Immediate Boot: Read from localStorage
    const savedTheme = localStorage.getItem(themeStorageKey);
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');

    // Apply immediately to prevent layout shift/flash
    if (initialTheme === 'dark') {
        html.classList.add('dark-mode');
        body.classList.add('dark-mode');
    } else {
        html.classList.remove('dark-mode');
        body.classList.remove('dark-mode');
    }

    /**
     * Toggles the global theme and persists state.
     */
    function toggleTheme() {
        const isDark = body.classList.toggle('dark-mode');
        html.classList.toggle('dark-mode', isDark);
        
        const newTheme = isDark ? 'dark' : 'light';
        localStorage.setItem(themeStorageKey, newTheme);
        
        // Sync icon/text if needed for elements with class 'theme-toggle-btn'
        console.log(`Global Theme: ${newTheme.toUpperCase()}`);
    }

    // 2. Event Delegation: Listen for clicks on anything with ID "theme-toggle"
    // This allows dynamically loaded elements or various templates to work without unique binding logic.
    document.addEventListener('click', function(e) {
        if (e.target.id === 'theme-toggle' || e.target.closest('#theme-toggle')) {
            toggleTheme();
        }
    });

    // Expose for manual calls if necessary
    window.setGlobalTheme = toggleTheme;
})();
