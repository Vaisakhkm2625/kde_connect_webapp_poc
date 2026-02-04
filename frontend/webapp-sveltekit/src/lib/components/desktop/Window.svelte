<script lang="ts">
    import { windowManager } from "$lib/stores/windows";
    import type { WindowState } from "$lib/stores/windows";
    import { X, Minus, Square, Maximize } from "lucide-svelte";

    export let window: WindowState;

    // Drag State
    let isDragging = false;
    let dragOffset = { x: 0, y: 0 };

    // Resize State
    let isResizing = false;
    let resizeStart = { x: 0, y: 0, width: 0, height: 0 };

    // Drag Handlers
    function handleMouseDown(e: MouseEvent) {
        if (window.maximized) return;
        // Only drag if left click
        if (e.button !== 0) return;

        windowManager.focus(window.id);
        isDragging = true;
        dragOffset = {
            x: e.clientX - window.x,
            y: e.clientY - window.y,
        };

        document.addEventListener("mousemove", handleMouseMove);
        document.addEventListener("mouseup", handleMouseUp);
    }

    function handleMouseMove(e: MouseEvent) {
        if (isDragging) {
            windowManager.move(
                window.id,
                e.clientX - dragOffset.x,
                e.clientY - dragOffset.y,
            );
        }
    }

    function handleMouseUp() {
        isDragging = false;
        document.removeEventListener("mousemove", handleMouseMove);
        document.removeEventListener("mouseup", handleMouseUp);
    }

    // Resize Handlers
    function startResize(e: MouseEvent) {
        if (window.maximized) return;
        e.stopPropagation(); // Prevent drag

        windowManager.focus(window.id);
        isResizing = true;
        resizeStart = {
            x: e.clientX,
            y: e.clientY,
            width: window.width,
            height: window.height,
        };

        document.addEventListener("mousemove", handleResizeMove);
        document.addEventListener("mouseup", handleResizeUp);
    }

    function handleResizeMove(e: MouseEvent) {
        if (isResizing) {
            const dx = e.clientX - resizeStart.x;
            const dy = e.clientY - resizeStart.y;
            windowManager.resize(
                window.id,
                resizeStart.width + dx,
                resizeStart.height + dy,
            );
        }
    }

    function handleResizeUp() {
        isResizing = false;
        document.removeEventListener("mousemove", handleResizeMove);
        document.removeEventListener("mouseup", handleResizeUp);
    }
</script>

<!-- svelte-ignore a11y-click-events-have-key-events -->
<div
    class="absolute flex flex-col bg-kde-card border border-kde-border rounded-lg shadow-window overflow-hidden transition-all duration-75 ease-out outline-none"
    class:ring-1={!window.maximized}
    class:ring-kde-border={!window.maximized}
    style="
    left: {window.maximized ? 0 : window.x}px;
    top: {window.maximized ? 0 : window.y}px;
    width: {window.maximized ? '100%' : window.width + 'px'};
    height: {window.maximized ? '100%' : window.height + 'px'};
    z-index: {window.zIndex};
    display: {window.minimized ? 'none' : 'flex'};
  "
    on:mousedown={() => windowManager.focus(window.id)}
>
    <!-- Title Bar -->
    <div
        class="h-8 bg-kde-bg border-b border-kde-border flex items-center justify-between px-2 select-none cursor-default shrink-0"
        on:mousedown={handleMouseDown}
        on:dblclick={() => windowManager.maximize(window.id)}
    >
        <div class="flex items-center gap-2 overflow-hidden">
            {#if window.icon}
                <img src={window.icon} alt="" class="w-4 h-4" />
            {/if}
            <span class="text-xs font-semibold text-kde-text truncate"
                >{window.title}</span
            >
        </div>
        <div class="flex items-center gap-1 shrink-0">
            <button
                class="p-1 hover:bg-kde-border rounded"
                on:click|stopPropagation={() =>
                    windowManager.minimize(window.id)}
            >
                <Minus size={12} />
            </button>
            <button
                class="p-1 hover:bg-kde-border rounded"
                on:click|stopPropagation={() =>
                    windowManager.maximize(window.id)}
            >
                {#if window.maximized}
                    <div class="rotate-180"><Maximize size={12} /></div>
                {:else}
                    <Square size={12} />
                {/if}
            </button>
            <button
                class="p-1 hover:bg-kde-danger hover:text-white rounded"
                on:click|stopPropagation={() => windowManager.close(window.id)}
            >
                <X size={12} />
            </button>
        </div>
    </div>

    <!-- Content -->
    <div class="flex-1 overflow-hidden bg-kde-card text-kde-text relative">
        <slot />
    </div>

    <!-- Resize Handle -->
    {#if !window.maximized}
        <div
            class="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize z-50 hover:bg-kde-blue/20 rounded-br-lg"
            on:mousedown={startResize}
        >
            <svg
                width="100%"
                height="100%"
                viewBox="0 0 16 16"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                class="text-kde-border"
            >
                <path
                    d="M12 12L12 4"
                    stroke="currentColor"
                    stroke-width="1"
                    stroke-linecap="round"
                />
                <path
                    d="M12 12L4 12"
                    stroke="currentColor"
                    stroke-width="1"
                    stroke-linecap="round"
                />
                <path
                    d="M8 12L12 8"
                    stroke="currentColor"
                    stroke-width="1"
                    stroke-linecap="round"
                />
            </svg>
        </div>
    {/if}
</div>
