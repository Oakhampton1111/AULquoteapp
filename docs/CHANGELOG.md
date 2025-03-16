# Changelog

All notable changes to the AUL Quote App will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-02-25

### Added
- Real-time code health monitoring with file watcher
- Knowledge graph-based code analysis
- Automated health score calculation
- Dependency tracking and analysis

### Changed
- Improved code organization with base mixins
- Enhanced rate card management system
- Standardized report generation system
- Consolidated documentation into README.md

### Fixed
- Health score calculation to stay within 0-100%
- Rate card validation and processing
- Database session management
- Error handling in API endpoints

## [1.0.0] - 2025-02-12

### Added
- **Frontend**: Complete migration to React with Vite and TypeScript
  - Modern component architecture
  - Enhanced type safety
  - Improved build performance

- **AI Integration**: Quote generation using FLAN-T5 model
  - Smart rate validation
  - Market analysis
  - Confidence scoring

- **Real-time Features**
  - Quote status updates
  - Customer notifications
  - Rate adjustments

- **Security**
  - Enhanced role-based access control
  - Improved authentication system
  - Audit logging

### Changed
- **Architecture**
  - Migrated from template-based to API-first design
  - Restructured backend services for better separation
  - Improved error handling and validation

- **Documentation**
  - Consolidated into `/docs` directory
  - Standardized component documentation
  - Added comprehensive guides

- **Database**
  - Optimized schema design
  - Improved query performance
  - Enhanced data validation

### Deprecated
- Legacy admin interface (to be removed in 2.0.0)
- Old API endpoints (to be removed in 2.0.0)
- Template-based rendering (removed)

### Removed
- Old template-based frontend
- Deprecated API endpoints
- Duplicate documentation
- Legacy database tables

### Fixed
- Rate calculation edge cases
- Authentication token handling
- Database connection pooling
- Frontend state management
- API response formats

### Security
- Updated dependencies
- Fixed authentication vulnerabilities
- Enhanced input validation
- Improved error handling
- Added security headers

## [0.9.0] - 2025-01-15

### Added
- **AI Features**
  - Initial AI quote assistance
  - Basic rate optimization
  - Context-aware suggestions

- **Rate Management**
  - Basic rate card system
  - Rate validation rules
  - Simple calculations

- **Authentication**
  - User authentication system
  - Basic role management
  - Session handling

### Changed
- **Database**
  - Updated schema for better performance
  - Improved indexing strategy
  - Enhanced relationships

- **API**
  - Standardized response formats
  - Added input validation
  - Improved error handling

### Fixed
- Various bug fixes in rate calculation
- Authentication edge cases
- Database connection handling
- API response consistency

### Security
- Updated vulnerable dependencies
- Fixed security configuration
- Added basic input sanitization

## [0.8.0] - 2024-12-01

### Added
- Initial project structure
- Basic quote management
- Simple user authentication
- Rate configuration
- Basic reporting

### Changed
- Set up initial architecture
- Configured basic API endpoints
- Designed database schema

[2.0.0]: https://github.com/username/aul-quote-app/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/username/aul-quote-app/compare/v0.9.0...v1.0.0
[0.9.0]: https://github.com/username/aul-quote-app/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/username/aul-quote-app/releases/tag/v0.8.0
