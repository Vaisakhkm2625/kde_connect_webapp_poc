<script lang="ts">
    import { Moon, Sun, Github, Info, Heart } from "lucide-svelte";
    import { APP_NAME } from "$lib/utils/constants";

    let isDark = true; // Default locked to dark for now given the theme

    function toggleTheme() {
        // Current theme is hardcoded dark in app.html class="dark"
        // We can toggle it on documentElement
        /*
    isDark = !isDark;
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    */
        // For now, simple placeholder toggle as the UI is designed for dark mode primarily.
    }
</script>

<div class="h-full flex flex-col bg-kde-bg text-kde-text p-6 gap-6">
    <div class="flex items-center gap-4 border-b border-kde-border pb-6">
        <div
            class="w-16 h-16 bg-kde-blue/20 rounded-xl flex items-center justify-center text-kde-blue"
        >
            <Info size={32} />
        </div>
        <div>
            <h1 class="text-2xl font-bold">{APP_NAME} Web Interface</h1>
            <p class="text-kde-text-dim">Version 2.0 (SvelteKit Edition)</p>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Appearance -->
        <div class="bg-kde-card border border-kde-border rounded-lg p-4">
            <h2 class="font-medium mb-4 flex items-center gap-2">Appearance</h2>
            <div class="flex items-center justify-between">
                <span>Theme Mode (Dark Only)</span>
                <button
                    class="bg-kde-bg p-2 rounded-full text-kde-text-dim cursor-not-allowed"
                >
                    <Moon size={18} />
                </button>
            </div>
            <p class="text-xs text-kde-text-dim mt-2">
                The current design is optimized for dark mode.
            </p>
        </div>

        <!-- About -->
        <div class="bg-kde-card border border-kde-border rounded-lg p-4">
            <h2 class="font-medium mb-4 flex items-center gap-2">About</h2>
            <p class="text-sm text-kde-text-dim mb-4 leading-relaxed">
                A modern web interface for KDE Connect, built with SvelteKit and
                Tailwind CSS. Manage your devices, send commands, and sync
                clipboard from your browser.
            </p>

            <div class="flex gap-2">
                <a
                    href="https://github.com/naisakh/kde-connect-webapp"
                    target="_blank"
                    class="flex items-center gap-2 text-xs bg-kde-bg hover:bg-kde-border px-3 py-1.5 rounded transition-colors"
                >
                    <Github size={14} /> GitHub
                </a>
                <div
                    class="flex items-center gap-2 text-xs bg-kde-bg px-3 py-1.5 rounded cursor-default"
                >
                    Made with <Heart size={12} class="text-kde-danger" />
                </div>
            </div>
        </div>
    </div>
</div>
