# Business Services

This directory contains the core business logic services for the Warehouse Quote Application. These services handle various calculations, validations, and business rules required for generating accurate quotes.

## Services Overview

### Rate Calculator (`rate_calculator.py`)
- Handles storage rate calculations
- Supports different storage types (standard, climate-controlled, hazardous)
- Applies appropriate surcharges and handling fees
- Calculates volume-based pricing

### Container Calculator (`container_calculator.py`)
- Specializes in container packing service calculations
- Supports both commercial and personal effects packing
- Handles different container sizes (20ft, 40ft)
- Calculates packing material costs and surcharges

### Distance Calculator (`distance_calculator.py`)
- Calculates distances between Australian postcodes
- Determines appropriate transport types based on zones
- Provides zone information for postcodes
- Uses the Haversine formula for distance calculations

### Transport Calculator (`transport_calculator.py`)
- Handles all transport-related rate calculations
- Supports local, long-haul, and container transport types
- Calculates fuel surcharges and terminal fees
- Validates transport requests and generates follow-up questions

### Rule Engine (`rule_engine.py`)
- Enforces business rules and validates service combinations
- Generates clarifying questions based on business rules
- Applies special rules based on context
- Provides natural language messages for rule violations

## Integration with Other Services

These business services are used by various other components in the application:

- **Quote Generator**: Uses these services to generate comprehensive quotes
- **Rate Admin Service**: Manages the rates used by these calculators
- **Conversation Services**: Integrates with these services to handle natural language queries

## Usage Example

```python
from warehouse_quote_app.app.services.business.rate_calculator import RateCalculator, StorageRequest, ServiceDimensions

# Create a calculator instance
calculator = RateCalculator()

# Create a storage request
request = StorageRequest(
    dimensions=ServiceDimensions(length=2.0, width=3.0, height=2.5),
    duration_weeks=4,
    quantity=2,
    storage_type="standard",
    has_dangerous_goods=False
)

# Calculate storage rate
result = calculator.calculate_storage_rate(request)

# Process the result
for item in result.line_items:
    print(f"{item['description']}: ${item['total']}")

print(f"Total: ${float(result.total_amount)}")
```

## Maintenance and Extension

When modifying these services:

1. Ensure all rate changes are properly documented
2. Update validation logic when adding new service types
3. Maintain backward compatibility with existing quote generation
4. Add comprehensive tests for new functionality

For more information on the rate rules and technical specifications, see the documentation in the `docs` directory.
