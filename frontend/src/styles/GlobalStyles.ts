import { createGlobalStyle } from 'styled-components';
import { appTheme } from './theme';

export const GlobalStyles = createGlobalStyle`
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  html {
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  body {
    font-family: ${appTheme.token.fontFamily};
    background-color: ${appTheme.token.colorBgLayout};
    color: rgba(0, 0, 0, 0.85);
    line-height: 1.5;
  }

  #root {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  h1, h2, h3, h4, h5, h6 {
    margin-bottom: 0.5em;
    color: rgba(0, 0, 0, 0.85);
    font-weight: 500;
  }

  p {
    margin-bottom: 1em;
  }

  a {
    color: ${appTheme.token.colorPrimary};
    text-decoration: none;
    transition: color 0.3s ease;

    &:hover {
      color: ${appTheme.token.colorPrimary}E6;
    }
  }

  img {
    max-width: 100%;
    height: auto;
  }

  /* Ant Design overrides */
  .ant-layout {
    background: ${appTheme.token.colorBgLayout};
  }

  .ant-layout-header {
    height: ${appTheme.components.Layout.headerHeight}px;
    padding: ${appTheme.components.Layout.headerPadding};
    background: ${appTheme.components.Layout.headerBg};
  }

  .ant-menu-item {
    height: ${appTheme.components.Menu.itemHeight}px;
    line-height: ${appTheme.components.Menu.itemHeight}px;
  }

  /* Responsive adjustments */
  @media (max-width: 768px) {
    html {
      font-size: 14px;
    }

    .ant-layout-content {
      padding: 16px;
      margin: 16px 8px;
    }
  }
`;
