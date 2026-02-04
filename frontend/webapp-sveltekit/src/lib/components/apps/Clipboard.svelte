<script lang="ts">
    import { Clipboard, Copy, Send } from "lucide-svelte";
    import { apiRequest } from "$lib/api/client";
    import { devicesApi, type Device } from "$lib/api/devices";
    import toast from "svelte-french-toast";
    import { onMount } from "svelte";

    let clipboardContent = $state("");
    let devices = $state<Device[]>([]);
    let selectedDeviceId = $state("");

    onMount(async () => {
        try {
            const res = await devicesApi.list();
            devices = res.devices;
            if (devices.length > 0) selectedDeviceId = devices[0].identifier;
        } catch (e) {
            console.error(e);
        }
    });

    async function sendClipboard() {
        if (!selectedDeviceId) return toast.error("Select a device");
        if (!clipboardContent) return toast.error("Content empty");

        try {
            // Packet type: kdeconnect.clipboard
            // Body: { content: "..." }
            await apiRequest(`/custom/${selectedDeviceId}`, "POST", {
                type: "kdeconnect.clipboard",
                body: { content: clipboardContent },
            });
            toast.success("Clipboard sent");
        } catch (e: any) {
            toast.error("Failed to send: " + e.message);
        }
    }

    async function pasteFromBrowser() {
        try {
            const text = await navigator.clipboard.readText();
            clipboardContent = text;
        } catch (e) {
            toast.error("Could not read clipboard permission");
        }
    }
</script>

<div class="h-full flex flex-col bg-kde-bg p-4 text-kde-text gap-4">
    <div class="flex items-center gap-2 mb-2">
        <Clipboard size={20} class="text-kde-blue" />
        <h2 class="font-medium">Clipboard Sync</h2>
    </div>

    <div class="flex flex-col gap-2">
        <label class="text-xs text-kde-text-dim">Target Device</label>
        <select
            bind:value={selectedDeviceId}
            class="bg-kde-card border border-kde-border rounded p-2 text-sm"
        >
            {#each devices as dev}
                <option value={dev.identifier}>{dev.name}</option>
            {/each}
        </select>
    </div>

    <div class="flex-1 flex flex-col gap-2">
        <label class="text-xs text-kde-text-dim flex justify-between">
            Content
            <button
                class="text-kde-blue hover:text-white flex items-center gap-1"
                on:click={pasteFromBrowser}
            >
                <Copy size={12} /> Paste from System
            </button>
        </label>
        <textarea
            bind:value={clipboardContent}
            class="flex-1 bg-kde-card border border-kde-border rounded p-3 font-mono text-sm resize-none focus:border-kde-blue focus:outline-none"
            placeholder="Paste text here to send..."
        ></textarea>
    </div>

    <button
        class="w-full py-2 bg-kde-blue hover:bg-kde-blue/90 text-white rounded font-medium flex items-center justify-center gap-2"
        on:click={sendClipboard}
    >
        <Send size={16} /> Send to Device
    </button>
</div>
