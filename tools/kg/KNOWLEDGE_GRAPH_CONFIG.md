# Knowledge Graph Configuration

This document outlines the configuration settings for the AUL Quote App knowledge graph generator. These settings have been carefully tuned to focus on operational code and meaningful relationships while excluding non-essential components.

**⚠️ WARNING: Do not modify these settings without explicit authorization from the project owner.**

## Directory Inclusion Settings

The following directories are included in the knowledge graph analysis:

```python
INCLUDED_DIRS = [
    'frontend/src/components',  # React/TypeScript UI components
    'frontend/src/api',         # API client code
    'frontend/src/services',    # Frontend services
    'warehouse_quote_app/app',  # Backend core app
    'warehouse_quote_app/app/services',  # Backend services
    'warehouse_quote_app/app/models'     # Backend data models
]
```

### Rationale
- Focuses on core operational code
- Captures frontend-backend interactions
- Includes business logic and data models
- Excludes build tools and configuration files

## Exclusion Patterns

The following patterns are excluded from analysis:

```python
EXCLUDED_PATTERNS = [
    r'.*\.git.*',              # Version control
    r'.*\.venv.*',             # Virtual environments
    r'.*__pycache__.*',        # Python cache
    r'.*\.pytest_cache.*',     # Test cache
    r'.*\.mypy_cache.*',       # Type checking cache
    r'.*\.vscode.*',           # Editor settings
    r'.*\.idea.*',             # IDE settings
    r'.*\.DS_Store.*',         # macOS files
    r'.*\.env.*',              # Environment files
    r'.*node_modules.*',       # NPM packages
    r'.*\.(test|spec)\.(ts|tsx|js|jsx|py)$',  # Test files
    r'.*/tests/.*',            # Test directories
    r'.*/scripts/.*',          # Utility scripts
    r'.*/migrations/.*',       # Database migrations
    r'.*/deployment/.*'        # Deployment configs
]
```

### Rationale
- Excludes non-operational code
- Prevents analysis of third-party dependencies
- Skips test files to focus on production code
- Ignores temporary and cache files

## File Types

The knowledge graph processes the following file types:
- `.py` - Python source files
- `.ts` - TypeScript source files
- `.tsx` - TypeScript React components

Files starting with `__` (e.g., `__init__.py`) are excluded to avoid processing Python module initialization files.

## Graph Generation Settings

- **Semantic Analysis**: Uses `all-MiniLM-L6-v2` model for semantic relationship detection
- **Batch Size**: 32 items per batch for efficient processing
- **Minimum Similarity**: 0.7 threshold for semantic relationships
- **Output Formats**: Both GraphML and JSON for maximum compatibility

## Output Files

The knowledge graph generator produces two files with timestamps:
1. `code_knowledge_graph_YYYYMMDD_HHMMSS.graphml` - NetworkX GraphML format
2. `code_knowledge_graph_YYYYMMDD_HHMMSS.json` - JSON format with metadata

## Health Metrics

The graph includes health analysis metrics:
- Node count and connectivity
- Interface implementation completeness
- Component coupling measurements
- Semantic relationship strengths
- Potential code duplication warnings

## Component Integration

### File Watcher Integration
The file watcher (`tools/kg/file_watcher.py`) is configured to use these exact same settings to ensure consistency with the knowledge graph:
- Uses identical included directories for monitoring
- Applies the same exclusion patterns
- Maintains the same focus on operational code

### Semantic Context Manager Integration
The semantic context manager (`tools/kg/semantic_context_manager.py`) also aligns with these settings:
- Loads context from the same included directories
- Respects identical exclusion patterns
- Supports all relevant file types: `.py`, `.ts`, `.tsx`, `.js`, `.jsx`

### Health Metrics
The integrated configuration has demonstrated improved health metrics:
- Base health score: ~78%
- Successfully tracks both frontend and backend changes
- Maintains consistent relationship mapping between components

## Usage Guidelines

1. **Do Not Modify Independently**: The configuration settings in this file are used by multiple components. Any changes must be synchronized across:
   - Knowledge Graph Generator
   - File Watcher
   - Semantic Context Manager

2. **Configuration Updates**: When updates are required:
   - Update this configuration file first
   - Synchronize changes across all three components
   - Run health analysis to verify improvement
   - Document any significant metric changes

3. **Health Monitoring**: Regular health checks should maintain:
   - Consistent scoring across file changes
   - Proper detection of cross-component dependencies
   - Accurate relationship mapping between frontend and backend

## Modification Process

To modify these settings:
1. Create a proposal document outlining the changes
2. Get explicit approval from the project owner
3. Test the changes in a separate branch
4. Document the impact on graph metrics
5. Update this configuration file with the approved changes

**Note**: Unauthorized modifications may lead to incomplete or incorrect code analysis, affecting the project's maintainability tracking.
