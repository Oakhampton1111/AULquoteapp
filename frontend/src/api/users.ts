/**
 * User management API endpoints.
 */

import apiClient from './client';

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
  preferences: Record<string, any>;
}

export interface Customer {
  id: number;
  name: string;
  email: string;
  company: string;
  phone: string;
  address: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
  is_admin?: boolean;
}

export interface UserUpdate {
  email?: string;
  is_active?: boolean;
  preferences?: Record<string, any>;
}

export interface CustomerCreate {
  name: string;
  email: string;
  company: string;
  phone: string;
  address: string;
}

export interface CustomerUpdate {
  name?: string;
  email?: string;
  company?: string;
  phone?: string;
  address?: string;
}

export const usersApi = {
  // User endpoints
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/users/me');
    return response.data;
  },

  updateCurrentUser: async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>('/users/me', data);
    return response.data;
  },

  getUsers: async (): Promise<User[]> => {
    const response = await apiClient.get<User[]>('/users');
    return response.data;
  },

  createUser: async (data: UserCreate): Promise<User> => {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  },

  updateUser: async (id: number, data: UserUpdate): Promise<User> => {
    const response = await apiClient.put<User>(`/users/${id}`, data);
    return response.data;
  },

  deleteUser: async (id: number): Promise<void> => {
    await apiClient.delete(`/users/${id}`);
  },

  // Customer endpoints
  getCustomers: async (): Promise<Customer[]> => {
    const response = await apiClient.get<Customer[]>('/users/customers');
    return response.data;
  },

  createCustomer: async (data: CustomerCreate): Promise<Customer> => {
    const response = await apiClient.post<Customer>('/users/customers', data);
    return response.data;
  },

  updateCustomer: async (id: number, data: CustomerUpdate): Promise<Customer> => {
    const response = await apiClient.put<Customer>(`/users/customers/${id}`, data);
    return response.data;
  },

  deleteCustomer: async (id: number): Promise<void> => {
    await apiClient.delete(`/users/customers/${id}`);
  },

  // User preferences
  getUserPreferences: async (): Promise<Record<string, any>> => {
    const response = await apiClient.get('/users/me/preferences');
    return response.data;
  },

  updateUserPreferences: async (preferences: Record<string, any>): Promise<User> => {
    const response = await apiClient.put<User>('/users/me/preferences', preferences);
    return response.data;
  }
};
