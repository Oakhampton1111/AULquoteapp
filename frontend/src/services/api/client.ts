import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import { handleApiError, logErrorToService } from '../../utils/errorHandling';

// API configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';
const API_TIMEOUT = 15000; // 15 seconds

// Create an Axios instance with default config
const apiClient = axios.create({
  baseURL: `${API_URL}/api/${API_VERSION}`,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: API_TIMEOUT,
});

// Add a request interceptor to include auth token
apiClient.interceptors.request.use(
  (config) => {
    // Add authorization header if token exists
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Add timestamp to prevent caching for GET requests
    if (config.method?.toLowerCase() === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now(),
      };
    }

    return config;
  },
  (error) => {
    // Log request errors
    logErrorToService(error, { type: 'request_error' });
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle common errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    // Handle specific HTTP status codes
    if (error.response) {
      const { status } = error.response;

      // Handle unauthorized access - redirect to login
      if (status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }

      // Handle forbidden access
      if (status === 403) {
        // Redirect to access denied page or show notification
        // window.location.href = '/access-denied';
      }

      // Handle server errors
      if (status >= 500) {
        logErrorToService(error, {
          type: 'server_error',
          status,
          url: error.config?.url
        });
      }
    }

    // Handle network errors
    if (error.code === 'ECONNABORTED' || !error.response) {
      logErrorToService(error, { type: 'network_error' });
    }

    return Promise.reject(error);
  }
);

/**
 * Generic API request function with error handling
 */
const apiRequest = async <T>(config: AxiosRequestConfig): Promise<T> => {
  try {
    const response: AxiosResponse<T> = await apiClient(config);
    return response.data;
  } catch (error) {
    // Handle the error but don't show notification (caller will handle UI)
    handleApiError(error, `Failed to ${config.method} ${config.url}`, false);
    throw error;
  }
};

// API functions for client dashboard
export const fetchClientDashboard = async () => {
  return apiRequest({
    method: 'GET',
    url: '/client/dashboard',
  });
};

export const updateClientProfile = async (profileData: any) => {
  return apiRequest({
    method: 'PATCH',
    url: '/client/profile',
    data: profileData,
  });
};

export default apiClient;
