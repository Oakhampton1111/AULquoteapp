"""
Shared code analysis functionality.
"""

from typing import List, Dict, Any, Optional
import torch
from sentence_transformers import util
import numpy as np
from dataclasses import dataclass
from pathlib import Path

from ..config.health_config import get_health_rules
from ..interfaces.health_analyzer import HealthMetric

@dataclass
class HealthMetric:
    """Represents a health metric with its value and threshold."""
    name: str
    value: float
    threshold: float
    description: str = ""

@dataclass
class AnalysisContext:
    """Context for code analysis operations"""
    embeddings: torch.Tensor  # Tensor of component embeddings
    components: List[Any]     # List of code components
    rules: Dict[str, Any]     # Rules for analysis

def calculate_duplication_rate(context: AnalysisContext) -> float:
    """Calculate code duplication rate."""
    if len(context.components) < 2:
        return 0.0
    
    # Calculate similarity matrix
    similarity_matrix = torch.matmul(context.embeddings, context.embeddings.T)
    
    # Get threshold from rules
    threshold = context.rules["duplication"]["threshold"]
    
    # Count duplicates (excluding self-similarity)
    mask = torch.triu(similarity_matrix > threshold, diagonal=1)
    duplication_count = torch.sum(mask).item()
    
    # Calculate rate as percentage
    total_possible = (len(context.components) * (len(context.components) - 1)) / 2
    return (duplication_count / total_possible) * 100 if total_possible > 0 else 0.0

def calculate_orphan_rate(context: AnalysisContext) -> float:
    """Calculate orphaned component rate."""
    if len(context.components) < 2:
        return 0.0
    
    # Calculate similarity matrix
    similarity_matrix = torch.matmul(context.embeddings, context.embeddings.T)
    
    # Get threshold from rules
    threshold = context.rules["orphaned"]["threshold"]
    min_connections = context.rules["orphaned"].get("min_connections", 1)
    
    # Count components with insufficient connections
    connections = torch.sum(similarity_matrix > threshold, dim=1)
    orphaned_count = torch.sum(connections < min_connections).item()
    
    # Calculate rate as percentage
    return (orphaned_count / len(context.components)) * 100

def calculate_divergence_rate(context: AnalysisContext) -> float:
    """Calculate code pattern divergence rate."""
    if len(context.components) < 2:
        return 0.0
    
    # Calculate similarity matrix
    similarity_matrix = torch.matmul(context.embeddings, context.embeddings.T)
    
    # Get threshold from rules
    threshold = context.rules["divergence"]["threshold"]
    
    # Calculate average similarity excluding self-similarity
    mask = torch.ones_like(similarity_matrix) - torch.eye(len(context.components))
    masked_similarity = similarity_matrix * mask
    avg_similarity = torch.sum(masked_similarity) / (torch.sum(mask))
    
    # Convert to divergence rate (percentage)
    divergence_rate = (1.0 - avg_similarity.item()) * 100
    return max(0.0, min(100.0, divergence_rate))

def calculate_health_score(metrics: Dict[str, float]) -> float:
    """Calculate overall health score from metrics."""
    # Define weights for each metric
    weights = {
        "duplication_rate": 0.4,
        "orphan_rate": 0.3,
        "divergence_rate": 0.3
    }
    
    # Calculate weighted score
    total_weight = 0.0
    weighted_score = 0.0
    
    for metric, value in metrics.items():
        if metric in weights:
            weight = weights[metric]
            # Convert rate to score (100 - rate)
            score = max(0.0, min(100.0, 100.0 - value))
            weighted_score += score * weight
            total_weight += weight
    
    # Return normalized score
    return weighted_score / total_weight if total_weight > 0 else 0.0
