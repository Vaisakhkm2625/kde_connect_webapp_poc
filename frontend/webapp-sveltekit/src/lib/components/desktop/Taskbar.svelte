<script lang="ts">
    import { windowManager } from "$lib/stores/windows";
    import { APPS } from "$lib/utils/constants";
    import {
        AppWindow,
        Settings,
        Smartphone,
        Bell,
        Terminal,
        FileText,
        Camera,
        Clipboard,
        Volume2,
    } from "lucide-svelte";
    import SystemTray from "./SystemTray.svelte";

    // Props
    let { toggleNotificationCenter } = $props();

    // Pinned apps configuration
    const PINNED_APPS = [
        { id: APPS.DEVICES, icon: Smartphone, component: "Devices" },
        { id: APPS.NOTIFICATIONS, icon: Bell, component: "Notifications" },
        { id: APPS.COMMANDS, icon: Terminal, component: "Commands" },
        { id: APPS.FILES, icon: FileText, component: "FileBrowser" },
        { id: APPS.CAMERA, icon: Camera, component: "Camera" },
        { id: APPS.CLIPBOARD, icon: Clipboard, component: "Clipboard" },
        { id: APPS.MEDIA, icon: Volume2, component: "MediaPlayer" },
        { id: APPS.SETTINGS, icon: Settings, component: "Settings" },
    ];

    /* 
     We need to subscribe to windowManager to know which apps are running.
     Since we iterate pinned apps separately, we check if they are open.
  */
    let openWindows = $state([]);

    $effect(() => {
        const unsub = windowManager.subscribe((val) => {
            openWindows = val;
        });
        return unsub;
    });

    function isOpen(appId: string) {
        return openWindows.some((w) => w.id === appId);
    }

    function launchApp(app: (typeof PINNED_APPS)[0]) {
        if (isOpen(app.id)) {
            const win = openWindows.find((w) => w.id === app.id);
            if (win?.minimized) {
                windowManager.focus(app.id);
            } else {
                windowManager.focus(app.id);
            }
        } else {
            windowManager.open(app.id, app.id, app.component);
        }
    }
</script>

<div
    class="h-12 bg-kde-card/90 backdrop-blur-md border-t border-kde-border absolute bottom-0 w-full flex items-center justify-between px-4 shadow-taskbar z-[1000]"
>
    <!-- Start Button / App Launcher -->
    <div class="flex items-center gap-4">
        <button
            class="p-2 hover:bg-white/10 rounded transition-colors text-kde-blue"
        >
            <AppWindow size={24} />
        </button>

        <!-- Pinned / Running Apps -->
        <div class="flex items-center gap-2">
            {#each PINNED_APPS as app}
                {@const isActive = isOpen(app.id)}
                <button
                    class="relative p-2 rounded transition-all duration-200 group flex items-center justify-center
                 {isActive ? 'bg-white/10' : 'hover:bg-white/5'}"
                    on:click={() => launchApp(app)}
                    title={app.id}
                >
                    <svelte:component
                        this={app.icon}
                        size={20}
                        class={isActive ? "text-kde-blue" : "text-kde-text"}
                    />

                    {#if isActive}
                        <span
                            class="absolute -bottom-1 w-1 h-1 bg-kde-blue rounded-full"
                        ></span>
                    {/if}
                </button>
            {/each}
        </div>
    </div>

    <!-- System Tray Area -->
    <div class="flex items-center h-full">
        <button
            class="h-full flex items-center px-1 hover:bg-white/5 rounded transition-colors focus:outline-none"
            on:click={toggleNotificationCenter}
        >
            <SystemTray />
        </button>
    </div>
</div>
