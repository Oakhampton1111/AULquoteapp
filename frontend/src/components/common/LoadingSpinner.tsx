import React from 'react';
import { Spin } from 'antd';
import styled from 'styled-components';

const SpinnerContainer = styled.div<{ fullPage?: boolean }>`
  display: flex;
  justify-content: center;
  align-items: center;
  height: ${props => props.fullPage ? '100vh' : '100%'};
  width: 100%;
  background: rgba(255, 255, 255, 0.8);
  position: ${props => props.fullPage ? 'fixed' : 'absolute'};
  top: 0;
  left: 0;
  z-index: 1000;
`;

interface LoadingSpinnerProps {
  fullPage?: boolean;
  tip?: string;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ fullPage = false, tip = 'Loading...' }) => {
  return (
    <SpinnerContainer fullPage={fullPage}>
      <Spin size="large" tip={tip} />
    </SpinnerContainer>
  );
};
