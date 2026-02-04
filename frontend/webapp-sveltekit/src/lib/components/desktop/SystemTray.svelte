<script lang="ts">
    import { Battery, Wifi, Volume2 } from "lucide-svelte";

    // Props could include battery status, signal strength, etc.
    let batteryLevel = 100;
    let isCharging = false;
    let signalStrength = 80;

    // Formatting time
    let time = $state(new Date());

    $effect(() => {
        const interval = setInterval(() => {
            time = new Date();
        }, 1000);

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
            class="flex items-center justify-center w-6 h-6 hover:bg-white/10 rounded cursor-pointer"
            title="Battery"
        >
            <Battery size={14} />
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
