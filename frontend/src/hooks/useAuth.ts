import { useContext, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { message } from 'antd';
import apiClient from '../services/api/apiClient';
import { User } from '../types/user';
import { AuthContext } from '../services/auth/AuthContext';

interface LoginCredentials {
  email: string;
  password: string;
}

interface AuthResponse {
  user: User;
  token: string;
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const useLogin = () => {
  const navigate = useNavigate();
  const { setUser, setToken } = useAuth();

  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
      return response;
    },
    onSuccess: (data) => {
      setUser(data.user);
      setToken(data.token);
      localStorage.setItem('token', data.token);
      message.success('Successfully logged in');
      navigate('/dashboard');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || 'Login failed');
    },
  });
};

export const useLogout = () => {
  const navigate = useNavigate();
  const { setUser, setToken } = useAuth();

  return useCallback(() => {
    localStorage.removeItem('token');
    setUser(null);
    setToken(null);
    navigate('/login');
    message.success('Successfully logged out');
  }, [navigate, setUser, setToken]);
};

export const useCurrentUser = () => {
  const { user, token } = useAuth();

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      if (!token) return null;
      const response = await apiClient.get<User>('/auth/me');
      return response;
    },
    initialData: user,
    enabled: !!token,
  });
};

export const useResetPassword = () => {
  return useMutation({
    mutationFn: async (email: string) => {
      await apiClient.post('/auth/reset-password', { email });
    },
    onSuccess: () => {
      message.success('Password reset instructions sent to your email');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || 'Failed to reset password');
    },
  });
};

export const useUpdatePassword = () => {
  return useMutation({
    mutationFn: async ({ token, password }: { token: string; password: string }) => {
      await apiClient.post('/auth/update-password', { token, password });
    },
    onSuccess: () => {
      message.success('Password successfully updated');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.message || 'Failed to update password');
    },
  });
};
