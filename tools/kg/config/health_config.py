"""
Configuration for code health analysis and semantic context management.
"""

import ast
from pathlib import Path
from typing import Dict, Any, List, Optional
import os
import json

def get_default_health_rules() -> Dict[str, Any]:
    """Get default health rules."""
    return {
        "duplication": {
            "threshold": 0.85,  # Maximum allowed similarity between components
            "min_lines": 10,    # Minimum lines for duplication check
            "impact_weight": 0.4,
            "description": "Code duplication"
        },
        "orphaned": {
            "threshold": 0.5,   # Minimum required similarity
            "min_connections": 1,  # Minimum required connections
            "impact_weight": 0.3,
            "description": "Orphaned components"
        },
        "divergence": {
            "threshold": 0.4,   # Maximum allowed semantic difference
            "impact_weight": 0.3,
            "description": "Divergent code patterns"
        }
    }

def get_health_rules(custom_rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Get health rules, optionally overriding with custom rules."""
    rules = get_default_health_rules()
    
    if custom_rules:
        for category, settings in custom_rules.items():
            if category in rules:
                rules[category].update(settings)
            else:
                rules[category] = settings
    
    return rules

def get_cache_paths() -> Dict[str, Path]:
    """Get paths for various cache files."""
    cache_dir = Path(__file__).parent.parent / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    return {
        "embeddings": cache_dir / "embeddings.pt",
        "context": cache_dir / "context.json",
        "visualizations": cache_dir / "visualizations"
    }

# Alias for backward compatibility
get_code_health_rules = get_default_health_rules

# Model configurations
MODEL_CONFIG = {
    'code_model': {
        'name': 'paraphrase-MiniLM-L3-v2',
        'device': 'cpu',
        'batch_size': 32
    },
    'doc_model': {
        'name': 'all-MiniLM-L6-v2',
        'device': 'cpu',
        'batch_size': 32
    }
}

# Cache configuration
CACHE_CONFIG = {
    'cache_dir': str(Path(__file__).parent.parent / ".cache"),
    'embeddings_cache_file': 'embeddings.pt',
    'graph_cache_file': 'dependency_graph.gpickle',
    'metrics_cache_file': 'health_metrics.json',
    'cache_ttl_days': 7,
}

# Visualization configuration
VISUALIZATION_CONFIG = {
    'graph_layout': 'spring',
    'node_size_factor': 1000,
    'edge_width_factor': 2,
    'label_font_size': 8,
    'title_font_size': 12,
    'dpi': 300,
    'figsize': (12, 8),
    'node_colors': {
        'interface': '#1f77b4',
        'implementation': '#2ca02c',
        'orphan': '#d62728',
        'duplicate': '#ff7f0e'
    },
    'edge_colors': {
        'implements': '#1f77b4',
        'semantic_relation': '#2ca02c',
        'duplicate': '#d62728'
    }
}
