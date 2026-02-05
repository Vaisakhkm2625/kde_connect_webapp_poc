<script lang="ts">
    import {
        Folder,
        File,
        Download,
        Upload,
        Settings,
        ArrowLeft,
        RefreshCw,
        X,
        Eye,
        EyeOff,
    } from "lucide-svelte";
    import { mockApi } from "$lib/api/mock";
    import toast from "svelte-french-toast";
    import { onMount } from "svelte";

    let { deviceId, initialPath = "/" } = $props<{
        deviceId?: string;
        initialPath?: string;
    }>();

    let files = $state<any[]>([]);
    let currentPath = $state(initialPath);
    let isLoading = $state(false);
    let error = $state<string | null>(null);

    let showHidden = $state(false);
    let visibleFiles = $derived(
        files.filter((f) => showHidden || !f.name.startsWith(".")),
    );

    async function loadFiles(path: string) {
        isLoading = true;
        error = null;
        try {
            console.log("Loading files from:", path);
            const res = await mockApi.getFiles(path);
            files = res.items.sort((a: any, b: any) => {
                const aDir = a.type === "directory";
                const bDir = b.type === "directory";
                if (aDir === bDir) return a.name.localeCompare(b.name);
                return aDir ? -1 : 1;
            });
            currentPath = res.current_path;
        } catch (e: any) {
            console.error(e);
            error = "Failed to load files: " + e.message;
            toast.error(error);
        } finally {
            isLoading = false;
        }
    }

    onMount(() => {
        loadFiles(initialPath);
    });

    // State for image preview
    let previewUrl = $state<string | null>(null);
    let previewName = $state<string>("");

    function isImage(filename: string) {
        const ext = filename.split(".").pop()?.toLowerCase();
        return ["jpg", "jpeg", "png", "gif", "webp", "svg"].includes(ext || "");
    }

    // Keeping these functions compatible
    function handleFileClick(file: any) {
        if (file.type === "directory") {
            loadFiles(file.path);
        } else {
            if (isImage(file.name)) {
                previewName = file.name;
                previewUrl = mockApi.getFileUrl(file.path);
            } else {
                // Trigger download
                const url = mockApi.getFileUrl(file.path);
                window.open(url, "_blank");
            }
        }
    }

    function closePreview() {
        previewUrl = null;
        previewName = "";
    }

    function handleUp() {
        if (
            currentPath === "/" ||
            currentPath === "/home" ||
            currentPath === ""
        ) {
            // Simple prevention of going too far up if desired, valid path usually starts with /
            // Let's just try to go to parent.
        }
        // Basic parent resolution
        const parent = currentPath.split("/").slice(0, -1).join("/") || "/";
        loadFiles(parent);
    }

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
        <button
            class="p-1.5 hover:bg-kde-border rounded text-kde-text-dim hover:text-kde-text"
            title={showHidden ? "Hide Hidden Files" : "Show Hidden Files"}
            onclick={() => (showHidden = !showHidden)}
        >
            {#if showHidden}
                <Eye size={18} />
            {:else}
                <EyeOff size={18} />
            {/if}
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
                        onclick={() => loadFiles(currentPath)}
                        >Retry Connection</button
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
                    {#each visibleFiles as file}
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
                                {#if file.type === "directory"}
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
                            {#if file.type !== "directory"}
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

    {#if previewUrl}
        <div
            class="absolute inset-0 z-50 bg-black/80 flex items-center justify-center p-4"
            role="dialog"
            tabindex="-1"
            onclick={closePreview}
            onkeydown={(e) => e.key === "Escape" && closePreview()}
        >
            <button
                class="absolute top-4 right-4 text-white hover:text-red-400"
                onclick={closePreview}
            >
                <X size={24} />
            </button>
            <div
                class="relative max-w-full max-h-full flex flex-col items-center"
            >
                <img
                    src={previewUrl}
                    alt={previewName}
                    class="max-w-full max-h-[80vh] object-contain rounded shadow-lg"
                    onclick={(e) => e.stopPropagation()}
                />
                <div class="mt-4 flex gap-4">
                    <button
                        class="px-4 py-2 bg-kde-card text-kde-text rounded hover:bg-kde-border flex items-center gap-2"
                        onclick={(e) => {
                            e.stopPropagation();
                            if (previewUrl) window.open(previewUrl, "_blank");
                        }}
                    >
                        <Download size={16} /> Download
                    </button>
                </div>
            </div>
        </div>
    {/if}
</div>
