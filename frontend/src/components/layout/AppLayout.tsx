import React from 'react';
import { Layout, theme, Breadcrumb } from 'antd';
import styled from 'styled-components';
import { MainNav } from '../navigation/MainNav';
import { useLocation } from 'react-router-dom';

const { Header, Content } = Layout;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
`;

const StyledHeader = styled(Header)`
  padding: 0;
  background: #fff;
  position: fixed;
  width: 100%;
  z-index: 1;
  padding-left: 200px;
  display: flex;
  align-items: center;
`;

const StyledContent = styled(Content)`
  margin: 88px 24px 24px;
  padding: 24px;
  background: #fff;
  min-height: 280px;
  margin-left: 200px;
`;

const getBreadcrumbItems = (pathname: string) => {
  const paths = pathname.split('/').filter(Boolean);
  return paths.map((path, index) => ({
    title: path.charAt(0).toUpperCase() + path.slice(1),
    key: paths.slice(0, index + 1).join('/'),
  }));
};

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();
  const location = useLocation();

  return (
    <StyledLayout>
      <MainNav />
      <Layout>
        <StyledHeader>
          <Breadcrumb
            style={{ margin: '16px 24px' }}
            items={[{ title: 'Home', key: '/' }, ...getBreadcrumbItems(location.pathname)]}
          />
        </StyledHeader>
        <StyledContent>{children}</StyledContent>
      </Layout>
    </StyledLayout>
  );
};
