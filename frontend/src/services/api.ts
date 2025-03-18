import { AuthResponse, LoginCredentials, RegisterData } from '../types';

const API_URL = 'http://localhost:8000';

export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `username=${encodeURIComponent(credentials.username)}&password=${encodeURIComponent(credentials.password)}`
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    return response.json();
  },

  register: async (data: RegisterData): Promise<void> => {
    const response = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error('Registration failed');
    }
  },
};

export const chatAPI = {
  connectWebSocket: (clientId: number) => {
    return new WebSocket(`ws://localhost:8000/ws/${clientId}`);
  },
}; 