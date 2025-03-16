"""
Interface for health analysis components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pytz
import torch

@dataclass
class HealthMetric:
    """Base class for health metrics."""
    name: str
    value: float
    threshold: float
    weight: float = 1.0
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'value': self.value,
            'threshold': self.threshold,
            'weight': self.weight,
            'description': self.description
        }

    def calculate_impact(self) -> float:
        """Calculate the impact of this metric."""
        if self.value <= self.threshold:
            return 0.0
        return (self.value - self.threshold) / self.threshold * self.weight

@dataclass
class HealthIssue:
    """Represents a health issue found in the codebase."""
    type: str  # 'error', 'warning', 'info'
    message: str
    component: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.type,
            'message': self.message,
            'component': self.component,
            'file_path': self.file_path,
            'line_number': self.line_number
        }

@dataclass
class HealthRecommendation:
    """Represents a recommendation for improving code health."""
    message: str
    priority: int  # 1-5, where 1 is highest priority
    effort: int  # 1-5, where 1 is least effort
    impact: int  # 1-5, where 5 is highest impact
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'message': self.message,
            'priority': self.priority,
            'effort': self.effort,
            'impact': self.impact
        }

@dataclass
class HealthReport:
    """Represents a complete health analysis report."""
    health_score: float
    issues: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime = datetime.now(pytz.UTC)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'health_score': self.health_score,
            'issues': self.issues,
            'metrics': self.metrics,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }

class HealthAnalyzer(ABC):
    """Interface for health analysis components."""
    
    @abstractmethod
    def analyze(self, context: Dict[str, Any]) -> List[HealthMetric]:
        """Analyze health and return metrics."""
        pass
    
    @abstractmethod
    def get_recommendations(self, metrics: List[HealthMetric]) -> List[str]:
        """Get recommendations based on metrics."""
        pass

class DuplicationAnalyzer(HealthAnalyzer):
    """Analyzes code duplication."""
    
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules
        
    def analyze(self, context: Dict[str, Any]) -> List[HealthMetric]:
        """Analyze code duplication."""
        metrics = []
        embeddings = context['embeddings']
        components = context['components']
        
        # Calculate similarity matrix
        similarity = torch.matmul(embeddings, embeddings.transpose(0, 1))
        
        # Find duplicates
        threshold = self.rules['duplication']['threshold']
        duplicates = torch.where(similarity > threshold)
        
        if len(duplicates[0]) > 0:
            duplication_rate = len(duplicates[0]) / (len(components) * 2)
            metrics.append(HealthMetric(
                name='duplication_rate',
                value=duplication_rate,
                threshold=threshold,
                description='Rate of code duplication'
            ))
            
        return metrics
        
    def get_recommendations(self, metrics: List[HealthMetric]) -> List[str]:
        """Get recommendations for duplication issues."""
        recommendations = []
        for metric in metrics:
            if metric.name == 'duplication_rate' and metric.value > metric.threshold:
                recommendations.append(
                    'Consider refactoring duplicate code into shared utilities'
                )
        return recommendations

class OrphanedAnalyzer(HealthAnalyzer):
    """Analyzes orphaned components."""
    
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules
        
    def analyze(self, context: Dict[str, Any]) -> List[HealthMetric]:
        """Analyze orphaned components."""
        metrics = []
        components = context['components']
        
        # Count components with no dependencies
        orphaned = sum(1 for comp in components if not comp.dependencies)
        if orphaned > 0:
            orphan_rate = orphaned / len(components)
            metrics.append(HealthMetric(
                name='orphan_rate',
                value=orphan_rate,
                threshold=self.rules['orphan']['threshold'],
                description='Rate of orphaned components'
            ))
            
        return metrics
        
    def get_recommendations(self, metrics: List[HealthMetric]) -> List[str]:
        """Get recommendations for orphaned components."""
        recommendations = []
        for metric in metrics:
            if metric.name == 'orphan_rate' and metric.value > metric.threshold:
                recommendations.append(
                    'Review and potentially remove or integrate orphaned components'
                )
        return recommendations

class DivergenceAnalyzer(HealthAnalyzer):
    """Analyzes component divergence."""
    
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules
        
    def analyze(self, context: Dict[str, Any]) -> List[HealthMetric]:
        """Analyze component divergence."""
        metrics = []
        components = context['components']
        
        # Calculate divergence between interface and implementation
        divergent = sum(1 for comp in components 
                       if hasattr(comp, 'interface') and 
                       self._calculate_divergence(comp.interface, comp.implementation) > self.rules['divergence']['threshold'])
                       
        if divergent > 0:
            divergence_rate = divergent / len(components)
            metrics.append(HealthMetric(
                name='divergence_rate',
                value=divergence_rate,
                threshold=self.rules['divergence']['threshold'],
                description='Rate of interface divergence'
            ))
            
        return metrics
        
    def _calculate_divergence(self, interface: Any, implementation: Any) -> float:
        """Calculate divergence between interface and implementation."""
        # Implementation depends on specific interface definition
        return 0.0
        
    def get_recommendations(self, metrics: List[HealthMetric]) -> List[str]:
        """Get recommendations for divergent components."""
        recommendations = []
        for metric in metrics:
            if metric.name == 'divergence_rate' and metric.value > metric.threshold:
                recommendations.append(
                    'Review and align divergent interface implementations'
                )
        return recommendations
