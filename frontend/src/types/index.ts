export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
}

export interface Message {
  content: string;
  sender: string;
  timestamp: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  full_name: string;
  username: string;
  email: string;
  password: string;
} 