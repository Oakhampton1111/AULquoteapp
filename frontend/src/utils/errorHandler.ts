import { message } from 'antd';
import axios, { AxiosError } from 'axios';

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ message: string }>;
    
    // Handle specific HTTP status codes
    switch (axiosError.response?.status) {
      case 401:
        // Unauthorized - redirect to login
        window.location.href = '/auth/login';
        return 'Session expired. Please log in again.';
      
      case 403:
        return 'You do not have permission to perform this action.';
      
      case 404:
        return 'The requested resource was not found.';
      
      case 422:
        return 'Invalid data provided. Please check your input.';
      
      case 500:
        return 'An internal server error occurred. Please try again later.';
      
      default:
        return axiosError.response?.data?.message || 'An unexpected error occurred.';
    }
  }
  
  return 'An unexpected error occurred.';
};

export const showErrorMessage = (error: unknown) => {
  const errorMessage = handleApiError(error);
  message.error(errorMessage);
};

export const showSuccessMessage = (msg: string) => {
  message.success(msg);
};

export const showWarningMessage = (msg: string) => {
  message.warning(msg);
};
