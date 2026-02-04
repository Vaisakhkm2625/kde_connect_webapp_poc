<script lang="ts">
    import { windowManager } from "$lib/stores/windows";
    import Window from "./Window.svelte";
    import Taskbar from "./Taskbar.svelte";
    import NotificationCenter from "./NotificationCenter.svelte";

    // App Components Registry
    import Devices from "../apps/Devices.svelte";
    import Settings from "../apps/Settings.svelte";
    import Notifications from "../apps/Notifications.svelte";
    import Commands from "../apps/Commands.svelte";
    import FileBrowser from "../apps/FileBrowser.svelte";
    import Camera from "../apps/Camera.svelte";
    import Clipboard from "../apps/Clipboard.svelte";
    import MediaPlayer from "../apps/MediaPlayer.svelte";

    const COMPONENT_MAP: Record<string, any> = {
        Devices: Devices,
        Settings: Settings,
        Notifications: Notifications,
        Commands: Commands,
        FileBrowser: FileBrowser,
        Camera: Camera,
        Clipboard: Clipboard,
        MediaPlayer: MediaPlayer,
    };

    import type { WindowState } from "$lib/stores/windows";

    let windows = $state<WindowState[]>([]);
    let isNotificationCenterOpen = $state(false);

    $effect(() => {
        const unsub = windowManager.subscribe((val) => {
            windows = val;
        });
        return unsub;
    });

    function toggleNotificationCenter() {
        isNotificationCenterOpen = !isNotificationCenterOpen;
    }
</script>

<div
    class="relative w-full h-full bg-gradient-to-br from-kde-bg to-[#15181a] overflow-hidden select-none"
>
    <!-- Desktop Area -->
    <div
        class="absolute inset-0 z-0"
        on:mousedown={() => {
            /* clear focus */
        }}
    >
        <!-- Abstract Pattern Background -->
        <svg
            class="absolute inset-0 w-full h-full opacity-10"
            xmlns="http://www.w3.org/2000/svg"
        >
            <defs>
                <pattern
                    id="grid"
                    width="40"
                    height="40"
                    patternUnits="userSpaceOnUse"
                >
                    <path
                        d="M 40 0 L 0 0 0 40"
                        fill="none"
                        stroke="white"
                        stroke-width="0.5"
                    />
                </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
    </div>

    <!-- Window Layer -->
    <div class="absolute inset-0 z-10 pointer-events-none">
        {#each windows as win (win.id)}
            <div class="pointer-events-auto contents">
                <Window window={win}>
                    {@const Comp = COMPONENT_MAP[win.component]}
                    {#if Comp}
                        <Comp {...win.props} />
                    {:else}
                        <div class="p-4 text-red-400">
                            Component '{win.component}' not found
                        </div>
                    {/if}
                </Window>
            </div>
        {/each}
    </div>

    <!-- Panels Layer -->
    <NotificationCenter
        isOpen={isNotificationCenterOpen}
        onClose={() => (isNotificationCenterOpen = false)}
    />

    <!-- Taskbar -->
    <Taskbar {toggleNotificationCenter} />
</div>
