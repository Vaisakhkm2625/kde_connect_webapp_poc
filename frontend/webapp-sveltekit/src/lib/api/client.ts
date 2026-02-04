
export interface ApiResponse<T> {
    success: boolean;
    message?: string;
    exception?: string;
    // Dynamic fields
    [key: string]: any;
}

export const API_BASE = '/api';

export class ApiError extends Error {
    constructor(public message: string, public status?: number) {
        super(message);
    }
}

export async function apiRequest<T>(
    path: string,
    method: string = 'GET',
    body?: any
): Promise<T> {
    const options: RequestInit = {
        method,
        headers: {}
    };

    if (body) {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE}${path}`, options);

        // Handle non-JSON responses or empty responses if necessary, 
        // but the backend seems to always return JSON.
        const text = await response.text();
        const data: ApiResponse<any> = text ? JSON.parse(text) : {};

        if (!response.ok) {
            // Backend returns error in body sometimes
            throw new ApiError(data.message || 'Request failed', response.status);
        }

        // Backend convention: success field
        if (data.success === false) {
            throw new ApiError(data.message || 'API Error');
        }

        return data as T;
    } catch (err: any) {
        console.error(`API Error (${method} ${path}):`, err);
        throw new ApiError(err.message || 'Network error');
    }
}
