import React from 'react';
import { Menu, Button, Dropdown, Space, Avatar } from 'antd';
import {
  HomeOutlined,
  FileTextOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  DollarOutlined,
  TeamOutlined,
  ShopOutlined,
  ContactsOutlined,
  FundOutlined,
} from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useLogout } from '../../hooks/useAuth';
import { User } from '../../types/user';

const StyledNav = styled.nav`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
`;

const Logo = styled(Link)`
  font-size: 20px;
  font-weight: bold;
  color: #1890ff;
  text-decoration: none;
`;

interface MainNavProps {
  user: User | null;
}

export const MainNav: React.FC<MainNavProps> = ({ user }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const logout = useLogout();

  const isAdmin = user?.roles.includes('admin');

  const items = [
    {
      key: '/dashboard',
      icon: <HomeOutlined />,
      label: <Link to="/dashboard">Dashboard</Link>,
    },
    {
      key: '/quotes',
      icon: <FileTextOutlined />,
      label: <Link to="/quotes">Quotes</Link>,
    },
    ...(isAdmin
      ? [
          {
            key: 'crm',
            icon: <ShopOutlined />,
            label: 'CRM',
            children: [
              {
                key: '/crm/dashboard',
                icon: <FundOutlined />,
                label: <Link to="/crm/dashboard">Dashboard</Link>,
              },
              {
                key: '/crm/customers',
                icon: <ContactsOutlined />,
                label: <Link to="/crm/customers">Customers</Link>,
              },
              {
                key: '/crm/deals',
                icon: <DollarOutlined />,
                label: <Link to="/crm/deals">Deals</Link>,
              },
            ],
          },
          {
            key: '/customers',
            icon: <TeamOutlined />,
            label: <Link to="/customers">Customers</Link>,
          },
          {
            key: '/rate-cards',
            icon: <DollarOutlined />,
            label: <Link to="/rate-cards">Rate Cards</Link>,
          },
        ]
      : []),
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      onClick: () => navigate('/profile'),
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      onClick: () => navigate('/settings'),
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: logout,
    },
  ];

  const userMenu = (
    <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
      <Space style={{ cursor: 'pointer' }}>
        <Avatar icon={<UserOutlined />} />
        <span>{user?.name}</span>
      </Space>
    </Dropdown>
  );

  return (
    <StyledNav>
      <Logo to="/dashboard">AUL Quote App</Logo>
      <Menu
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={items}
        style={{ flex: 1, justifyContent: 'center' }}
      />
      {user && userMenu}
    </StyledNav>
  );
};
