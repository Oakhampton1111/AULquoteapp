"""
Memory Enforcer
Ensures strict compliance with system memories and policies
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

@dataclass
class MemoryValidation:
    """Result of memory compliance validation"""
    is_valid: bool
    checked_memories: List[str]
    violations: List[str]
    warnings: List[str]
    validation_data: Dict[str, Any]

class MemoryEnforcer:
    """
    Enforces strict compliance with system memories and policies.
    Acts as a gatekeeper for all operations.
    """
    
    def __init__(self, memories_path: Path):
        self.memories_path = memories_path
        self.memories_path.mkdir(exist_ok=True)
        self.validation_history: List[Dict] = []
        self.load_memories()
        
    def load_memories(self):
        """Load all memories from storage"""
        self.memories = {}
        try:
            memory_files = list(self.memories_path.glob("*.json"))
            for mf in memory_files:
                with open(mf, 'r') as f:
                    memory = json.load(f)
                    self.memories[memory['id']] = memory
        except Exception as e:
            logger.error(f"Error loading memories: {e}")
            raise
            
    def validate_operation(self, operation_type: str, context: Dict) -> MemoryValidation:
        """
        Validate an operation against all applicable memories
        Returns MemoryValidation with detailed results
        """
        checked_memories = []
        violations = []
        warnings = []
        validation_data = {}
        
        for memory_id, memory in self.memories.items():
            checked_memories.append(memory_id)
            
            # Check if memory applies to this operation
            if not self._memory_applies(memory, operation_type, context):
                continue
                
            # Validate against memory requirements
            memory_violations = self._check_memory_compliance(memory, context)
            if memory_violations:
                violations.extend(memory_violations)
                
            # Gather validation data
            validation_data[memory_id] = {
                'title': memory.get('title'),
                'checked_rules': len(memory.get('content', '').split('\n')),
                'violations': memory_violations
            }
            
        # Record validation
        self._record_validation(operation_type, context, violations)
        
        return MemoryValidation(
            is_valid=len(violations) == 0,
            checked_memories=checked_memories,
            violations=violations,
            warnings=warnings,
            validation_data=validation_data
        )
        
    def _memory_applies(self, memory: Dict, operation_type: str, context: Dict) -> bool:
        """Check if a memory applies to the current operation"""
        # Global memories always apply
        if 'user_global' in memory.get('tags', []):
            return True
            
        # Check operation-specific memories
        if operation_type in memory.get('tags', []):
            return True
            
        # Check context-specific memories
        if any(tag in context.get('tags', []) for tag in memory.get('tags', [])):
            return True
            
        return False
        
    def _check_memory_compliance(self, memory: Dict, context: Dict) -> List[str]:
        """Check compliance with a specific memory"""
        violations = []
        content = memory.get('content', '')
        
        # Parse requirements from memory content
        requirements = self._parse_requirements(content)
        
        for req in requirements:
            if not self._requirement_satisfied(req, context):
                violations.append(f"Violation of {memory['title']}: {req}")
                
        return violations
        
    def _parse_requirements(self, content: str) -> List[str]:
        """Parse requirements from memory content"""
        requirements = []
        
        # Split on numbered lists
        numbered = re.split(r'\d+\.\s+', content)
        if len(numbered) > 1:
            requirements.extend([req.strip() for req in numbered[1:]])
            
        # Split on bullet points
        bulleted = re.split(r'[-•]\s+', content)
        if len(bulleted) > 1:
            requirements.extend([req.strip() for req in bulleted[1:]])
            
        # If no structured lists found, treat each line as a requirement
        if not requirements:
            requirements = [line.strip() for line in content.split('\n') if line.strip()]
            
        return requirements
        
    def _requirement_satisfied(self, requirement: str, context: Dict) -> bool:
        """Check if a specific requirement is satisfied"""
        # Convert requirement to lowercase for matching
        req_lower = requirement.lower()
        
        # Check for file operations
        if 'file' in req_lower:
            if 'file_operations' not in context:
                return False
            if 'readme.md' in req_lower and not any('readme.md' in op.lower() for op in context['file_operations']):
                return False
                
        # Check for search operations
        if 'search' in req_lower:
            if 'search_performed' not in context or not context['search_performed']:
                return False
                
        # Check for validation
        if 'validate' in req_lower or 'check' in req_lower:
            if 'validation_performed' not in context or not context['validation_performed']:
                return False
                
        # Check for semantic context
        if 'semantic' in req_lower or 'context' in req_lower:
            if 'semantic_context_checked' not in context or not context['semantic_context_checked']:
                return False
                
        return True
        
    def _record_validation(self, operation_type: str, context: Dict, violations: List[str]):
        """Record validation for history and analysis"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'operation_type': operation_type,
            'context_summary': {k: str(v) for k, v in context.items()},
            'violations': violations
        }
        
        self.validation_history.append(record)
        
        # Keep only last 1000 validations
        if len(self.validation_history) > 1000:
            self.validation_history = self.validation_history[-1000:]
            
    def get_validation_history(self, operation_type: Optional[str] = None) -> List[Dict]:
        """Get validation history, optionally filtered by operation type"""
        if operation_type:
            return [
                record for record in self.validation_history
                if record['operation_type'] == operation_type
            ]
        return self.validation_history
