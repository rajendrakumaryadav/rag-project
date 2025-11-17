import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

export interface User {
    id: number;
    email: string;
    username: string;
    full_name?: string;
    is_active: boolean;
    created_at: string;
}

export interface Conversation {
    id: number;
    title: string;
    provider: string;
    model: string;
    created_at: string;
    updated_at: string;
}

export interface Message {
    id: number;
    conversation_id: number;
    role: string;
    content: string;
    created_at: string;
    sources?: any[];
}

export interface ChatResponse {
    conversation_id: number;
    user_message: Message;
    assistant_message: Message;
    answer: string;
    sources: any[];
}

export interface LoginRequest {
    username: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    username: string;
    password: string;
    full_name?: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export const authAPI = {
    login: async (data: LoginRequest): Promise<TokenResponse> => {
        // OAuth2 requires form-urlencoded format
        const formData = new URLSearchParams();
        formData.append('username', data.username);
        formData.append('password', data.password);

        const response = await api.post('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },

    register: async (data: RegisterRequest): Promise<User> => {
        const response = await api.post('/auth/register', data);
        return response.data;
    },

    getCurrentUser: async (): Promise<User> => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    refreshToken: async (): Promise<TokenResponse> => {
        const response = await api.post('/auth/refresh-token');
        return response.data;
    },
};

export const chatAPI = {
    createConversation: async (data: { title: string; provider?: string; model?: string }): Promise<Conversation> => {
        const response = await api.post('/chat/conversations', data);
        return response.data;
    },

    listConversations: async (): Promise<Conversation[]> => {
        const response = await api.get('/chat/conversations');
        return response.data;
    },

    getConversationMessages: async (conversationId: number): Promise<Message[]> => {
        const response = await api.get(`/chat/conversations/${conversationId}/messages`);
        return response.data;
    },

    sendMessage: async (data: { message: string; provider?: string; conversation_id?: number }): Promise<ChatResponse> => {
        const response = await api.post('/chat/send', data);
        return response.data;
    },

    deleteConversation: async (conversationId: number): Promise<void> => {
        await api.delete(`/chat/conversations/${conversationId}`);
    },

    // New: Upload document with optional conversation link
    uploadDocument: async (file: File, conversationId?: number): Promise<any> => {
        const formData = new FormData();
        formData.append('file', file);
        if (conversationId) {
            formData.append('conversation_id', conversationId.toString());
        }

        const response = await api.post('/chat/upload-document', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    // New: List documents for user or conversation
    listChatDocuments: async (conversationId?: number): Promise<any[]> => {
        const params = conversationId ? { conversation_id: conversationId } : {};
        const response = await api.get('/chat/documents', { params });
        return response.data;
    },
};

export const configAPI = {
    getConfig: async () => {
        const response = await api.get('/config');
        return response.data;
    },
};

export interface Document {
    name: string;
    size_bytes: number;
    uploaded_at: string;
    path: string;
}

export interface UploadResponse {
    message: string;
    filename: string;
    path: string;
    processed_data: any;
}

export const documentAPI = {
    upload: async (file: File): Promise<UploadResponse> => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await api.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    },

    list: async (): Promise<{ count: number; documents: Document[] }> => {
        const response = await api.get('/documents');
        return response.data;
    },

    delete: async (filename: string): Promise<void> => {
        await api.delete(`/documents/${encodeURIComponent(filename)}`);
    },
};

export default api;

