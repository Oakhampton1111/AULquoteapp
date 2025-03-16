import React from 'react';
import { Spin, Skeleton, Result } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const LoadingContainer = styled.div<{ fullscreen?: boolean }>`
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: ${props => props.fullscreen ? '100vh' : '100%'};
  min-height: 200px;
`;

const StyledSpin = styled(Spin)`
  .ant-spin-dot {
    font-size: 24px;
  }
`;

interface LoadingStateProps {
  loading: boolean;
  error?: Error | null;
  fullscreen?: boolean;
  skeleton?: boolean;
  children: React.ReactNode;
  retry?: () => void;
}

const antIcon = <LoadingOutlined style={{ fontSize: 24 }} spin />;

export const LoadingState: React.FC<LoadingStateProps> = ({
  loading,
  error,
  fullscreen = false,
  skeleton = false,
  children,
  retry,
}) => {
  if (error) {
    return (
      <Result
        status="error"
        title="Failed to load"
        subTitle={error.message}
        extra={
          retry && [
            <button key="retry" onClick={retry}>
              Try Again
            </button>,
          ]
        }
      />
    );
  }

  if (loading) {
    if (skeleton) {
      return <Skeleton active />;
    }

    return (
      <LoadingContainer fullscreen={fullscreen}>
        <StyledSpin indicator={antIcon} />
      </LoadingContainer>
    );
  }

  return <>{children}</>;
};
