import axios from 'axios';
import { AuthResponse, LoginCredentials, RegisterData } from '../types';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await api.post('/login', credentials);
    return response.data;
  },

  register: async (data: RegisterData): Promise<void> => {
    await api.post('/register', data);
  },
};

export const chatAPI = {
  connectWebSocket: (clientId: number) => {
    return new WebSocket(`ws://localhost:8000/ws/${clientId}`);
  },
}; 