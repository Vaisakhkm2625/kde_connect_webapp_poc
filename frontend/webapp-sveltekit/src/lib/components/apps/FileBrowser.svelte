<script lang="ts">
    import {
        Folder,
        File,
        Download,
        Upload,
        Settings,
        ArrowLeft,
        RefreshCw,
    } from "lucide-svelte";
    import { devicesApi, type Device } from "$lib/api/devices";
    import toast from "svelte-french-toast";
    import { onMount } from "svelte";

    let { deviceId, initialPath = "/" } = $props<{
        deviceId: string;
        initialPath?: string;
    }>();

    let files = $state<any[]>([]);
    let currentPath = $state(initialPath);
    let isLoading = $state(false);
    let error = $state<string | null>(null);
    let isConnected = $state(false);

    async function initSftp() {
        isLoading = true;
        error = null;
        try {
            await devicesApi.sftpStart(deviceId);
            isConnected = true;
            await loadFiles(currentPath);
        } catch (e: any) {
            console.error(e);
            error =
                "Failed to establish SFTP connection. Ensure the device is reachable.";
            toast.error(error);
        } finally {
            isLoading = false;
        }
    }

    async function loadFiles(path: string) {
        isLoading = true;
        error = null;
        try {
            const res = await devicesApi.sftpBrowse(deviceId, path);
            files = res.files.sort((a, b) => {
                if (a.isDirectory === b.isDirectory)
                    return a.name.localeCompare(b.name);
                return a.isDirectory ? -1 : 1;
            });
            currentPath = res.path;
        } catch (e: any) {
            console.error(e);
            error = "Failed to load files.";
            toast.error(error);
        } finally {
            isLoading = false;
        }
    }

    function handleFileClick(file: any) {
        if (file.isDirectory) {
            const newPath =
                currentPath === "/"
                    ? `/${file.name}`
                    : `${currentPath}/${file.name}`;
            loadFiles(newPath);
        } else {
            toast("File downloading not implemented yet", { icon: "ℹ️" });
        }
    }

    function handleUp() {
        if (currentPath === "/") return;
        const parent = currentPath.substring(0, currentPath.lastIndexOf("/"));
        loadFiles(parent || "/");
    }

    onMount(() => {
        if (deviceId) {
            initSftp();
        } else {
            error = "No device specified";
        }
    });

    function formatSize(bytes: number) {
        if (bytes === 0) return "0 B";
        const k = 1024;
        const sizes = ["B", "KB", "MB", "GB", "TB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }
</script>

<div class="h-full flex flex-col bg-kde-bg text-kde-text">
    <!-- Toolbar -->
    <div
        class="h-10 border-b border-kde-border flex items-center px-2 gap-2 bg-kde-card"
    >
        <button
            class="p-1.5 hover:bg-kde-border rounded text-kde-text-dim hover:text-kde-text"
            title="Up"
            onclick={handleUp}
            disabled={currentPath === "/"}
        >
            <ArrowLeft size={18} />
        </button>
        <button
            class="p-1.5 hover:bg-kde-border rounded text-kde-text-dim hover:text-kde-text"
            title="Refresh"
            onclick={() => loadFiles(currentPath)}
        >
            <RefreshCw size={18} class={isLoading ? "animate-spin" : ""} />
        </button>

        <div class="h-4 w-px bg-kde-border mx-1"></div>

        <div
            class="flex-1 flex items-center gap-2 text-sm text-kde-text-dim px-2 bg-kde-bg border border-kde-border rounded h-7 overflow-hidden whitespace-nowrap"
        >
            <Folder size={14} />
            <span class="truncate">{currentPath}</span>
        </div>
    </div>

    <div class="flex-1 flex overflow-hidden">
        <!-- Main Content -->
        <div class="flex-1 p-2 overflow-y-auto">
            {#if error}
                <div
                    class="flex flex-col items-center justify-center h-full text-kde-danger gap-2"
                >
                    <span>{error}</span>
                    <button
                        class="px-3 py-1 bg-kde-card border border-kde-border rounded hover:bg-kde-border text-kde-text"
                        onclick={initSftp}>Retry Connection</button
                    >
                </div>
            {:else if isLoading && files.length === 0}
                <div
                    class="flex flex-col items-center justify-center h-full text-kde-text-dim"
                >
                    Loading...
                </div>
            {:else if files.length === 0}
                <div
                    class="flex flex-col items-center justify-center h-full text-kde-text-dim"
                >
                    Empty folder
                </div>
            {:else}
                <div
                    class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2"
                >
                    {#each files as file}
                        <div
                            class="p-2 flex flex-col items-center gap-2 rounded hover:bg-kde-border/50 cursor-pointer border border-transparent hover:border-kde-border/30 group outline-none focus:bg-kde-border/50"
                            role="button"
                            tabindex="0"
                            onclick={() => handleFileClick(file)}
                            onkeydown={(e) =>
                                e.key === "Enter" && handleFileClick(file)}
                            title={file.name}
                        >
                            <div
                                class="w-12 h-12 flex items-center justify-center text-kde-text-dim group-hover:text-kde-blue transition-colors"
                            >
                                {#if file.isDirectory}
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
                            {#if !file.isDirectory}
                                <span class="text-[10px] text-kde-text-dim"
                                    >{formatSize(file.size)}</span
                                >
                            {/if}
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>
</div>
