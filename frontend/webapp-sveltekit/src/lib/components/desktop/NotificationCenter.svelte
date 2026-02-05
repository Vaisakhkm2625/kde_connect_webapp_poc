<script lang="ts">
    import { X, BellOff, Bell } from "lucide-svelte";
    import { fly } from "svelte/transition";
    import { onMount } from "svelte";
    import { MOCK_API_BASE } from "$lib/api/mock";
    import toast from "svelte-french-toast";

    let { isOpen = false, onClose } = $props<{
        isOpen?: boolean;
        onClose: () => void;
    }>();

    interface Notification {
        id: number;
        title: string;
        app: string;
        text: string;
        time: string;
    }

    let notifications = $state<Notification[]>([]);

    function clearAll() {
        notifications = [];
    }

    function removeNotification(id: number) {
        notifications = notifications.filter((n) => n.id !== id);
    }

    onMount(() => {
        console.log("Connecting to Notification Stream...");
        const evtSource = new EventSource(
            `${MOCK_API_BASE}/notifications/stream`,
        );

        evtSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("New Notification:", data);

                const newNotif: Notification = {
                    id: Date.now(),
                    title: data.title || "Notification",
                    app: data.appName || "System",
                    text: data.body || "",
                    time: "Just now",
                };

                notifications = [newNotif, ...notifications];

                // Also show a toast for immediate feedback
                toast(data.title + (data.body ? ": " + data.body : ""), {
                    icon: "🔔",
                    position: "top-right",
                });
            } catch (e) {
                console.error("Error parsing notification:", e);
            }
        };

        evtSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            // Reconnection is usually automatic for EventSource, but maybe log it.
        };

        return () => {
            evtSource.close();
        };
    });
</script>

{#if isOpen}
    <div
        class="absolute top-2 right-2 bottom-12 w-80 bg-kde-card/95 backdrop-blur-xl border border-kde-border shadow-window rounded-xl z-[900] flex flex-col overflow-hidden"
        transition:fly={{ x: 300, duration: 300 }}
    >
        <!-- Header -->
        <div
            class="p-4 border-b border-kde-border flex items-center justify-between"
        >
            <h3 class="font-semibold text-kde-text">Notifications</h3>
            <div class="flex items-center gap-1">
                <button
                    class="p-1.5 hover:bg-kde-border rounded-md text-kde-text-dim hover:text-kde-text transition-colors"
                    title="Do Not Disturb"
                >
                    <BellOff size={16} />
                </button>
                <button
                    class="p-1.5 hover:bg-kde-border rounded-md text-kde-text-dim hover:text-kde-text transition-colors"
                    title="Close"
                    onclick={onClose}
                >
                    <X size={16} />
                </button>
            </div>
        </div>

        <!-- Content -->
        <div class="flex-1 overflow-y-auto p-2 space-y-2">
            {#if notifications.length === 0}
                <div
                    class="h-full flex flex-col items-center justify-center text-kde-text-dim gap-2 opacity-50"
                >
                    <Bell size={32} />
                    <span>No new notifications</span>
                </div>
            {:else}
                {#each notifications as notif (notif.id)}
                    <div
                        class="bg-kde-bg/50 border border-kde-border rounded-lg p-3 relative group hover:bg-kde-bg transition-colors"
                    >
                        <div class="flex items-center gap-2 mb-1">
                            <div
                                class="w-4 h-4 bg-kde-blue rounded-full flex items-center justify-center text-[10px] text-white font-bold"
                            >
                                {notif.app[0]}
                            </div>
                            <span class="text-xs text-kde-text-dim font-medium"
                                >{notif.app}</span
                            >
                            <span class="text-[10px] text-kde-text-dim ml-auto"
                                >{notif.time}</span
                            >
                        </div>
                        <h4 class="text-sm font-medium text-kde-text mb-0.5">
                            {notif.title}
                        </h4>
                        <p class="text-xs text-kde-text-dim leading-relaxed">
                            {notif.text}
                        </p>

                        <button
                            class="absolute top-2 right-2 p-1 text-kde-text-dim opacity-0 group-hover:opacity-100 hover:text-kde-danger transition-all"
                            onclick={() => removeNotification(notif.id)}
                        >
                            <X size={12} />
                        </button>
                    </div>
                {/each}
            {/if}
        </div>

        <!-- Footer -->
        {#if notifications.length > 0}
            <div class="p-3 border-t border-kde-border bg-kde-bg/30">
                <button
                    class="w-full py-1.5 text-xs font-medium text-kde-text-dim hover:text-kde-text hover:bg-kde-border rounded transition-colors"
                    onclick={clearAll}
                >
                    Clear All
                </button>
            </div>
        {/if}
    </div>
{/if}
