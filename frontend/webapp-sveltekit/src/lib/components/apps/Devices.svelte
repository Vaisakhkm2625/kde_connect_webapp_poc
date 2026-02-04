<script lang="ts">
    import { onMount } from "svelte";
    import { RefreshCw } from "lucide-svelte";
    import { devicesApi, type Device } from "$lib/api/devices";
    import DeviceCard from "../widgets/DeviceCard.svelte";
    import toast from "svelte-french-toast";

    let devices = $state<Device[]>([]);
    let isLoading = $state(true);

    async function loadDevices() {
        try {
            const res = await devicesApi.list();
            devices = res.devices;
        } catch (e: any) {
            toast.error("Failed to load devices");
            console.error(e);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        loadDevices();
        const interval = setInterval(loadDevices, 5000); // Poll every 5s
        return () => clearInterval(interval);
    });
</script>

<div class="h-full flex flex-col p-2">
    <div class="flex items-center justify-between mb-4 px-2">
        <h2 class="text-lg font-semibold text-kde-text">Discovered Devices</h2>
        <button
            class="p-2 hover:bg-kde-border rounded-full transition-colors text-kde-text-dim hover:text-kde-text"
            on:click={loadDevices}
            title="Refresh"
        >
            <RefreshCw size={18} class={isLoading ? "animate-spin" : ""} />
        </button>
    </div>

    {#if isLoading && devices.length === 0}
        <div class="flex-1 flex items-center justify-center text-kde-text-dim">
            Loading devices...
        </div>
    {:else if devices.length === 0}
        <div
            class="flex-1 flex flex-col items-center justify-center text-kde-text-dim gap-2"
        >
            <span>No devices found</span>
            <button
                class="text-kde-blue hover:underline text-sm"
                on:click={loadDevices}>Retry</button
            >
        </div>
    {:else}
        <div
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 overflow-y-auto p-2"
        >
            {#each devices as device (device.identifier)}
                <DeviceCard {device} onUpdate={loadDevices} />
            {/each}
        </div>
    {/if}
</div>
