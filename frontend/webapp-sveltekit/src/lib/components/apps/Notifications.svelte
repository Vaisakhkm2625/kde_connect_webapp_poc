<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { Bell, X, Send, Trash2, Smartphone } from "lucide-svelte";
    import { apiRequest } from "$lib/api/client";
    import { devicesApi, type Device } from "$lib/api/devices";
    import toast from "svelte-french-toast";

    interface Notification {
        device: string; // Device Name
        identifier: string; // Device ID
        title: string;
        text: string;
        reference: string;
    }

    let notifications = $state<Notification[]>([]);
    let devices = $state<Device[]>([]);
    let isLoading = $state(false);

    // Send form
    let selectedDeviceId = $state("");
    let sendTitle = $state("");
    let sendText = $state("");
    let sendApp = $state("KDE Connect Web");

    async function loadData() {
        try {
            const [notifsRes, devsRes] = await Promise.all([
                apiRequest<{ notifications: Notification[] }>("/notification"),
                devicesApi.list(),
            ]);
            notifications = notifsRes.notifications;
            devices = devsRes.devices;
            if (!selectedDeviceId && devices.length > 0) {
                selectedDeviceId = devices[0].identifier;
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function sendNotification() {
        if (!selectedDeviceId) return toast.error("Select a device");
        if (!sendTitle || !sendText)
            return toast.error("Title and message required");

        try {
            await apiRequest(`/notification/${selectedDeviceId}`, "POST", {
                title: sendTitle,
                text: sendText,
                application: sendApp,
            });
            toast.success("Notification sent");
            sendTitle = "";
            sendText = "";
            loadData();
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    async function cancelNotification(deviceId: string, reference: string) {
        try {
            // Note: The API response for list notification gives 'device' as name, and 'identifier' as ID.
            // But cancel needs device identifier. The Notification interface above matches API response.
            await apiRequest(
                `/notification/${deviceId}/${reference}`,
                "DELETE",
            );
            toast.success("Notification cancelled");
            loadData();
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    onMount(() => {
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    });
</script>

<div class="h-full flex flex-col md:flex-row bg-kde-bg text-kde-text">
    <!-- Left: Active Notifications -->
    <div class="flex-1 flex flex-col border-r border-kde-border min-w-[300px]">
        <div
            class="p-3 border-b border-kde-border bg-kde-card/50 flex justify-between items-center"
        >
            <h3 class="font-medium text-sm">Active Notifications</h3>
            <button
                on:click={loadData}
                class="p-1 hover:bg-kde-border rounded text-kde-text-dim hover:text-kde-text"
            >
                <smartphone size={16} />
            </button>
        </div>

        <div class="flex-1 overflow-y-auto p-2 space-y-2">
            {#if notifications.length === 0}
                <div
                    class="h-full flex flex-col items-center justify-center text-kde-text-dim opacity-50 gap-2"
                >
                    <Bell size={24} />
                    <span class="text-sm">No remote notifications</span>
                </div>
            {:else}
                {#each notifications as notif}
                    <div
                        class="bg-kde-card border border-kde-border rounded p-3 relative group"
                    >
                        <div class="flex justify-between items-start mb-1">
                            <span class="text-xs font-bold text-kde-blue"
                                >{notif.device}</span
                            >
                            <button
                                class="text-kde-text-dim hover:text-kde-danger p-1 rounded hover:bg-kde-border"
                                on:click={() =>
                                    cancelNotification(
                                        notif.identifier,
                                        notif.reference,
                                    )}
                                title="Cancel/Dismiss"
                            >
                                <X size={14} />
                            </button>
                        </div>
                        <h4 class="font-medium text-sm">{notif.title}</h4>
                        <p class="text-xs text-kde-text-dim mt-1">
                            {notif.text}
                        </p>
                        <div
                            class="mt-2 text-[10px] text-kde-text-dim font-mono bg-kde-bg/50 inline-block px-1 rounded"
                        >
                            REF: {notif.reference}
                        </div>
                    </div>
                {/each}
            {/if}
        </div>
    </div>

    <!-- Right: Send Panel -->
    <div class="w-full md:w-80 flex flex-col bg-kde-card/30">
        <div class="p-3 border-b border-kde-border bg-kde-card/50">
            <h3 class="font-medium text-sm">Send Notification</h3>
        </div>

        <div class="p-4 flex flex-col gap-3">
            <div>
                <label class="block text-xs text-kde-text-dim mb-1"
                    >Target Device</label
                >
                <select
                    bind:value={selectedDeviceId}
                    class="w-full bg-kde-bg border border-kde-border rounded p-2 text-sm"
                >
                    {#each devices as dev}
                        <option value={dev.identifier}>{dev.name}</option>
                    {/each}
                </select>
            </div>

            <div>
                <label class="block text-xs text-kde-text-dim mb-1">Title</label
                >
                <input
                    bind:value={sendTitle}
                    type="text"
                    class="w-full bg-kde-bg border border-kde-border rounded p-2 text-sm"
                    placeholder="Notification Title"
                />
            </div>

            <div>
                <label class="block text-xs text-kde-text-dim mb-1"
                    >Application Name</label
                >
                <input
                    bind:value={sendApp}
                    type="text"
                    class="w-full bg-kde-bg border border-kde-border rounded p-2 text-sm"
                />
            </div>

            <div class="flex-1">
                <label class="block text-xs text-kde-text-dim mb-1"
                    >Message</label
                >
                <textarea
                    bind:value={sendText}
                    class="w-full h-32 bg-kde-bg border border-kde-border rounded p-2 text-sm resize-none"
                    placeholder="Enter message here..."
                ></textarea>
            </div>

            <button
                class="w-full py-2 bg-kde-blue hover:bg-kde-blue/90 text-white rounded flex items-center justify-center gap-2 text-sm font-medium"
                on:click={sendNotification}
            >
                <Send size={16} /> Send
            </button>
        </div>
    </div>
</div>
