import axios from 'axios';
import { User, UserFormData } from '../../types/user';

const API_URL = import.meta.env.VITE_API_URL;

export const fetchUsers = async (): Promise<User[]> => {
  const { data } = await axios.get(`${API_URL}/api/users`);
  return data;
};

export const createUser = async (userData: UserFormData): Promise<User> => {
  const { data } = await axios.post(`${API_URL}/api/users`, userData);
  return data;
};

export const updateUser = async (id: string, userData: Partial<UserFormData>): Promise<User> => {
  const { data } = await axios.patch(`${API_URL}/api/users/${id}`, userData);
  return data;
};

export const deleteUser = async (id: string): Promise<void> => {
  await axios.delete(`${API_URL}/api/users/${id}`);
};
