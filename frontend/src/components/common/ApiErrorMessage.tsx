import React from 'react';
import { Alert, Space, Button } from 'antd';
import { AxiosError } from 'axios';

interface ApiErrorMessageProps {
  error: AxiosError | Error | null;
  onRetry?: () => void;
}

const getErrorMessage = (error: AxiosError | Error) => {
  if (error instanceof AxiosError) {
    const status = error.response?.status;
    const message = error.response?.data?.message || error.message;

    switch (status) {
      case 400:
        return 'Invalid request. Please check your input and try again.';
      case 401:
        return 'Your session has expired. Please log in again.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'The requested resource was not found.';
      case 409:
        return 'This operation could not be completed due to a conflict.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'An internal server error occurred. Please try again later.';
      default:
        return message || 'An unexpected error occurred.';
    }
  }
  
  return error.message || 'An unexpected error occurred.';
};

export const ApiErrorMessage: React.FC<ApiErrorMessageProps> = ({ error, onRetry }) => {
  if (!error) return null;

  return (
    <Space direction="vertical" style={{ width: '100%' }}>
      <Alert
        message="Error"
        description={getErrorMessage(error)}
        type="error"
        showIcon
        action={
          onRetry && (
            <Button size="small" type="ghost" onClick={onRetry}>
              Try Again
            </Button>
          )
        }
      />
    </Space>
  );
};
