# Conversation Test Specification

## Overview
This document outlines test cases for the quote system's conversation handling, including standard flows and edge cases. Each test case includes expected inputs, outputs, and handling procedures.

## Standard Flow Test Cases

### Test Case 1: Standard Business Storage
**Scenario**: Construction company requiring machinery storage
```yaml
Input:
  - Storage Type: Heavy machinery
  - Floor Space: 500m²
  - Duration: 6 months
  - DG Items: 8 (lithium batteries)
  - Oversized Items: 2 cranes
  - Storage Type: Mixed (floor + racking)

Expected Calculations:
  - Base Storage: $2.50/m²/week × 500m² × 26 weeks = $32,500
  - DG Handling: $15/item × 8 items = $120
  - Free Period: First 2 weeks
  
Expected Response:
  - Total Cost: $32,620
  - Required Notifications:
    - DG handling procedures
    - Oversized item accommodation
    - Free period application
```

## Edge Case Test Cases

### Test Case 2: Non-English Speaker
**Scenario**: Japanese customer requiring machine storage
```yaml
Input:
  - Language: Japanese
  - Storage Type: Heavy machinery
  - Dimensions: 5m × 4m × 3m (60m³)
  - Duration: 3 months
  - Features: Battery (DG), Heavy equipment

Expected Handling:
  - Use simple English with Japanese translations
  - Employ visual aids (icons, diagrams)
  - Break down complex terms
  
Expected Calculations:
  - Volume Storage: $4/m³/week × 60m³ × 13 weeks = $3,120
  - DG Handling: $25
  - Heavy Equipment Fee: $150
  
Expected Response:
  - Total Cost: $2,335
  - Dual language key points
  - Visual breakdowns
```

### Test Case 3: Extreme Dimensions
**Scenario**: Aircraft component storage
```yaml
Input:
  - Dimensions: 45m × 12m × 8m (4,320m³)
  - Duration: 2 weeks
  - Special Requirements:
    - Indoor storage
    - Composite materials
    - Aviation fuel residue

Expected Handling:
  - Escalation triggers:
    - Volume > 1,000m³
    - Class A hazardous materials
    - Specialized facility requirement

Expected Calculations:
  - Base Storage: $4/m³/week × 4,320m³ × 2 weeks = $34,560
  - Hazmat Handling: $2,500
  - Special Facility: $5,000
  - Environmental Compliance: $1,800
  
Expected Response:
  - Total Cost: $43,860
  - Escalation to specialist team
  - Required certifications list
```

### Test Case 4: Incomplete Information
**Scenario**: Residential customer with vague requirements
```yaml
Input:
  - Initial Request: Minimal information
  - Storage Type: Household items (determined through conversation)
  - Size: "Medium" (guided to 40m²)
  - Duration: 1 month

Expected Handling:
  - Progressive information gathering
  - Size visualization aids
  - Category-based guidance
  
Expected Calculations:
  - Base Storage: 40m² × standard rate
  - Free Period: 2 weeks included
  
Expected Response:
  - Total Cost: $400/month
  - Additional service options
  - Visual size comparisons
```

## Test Validation Criteria

### Response Time Requirements
- Initial Response: < 5 seconds
- Calculation Response: < 3 seconds
- Follow-up Questions: < 2 seconds

### Accuracy Requirements
- Pricing Calculations: Within 0.1% of expected values
- Volume Calculations: Accepted variance < $0.30
- Currency Display: Always 2 decimal places

### Language Support Requirements
- Clear communication despite language barriers
- Essential information in dual languages
- Use of universal symbols and icons

### Edge Case Handling Requirements
- Automatic escalation for oversized items
- Clear documentation of special requirements
- Proper handling of regulatory requirements

## Test Execution

### Prerequisites
1. Rate calculator configuration loaded
2. Current pricing matrix available
3. Language support modules active
4. Regulatory compliance rules updated

### Test Steps
1. Execute each test case independently
2. Verify calculations against expected results
3. Validate response formatting and clarity
4. Check escalation triggers and routing
5. Verify all required notifications are present

### Success Criteria
- All calculations within specified variance
- Proper escalation of edge cases
- Clear communication regardless of language
- Appropriate handling of incomplete information
- Correct application of business rules
