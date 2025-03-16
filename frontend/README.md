# AUL Quote App Frontend

Modern React frontend for the AUL Quote App, built with Vite, TypeScript, and Ant Design.

## Features

- ⚡️ Vite - Lightning fast builds
- 🎨 Ant Design - Beautiful UI components
- 📝 TypeScript - Type safety
- 🔄 React Query - Data fetching and caching
- 🎯 React Router - Client-side routing
- 💅 Styled Components - CSS-in-JS styling
- 🛡️ Enhanced Authentication System
- 🔍 Smart Form Validation
- ⚠️ Comprehensive Error Handling
- 📊 Interactive Dashboards
- 🤖 AI-Powered Quote Generation and Rate Optimization
- 📧 Real-time Notifications
- 👥 Customer Management
- 💰 Rate Card Management
- 🎭 Role-based Navigation
- 💫 Skeleton Loading States

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm test

# Run E2E tests
npm run test:e2e
```

## Project Structure

```
src/
├── components/           # Reusable components
│   ├── admin/           # Admin-specific components
│   │   ├── QuoteManager/    # Quote management
│   │   ├── RateManager/     # Rate card management
│   │   └── Reports/         # Admin reports
│   ├── auth/            # Authentication components
│   │   ├── AuthProvider.tsx # Auth context provider
│   │   ├── LoginForm.tsx    # Login form with reset
│   │   ├── ProtectedRoute.tsx # Route protection
│   │   └── ResetPassword.tsx # Password reset
│   ├── common/          # Shared components
│   │   ├── ErrorBoundary.tsx  # Error handling
│   │   ├── LoadingState.tsx   # Loading states
│   │   └── BaseLayout.tsx     # Layout wrapper
│   ├── customer/        # Customer components
│   │   ├── QuoteForm/      # Quote creation
│   │   └── Dashboard/      # Customer dashboard
│   ├── navigation/      # Navigation components
│   │   └── MainNav.tsx     # Main navigation
│   ├── forms/           # Form components
│   └── ai/              # AI Components (LLM integration)
│       ├── chat/         # Chat service
│       ├── rag/          # RAG service
│       └── rates/        # Rate optimization
├── hooks/              # Custom React hooks
│   ├── useAuth.ts      # Authentication hooks
│   ├── useQuotes.ts    # Quote management hooks
│   └── useRateCards.ts # Rate card hooks
├── services/           # API and business logic
│   ├── api/           # API clients
│   │   ├── apiClient.ts # Base API client
│   │   ├── quotes.ts    # Quote endpoints
│   │   └── rates.ts     # Rate endpoints
│   ├── llm/          # LLM integration
│   │   ├── chat.ts     # Chat service
│   │   ├── rag.ts      # RAG service
│   │   └── rates.ts    # Rate optimization
│   └── utils/         # Utility functions
├── types/             # TypeScript types
├── styles/             # Theme and styling
│   ├── theme.ts        # Theme configuration
│   ├── GlobalStyles.ts # Global styles
│   └── animations.ts   # Animation keyframes
└── pages/             # Page components
    ├── admin/         # Admin pages
    └── customer/      # Customer pages
