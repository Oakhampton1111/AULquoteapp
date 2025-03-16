import { ThemeConfig } from 'antd';

export const appTheme: ThemeConfig = {
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 4,
    colorBgLayout: '#f5f5f5',
    colorBgContainer: '#ffffff',
    boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
    fontFamily: "'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif",
  },
  components: {
    Layout: {
      headerBg: '#ffffff',
      headerHeight: 64,
      headerPadding: '0 24px',
    },
    Menu: {
      itemHeight: 40,
      activeBarBorderWidth: 3,
    },
  },
};
