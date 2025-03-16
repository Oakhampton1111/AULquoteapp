/**
 * Authentication API endpoints.
 */

import apiClient from './client';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

export const authApi = {
  login: async (data: LoginRequest): Promise<Token> => {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);
    
    const response = await apiClient.post<Token>('/auth/token', formData);
    return response.data;
  },

  requestPasswordReset: async (data: PasswordResetRequest): Promise<void> => {
    await apiClient.post('/auth/reset-password/request', data);
  },

  confirmPasswordReset: async (data: PasswordResetConfirm): Promise<void> => {
    await apiClient.post('/auth/reset-password/confirm', data);
  }
};
