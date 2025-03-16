import axios from 'axios';
import { User } from '../../types/user';

const API_URL = import.meta.env.VITE_API_URL;

export const login = async (email: string, password: string): Promise<User> => {
  const { data } = await axios.post(`${API_URL}/api/auth/login`, {
    email,
    password,
  });
  
  localStorage.setItem('token', data.token);
  axios.defaults.headers.common['Authorization'] = `Bearer ${data.token}`;
  
  return data.user;
};

export const logout = async (): Promise<void> => {
  localStorage.removeItem('token');
  delete axios.defaults.headers.common['Authorization'];
  await axios.post(`${API_URL}/api/auth/logout`);
};

export const getCurrentUser = async (): Promise<User> => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('No token found');
  }
  
  axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  const { data } = await axios.get(`${API_URL}/api/auth/me`);
  return data;
};
