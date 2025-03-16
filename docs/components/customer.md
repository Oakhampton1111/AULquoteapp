# Customer Component

## Overview

The Customer component manages customer profiles, metrics, and preferences in the warehouse quote system. It provides a comprehensive suite of tools for customer relationship management and analytics.

## Interface Definition

### Props

```typescript
interface CustomerProps {
  // Core props
  customerId: string;
  initialData?: CustomerData;
  onUpdate?: (customer: CustomerData) => Promise<void>;
  
  // Optional props
  showMetrics?: boolean;
  enableEditing?: boolean;
  className?: string;
  
  // Event handlers
  onError?: (error: Error) => void;
  onStatusChange?: (status: CustomerStatus) => void;
}

interface CustomerData {
  id: string;
  name: string;
  email: string;
  phone: string;
  address: string;
  company_name: string;
  notes: string;
  preferences: CustomerPreferences;
  metrics: CustomerMetrics;
}

interface CustomerPreferences {
  preferred_contact_method: 'email' | 'phone' | 'sms';
  notification_preferences: string[];
  special_requirements: string;
}

interface CustomerMetrics {
  total_quotes: number;
  accepted_quotes: number;
  total_spent: number;
  last_activity: Date;
}
```

### Events

```typescript
interface CustomerEvents {
  // Lifecycle events
  onMount: () => void;
  onUnmount: () => void;
  
  // Data events
  onDataChange: (data: CustomerData) => void;
  onPreferenceUpdate: (prefs: CustomerPreferences) => void;
  
  // Status events
  onStatusChange: (status: CustomerStatus) => void;
  onError: (error: Error) => void;
}
```

### Public Methods

```typescript
interface CustomerMethods {
  // Data methods
  refresh(): Promise<void>;
  update(data: Partial<CustomerData>): Promise<void>;
  
  // UI methods
  scrollToSection(section: string): void;
  toggleEditMode(): void;
  
  // State methods
  reset(): void;
  validate(): boolean;
}
```

## Architecture

### Models

#### Customer Model (`app/models/customer.py`)
- Basic customer information (name, email, phone)
- Metrics tracking (quotes, spending)
- Preference management
- Relationship mappings
- Audit fields:
  - Created date
  - Updated date
  - Last activity
  - Status

### Services

#### Customer Service (`app/services/customer.py`)
- Core customer management
- Dashboard functionality
- Preference management
- Metric calculations
- Integration with notification system

#### Analytics Service (`app/services/analytics/customer.py`)
- Customer metrics
- Quote analytics
- Spending analysis
- Activity tracking

### Integration

#### Notification Service (`app/services/notification.py`)
- Email notifications
- SMS alerts
- Preference-based delivery
- Template management

#### Quote Service (`app/services/quote.py`)
- Quote relationship
- Quote history
- Spending calculation
- Activity tracking

## Dependencies

### Direct Dependencies
```json
{
  "frontend": {
    "@mui/material": "^5.15.0",
    "@mui/icons-material": "^5.15.0",
    "react-query": "^3.39.0",
    "date-fns": "^2.30.0",
    "yup": "^1.3.2"
  },
  "backend": {
    "fastapi": "^0.104.0",
    "sqlalchemy": "^2.0.23",
    "pydantic": "^2.4.2"
  }
}
```

### Internal Dependencies
- `QuoteList` component for displaying customer quotes
- `MetricsDisplay` component for showing customer metrics
- `AddressForm` component for address input
- `PreferencesEditor` for managing preferences

### Services
- `CustomerService` for data operations
- `NotificationService` for customer notifications
- `MetricsService` for analytics
- `ValidationService` for input validation

## Features

### Profile Management
- Create and update profiles
- Contact information
- Business details
- Document management
- Activity history

### Analytics Dashboard
- Quote metrics
- Spending analysis
- Activity tracking
- Custom widgets
- Data visualization

### Preference Management
- Contact preferences
- Notification settings
- Quote defaults
- UI customization
- Privacy settings

### Integration Features
- CRM integration
- Quote management
- Document storage
- Notification system
- Analytics platform

## Usage Examples

