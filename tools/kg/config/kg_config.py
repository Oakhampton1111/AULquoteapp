"""
Knowledge Graph Configuration
"""

from pathlib import Path
import re
from enum import Enum, auto

class DomainGroup(Enum):
    """Domain groups for code organization"""
    QUOTE_MANAGEMENT = auto()
    RATE_CALCULATION = auto()
    STORAGE_MANAGEMENT = auto()
    USER_MANAGEMENT = auto()
    REPORTING = auto()
    CONFIGURATION = auto()
    UTILITIES = auto()

class InterfaceType(Enum):
    """Types of interfaces in the system"""
    DATA_MODEL = auto()
    API_CONTRACT = auto()
    SERVICE_INTERFACE = auto()
    EVENT_HANDLER = auto()
    NONE = auto()

# Interface definitions and their expected methods
INTERFACE_DEFINITIONS = {
    "DataModel": {
        "required_methods": ["to_dict", "from_dict"],
        "type": InterfaceType.DATA_MODEL
    },
    "APIContract": {
        "required_methods": ["validate"],
        "type": InterfaceType.API_CONTRACT
    },
    "ServiceInterface": {
        "required_methods": ["execute"],
        "type": InterfaceType.SERVICE_INTERFACE
    },
    "EventHandler": {
        "required_methods": ["handle_event"],
        "type": InterfaceType.EVENT_HANDLER
    }
}

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# Directories to include in knowledge graph
INCLUDED_DIRS = [
    PROJECT_ROOT / "warehouse_quote_app/app",  # Core backend only
    PROJECT_ROOT / "frontend/src",             # Core frontend only
    PROJECT_ROOT / "config",                   # Essential configs
    PROJECT_ROOT / "shared/types",             # Shared type definitions
]

# File patterns to include
INCLUDED_PATTERNS = [
    "*.py",      # Python backend
    "*.tsx",     # React TypeScript components
    "*.ts",      # TypeScript utilities
    "*.json",    # Essential configs
]

# Directories and patterns to exclude
EXCLUDED_DIRS = [
    # Environment and build directories
    "**/.venv/**", 
    "**/node_modules/**",
    "**/build/**", 
    "**/dist/**",
    "**/.next/**",
    "**/__pycache__/**",
    "**/*.egg-info/**",
    "**/vendor/**",
    
    # Version control
    "**/.git/**",
    "**/.github/**",
    
    # Cache directories
    "**/.pytest_cache/**",
    "**/.mypy_cache/**",
    "**/logs/**",
    "**/.cache/**",
    
    # Test directories
    "**/test/**",
    "**/tests/**",
    
    # Documentation
    "**/docs/**",
    
    # Tool directories (except kg)
    "**/tools/cleanup/**",
    "**/tools/migrations/**"
]

# File patterns to exclude
EXCLUDED_PATTERNS = [
    # Generated and minified files
    "*.min.js",
    "*.chunk.js",
    "*.bundle.js",
    "*.generated.*",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.egg",
    
    # Configuration files
    "*.config.js",
    "tsconfig.json",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    
    # Test files
    "*_test.py",
    "*.test.js",
    "*.test.ts",
    "*.test.tsx",
    "*.spec.js",
    "*.spec.ts",
    "*.spec.tsx",
    
    # Documentation
    "README.md",
    "*.md"
]

# Semantic grouping rules
SEMANTIC_GROUPS = {
    "QUOTE_MANAGEMENT": {
        "patterns": [
            r".*quote.*",
            r".*pricing.*",
            r".*estimate.*",
        ],
        "related_domains": [
            "RATE_CALCULATION",
            "BILLING",
        ]
    },
    "RATE_CALCULATION": {
        "patterns": [
            r".*rate.*",
            r".*calculator.*",
            r".*pricing.*",
        ],
        "related_domains": [
            "QUOTE_MANAGEMENT",
            "STORAGE_MANAGEMENT",
        ]
    },
    # Add other semantic groups...
}

# Code health rules
CODE_HEALTH_RULES = {
    "duplication": {
        "max_similarity": 0.85,  # Maximum allowed similarity between components
        "min_lines": 10,  # Minimum lines for duplication check
        "exclude_patterns": [
            r".*test.*",  # Exclude test files from duplication checks
        ]
    },
    "divergence": {
        "interface_drift_threshold": 0.3,  # Maximum allowed drift from interface
        "check_patterns": [
            "*/interfaces/*",
            "*/contracts/*",
            "*/schemas/*",
        ]
    },
    "orphan": {
        "min_references": 1,  # Minimum number of references required
        "exclude_patterns": [
            r".*index\.[tj]sx?$",  # Exclude index files
            r".*\.test\.[tj]sx?$",  # Exclude test files
        ]
    }
}

# High-priority paths focusing on interfaces
HIGH_PRIORITY_PATHS = [
    # API Contracts
    "warehouse_quote_app/app/schemas",
    "warehouse_quote_app/app/services/interfaces",
    # Core Domain Models
    "warehouse_quote_app/app/models",
    # Event Handlers
    "warehouse_quote_app/app/events",
]

# Relationship types with weights
RELATIONSHIP_TYPES = {
    "implements_interface": {
        "weight": 2.0,
        "description": "Implementation of an interface"
    },
    "extends_interface": {
        "weight": 1.8,
        "description": "Extension of an interface"
    },
    "api_contract": {
        "weight": 2.0,
        "description": "API contract definition/usage"
    },
    "event_handler": {
        "weight": 1.5,
        "description": "Event handling relationship"
    },
    "data_flow": {
        "weight": 1.3,
        "description": "Data flow between components"
    },
    "semantic_relation": {
        "weight": 1.2,
        "description": "Related by domain semantics"
    }
}

def get_domain_group(path: str) -> str:
    """Determine the domain group for a given path based on semantic rules"""
    for domain, rules in SEMANTIC_GROUPS.items():
        for pattern in rules["patterns"]:
            if re.search(pattern, path, re.IGNORECASE):
                return domain
    return None

def get_interface_type(path: str) -> str:
    """Determine the interface type for a given path"""
    if "/schemas/" in path or "/types/" in path:
        return "DATA_MODEL"
    elif "/api/" in path:
        return "API_CONTRACT"
    elif "/services/interfaces" in path:
        return "SERVICE_INTERFACE"
    elif "/events/" in path:
        return "EVENT_HANDLER"
    return None

def get_full_path(relative_path: str) -> Path:
    """Convert relative path to full path from project root"""
    return PROJECT_ROOT / relative_path

def get_high_priority_paths() -> list:
    """Get list of high priority paths as Path objects"""
    return [get_full_path(p) for p in HIGH_PRIORITY_PATHS]

def should_exclude_path(path: str) -> bool:
    """Check if a path should be excluded based on configured patterns"""
    from pathlib import Path
    from fnmatch import fnmatch
    
    path_obj = Path(path)
    path_str = str(path_obj).replace('\\', '/')  # Normalize path separators
    
    # Check excluded directories
    for excluded_dir in EXCLUDED_DIRS:
        if fnmatch(path_str, excluded_dir):
            return True
            
    # Check excluded patterns
    for pattern in EXCLUDED_PATTERNS:
        if fnmatch(path_str, pattern):
            return True
            
    return False

def get_relationship_config() -> dict:
    """Get relationship type configuration"""
    return RELATIONSHIP_TYPES

def get_code_health_rules() -> dict:
    """Get code health rules configuration"""
    return CODE_HEALTH_RULES