```

## Architecture

The frontend follows a modular, component-based architecture:

### Directory Structure

```
src/
├── api/          # API integration layer
├── assets/       # Static assets (images, fonts)
├── components/   # Reusable UI components
│   ├── admin/    # Admin-specific components
│   ├── auth/     # Authentication components
│   ├── client/   # Client-facing components
│   ├── common/   # Shared components
│   ├── forms/    # Form components
│   ├── layout/   # Layout components
│   ├── ai/       # AI Components (LLM integration)
│   └── navigation/ # Navigation components
├── hooks/        # Custom React hooks
├── pages/        # Route components
├── services/     # Business logic services
├── store/        # Global state management
│   ├── queries/  # React Query configurations
│   └── slices/   # Redux slices
├── styles/       # Global styles and themes
├── types/        # TypeScript type definitions
└── utils/        # Utility functions
```

### Component Architecture

1. **Component Types**
   - Page Components (routes)
   - Feature Components (business logic)
   - Common Components (reusable UI)
   - Layout Components (structure)
   - AI Components (LLM integration)

2. **Component Structure**
   ```typescript
   ComponentName/
   ├── index.ts           # Main export
   ├── Component.tsx      # Implementation
   ├── Component.test.tsx # Tests
   ├── styles.ts          # Styled components
   ├── types.ts          # TypeScript types
   └── hooks.ts          # Custom hooks
   ```

3. **Component Guidelines**
   - Single responsibility
   - Prop type validation
   - Error boundaries
   - Loading states
   - Accessibility
   - Documentation

### State Management

1. **Server State** (React Query)
   ```typescript
   // API data management
   const { data, isLoading } = useQuery(['key'], fetchData);
   ```

2. **Global State** (Redux Toolkit)
   ```typescript
   // Application state
   const dispatch = useDispatch();
   const data = useSelector(selectData);
   ```

3. **Local State** (React)
   ```typescript
   // Component state
   const [state, setState] = useState(initial);
   ```

### Utility Organization

1. **Error Handling**
   ```typescript
   // Centralized error handling
   import { handleApiError } from '@/utils/errorHandler';
   ```

2. **Validation**
   ```typescript
   // Form validation
   import { validateForm } from '@/utils/validation';
   ```

3. **Formatting**
   ```typescript
   // Data formatting
   import { formatCurrency } from '@/utils/formatting';
   ```

## Theme System

The application uses a comprehensive theme system built with Ant Design and styled-components:

### Theme Configuration

The theme system is organized into three main files:

1. **theme.ts**: Central theme configuration
   - Defines color palette, typography, and spacing
   - Configures Ant Design component styles
   - Ensures consistent design tokens across the app

2. **GlobalStyles.ts**: Global style definitions
   - Sets base styles for HTML elements
   - Applies consistent typography
   - Handles responsive design adjustments
   - Overrides Ant Design default styles

3. **animations.ts**: Reusable animations
   - Defines keyframe animations
   - Provides animation presets
   - Includes helper functions for custom animations

### Usage Example

```typescript
// Using theme tokens
import { appTheme } from '@/styles/theme';
import styled from 'styled-components';

const StyledComponent = styled.div`
  color: ${appTheme.token.colorPrimary};
  border-radius: ${appTheme.token.borderRadius}px;
`;

// Using animations
import { animations } from '@/styles/animations';

const AnimatedComponent = styled.div`
  ${animations.fadeIn}
  // Or custom animation:
  animation: ${animations.createAnimation(animations.slideInFromRight, '0.5s')}
`;
```

### Theme Customization

To modify the theme:

1. Update token values in `src/styles/theme.ts`
2. Adjust global styles in `src/styles/GlobalStyles.ts`
3. Add new animations in `src/styles/animations.ts`

The theme system automatically propagates changes throughout the application.

## Build System

The frontend uses a modern build system based on Vite:

### Configuration

1. **Package Management**
   ```json
   {
     "name": "@aul-quote-app/frontend",
     "version": "1.0.0",
     "type": "module"
   }
   ```

2. **Build Tools**
   - Vite for development and production builds
   - TypeScript for type checking
   - ESLint and Prettier for code quality

3. **Development Server**
   ```typescript
   // vite.config.ts
   export default defineConfig({
     plugins: [react()],
     resolve: {
       alias: {
         '@': '/src',
         '@shared': '/shared'
       }
     },
     server: {
       port: 3000,
       proxy: {
         '/api': 'http://localhost:8000'
       }
     }
   });
   ```

### Scripts

```bash
# Development
yarn start          # Start dev server
yarn build         # Production build
yarn preview       # Preview production build

