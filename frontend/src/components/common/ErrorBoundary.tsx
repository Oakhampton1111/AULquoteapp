import React, { Component, ErrorInfo } from 'react';
import { Result, Button } from 'antd';
import styled from 'styled-components';

const ErrorContainer = styled.div`
  padding: 24px;
  text-align: center;
`;

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to your error reporting service
    console.error('Uncaught error:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleGoHome = () => {
    window.location.href = '/';
  };

  public render() {
    if (this.state.hasError) {
      const isProd = process.env.NODE_ENV === 'production';
      
      return (
        <ErrorContainer>
          <Result
            status="error"
            title="Something went wrong"
            subTitle={isProd 
              ? "We're sorry, but something went wrong. Please try again or contact support if the problem persists."
              : this.state.error?.message
            }
            extra={[
              <Button key="reload" type="primary" onClick={this.handleReload}>
                Try Again
              </Button>,
              <Button key="home" onClick={this.handleGoHome}>
                Go Home
              </Button>,
            ]}
          >
            {!isProd && this.state.errorInfo && (
              <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left', marginTop: 16 }}>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo.componentStack}
              </details>
            )}
          </Result>
        </ErrorContainer>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
