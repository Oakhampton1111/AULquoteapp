# AUL Quote App

This repository contains the AUL Quote App, a comprehensive warehouse quote management system.

## Project Structure

```
.
├── app/                    # Main application code
│   ├── api/               # API endpoints and routing
│   ├── models/            # Database models and schemas
│   ├── repositories/      # Data access layer
│   └── services/          # Business logic layer
├── deployment/            # Deployment scripts and configurations
│   └── scripts/          # Database and setup scripts
├── shared/               # Shared code between frontend and backend
│   ├── types/           # Common TypeScript types
│   ├── ai/             # AI-related shared code
│   └── utils/          # Shared utilities
├── tools/               # Development and analysis tools
│   └── kg/             # Knowledge graph tools
└── tests/              # Test suites
```

## Recent Improvements

### Code Organization
- Created base mixins for common model functionality:
  - `TimestampMixin`: Handles creation and update timestamps
  - `SerializationMixin`: Provides methods for serializing models
  - `StatusTrackingMixin`: Manages status transitions and timestamps
  - `ValidityMixin`: Manages validity periods for models
  - `OptimizationMixin`: Handles AI optimization data
  - `MetricsMixin`: Tracks business metrics

### Database Layer
- Improved database script organization with `base_script.py`
- Enhanced rate card management with more detailed rate structures
- Added handling fees and unit specifications to rate cards

### Reporting System
- Created base report schemas for consistent reporting:
  - `ReportMetadata`: Common report metadata
  - `ActivityMetrics`: Base for activity metrics
  - `ValueMetrics`: Base for value metrics
  - `BaseReport`: Common report structure
- Implemented specialized report types:
  - `CustomerActivityReport`: Customer behavior analysis
  - `ServiceUsageReport`: Service utilization metrics

### Code Health Tools
- Enhanced code health analysis tools:
  - Duplication detection with configurable thresholds
  - Orphaned code identification
  - Divergent component analysis
  - Structural health metrics

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run database setup: `python deployment/scripts/db/setup.py`
4. Start the application: `python app/main.py`

## Development Tools

### Code Health Analysis
Run the code health analysis tool:
```bash
python tools/analyze_health.py --report --path .
```

This will generate:
- A detailed JSON report with all findings
- A summary markdown report with key metrics
- Console output with immediate action items

## Contributing

1. Create a feature branch
2. Make your changes
3. Run code health analysis
4. Submit a pull request

## License

Copyright 2025 AUL. All rights reserved.
