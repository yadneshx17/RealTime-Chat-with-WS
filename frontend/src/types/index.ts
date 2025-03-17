export interface User {
  id: number;
  full_name: string;
  username: string;
  email: string;
}

export interface Message {
  id: number;
  content: string;
  sender_id: number;
  created_at: string;
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