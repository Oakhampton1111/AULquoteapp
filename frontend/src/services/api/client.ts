import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;
const API_VERSION = 'v1';

const apiClient = axios.create({
  baseURL: `${API_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const fetchClientDashboard = async () => {
  try {
    const { data } = await apiClient.get('/client/dashboard');
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to load dashboard data');
    }
    throw error;
  }
};

export const updateClientProfile = async (profileData: any) => {
  try {
    const { data } = await apiClient.patch('/client/profile', profileData);
    return data;
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.message || 'Failed to update profile');
    }
    throw error;
  }
};
