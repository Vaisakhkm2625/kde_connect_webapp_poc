export const MOCK_API_BASE = "http://localhost:5000/api";

export const mockApi = {
    // Notifications
    // SSE must be handled directly in the component via EventSource

    // Files
    async getFiles(path: string = "/") {
        const res = await fetch(`${MOCK_API_BASE}/files?path=${encodeURIComponent(path)}`);
        if (!res.ok) throw new Error("Failed to fetch files");
        return res.json();
    },

    getFileUrl(path: string) {
        return `${MOCK_API_BASE}/files/download?path=${encodeURIComponent(path)}`;
    },

    // Clipboard
    async getClipboard() {
        const res = await fetch(`${MOCK_API_BASE}/clipboard`);
        if (!res.ok) throw new Error("Failed to get clipboard");
        return res.json();
    },

    async setClipboard(content: string) {
        const res = await fetch(`${MOCK_API_BASE}/clipboard`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ content }),
        });
        if (!res.ok) throw new Error("Failed to set clipboard");
        return res.json();
    },

    // Battery
    async getBattery() {
        const res = await fetch(`${MOCK_API_BASE}/battery`);
        if (!res.ok) throw new Error("Failed to get battery");
        return res.json();
    },

    // Media
    async getMediaStatus() {
        const res = await fetch(`${MOCK_API_BASE}/media`);
        if (!res.ok) throw new Error("Failed to get media status");
        return res.json();
    },

    async controlMedia(action: "play_pause" | "next" | "previous") {
        const res = await fetch(`${MOCK_API_BASE}/media/control`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ action }),
        });
        if (!res.ok) throw new Error("Failed to control media");
        return res.json();
    }
};
