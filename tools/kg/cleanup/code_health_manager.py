"""
Code Health Manager
Unified interface for analyzing and improving code health
"""

from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import ast
import logging
import networkx as nx
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
import threading
from datetime import datetime
import pytz
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
import matplotlib.pyplot as plt
import torch

from ..semantic_context_manager import SemanticContextManager
from ..config.kg_config import InterfaceType
from ..config.health_config import get_code_health_rules, get_cache_paths, get_health_rules, get_default_health_rules
from ..analysis.code_analysis import (
    calculate_duplication_rate,
    calculate_orphan_rate,
    calculate_divergence_rate,
    calculate_health_score,
    AnalysisContext
)

logger = logging.getLogger(__name__)

class HealthIssueType(Enum):
    """Types of health issues that can be detected."""
    DUPLICATION = "duplication"
    ORPHANED = "orphaned"
    DIVERGENT = "divergent"
    STRUCTURAL = "structural"
    COMPLEXITY = "complexity"

class SeverityLevel(Enum):
    """Severity levels for health issues."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class HealthIssue:
    """Represents a code health issue."""
    type: HealthIssueType
    severity: SeverityLevel
    component: str
    details: str
    impact: float
    related_components: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'type': self.type.value,
            'severity': self.severity.value,
            'component': self.component,
            'details': self.details,
            'impact': self.impact,
            'related_components': self.related_components,
            'recommendations': self.recommendations
        }

@dataclass
class HealthMetric:
    name: str
    value: float
    threshold: float
    description: str

@dataclass
class HealthReport:
    """Complete health report for the codebase."""
    health_score: float
    issues: List[Dict[str, Any]]
    metrics: Dict[str, HealthMetric]
    timestamp: str = field(default_factory=lambda: datetime.now(pytz.UTC).isoformat())
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'health_score': self.health_score,
            'issues': self.issues,
            'metrics': {name: asdict(metric) for name, metric in self.metrics.items()},
            'timestamp': self.timestamp,
            'recommendations': self.recommendations
        }

class CodeHealthManager:
    """Manages code health analysis and provides recommendations."""
    
    def __init__(self, semantic_manager=None):
        """Initialize with optional semantic manager."""
        self.logger = logging.getLogger(__name__)
        
        # Import here to avoid circular imports
        from ..config.health_config import get_default_health_rules
        
        self.health_rules = get_default_health_rules()
        self.semantic_manager = semantic_manager
        
        if not self.semantic_manager:
            try:
                from ..semantic_context_manager import SemanticContextManager
                self.semantic_manager = SemanticContextManager(".")
            except Exception as e:
                self.logger.error(f"Failed to initialize semantic manager: {e}")
                # Don't raise here, allow the class to initialize even without semantic manager
    
    def analyze_codebase(self, root_dir: str = ".") -> Dict[str, Any]:
        """Analyze the codebase health."""
        try:
            # Check if semantic manager is available
            if not self.semantic_manager:
                self.logger.error("Semantic manager is not available")
                return {
                    "health_score": 0.0,
                    "metrics": {},
                    "issues": [],
                    "error": "Semantic manager is not available"
                }
            
            # Ensure the semantic manager has data
            if not hasattr(self.semantic_manager, 'components') or not self.semantic_manager.components:
                self.semantic_manager.load_context()
            
            # Get valid components with embeddings
            valid_components = []
            embeddings = []
            for comp in self.semantic_manager.components.values():
                if comp.semantic_context and isinstance(comp.semantic_context.embedding, (np.ndarray, list)):
                    valid_components.append(comp)
                    embeddings.append(comp.semantic_context.embedding)
            
            if not valid_components:
                self.logger.warning("No valid components found with embeddings")
                return {
                    "health_score": 0.0,
                    "metrics": {
                        "duplication_rate": None,
                        "orphan_rate": None,
                        "divergence_rate": None
                    },
                    "issues": [{
                        "type": "structural",
                        "severity": "high",
                        "details": "No valid code components found with embeddings. This could indicate issues with code parsing or analysis.",
                        "recommendations": [
                            "Ensure all code files are properly formatted and can be parsed",
                            "Check that the semantic analysis is correctly configured",
                            "Verify that file paths and extensions are correctly specified"
                        ]
                    }],
                    "recommendations": [
                        "Review code file formats and ensure they can be properly analyzed",
                        "Check semantic analysis configuration in tools/kg/config/health_config.py"
                    ]
                }
            
            # Import here to avoid circular imports
            from ..analysis.code_analysis import AnalysisContext, calculate_duplication_rate
            from ..analysis.code_analysis import calculate_orphan_rate, calculate_divergence_rate
            from ..analysis.code_analysis import calculate_health_score
            
            # Create analysis context with numpy array conversion to avoid warning
            embeddings_array = np.array(embeddings)
            embeddings_tensor = torch.tensor(embeddings_array, dtype=torch.float32)
            context = AnalysisContext(
                embeddings=embeddings_tensor,
                components=valid_components,
                rules=self.health_rules
            )
            
            # Calculate metrics
            duplication_result = calculate_duplication_rate(context)
            orphan_result = calculate_orphan_rate(context)
            divergence_result = calculate_divergence_rate(context)
            
            # Extract metrics dictionary - handle both HealthMetric objects and float values
            metrics = {}
            
            # Helper function to extract value from result (handles both objects and floats)
            def get_value(result):
                if hasattr(result, 'value'):  # If it's a HealthMetric object
                    return result.value
                return float(result)  # Otherwise assume it's a float or convertible to float
            
            metrics["duplication_rate"] = get_value(duplication_result)
            metrics["orphan_rate"] = get_value(orphan_result)
            metrics["divergence_rate"] = get_value(divergence_result)
            
            # Calculate health score
            health_score = calculate_health_score(metrics)
            
            # Generate issues
            issues = self._identify_issues(metrics)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics)
            
            return {
                "health_score": health_score,
                "metrics": metrics,
                "issues": issues,
                "recommendations": recommendations
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing codebase: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return {
                "health_score": 0.0,
                "metrics": {},
                "issues": [],
                "error": str(e)
            }
    
    def _identify_issues(self, metrics: Dict[str, float]) -> List[Dict[str, Any]]:
        """Identify issues based on metrics and thresholds."""
        issues = []
        
        # Map metric names to rule categories
        metric_to_rule = {
            "duplication_rate": "duplication",
            "orphan_rate": "orphaned",
            "divergence_rate": "divergence"
        }
        
        # Check each metric against its threshold
        for metric, value in metrics.items():
            rule_category = metric_to_rule.get(metric)
            if not rule_category or rule_category not in self.health_rules:
                continue
                
            threshold = self.health_rules[rule_category]["threshold"] * 100
            if value > threshold:
                if metric == "duplication_rate":
                    severity = "high" if value > 20 else "medium"
                    issues.append({
                        "type": "duplication",
                        "severity": severity,
                        "description": f"Code duplication rate is {value:.1f}%, above the threshold of {threshold:.1f}%",
                        "recommendation": "Refactor duplicate code into shared utilities or base classes"
                    })
                elif metric == "orphan_rate":
                    issues.append({
                        "type": "orphaned",
                        "severity": "medium",
                        "description": f"Orphaned component rate is {value:.1f}%, above the threshold of {threshold:.1f}%",
                        "recommendation": "Review orphaned components for proper integration or removal"
                    })
                elif metric == "divergence_rate":
                    issues.append({
                        "type": "divergence",
                        "severity": "medium",
                        "description": f"Code pattern divergence rate is {value:.1f}%, above the threshold of {threshold:.1f}%",
                        "recommendation": "Standardize implementation patterns across the codebase"
                    })
        
        return issues
    
    def _generate_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on metrics."""
        recommendations = []
        
        # Map metric names to rule categories
        metric_to_rule = {
            "duplication_rate": "duplication",
            "orphan_rate": "orphaned",
            "divergence_rate": "divergence"
        }
        
        # Check each metric
        for metric, value in metrics.items():
            rule_category = metric_to_rule.get(metric)
            if not rule_category or rule_category not in self.health_rules:
                continue
                
            threshold = self.health_rules[rule_category]["threshold"] * 100
            
            if value > threshold:
                if metric == "duplication_rate":
                    recommendations.append(
                        f"Code duplication rate is {value:.1f}%. "
                        "Consider refactoring duplicate code into shared utilities or base classes."
                    )
                elif metric == "orphan_rate":
                    recommendations.append(
                        f"Orphaned component rate is {value:.1f}%. "
                        "Review orphaned components for proper integration or removal."
                    )
                elif metric == "divergence_rate":
                    recommendations.append(
                        f"Code pattern divergence rate is {value:.1f}%. "
                        "Standardize implementation patterns across the codebase."
                    )
        
        # Add general recommendation
        if len(recommendations) > 1:
            recommendations.append(
                "Consider implementing a systematic code review process to maintain "
                "consistency and reduce technical debt."
            )
        
        return recommendations
    
    def cleanup(self):
        """Clean up resources."""
        if self.semantic_manager:
            try:
                self.semantic_manager.cleanup()
            except Exception as e:
                # Ignore shutdown-related errors
                if "sys.meta_path is None" not in str(e):
                    self.logger.error(f"Error during cleanup: {str(e)}")
    
    def __del__(self):
        """Clean up resources when the object is deleted."""
        try:
            self.cleanup()
        except Exception as e:
            # Only log non-shutdown errors
            if hasattr(self, 'logger') and "sys.meta_path is None" not in str(e):
                self.logger.error(f"Error during cleanup in __del__: {str(e)}")

    def print_report(self, report: Dict[str, Any]) -> None:
        """Print a formatted analysis report to the console."""
        print("\n=== Code Health Analysis Report ===")
        print(f"\nHealth Score: {report['health_score']:.1f}/100")
        
        print("\nMetrics:")
        for name, value in report['metrics'].items():
            print(f"  {name.replace('_', ' ').title()}: {value:.1f}%")
        
        if report.get('issues'):
            print("\nIssues Found:")
            for issue in report['issues']:
                print(f"\n  - Type: {issue['type'].title()}")
                print(f"    Severity: {issue['severity'].title()}")
                print(f"    Description: {issue['description']}")
                if 'recommendation' in issue:
                    print(f"    Recommendation: {issue['recommendation']}")
        
        if report.get('recommendations'):
            print("\nRecommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
        
        if report.get('error'):
            print(f"\nError: {report['error']}")
        print("\n" + "="*35)

    def save_report(self, report: Dict[str, Any], output_file: str = "code_health_report.json") -> None:
        """Save the analysis report to a JSON file."""
        import json
        from pathlib import Path
        
        try:
            # Ensure the output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save the report
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"Report saved to {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving report: {str(e)}")

def main():
    """Main entry point for code health analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze code health metrics")
    parser.add_argument('--dir', default='.', help='Directory to analyze')
    parser.add_argument('--output', default='code_health_report.json', help='Output file for the report')
    args = parser.parse_args()
    
    try:
        manager = CodeHealthManager()
        report = manager.analyze_codebase(args.dir)
        
        # Print report to console
        manager.print_report(report)
        
        # Save report to file
        manager.save_report(report, args.output)
        
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")
        import traceback
        logging.debug(traceback.format_exc())
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