# Testing
yarn test          # Run all tests
yarn test:unit     # Run unit tests
yarn test:e2e      # Run E2E tests
yarn test:coverage # Run tests with coverage

# Code Quality
yarn lint          # Run ESLint
yarn lint:fix      # Fix ESLint issues
yarn format        # Run Prettier
yarn format:check  # Check formatting
yarn type-check    # Run TypeScript checks

# Maintenance
yarn clean         # Clean build artifacts
```

### Dependencies

1. **Runtime Dependencies**
   - React and React DOM
   - Ant Design for UI components
   - React Router for routing
   - React Query for data fetching
   - Redux Toolkit for state management

2. **Development Dependencies**
   - TypeScript for type checking
   - Jest for unit testing
   - Playwright for E2E testing
   - ESLint for linting
   - Prettier for formatting

### Integration

The frontend build system is integrated with:

1. **Monorepo Structure**
   - Yarn Workspaces for package management
   - Shared code dependencies
   - Consistent versioning

2. **Backend Integration**
   - API proxy configuration
   - Shared type definitions
   - Environment configuration

3. **CI/CD Pipeline**
   - Automated testing
   - Build verification
   - Deployment checks

### Best Practices

1. **Development**
   - Fast refresh enabled
   - Source maps for debugging
   - Hot module replacement
   - Error overlay

2. **Production**
   - Code splitting
   - Tree shaking
   - Minification
   - Cache optimization

3. **Testing**
   - Unit test coverage
   - E2E test scenarios
   - Visual regression tests
   - Performance testing

4. **Maintenance**
   - Regular dependency updates
   - Security audits
   - Version management
   - Documentation updates

## Authentication System

The authentication system has been enhanced with:
- Unified `AuthProvider` for state management
- Token-based authentication with secure storage
- Role-based access control
- Password reset functionality
- Enhanced error handling
- Persistent session management

## Component Architecture

### Layout Components
- `BaseLayout`: Main layout wrapper with error boundary
- `ErrorBoundary`: Enhanced error handling with retry
- `LoadingState`: Skeleton loading support
- `MainNav`: Role-based navigation

### Form Components
- Smart validation with error messages
- Real-time field validation
- TypeScript type safety
- Reusable form elements

### Admin Components
- Enhanced quote management
- Rate card configuration
- Report generation
- User management

### Customer Components
- Interactive quote creation
- Dashboard with analytics
- Profile management
- Document handling

## Environment Variables

Create a `.env.local` file:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=AUL Quote App
```

## Error Handling

- Global error boundary
- API error handling
- Form validation errors
- Network error recovery
- User-friendly error messages

## State Management

- React Query for server state
- Context for auth state
- Local state for UI
- Persistent storage

## Testing

### Test Structure

```
tests/
├── components/          # Component tests
│   ├── admin/          # Admin component tests
│   │   ├── QuoteManager.test.tsx
│   │   ├── RateManager.test.tsx
│   │   └── Reports.test.tsx
│   ├── auth/           # Auth component tests
│   │   ├── LoginForm.test.tsx
│   │   └── ResetPassword.test.tsx
│   └── common/         # Common component tests
├── e2e/               # End-to-end tests
│   ├── auth.spec.ts   # Auth flows
│   ├── quotes.spec.ts # Quote flows
│   └── admin.spec.ts  # Admin flows
├── hooks/             # Hook tests
├── utils/             # Utility tests
└── __mocks__/         # Test mocks
```

### Running Tests

```bash
# Run unit tests
npm test

# Run unit tests with coverage
npm test -- --coverage

# Run E2E tests
npm run test:e2e

# Run E2E tests in UI mode
npm run test:e2e:ui
```

For more details on testing, see the main project [Testing Guide](../docs/TESTING.md).

## Performance

- Code splitting
- Lazy loading
- Memoization
- Skeleton loading
- Efficient re-renders

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT License - see LICENSE for details
