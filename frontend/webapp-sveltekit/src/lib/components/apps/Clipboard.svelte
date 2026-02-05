<script lang="ts">
    import { Clipboard, Copy, Send } from "lucide-svelte";
    import { mockApi } from "$lib/api/mock";
    import toast from "svelte-french-toast";
    import { onMount } from "svelte";

    let clipboardContent = $state("");

    // We don't need device lists for the mock system integration
    // let devices = $state<Device[]>([]);
    // let selectedDeviceId = $state("");

    onMount(async () => {
        try {
            // Initial fetch
            const res = await mockApi.getClipboard();
            if (res.content) clipboardContent = res.content;
        } catch (e) {
            console.error(e);
        }
    });

    async function sendClipboard() {
        if (!clipboardContent) return toast.error("Content empty");

        try {
            await mockApi.setClipboard(clipboardContent);
            toast.success("Clipboard sent to System");
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
        <h2 class="font-medium">System Clipboard</h2>
    </div>

    <!-- Device selector removed -->

    <div class="flex-1 flex flex-col gap-2">
        <label class="text-xs text-kde-text-dim flex justify-between">
            Content
            <button
                class="text-kde-blue hover:text-white flex items-center gap-1"
                onclick={pasteFromBrowser}
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
        onclick={sendClipboard}
    >
        <Send size={16} /> Set System Clipboard
    </button>
</div>
