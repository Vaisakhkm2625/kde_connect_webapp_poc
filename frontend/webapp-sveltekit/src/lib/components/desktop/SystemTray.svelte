<script lang="ts">
    import { Battery, Wifi, Volume2 } from "lucide-svelte";
    import { mockApi } from "$lib/api/mock";
    import { onMount } from "svelte";

    // Props could include battery status, signal strength, etc.
    let batteryLevel = $state(100);
    let isCharging = $state(false);
    let signalStrength = 80;

    // Formatting time
    let time = $state(new Date());

    async function updateBattery() {
        try {
            const data = await mockApi.getBattery();
            batteryLevel = data.percentage;
            isCharging = data.is_charging;
        } catch (e) {
            console.error("Battery fetch error:", e);
        }
    }

    $effect(() => {
        const interval = setInterval(() => {
            time = new Date();
        }, 1000);

        return () => clearInterval(interval);
    });

    onMount(() => {
        updateBattery();
        const interval = setInterval(updateBattery, 10000); // Check battery every 10s
        return () => clearInterval(interval);
    });
</script>

<div class="flex items-center gap-3 text-kde-text-dim text-xs h-full">
    <!-- Status Icons -->
    <div class="flex items-center gap-2 px-2">
        <div
            class="flex items-center justify-center w-6 h-6 hover:bg-white/10 rounded cursor-pointer"
            title="Signal Strength"
        >
            <Wifi size={14} />
        </div>
        <div
            class="flex items-center justify-center w-6 h-6 hover:bg-white/10 rounded cursor-pointer"
            title="Volume"
        >
            <Volume2 size={14} />
        </div>
        <div
            class="flex items-center justify-center w-6 h-6 hover:bg-white/10 rounded cursor-pointer relative group"
            title={`Battery: ${batteryLevel}% ${isCharging ? "(Charging)" : ""}`}
        >
            <Battery size={14} class={isCharging ? "text-green-400" : ""} />
            <!-- Charging indicator overlay -->
            {#if isCharging}
                <div
                    class="absolute -top-0.5 -right-0.5 w-2 h-2 bg-green-500 rounded-full border border-[#15181a]"
                ></div>
            {/if}
        </div>
    </div>

    <!-- Clock -->
    <div
        class="px-3 py-1 hover:bg-white/10 rounded cursor-default h-full flex items-center transition-colors"
    >
        <div class="text-center leading-tight">
            <div class="font-medium text-kde-text">
                {time.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                })}
            </div>
            <div class="text-[10px] text-kde-text-dim">
                {time.toLocaleDateString([], {
                    month: "short",
                    day: "numeric",
                })}
            </div>
        </div>
    </div>
</div>
