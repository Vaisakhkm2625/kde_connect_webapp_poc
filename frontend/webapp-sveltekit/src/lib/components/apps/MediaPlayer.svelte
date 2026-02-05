<script lang="ts">
    import { Play, Pause, SkipBack, SkipForward, Volume2 } from "lucide-svelte";
    import { mockApi } from "$lib/api/mock";
    import { onMount } from "svelte";
    import toast from "svelte-french-toast";

    // Mock State
    let isPlaying = $state(false);
    let trackTitle = $state("Unknown Track");
    let trackArtist = $state("Unknown Artist");

    async function updateStatus() {
        try {
            const status = await mockApi.getMediaStatus();
            if (status.status) {
                isPlaying = status.status === "Playing";
                trackTitle = status.title || "Unknown Track";
                trackArtist = status.artist || "Unknown Artist";
            }
        } catch (e) {
            console.error(e);
        }
    }

    onMount(() => {
        updateStatus();
        const interval = setInterval(updateStatus, 2000); // Poll status every 2s
        return () => clearInterval(interval);
    });

    async function sendAction(action: "play_pause" | "next" | "previous") {
        try {
            await mockApi.controlMedia(action);
            // Optimistic update
            if (action === "play_pause") isPlaying = !isPlaying;
            setTimeout(updateStatus, 500); // Fetch real status shortly after
        } catch (e: any) {
            toast.error(e.message);
        }
    }
</script>

<div
    class="h-full flex flex-col bg-kde-card text-kde-text items-center justify-center p-6 gap-6"
>
    <!-- Album Art Placeholder -->
    <div
        class="w-48 h-48 bg-kde-bg rounded-lg shadow-lg flex items-center justify-center border border-kde-border"
    >
        <Volume2 size={48} class="text-kde-text-dim opacity-20" />
    </div>

    <!-- Info -->
    <div class="text-center">
        <h2 class="text-xl font-bold">{trackTitle}</h2>
        <p class="text-kde-text-dim">{trackArtist}</p>
    </div>

    <!-- Controls -->
    <div class="flex items-center gap-6">
        <button
            class="p-2 hover:text-kde-blue transition-colors"
            onclick={() => sendAction("previous")}
        >
            <SkipBack size={24} />
        </button>

        <button
            class="w-16 h-16 rounded-full bg-kde-blue hover:bg-kde-blue/90 text-white flex items-center justify-center shadow-lg transition-transform active:scale-95"
            onclick={() => sendAction("play_pause")}
        >
            {#if isPlaying}
                <Pause size={28} fill="currentColor" />
            {:else}
                <Play size={28} fill="currentColor" class="ml-1" />
            {/if}
        </button>

        <button
            class="p-2 hover:text-kde-blue transition-colors"
            onclick={() => sendAction("next")}
        >
            <SkipForward size={24} />
        </button>
    </div>

    <div class="text-xs text-kde-text-dim mt-4">
        (Controls System Media via DBus)
    </div>
</div>
