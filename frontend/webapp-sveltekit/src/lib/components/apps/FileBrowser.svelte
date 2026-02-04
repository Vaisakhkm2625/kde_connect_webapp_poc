<script lang="ts">
    import { Folder, File, Download, Upload, Settings } from "lucide-svelte";
    import { devicesApi, type Device } from "$lib/api/devices";
    import toast from "svelte-french-toast";

    let devices = $state<Device[]>([]);
    let selectedDeviceId = $state("");
    let currentPath = $state("~/Downloads/kdeconnect");
    let configMode = $state(false);

    // Mocks
    let files = [
        { name: "Document.pdf", type: "file", size: "2.4 MB" },
        { name: "Photos", type: "folder", size: "-" },
        { name: "Music", type: "folder", size: "-" },
        { name: "notes.txt", type: "file", size: "12 KB" },
    ];

    async function loadDeviceConfig() {
        // API doesn't allow reading config back easily without listing devices again
        // We assume devices list has path info
        const res = await devicesApi.list();
        devices = res.devices;
        if (selectedDeviceId) {
            const dev = devices.find((d) => d.identifier === selectedDeviceId);
            if (dev?.path) currentPath = dev.path;
        }
    }

    async function saveConfig() {
        if (!selectedDeviceId) return toast.error("Select a device");
        try {
            // apiRequest(`/share/${selectedDeviceId}`, 'PATCH', { path: currentPath })
            // Need to add this method to devicesApi or client
            // For now using fetch directly or extending api
            // ... assuming devicesApi extension or generic call
            // Let's assume we extended devicesApi or use client
            await fetch(`/api/share/${selectedDeviceId}`, {
                method: "PATCH",
                body: JSON.stringify({ path: currentPath }),
                headers: { "Content-Type": "application/json" },
            });
            toast.success("Receive path updated");
            configMode = false;
        } catch (e) {
            toast.error("Failed to update path");
        }
    }

    $effect(() => {
        loadDeviceConfig();
    });
</script>

<div class="h-full flex flex-col bg-kde-bg text-kde-text">
    <!-- Toolbar -->
    <div
        class="h-10 border-b border-kde-border flex items-center px-2 gap-2 bg-kde-card"
    >
        <button
            class="p-1.5 hover:bg-kde-border rounded text-kde-text-dim hover:text-kde-text {configMode
                ? 'bg-kde-border text-kde-text'
                : ''}"
            title="Configuration"
            on:click={() => (configMode = !configMode)}
        >
            <Settings size={18} />
        </button>
        <div class="h-4 w-px bg-kde-border mx-1"></div>
        <div
            class="flex-1 flex items-center gap-2 text-sm text-kde-text-dim px-2 bg-kde-bg border border-kde-border rounded h-7"
        >
            <Folder size={14} />
            <span>/ Home / Downloads</span>
        </div>
    </div>

    <div class="flex-1 flex overflow-hidden">
        <!-- Sidebar -->
        <div
            class="w-48 border-r border-kde-border p-2 bg-kde-card/50 flex flex-col gap-1 text-sm"
        >
            <div
                class="p-1.5 rounded hover:bg-kde-border cursor-pointer flex items-center gap-2 text-kde-blue font-medium bg-kde-blue/10"
            >
                <Folder size={16} /> Home
            </div>
            <div
                class="p-1.5 rounded hover:bg-kde-border cursor-pointer flex items-center gap-2 text-kde-text-dim"
            >
                <Download size={16} /> Downloads
            </div>
            <div class="mt-auto">
                <label class="block text-xs text-kde-text-dim mb-1 px-1"
                    >Device source</label
                >
                <select
                    bind:value={selectedDeviceId}
                    class="w-full bg-kde-bg border border-kde-border rounded text-xs p-1"
                >
                    <option value="">Select Device</option>
                    {#each devices as dev}
                        <option value={dev.identifier}>{dev.name}</option>
                    {/each}
                </select>
            </div>
        </div>

        <!-- Main Content -->
        <div class="flex-1 p-2 overflow-y-auto">
            {#if configMode}
                <div
                    class="max-w-md mx-auto mt-10 p-6 bg-kde-card border border-kde-border rounded-lg shadow-sm"
                >
                    <h3 class="font-medium text-lg mb-4">
                        Receive Files Configuration
                    </h3>
                    <p class="text-xs text-kde-text-dim mb-4">
                        Configure where files received from the selected device
                        should be saved on this server.
                    </p>

                    <label class="block text-sm mb-1">Target Device</label>
                    <select
                        bind:value={selectedDeviceId}
                        class="w-full bg-kde-bg border border-kde-border rounded p-2 mb-4 text-sm"
                    >
                        <option value="">-- Select Device --</option>
                        {#each devices as dev}
                            <option value={dev.identifier}>{dev.name}</option>
                        {/each}
                    </select>

                    <label class="block text-sm mb-1">Download Path</label>
                    <div class="flex gap-2">
                        <input
                            bind:value={currentPath}
                            type="text"
                            class="flex-1 bg-kde-bg border border-kde-border rounded p-2 text-sm"
                            placeholder="e.g. ~/Downloads"
                        />
                        <button
                            class="bg-kde-blue text-white px-4 rounded hover:bg-kde-blue/90"
                            on:click={saveConfig}>Save</button
                        >
                    </div>
                </div>
            {:else}
                <!-- File Grid Mock -->
                <div
                    class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2"
                >
                    {#each files as file}
                        <div
                            class="p-2 flex flex-col items-center gap-2 rounded hover:bg-kde-border/50 cursor-pointer border border-transparent hover:border-kde-border/30 group"
                        >
                            <div
                                class="w-12 h-12 flex items-center justify-center text-kde-text-dim group-hover:text-kde-blue transition-colors"
                            >
                                {#if file.type === "folder"}
                                    <Folder
                                        size={40}
                                        fill="currentColor"
                                        class="opacity-20"
                                    />
                                {:else}
                                    <File size={32} />
                                {/if}
                            </div>
                            <span class="text-xs text-center truncate w-full"
                                >{file.name}</span
                            >
                        </div>
                    {/each}
                </div>

                <div class="mt-8 text-center text-kde-text-dim text-sm italic">
                    (Remote file browsing is not supported by the current API)
                </div>
            {/if}
        </div>
    </div>
</div>
