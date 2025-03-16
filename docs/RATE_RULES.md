# Rate Rules and Relationships

## Mandatory Charges and Dependencies

### Transport-Related Mandatory Charges
Any transport service automatically includes the following mandatory charges:
1. **Fuel Surcharge**
   - Applied to all transport services
   - Current rate: 19.67% on cartage rates
   - Applies to:
     - Container Side Loader Cartage
     - Local Transport (24% for Semi-Trailer and B-Double)
     - Long Haul Transport (15% for both Semi-Trailer and B-Double)

2. **Road Tolls**
   - Mandatory $50.00 charge
   - Applied to all transport services
   - Non-negotiable component

### Service Exclusions and Special Rules

1. **Container Packing Exclusions**
   - HANDLING OUT charges are NEVER applied to container packing services
   - This applies to:
     - 20FT Container Packing
     - 40FT Container Packing
     - Personal Effects Container Packing

## Rate Dependencies and Relationships

### Storage Services
1. **Standard Pallet Storage (Internal)**
   - Base rate: $5.00 per pallet per week
   - Dependencies:
     - Handling In charges apply
     - Handling Out charges apply
     - DG surcharges if applicable

2. **Oversize Cargo Storage**
   - Internal: $4.00 per SQM/CBM per week
   - External: $3.00 per SQM/CBM per week
   - Common dependencies:
     - 2 weeks free storage period
     - Handling charges based on SQM/CBM
     - DG surcharges if applicable

3. **External Pallet Storage**
   - Rate: $3.50 per pallet per week
   - Dependencies:
     - 2 weeks free storage period
     - Standard handling charges apply
     - DG surcharges if applicable

### Container Services
1. **Container Packing**
   - 20FT Base Rate: $350.00
   - 40FT Base Rate: $540.00
   - Quantity breakpoints:
     - Over 400 items: +$150.00
     - Over 800 items (40FT only): +$275.00
   - NO Handling Out charges apply
   - Dependencies:
     - DG surcharges if applicable ($7.50 per piece)
     - Container transport charges if required
     - Packing materials as needed

2. **Personal Effects**
   - 20FT: $700.00
   - 40FT: $1,100.00
   - Special considerations:
     - Different pricing from standard commercial packing
     - NO Handling Out charges apply
     - May require special documentation

### Transport Services
1. **Container Transport**
   - Always includes:
     - Base rate
     - Fuel surcharge (19.67%)
     - Road tolls ($50.00)
   - Additional mandatory charges if applicable:
     - Terminal fees (at carrier's cost)
     - Overweight surcharges
     - VGM/CWD fees

2. **Local Transport**
   - Always includes:
     - Base hourly rate
     - 24% fuel surcharge
     - Road tolls
     - Minimum 4-hour charge

3. **Long Haul Transport**
   - Always includes:
     - Base per-km rate (both ways)
     - 15% fuel surcharge
     - Road tolls
     - Return journey charges

## Unit Standardization
1. **Time-based Units**
   - per_week
   - per_week_or_part (for container storage)
   - per_hour (for labor and waiting time)

2. **Volume/Weight Units**
   - per_pallet
   - per_sqm_cbm (for oversize cargo)
   - per_kg_chargeable (for air cargo)

3. **Container Units**
   - per_container (20ft or 40ft specific)
   - per_piece (for DG surcharges)

4. **Distance Units**
   - per_km_both_ways (for long haul transport)

## Service Type Categories
1. **Storage**
   - Internal Storage
   - External Storage
   - Container Storage

2. **Handling**
   - Standard Handling
   - Oversize Handling
   - Container Packing

3. **Transport**
   - Container Transport
   - Local Transport
   - Long Haul
   - Air Cargo

4. **Additional Services**
   - DG Handling
   - Labelling
   - Re-weighing
   - Additional Labour

## Business Rules for Quote Generation
1. **Transport Services**
   - ALWAYS include fuel surcharge
   - ALWAYS include road tolls
   - Calculate both ways for long haul
   - Apply minimum hours for local transport

2. **Container Packing**
   - NEVER include handling out charges
   - Check item quantity for additional charges
   - Verify if DG surcharges apply
   - Include packing materials if specified

3. **Storage Services**
   - Apply free period calculations first
   - Include both handling in and out (except for container packing)
   - Calculate weekly rates including partial weeks
   - Apply DG surcharges if applicable

4. **Combined Services**
   - Calculate mandatory charges first
   - Apply service-specific exclusions
   - Include all relevant surcharges
   - Verify customer type (personal vs commercial)
