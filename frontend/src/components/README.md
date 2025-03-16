# Component Architecture

This directory contains all React components organized by domain and responsibility.

## Structure

```
components/
├── admin/       # Admin-specific components
├── auth/        # Authentication components
├── client/      # Client-facing components
├── common/      # Shared components
├── forms/       # Form components
├── layout/      # Layout components
├── ai/         # AI Integration components
│   ├── chat/    # Chat service components
│   ├── rag/     # RAG service components
│   └── rates/   # Rate optimization components
└── navigation/  # Navigation components
```

## Component Guidelines

### 1. Component Structure

Every component should follow this structure:
```typescript
// imports
import React from 'react';
import type { ComponentProps } from './types';
import { useComponentLogic } from './hooks';
import { StyledComponent } from './styles';

// component
export const Component: React.FC<ComponentProps> = ({ prop1, prop2 }) => {
  // hooks
  const { data, actions } = useComponentLogic();

  // render
  return (
    <StyledComponent>
      {/* component content */}
    </StyledComponent>
  );
};
```

### 2. File Organization

Each component directory should contain:
```
ComponentName/
├── index.ts           # Main export
├── Component.tsx      # Component implementation
├── Component.test.tsx # Component tests
├── styles.ts          # Styled components
├── types.ts          # TypeScript types
└── hooks.ts          # Custom hooks
```

### 3. Component Types

1. **Page Components** (`pages/`)
   - Route components
   - Layout composition
   - Data fetching
   - State management

2. **Feature Components** (`admin/`, `client/`)
   - Business logic
   - Complex state
   - API integration
   - Event handling

3. **Common Components** (`common/`)
   - Reusable UI elements
   - No business logic
   - Prop-driven
   - Highly composable

4. **Layout Components** (`layout/`)
   - Page structure
   - Responsive design
   - Theme integration
   - Navigation state

5. **AI Components** (`ai/`)
   - LLM integration
   - Chat interface
   - RAG service
   - Rate optimization
   - Model state management
   - Response streaming

### 4. Best Practices

1. **Component Design**
   - Single responsibility
   - Prop type validation
   - Default props
   - Error boundaries
   - Loading states
   - Accessibility

2. **State Management**
   - Local state for UI
   - Redux for global state
   - React Query for server state
   - Context for theme/auth

3. **Performance**
   - Memoization
   - Code splitting
   - Lazy loading
   - Bundle optimization

4. **Testing**
   - Unit tests
   - Integration tests
   - Snapshot tests
   - Accessibility tests

### 5. Style Guidelines

1. **CSS Organization**
   ```typescript
   // styles.ts
   export const StyledComponent = styled.div`
     // Layout
     display: flex;
     position: relative;

     // Spacing
     margin: ${theme.spacing.md};
     padding: ${theme.spacing.sm};

     // Visual
     background: ${theme.colors.background};
     border-radius: ${theme.radius.md};

     // Typography
     font-size: ${theme.text.md};
     color: ${theme.colors.text};

     // Animation
     transition: all 0.2s ease;
   `;
   ```

2. **Theme Integration**
   - Use theme variables
   - Responsive design
   - Dark mode support
   - Accessibility

3. **Styled Components**
   - Semantic naming
   - Component composition
   - Props API
   - Global styles

### 6. Documentation

Each component should have:
1. JSDoc comments
2. Props documentation
3. Usage examples
4. Edge cases
5. Performance notes

Example:
```typescript
/**
 * DataTable component for displaying and managing tabular data.
 * 
 * @example
 * ```tsx
 * <DataTable
 *   data={items}
 *   columns={columns}
 *   onSort={handleSort}
 *   loading={isLoading}
 * />
 * ```
 */
export const DataTable: React.FC<DataTableProps> = ({
  data,
  columns,
  onSort,
  loading,
}) => {
  // implementation
};
