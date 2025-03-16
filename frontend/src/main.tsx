import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ConfigProvider } from 'antd'
import { appTheme } from './styles/theme'
import { GlobalStyles } from './styles/GlobalStyles'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider theme={appTheme}>
      <GlobalStyles />
      <App />
    </ConfigProvider>
  </StrictMode>,
)
