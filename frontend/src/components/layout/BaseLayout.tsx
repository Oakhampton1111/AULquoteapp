import React from 'react';
import { Layout, ConfigProvider } from 'antd';
import styled from 'styled-components';
import { ErrorBoundary } from '../common/ErrorBoundary';
import { MainNav } from '../navigation/MainNav';
import { useAuth } from '../../hooks/useAuth';

const { Header, Content, Footer } = Layout;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
`;

const StyledContent = styled(Content)`
  padding: 24px;
  margin: 24px;
  background: #fff;
  min-height: 280px;
  border-radius: 4px;
`;

const StyledHeader = styled(Header)`
  background: #fff;
  padding: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 1;
  width: 100%;
`;

const StyledFooter = styled(Footer)`
  text-align: center;
  background: transparent;
`;

interface BaseLayoutProps {
  children: React.ReactNode;
}

export const BaseLayout: React.FC<BaseLayoutProps> = ({ children }) => {
  const { user } = useAuth();

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 4,
        },
      }}
    >
      <StyledLayout>
        <StyledHeader>
          <MainNav user={user} />
        </StyledHeader>
        
        <StyledContent>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </StyledContent>

        <StyledFooter>
          AUL Quote App ©{new Date().getFullYear()} Created by Your Company
        </StyledFooter>
      </StyledLayout>
    </ConfigProvider>
  );
};
