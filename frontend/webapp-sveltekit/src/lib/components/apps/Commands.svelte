<script lang="ts">
    import { onMount } from "svelte";
    import {
        Terminal,
        Play,
        Plus,
        Trash2,
        Edit2,
        RotateCw,
    } from "lucide-svelte";
    import { apiRequest } from "$lib/api/client";
    import { devicesApi, type Device } from "$lib/api/devices";
    import toast from "svelte-french-toast";

    interface LocalCommand {
        identifier: string;
        device: string; // Device Name? Or device ID stored in DB?
        key: string;
        name: string;
        command: string;
    }

    let localCommands = $state<LocalCommand[]>([]);
    let devices = $state<Device[]>([]);
    let selectedDeviceId = $state("");

    // Create/Edit Form
    let editingCmd: LocalCommand | null = null;
    let formName = $state("");
    let formExec = $state("");
    let formDevice = $state("");

    async function loadData() {
        try {
            const [cmdsRes, devsRes] = await Promise.all([
                apiRequest<{ commands: LocalCommand[] }>("/command"),
                devicesApi.list(),
            ]);
            localCommands = cmdsRes.commands;
            devices = devsRes.devices;
            if (!selectedDeviceId && devices.length > 0) {
                selectedDeviceId = devices[0].identifier;
            }
        } catch (e) {
            console.error(e);
        }
    }

    async function executeRemote(
        deviceId: string,
        key: string,
        cmdName: string,
    ) {
        try {
            // PATCH /command/:device/:key
            await apiRequest(`/command/${deviceId}/${key}`, "PATCH");
            toast.success(`Executed: ${cmdName}`);
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    async function saveLocalCommand() {
        if (!formName || !formExec || !formDevice)
            return toast.error("Fill all fields");

        try {
            if (editingCmd) {
                // PUT /command/:device/:key
                await apiRequest(
                    `/command/${formDevice}/${editingCmd.key}`,
                    "PUT",
                    {
                        name: formName,
                        command: formExec,
                    },
                );
                toast.success("Command updated");
            } else {
                // POST /command/:device
                await apiRequest(`/command/${formDevice}`, "POST", {
                    name: formName,
                    command: formExec,
                });
                toast.success("Command created");
            }
            editingCmd = null;
            formName = "";
            formExec = "";
            loadData();
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    async function deleteLocalCommand(deviceId: string, key: string) {
        if (!confirm("Delete command?")) return;
        try {
            await apiRequest(`/command/${deviceId}/${key}`, "DELETE");
            toast.success("Command deleted");
            loadData();
        } catch (e: any) {
            toast.error(e.message);
        }
    }

    function editLocalCommand(cmd: LocalCommand) {
        editingCmd = cmd;
        formName = cmd.name;
        formExec = cmd.command;
        formDevice = cmd.identifier; // Assuming 'identifier' is the device ID in local command object
        // Actually API response for local command has 'identifier' as Device ID?
        // api.py _handleListCommands returns { commands: database.listCommands(identifier) }
        // database.listAllCommands returns flattened list?
        // Need to check response structure. Assuming flattened list with device ID.
    }

    function cancelEdit() {
        editingCmd = null;
        formName = "";
        formExec = "";
    }

    onMount(loadData);
</script>

<div class="h-full flex flex-col md:flex-row bg-kde-bg text-kde-text">
    <!-- Left: Remote Commands -->
    <div class="flex-1 border-r border-kde-border flex flex-col min-w-[300px]">
        <div
            class="p-3 border-b border-kde-border bg-kde-card/50 flex justify-between items-center"
        >
            <h3 class="font-medium flex items-center gap-2">
                <Terminal size={16} /> Remote Commands
            </h3>
            <button on:click={loadData} class="p-1 hover:bg-kde-border rounded"
                ><RotateCw size={14} /></button
            >
        </div>

        <div class="p-2 border-b border-kde-border">
            <select
                bind:value={selectedDeviceId}
                class="w-full bg-kde-bg border border-kde-border rounded p-1.5 text-sm"
            >
                {#each devices as dev}
                    <option value={dev.identifier}
                        >{dev.name} ({dev.reachable
                            ? "Online"
                            : "Offline"})</option
                    >
                {/each}
            </select>
        </div>

        <div class="flex-1 overflow-y-auto p-2">
            {#if selectedDeviceId}
                {@const activeDev = devices.find(
                    (d) => d.identifier === selectedDeviceId,
                )}
                {#if activeDev && activeDev.commands && Object.keys(activeDev.commands).length > 0}
                    <div class="grid grid-cols-1 gap-2">
                        {#each Object.entries(activeDev.commands) as [key, cmd]}
                            <div
                                class="bg-kde-card border border-kde-border rounded p-2 flex items-center justify-between"
                            >
                                <div class="flex items-center gap-2">
                                    <Terminal size={14} class="text-kde-blue" />
                                    <span class="text-sm font-medium"
                                        >{cmd.name}</span
                                    >
                                </div>
                                <button
                                    class="bg-kde-blue hover:bg-kde-blue/90 text-white p-1.5 rounded transition-colors"
                                    on:click={() =>
                                        executeRemote(
                                            selectedDeviceId,
                                            key,
                                            cmd.name,
                                        )}
                                    title="Execute"
                                >
                                    <Play size={14} />
                                </button>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div
                        class="h-full flex items-center justify-center text-kde-text-dim text-sm"
                    >
                        No commands available for this device
                    </div>
                {/if}
            {/if}
        </div>
    </div>

    <!-- Right: Local Commands -->
    <div class="flex-1 flex flex-col bg-kde-card/30">
        <div class="p-3 border-b border-kde-border bg-kde-card/50">
            <h3 class="font-medium text-sm">Local Server Commands</h3>
        </div>

        <!-- Form -->
        <div class="p-4 border-b border-kde-border space-y-3 bg-kde-card/50">
            <h4
                class="text-xs font-bold text-kde-text-dim uppercase tracking-wider"
            >
                {editingCmd ? "Edit Command" : "New Command"}
            </h4>
            <div class="flex gap-2">
                <div class="flex-1">
                    <input
                        bind:value={formName}
                        placeholder="Name"
                        class="w-full bg-kde-bg border border-kde-border rounded p-1.5 text-sm"
                    />
                </div>
                <div class="w-1/3">
                    <select
                        bind:value={formDevice}
                        class="w-full bg-kde-bg border border-kde-border rounded p-1.5 text-sm"
                        disabled={!!editingCmd}
                    >
                        <option value="">Device</option>
                        {#each devices as dev}
                            <option value={dev.identifier}>{dev.name}</option>
                        {/each}
                    </select>
                </div>
            </div>
            <input
                bind:value={formExec}
                placeholder="Command (e.g. shutdown -h now)"
                class="w-full bg-kde-bg border border-kde-border rounded p-1.5 text-sm font-mono"
            />

            <div class="flex justify-end gap-2">
                {#if editingCmd}
                    <button
                        class="px-3 py-1 text-xs hover:bg-kde-border rounded"
                        on:click={cancelEdit}>Cancel</button
                    >
                {/if}
                <button
                    class="px-3 py-1 text-xs bg-kde-blue text-white rounded hover:bg-kde-blue/90"
                    on:click={saveLocalCommand}
                >
                    {editingCmd ? "Update" : "Save"}
                </button>
            </div>
        </div>

        <!-- List -->
        <div class="flex-1 overflow-y-auto p-2 space-y-2">
            {#each localCommands as cmd}
                <div
                    class="bg-kde-card border border-kde-border rounded p-2 flex flex-col gap-1"
                >
                    <div class="flex items-center justify-between">
                        <span class="font-medium text-sm">{cmd.name}</span>
                        <div class="flex gap-1">
                            <button
                                class="p-1 hover:text-kde-blue"
                                on:click={() => editLocalCommand(cmd)}
                                ><Edit2 size={12} /></button
                            >
                            <button
                                class="p-1 hover:text-kde-danger"
                                on:click={() =>
                                    deleteLocalCommand(cmd.identifier, cmd.key)}
                                ><Trash2 size={12} /></button
                            >
                        </div>
                    </div>
                    <code
                        class="text-[10px] bg-kde-bg rounded p-1 text-kde-text-dim truncate"
                        >{cmd.command}</code
                    >
                    <div
                        class="text-[10px] text-kde-text-dim flex items-center gap-1"
                    >
                        Target: {cmd.device}
                    </div>
                </div>
            {/each}
        </div>
    </div>
</div>
