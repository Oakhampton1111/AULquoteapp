"""
Semantic Context Checker
Enforces the policy that semantic context must be consulted before any code changes
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime

from .semantic_context_manager import SemanticContextManager

logger = logging.getLogger(__name__)

@dataclass
class ContextValidation:
    """Result of semantic context validation"""
    is_valid: bool
    context_data: Dict
    related_files: Set[str]
    impact_assessment: Dict
    error: Optional[str] = None
    warnings: List[str] = []

class SemanticContextChecker:
    """
    Enforces the policy that semantic context must be consulted before any code changes.
    This class acts as a pre-validation step for all code modifications.
    """
    
    def __init__(self, semantic_manager: SemanticContextManager):
        self.semantic_manager = semantic_manager
        self.validation_history: List[Tuple[str, ContextValidation]] = []
        
    def validate_change(self, file_path: str, proposed_content: str) -> ContextValidation:
        """
        Validates a proposed change against the semantic context.
        Must be called before any code modifications.
        """
        try:
            # Get current semantic context
            current_context = self.semantic_manager.get_context(file_path)
            if not current_context:
                return ContextValidation(
                    False,
                    {},
                    set(),
                    {},
                    "No semantic context found for file"
                )
                
            # Analyze semantic impact
            semantic_impact = self.semantic_manager.analyze_changes(
                current_context.get("content", ""),
                proposed_content
            )
            
            # Get related files
            related_files = set()
            for relationship_type in ["new_relationships", "removed_relationships", "maintained_relationships"]:
                related_files.update(semantic_impact.get(relationship_type, []))
                
            # Assess impact
            impact_assessment = self._assess_impact(semantic_impact)
            
            # Record validation
            validation = ContextValidation(
                True,
                current_context,
                related_files,
                impact_assessment
            )
            
            # Add warnings for high impact changes
            if impact_assessment["impact_score"] > 0.7:
                validation.warnings.append(
                    f"High impact change detected (score: {impact_assessment['impact_score']:.2f})"
                )
                
            # Record validation history
            self._record_validation(file_path, validation)
            
            return validation
            
        except Exception as e:
            logger.error(f"Error validating semantic context for {file_path}: {e}")
            return ContextValidation(
                False,
                {},
                set(),
                {},
                str(e)
            )
            
    def _assess_impact(self, semantic_impact: Dict) -> Dict:
        """Assess the impact of semantic changes"""
        impact = {
            "impact_score": 0.0,
            "breaking_changes": [],
            "new_patterns": [],
            "affected_patterns": []
        }
        
        # Calculate impact score
        removed = len(semantic_impact.get("removed_relationships", []))
        new = len(semantic_impact.get("new_relationships", []))
        maintained = len(semantic_impact.get("maintained_relationships", []))
        
        # Higher score for removing relationships
        impact["impact_score"] += removed * 0.2
        
        # Medium score for new relationships
        impact["impact_score"] += new * 0.1
        
        # Lower score if maintaining relationships
        impact["impact_score"] = max(0.0, impact["impact_score"] - (maintained * 0.05))
        
        # Cap at 1.0
        impact["impact_score"] = min(impact["impact_score"], 1.0)
        
        # Identify breaking changes
        if removed > 0:
            impact["breaking_changes"].extend(
                semantic_impact.get("removed_relationships", [])
            )
            
        # Identify new patterns
        if new > maintained:
            impact["new_patterns"].extend(
                semantic_impact.get("new_relationships", [])
            )
            
        # Identify affected patterns
        impact["affected_patterns"].extend(
            semantic_impact.get("maintained_relationships", [])
        )
        
        return impact
        
    def _record_validation(self, file_path: str, validation: ContextValidation):
        """Record validation for history and analysis"""
        self.validation_history.append((
            datetime.now().isoformat(),
            file_path,
            validation
        ))
        
        # Keep only last 100 validations
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]
            
    def get_validation_history(self, file_path: Optional[str] = None) -> List[Tuple]:
        """Get validation history, optionally filtered by file"""
        if file_path:
            return [
                (ts, fp, val) for ts, fp, val in self.validation_history
                if fp == file_path
            ]
        return self.validation_history
        
    def get_last_validation(self, file_path: str) -> Optional[ContextValidation]:
        """Get the last validation for a specific file"""
        history = self.get_validation_history(file_path)
        return history[-1][2] if history else None