### Creating a Customer
```python
customer_data = CustomerCreate(
    name="John Doe",
    email="john@example.com",
    phone="+1234567890",
    preferences={"contact_method": "email"}
)
customer = await customer_service.create_customer(customer_data)
```

### Managing Preferences
```python
preferences = CustomerPreferences(
    contact_method="email",
    notifications=["quotes", "invoices"],
    frequency="daily"
)
await customer_service.update_preferences(customer_id=1, preferences=preferences)
```

### Getting Analytics
```python
analytics = await analytics_service.get_customer_metrics(
    customer_id=1,
    period="last_30_days"
)
```

## Testing

### Test Structure
```
tests/
├── api/
│   └── customer/           # Customer API tests
│       └── test_endpoints.py  # API endpoint tests
└── unit/
    └── customer/           # Customer unit tests
        ├── test_service.py    # Service tests
        └── test_analytics.py  # Analytics tests
```

### Test Coverage

#### Unit Tests
- Customer creation and validation
- Preference management
- Metric calculations
- Dashboard functionality
- Integration points

#### API Tests
- CRUD operations
- Preference updates
- Analytics retrieval
- Error handling
- Authorization

#### Integration Tests
- Quote integration
- Notification delivery
- Analytics calculation
- Document management
- CRM sync

## API Endpoints

### Profile Management
- `GET /api/v1/customers`
  - List customers with filters
  - Query params: status, type, search
  - Returns: Paginated customer list

- `POST /api/v1/customers`
  - Create new customer
  - Body: Customer details
  - Returns: Created customer

- `GET /api/v1/customers/{id}`
  - Get customer details
  - Returns: Full customer profile

- `PUT /api/v1/customers/{id}`
  - Update customer
  - Body: Updated details
  - Returns: Updated customer

### Analytics
- `GET /api/v1/customers/{id}/analytics`
  - Get customer analytics
  - Query params: period, metrics
  - Returns: Analytics data

### Preferences
- `GET /api/v1/customers/{id}/preferences`
  - Get customer preferences
  - Returns: Current preferences

- `PUT /api/v1/customers/{id}/preferences`
  - Update preferences
  - Body: New preferences
  - Returns: Updated preferences

## State Management

### Local State
```typescript
interface CustomerState {
  loading: boolean;
  error: Error | null;
  data: CustomerData | null;
  editMode: boolean;
  dirtyFields: Set<string>;
}
```

### Global State
- Customer preferences in Redux store
- Authentication state for permissions
- Theme settings for UI customization

### Cache Strategy
- Customer data cached with React Query
- Metrics cached for 5 minutes
- Preferences cached until changed

## Error Handling

### Error Types
```typescript
type CustomerError =
  | 'VALIDATION_ERROR'
  | 'API_ERROR'
  | 'NETWORK_ERROR'
  | 'PERMISSION_ERROR';

interface CustomerErrorHandler {
  type: CustomerError;
  message: string;
  retry?: () => Promise<void>;
  fallback?: () => void;
}
```

### Recovery Strategies
- Automatic retry for network errors
- Form validation recovery
- State rollback on failure
- Error boundary fallbacks

## Performance

### Optimizations
- Lazy loading of heavy features
- Debounced updates
- Memoized calculations
- Virtual scrolling for lists

### Metrics
- Time to interactive < 200ms
- Update latency < 100ms
- Memory usage < 5MB
- Bundle size < 50KB

## Accessibility

### ARIA Attributes
- Proper role assignments
- State announcements
- Focus management
- Keyboard navigation

### Standards
- WCAG 2.1 AA compliant
- Screen reader support
- High contrast support
- Keyboard accessible

## Future Enhancements

1. Advanced Features
   - AI-powered suggestions
   - Advanced analytics
   - Custom dashboards
   - Bulk operations

2. Technical Improvements
   - GraphQL integration
   - Real-time updates
   - Enhanced caching
   - Performance optimizations

## Related Documentation
- [API Documentation](../api.md)
- [Testing Guide](../TESTING.md)
- [Security Guidelines](../SECURITY.md)
- [Performance Guide](../PERFORMANCE.md)
