# API Documentation

## API Versioning

The AUL Quote App API uses semantic versioning in the URL path. Current versions:

- **v1** (Current): Base version with core functionality
- **v2** (Planned): Enhanced AI features and real-time capabilities

### Version Lifecycle
- **Beta**: Early access, subject to changes
- **Stable**: Production-ready, backwards compatible
- **Deprecated**: Scheduled for removal
- **Sunset**: No longer supported

### Version Support
- Active versions are supported for 12 months after a new version release
- Security updates are provided for 18 months
- Migration guides are provided 3 months before deprecation

## Authentication

All API endpoints require authentication using JWT tokens.

### Headers
```
Authorization: Bearer <token>
```

### Rate Limiting
- 100 requests per minute per IP
- 1000 requests per hour per user
- Bulk endpoints have separate limits

## Common Response Formats

### Success Response
```json
{
  "status": "success",
  "data": {
    // Response data
  },
  "meta": {
    "version": "1.0.0",
    "timestamp": "2025-02-12T03:38:38Z"
  }
}
```

### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "version": "1.0.0",
    "timestamp": "2025-02-12T03:38:38Z"
  }
}
```

## API Endpoints

### Customer API (v1)

#### Create Customer
**POST** `/api/v1/customers`

Create a new customer record.

**Request Body**
```json
{
  "name": "string",
  "email": "user@example.com",
  "phone": "string",
  "address": "string",
  "company_name": "string",
  "notes": "string"
}
```

**Response**
```json
{
  "status": "success",
  "data": {
    "id": "cust_123",
    "name": "string",
    "email": "user@example.com",
    "created_at": "2025-02-12T03:38:38Z"
  },
  "meta": {
    "version": "1.0.0"
  }
}
```

**Error Codes**
- `VALIDATION_ERROR`: Invalid input data
- `EMAIL_EXISTS`: Email already registered
- `RATE_LIMIT`: Too many requests

#### Get Customer
**GET** `/api/v1/customers/{customer_id}`

Retrieve customer details by ID.

**Parameters**
- `customer_id` (path): Customer unique identifier

**Response**
```json
{
  "status": "success",
  "data": {
    "id": "cust_123",
    "name": "string",
    "email": "user@example.com",
    "phone": "string",
    "address": "string",
    "company_name": "string",
    "notes": "string",
    "created_at": "2025-02-12T03:38:38Z",
    "updated_at": "2025-02-12T03:38:38Z"
  },
  "meta": {
    "version": "1.0.0"
  }
}
```

**Error Codes**
- `NOT_FOUND`: Customer not found
- `UNAUTHORIZED`: Invalid credentials
- `FORBIDDEN`: Insufficient permissions

### Quote API (v1)

#### Create Quote
**POST** `/api/v1/quotes`

Create a new quote.

**Request Body**
```json
{
  "customer_id": "cust_123",
  "service_type": "export",
  "items": [
    {
      "type": "pallet",
      "quantity": 10,
      "dangerous_goods_class": "3"
    }
  ],
  "additional_services": [
    {
      "type": "labelling",
      "quantity": 10
    }
  ],
  "dates": {
    "start_date": "2025-02-11",
    "end_date": "2025-02-25"
  }
}
```

**Response**
```json
{
  "status": "success",
  "data": {
    "quote_id": "quote_123",
    "customer_id": "cust_123",
    "total_cost": 225.00,
    "breakdown": {
      "handling": 120.00,
      "labelling": 5.00,
      "base_rate": 100.00
    },
    "currency": "AUD",
    "created_at": "2025-02-12T03:38:38Z",
    "valid_until": "2025-02-19T03:38:38Z"
  },
  "meta": {
    "version": "1.0.0",
    "ai_confidence": 0.95
  }
}
```

**Error Codes**
- `VALIDATION_ERROR`: Invalid input data
- `CUSTOMER_NOT_FOUND`: Invalid customer ID
- `RATE_UNAVAILABLE`: Rate calculation failed

#### Bulk Quote Creation
**POST** `/api/v1/quotes/bulk`

Create multiple quotes in bulk.

**Request Body**
```json
{
  "quotes": [
    {
      "quote_id": "QUOTE-001",
      "customer_id": "CUST-001",
      "requests": [
        {
          "service_type": "export",
          "items": [
            {
              "type": "pallet",
              "quantity": 10
            }
          ]
        }
      ]
    }
  ]
}
```

**Response**
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "quote_id": "QUOTE-001",
        "status": "success",
        "total_cost": 120.00,
        "currency": "AUD"
      }
    ],
    "summary": {
      "total": 1,
      "successful": 1,
      "failed": 0
    }
  },
  "meta": {
    "version": "1.0.0",
    "processing_time": "1.2s"
  }
}
```

**Error Codes**
- `PARTIAL_SUCCESS`: Some quotes failed
- `BATCH_TOO_LARGE`: Too many quotes in batch
- `RATE_LIMIT`: Too many requests

### Rate API (v1)

#### Get Rate Card
**GET** `/api/v1/rates/{rate_id}`

Get rate card details.

**Parameters**
- `rate_id` (path): Rate card identifier

**Response**
```json
{
  "status": "success",
  "data": {
    "id": "rate_123",
    "name": "Standard Storage",
    "base_rate": 5.00,
    "currency": "AUD",
    "conditions": {
      "min_quantity": 1,
      "max_quantity": 1000
    },
    "valid_from": "2025-02-12T03:38:38Z",
    "valid_until": "2025-12-31T23:59:59Z"
  },
  "meta": {
    "version": "1.0.0"
  }
}
```

**Error Codes**
- `NOT_FOUND`: Rate not found
- `EXPIRED`: Rate no longer valid
- `UNAUTHORIZED`: Invalid credentials

## Deprecation Schedule

### v1 Endpoints
- All v1 endpoints are currently stable
- No deprecations planned

### Future Changes (v2)
Planned for Q3 2025:
- Enhanced AI quote generation
- Real-time rate updates
- Improved bulk operations
- WebSocket integration

## Best Practices

### Rate Limiting
- Implement exponential backoff
- Cache responses when possible
- Use bulk endpoints for multiple operations

### Error Handling
- Always check error responses
- Implement retry logic with backoff
- Log correlation IDs for debugging

### Security
- Rotate API keys regularly
- Use HTTPS for all requests
- Validate all input data

## Support

For API support:
- Email: api-support@aulogistics.com
- Documentation: https://docs.aulogistics.com
- Status: https://status.aulogistics.com
