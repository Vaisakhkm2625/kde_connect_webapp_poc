<script lang="ts">
    import {
        Smartphone,
        Monitor,
        Tablet,
        Watch,
        Laptop,
        Wifi,
        WifiOff,
    } from "lucide-svelte";
    import type { Device } from "$lib/api/devices";
    import { devicesApi } from "$lib/api/devices";
    import toast from "svelte-french-toast";

    export let device: Device;
    export let onUpdate: () => void;

    let isLoading = false;

    async function handlePair() {
        isLoading = true;
        try {
            await devicesApi.pair(device.identifier);
            toast.success("Pairing request sent");
            onUpdate();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            isLoading = false;
        }
    }

    async function handleUnpair() {
        if (!confirm(`Unpair ${device.name}?`)) return;
        isLoading = true;
        try {
            await devicesApi.unpair(device.identifier);
            toast.success("Device unpaired");
            onUpdate();
        } catch (e: any) {
            toast.error(e.message);
        } finally {
            isLoading = false;
        }
    }

    async function handlePing() {
        try {
            await devicesApi.ping(device.identifier);
            toast.success("Ping sent");
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    async function handleRing() {
        try {
            await devicesApi.ring(device.identifier);
            toast.success("Ring request sent");
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    function getIcon(type: string) {
        switch (type.toLowerCase()) {
            case "desktop":
                return Monitor;
            case "laptop":
                return Laptop;
            case "tablet":
                return Tablet;
            case "watch":
                return Watch;
            default:
                return Smartphone;
        }
    }
</script>

<div
    class="bg-kde-bg border border-kde-border rounded-lg p-4 flex flex-col gap-3 hover:border-kde-blue/50 transition-colors group"
>
    <div class="flex items-start justify-between">
        <div class="flex items-center gap-3">
            <div
                class="w-10 h-10 bg-kde-card rounded-full flex items-center justify-center text-kde-blue"
            >
                <svelte:component this={getIcon(device.type)} size={20} />
            </div>
            <div>
                <h3 class="font-medium text-kde-text">{device.name}</h3>
                <p class="text-xs text-kde-text-dim flex items-center gap-1">
                    {#if device.reachable}
                        <Wifi size={12} class="text-kde-success" /> Online
                    {:else}
                        <WifiOff size={12} class="text-kde-danger" /> Offline
                    {/if}
                </p>
            </div>
        </div>

        <div
            class="px-2 py-0.5 rounded text-[10px] font-medium border
       {device.trusted
                ? 'border-kde-success/30 text-kde-success bg-kde-success/10'
                : 'border-kde-warning/30 text-kde-warning bg-kde-warning/10'}"
        >
            {device.trusted ? "Paired" : "Not Paired"}
        </div>
    </div>

    <div class="flex items-center gap-2 mt-auto pt-2">
        {#if device.trusted}
            <button
                class="flex-1 py-1.5 text-xs bg-kde-card hover:bg-kde-border border border-kde-border rounded transition-colors"
                disabled={!device.reachable}
                on:click={handlePing}
            >
                Ping
            </button>
            <button
                class="flex-1 py-1.5 text-xs bg-kde-card hover:bg-kde-border border border-kde-border rounded transition-colors"
                disabled={!device.reachable}
                on:click={handleRing}
            >
                Ring
            </button>
            <button
                class="px-3 py-1.5 text-xs bg-kde-danger/10 hover:bg-kde-danger text-kde-danger hover:text-white border border-kde-danger/20 rounded transition-colors"
                on:click={handleUnpair}
            >
                Unpair
            </button>
        {:else}
            <button
                class="w-full py-1.5 text-xs bg-kde-blue hover:bg-kde-blue/90 text-white rounded transition-colors font-medium"
                on:click={handlePair}
            >
                Request Pair
            </button>
        {/if}
    </div>
</div>
