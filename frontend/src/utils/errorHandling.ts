import { AxiosError } from 'axios';
import { notification } from 'antd';

/**
 * Standard error response structure from the API
 */
export interface ApiErrorResponse {
  message: string;
  status: number;
  errors?: Record<string, string[]>;
}

/**
 * Handles API errors in a consistent way across the application
 * @param error The error object from the API call
 * @param fallbackMessage A fallback message to display if the error doesn't have a message
 * @param showNotification Whether to show a notification to the user
 * @returns The error message
 */
export const handleApiError = (
  error: unknown,
  fallbackMessage = 'An unexpected error occurred',
  showNotification = true
): string => {
  let errorMessage = fallbackMessage;
  let errorDetails: string | undefined;

  if (error instanceof Error) {
    // Handle Axios errors
    if ((error as AxiosError).isAxiosError) {
      const axiosError = error as AxiosError<ApiErrorResponse>;
      
      // Get error message from response if available
      if (axiosError.response?.data) {
        const { data } = axiosError.response;
        errorMessage = data.message || errorMessage;
        
        // Handle validation errors
        if (data.errors) {
          errorDetails = Object.entries(data.errors)
            .map(([field, messages]) => `${field}: ${messages.join(', ')}`)
            .join('\n');
        }
      }
    } else {
      // Handle regular JavaScript errors
      errorMessage = error.message || errorMessage;
    }
  }

  // Show notification if requested
  if (showNotification) {
    notification.error({
      message: 'Error',
      description: errorDetails ? `${errorMessage}\n\n${errorDetails}` : errorMessage,
      duration: 5,
    });
  }

  // Log error to console in development
  if (process.env.NODE_ENV !== 'production') {
    console.error('API Error:', error);
  }

  // Return the error message for further handling if needed
  return errorMessage;
};

/**
 * Logs errors to an error tracking service (e.g., Sentry)
 * @param error The error object
 * @param context Additional context information
 */
export const logErrorToService = (error: unknown, context?: Record<string, unknown>): void => {
  // In a real application, this would send the error to a service like Sentry
  // Example: Sentry.captureException(error, { extra: context });
  
  // For now, just log to console in development
  if (process.env.NODE_ENV !== 'production') {
    console.error('Error logged to service:', error, context);
  }
};
