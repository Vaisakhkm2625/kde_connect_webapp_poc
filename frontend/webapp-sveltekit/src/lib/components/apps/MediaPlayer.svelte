<script lang="ts">
    import {
        Play,
        Pause,
        SkipBack,
        SkipForward,
        Volume2,
        Volume1,
        VolumeX,
    } from "lucide-svelte";
    import { apiRequest } from "$lib/api/client";
    import { devicesApi, type Device } from "$lib/api/devices";
    import { onMount } from "svelte";
    import toast from "svelte-french-toast";

    let devices = $state<Device[]>([]);
    let selectedDeviceId = $state("");

    // Mock State
    let isPlaying = $state(false);
    let trackTitle = "Unknown Track";
    let trackArtist = "Unknown Artist";

    onMount(async () => {
        const res = await devicesApi.list();
        devices = res.devices;
        if (devices.length) selectedDeviceId = devices[0].identifier;
    });

    async function sendAction(action: string) {
        if (!selectedDeviceId) return;

        // Packet type: kdeconnect.multimedia.request (or generic action?)
        // Usually control packet: type "kdeconnect.multimedia.request" ?
        // No, looking at protocols, it's "kdeconnect.multimedia.request" with body: { action: "play" } etc.
        // But let's check standard. "kdeconnect.multimedia" is for status updates from device.
        // "kdeconnect.multimedia.request" is to Control.

        try {
            await apiRequest(`/custom/${selectedDeviceId}`, "POST", {
                type: "kdeconnect.multimedia.request",
                body: { action },
            });

            if (action === "play") isPlaying = true;
            if (action === "pause") isPlaying = false;
            if (action === "playPause") isPlaying = !isPlaying;

            toast.success(`Sent: ${action}`);
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    /* 
     Actions: play, pause, playPause, next, previous, volume (setVolume: int)
  */
</script>

<div
    class="h-full flex flex-col bg-kde-card text-kde-text items-center justify-center p-6 gap-6"
>
    <select
        bind:value={selectedDeviceId}
        class="absolute top-4 right-4 bg-kde-bg border border-kde-border rounded p-1 text-xs"
    >
        {#each devices as dev}
            <option value={dev.identifier}>{dev.name}</option>
        {/each}
    </select>

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
            on:click={() => sendAction("previous")}
        >
            <SkipBack size={24} />
        </button>

        <button
            class="w-16 h-16 rounded-full bg-kde-blue hover:bg-kde-blue/90 text-white flex items-center justify-center shadow-lg transition-transform active:scale-95"
            on:click={() => sendAction("playPause")}
        >
            {#if isPlaying}
                <Pause size={28} fill="currentColor" />
            {:else}
                <Play size={28} fill="currentColor" class="ml-1" />
            {/if}
        </button>

        <button
            class="p-2 hover:text-kde-blue transition-colors"
            on:click={() => sendAction("next")}
        >
            <SkipForward size={24} />
        </button>
    </div>

    <div class="text-xs text-kde-text-dim mt-4">
        (Note: One-way control. Metadata update requires backend push events)
    </div>
</div>
