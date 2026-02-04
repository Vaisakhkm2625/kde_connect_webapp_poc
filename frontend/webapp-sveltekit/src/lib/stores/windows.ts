import { writable, get } from 'svelte/store';
import { WINDOW_DEFAULT_SIZE, WINDOW_MIN_SIZE } from '../utils/constants';

export interface WindowState {
    id: string;
    title: string;
    component: string;
    props?: Record<string, any>;
    x: number;
    y: number;
    width: number;
    height: number;
    minimized: boolean;
    maximized: boolean;
    zIndex: number;
    icon?: string;
}

function createWindowStore() {
    const { subscribe, update, set } = writable<WindowState[]>([]);

    let maxZIndex = 100;

    return {
        subscribe,
        open: (id: string, title: string, component: string, props = {}, icon?: string) => {
            update(windows => {
                const existing = windows.find(w => w.id === id);
                if (existing) {
                    if (existing.minimized) existing.minimized = false;
                    existing.zIndex = ++maxZIndex;
                    return [...windows]; // Trigger update
                }

                // Center window initially
                const x = (typeof window !== 'undefined' ? window.innerWidth / 2 - WINDOW_DEFAULT_SIZE.width / 2 : 100);
                const y = (typeof window !== 'undefined' ? window.innerHeight / 2 - WINDOW_DEFAULT_SIZE.height / 2 : 100);

                return [...windows, {
                    id,
                    title,
                    component,
                    props,
                    x,
                    y,
                    width: WINDOW_DEFAULT_SIZE.width,
                    height: WINDOW_DEFAULT_SIZE.height,
                    minimized: false,
                    maximized: false,
                    zIndex: ++maxZIndex,
                    icon
                }];
            });
        },

        close: (id: string) => {
            update(windows => windows.filter(w => w.id !== id));
        },

        focus: (id: string) => {
            update(windows => {
                const win = windows.find(w => w.id === id);
                if (win) {
                    win.zIndex = ++maxZIndex;
                    if (win.minimized) win.minimized = false;
                }
                return [...windows]; // Trigger reactivity
            });
        },

        minimize: (id: string) => {
            update(windows => {
                const win = windows.find(w => w.id === id);
                if (win) win.minimized = true;
                return [...windows];
            });
        },

        maximize: (id: string) => {
            update(windows => {
                const win = windows.find(w => w.id === id);
                if (win) {
                    // Toggle maximized
                    win.maximized = !win.maximized;
                    // Logic to restore size is handled in component often, but state needs to track it
                }
                return [...windows];
            });
        },

        move: (id: string, x: number, y: number) => {
            update(windows => {
                const win = windows.find(w => w.id === id);
                if (win && !win.maximized) {
                    win.x = x;
                    win.y = y;
                }
                return [...windows];
            });
        },

        resize: (id: string, width: number, height: number) => {
            update(windows => {
                const win = windows.find(w => w.id === id);
                if (win && !win.maximized) {
                    win.width = Math.max(width, WINDOW_MIN_SIZE.width);
                    win.height = Math.max(height, WINDOW_MIN_SIZE.height);
                }
                return [...windows];
            })
        }
    };
}

export const windowManager = createWindowStore();
export const activeWindow = writable<string | null>(null);
