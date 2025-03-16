# Frontend Utilities

This directory contains shared utility functions and helpers.

## Structure

```
utils/
├── errorHandler.ts  # Error handling utilities
├── validation.ts    # Form validation utilities
├── ai/            # AI utilities
│   ├── chat.ts     # Chat service utilities
│   ├── rag.ts      # RAG service utilities
│   └── rates.ts    # Rate optimization utilities
└── formatting.ts   # Formatting utilities
```

## Categories

### 1. Error Handling (`errorHandler.ts`)

```typescript
// Error types
export interface AppError extends Error {
  code: string;
  details?: Record<string, unknown>;
}

// Error handlers
export const handleApiError = (error: unknown): AppError => {
  if (isAxiosError(error)) {
    return {
      name: 'ApiError',
      message: error.response?.data?.message || 'API Error',
      code: error.response?.status.toString() || '500',
      details: error.response?.data,
    };
  }
  return {
    name: 'UnknownError',
    message: 'An unknown error occurred',
    code: 'UNKNOWN',
  };
};
```

### 2. Validation (`validation.ts`)

```typescript
// Validation rules
export const validationRules = {
  required: (message: string): Rule => ({
    required: true,
    message,
  }),
  email: (): Rule => ({
    type: 'email',
    message: 'Invalid email format',
  }),
};

// Form validators
export const validateForm = async (
  values: Record<string, unknown>,
  rules: ValidationRules
): Promise<ValidationErrors> => {
  // Implementation
};
```

### 3. AI Utilities (`ai/`)

```typescript
// Chat service utilities
export const formatChatMessage = (message: ChatMessage): string => {
  // Implementation
};

// RAG service utilities
export const formatRAGContext = (context: RAGContext): string => {
  // Implementation
};

// Rate optimization utilities
export const formatRateOptimization = (optimization: RateOptimization): string => {
  // Implementation
};
```

## Best Practices

### 1. Type Safety

```typescript
// Use TypeScript features
type ValidationRule<T> = (value: T) => boolean | Promise<boolean>;

interface ValidationResult {
  valid: boolean;
  errors: string[];
}
```

### 2. Error Handling

```typescript
// Consistent error handling
try {
  await apiCall();
} catch (error) {
  const appError = handleApiError(error);
  logError(appError);
  showErrorNotification(appError);
}
```

### 3. Testing

```typescript
// Unit tests for utilities
describe('validateEmail', () => {
  it('validates correct email', () => {
    expect(validateEmail('test@example.com')).toBe(true);
  });
});
```

### 4. Documentation

```typescript
/**
 * Formats a number as currency
 * @param value - The number to format
 * @param currency - The currency code (default: 'USD')
 * @returns Formatted currency string
 * 
 * @example
 * formatCurrency(1234.56) // '$1,234.56'
 */
export const formatCurrency = (
  value: number,
  currency = 'USD'
): string => {
  // Implementation
};
```

## Usage Guidelines

### 1. Error Handling

```typescript
// In components
try {
  await submitForm(data);
} catch (error) {
  const appError = handleApiError(error);
  notification.error({
    message: 'Error',
    description: appError.message,
  });
}
```

### 2. Validation

```typescript
// In forms
const validateForm = async (values: FormValues) => {
  const errors: FormErrors = {};
  
  if (!values.email) {
    errors.email = 'Email is required';
  } else if (!isValidEmail(values.email)) {
    errors.email = 'Invalid email format';
  }
  
  return errors;
};
```

### 3. Formatting

```typescript
// In components
const price = formatCurrency(product.price);
const date = formatDate(order.createdAt);
const size = formatFileSize(file.size);
```

## Adding New Utilities

1. **Create Utility File**
   ```typescript
   // utils/datetime.ts
   export const formatDate = (date: Date): string => {
     // Implementation
   };
   ```

2. **Add Types**
   ```typescript
   // utils/types.ts
   export interface DateFormatOptions {
     format: 'short' | 'long';
     timezone?: string;
   }
   ```

3. **Add Tests**
   ```typescript
   // utils/__tests__/datetime.test.ts
   describe('formatDate', () => {
     // Test cases
   });
   ```

4. **Update Documentation**
   ```typescript
   /**
    * @param date - Date to format
    * @param options - Format options
    * @returns Formatted date string
    */
   ```

## Security

### 1. Input Sanitization

```typescript
export const sanitizeHtml = (html: string): string => {
  // Implementation using DOMPurify
};
```

### 2. Data Validation

```typescript
export const validateUserInput = (input: unknown): boolean => {
  // Implementation
};
```

### 3. Error Messages

```typescript
export const sanitizeErrorMessage = (message: string): string => {
  // Remove sensitive information
};
