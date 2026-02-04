<script lang="ts">
    import { onMount, onDestroy } from "svelte";
    import { Camera, RefreshCw, Download, Send, Trash2 } from "lucide-svelte";
    import toast from "svelte-french-toast";

    let videoElement: HTMLVideoElement;
    let canvasElement: HTMLCanvasElement;
    let stream: MediaStream | null = null;
    let capturedImage: string | null = null;
    let devices: MediaDeviceInfo[] = [];
    let selectedDeviceId: string = "";

    onMount(async () => {
        await getCameras();
        await startCamera();
    });

    onDestroy(() => {
        stopCamera();
    });

    async function getCameras() {
        try {
            const allDevices = await navigator.mediaDevices.enumerateDevices();
            devices = allDevices.filter((d) => d.kind === "videoinput");
            if (devices.length > 0) {
                selectedDeviceId = devices[0].deviceId;
            }
        } catch (e) {
            console.error("Error listing cameras:", e);
        }
    }

    async function startCamera() {
        if (stream) stopCamera();

        try {
            stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    deviceId: selectedDeviceId
                        ? { exact: selectedDeviceId }
                        : undefined,
                },
            });
            if (videoElement) {
                videoElement.srcObject = stream;
            }
        } catch (e) {
            toast.error("Could not access camera");
            console.error(e);
        }
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach((track) => track.stop());
            stream = null;
        }
    }

    function capture() {
        if (!videoElement || !canvasElement) return;

        const ctx = canvasElement.getContext("2d");
        if (ctx) {
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;
            ctx.drawImage(videoElement, 0, 0);
            capturedImage = canvasElement.toDataURL("image/png");
        }
    }

    function retake() {
        capturedImage = null;
    }

    async function downloadImage() {
        if (!capturedImage) return;
        const a = document.createElement("a");
        a.href = capturedImage;
        a.download = `capture-${Date.now()}.png`;
        a.click();
    }

    function sendToDevice() {
        toast("Sending not implemented yet (requires backend API update)", {
            icon: "🚧",
        });
    }

    async function switchCamera() {
        // logic to toggle index in devices array
        const idx = devices.findIndex((d) => d.deviceId === selectedDeviceId);
        if (idx !== -1 && devices.length > 1) {
            selectedDeviceId = devices[(idx + 1) % devices.length].deviceId;
            await startCamera();
        }
    }
</script>

<div class="h-full flex flex-col bg-black text-white overflow-hidden relative">
    <!-- Viewport -->
    <div class="flex-1 relative flex items-center justify-center bg-zinc-900">
        {#if !capturedImage}
            <!-- svelte-ignore a11y-media-has-caption -->
            <video
                bind:this={videoElement}
                autoplay
                playsinline
                class="max-w-full max-h-full object-contain"
            ></video>
        {:else}
            <img
                src={capturedImage}
                alt="Captured"
                class="max-w-full max-h-full object-contain"
            />
        {/if}

        <canvas bind:this={canvasElement} class="hidden"></canvas>
    </div>

    <!-- Controls -->
    <div
        class="h-20 bg-zinc-900/80 backdrop-blur flex items-center justify-center gap-8 relative z-10"
    >
        {#if !capturedImage}
            {#if devices.length > 1}
                <button
                    class="p-3 rounded-full bg-zinc-800 hover:bg-zinc-700 transition"
                    on:click={switchCamera}
                    title="Switch Camera"
                >
                    <RefreshCw size={20} />
                </button>
            {/if}

            <button
                class="w-16 h-16 rounded-full border-4 border-white flex items-center justify-center hover:bg-white/20 transition-all active:scale-95"
                on:click={capture}
            >
                <div class="w-12 h-12 bg-white rounded-full"></div>
            </button>
        {:else}
            <button
                class="flex flex-col items-center gap-1 text-xs text-zinc-400 hover:text-white"
                on:click={retake}
            >
                <div class="p-2 rounded-full bg-zinc-800">
                    <Trash2 size={20} />
                </div>
                Retake
            </button>

            <button
                class="flex flex-col items-center gap-1 text-xs text-zinc-400 hover:text-white"
                on:click={downloadImage}
            >
                <div class="p-2 rounded-full bg-zinc-800">
                    <Download size={20} />
                </div>
                Save
            </button>

            <button
                class="flex flex-col items-center gap-1 text-xs text-kde-blue hover:text-white"
                on:click={sendToDevice}
            >
                <div class="p-2 rounded-full bg-kde-blue text-white">
                    <Send size={20} />
                </div>
                Send
            </button>
        {/if}
    </div>
</div>
