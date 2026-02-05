import { apiRequest } from './client';

export interface Device {
    identifier: string;
    name: string;
    type: string;
    reachable: boolean;
    trusted: boolean;
    commands?: Record<string, any>;
    path?: string;
}

export const devicesApi = {
    list: () => apiRequest<{ devices: Device[] }>('/device'),

    get: (id: string) => apiRequest<Device>(`/device/${id}`),

    pair: (id: string) => apiRequest<void>(`/pair/${id}`, 'POST'),

    unpair: (id: string) => apiRequest<void>(`/pair/${id}`, 'DELETE'),

    ping: (id: string) => apiRequest<void>(`/ping/${id}`, 'POST'),

    ring: (id: string) => apiRequest<void>(`/ring/${id}`, 'POST'),

    sftpStart: (id: string) => apiRequest<void>(`/sftp/${id}`, 'POST'),

    sftpBrowse: (id: string, path: string = "/") => apiRequest<{ files: any[], path: string }>(`/sftp/${id}/${encodeURIComponent(path)}`, 'GET'),
};
