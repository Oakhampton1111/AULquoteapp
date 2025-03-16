"""
Automated Knowledge Graph Updater
Watches for file changes and updates the knowledge graph accordingly
Enhanced with semantic context tracking
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import networkx as nx
from pathlib import Path
import logging
from typing import Set, Dict, Any, Optional, List, Tuple
import ast
from concurrent.futures import ThreadPoolExecutor
import threading
import hashlib
import json
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime, timedelta
import tempfile
from copy import deepcopy

from .ts_analyzer import TypeScriptAnalyzer
from .semantic_context_manager import SemanticContextManager
from .semantic_context_checker import SemanticContextChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UpdateType(Enum):
    """Types of updates that can occur"""
    SYNTAX_ONLY = "syntax_only"  # Only whitespace or comments changed
    MINOR = "minor"  # Small changes that don't affect structure
    STRUCTURAL = "structural"  # Changes that affect code structure
    BREAKING = "breaking"  # Changes that could break dependencies
    CIRCULAR = "circular"  # Introduces circular dependencies
    SECURITY = "security"  # Potential security issues
    PERFORMANCE = "performance"  # Performance impact changes
    SEMANTIC = "semantic"  # Changes affecting semantic relationships
    HEALTH = "health"  # Changes affecting codebase health metrics

@dataclass
class UpdateValidation:
    """Validation result for a file update"""
    is_valid: bool
    update_type: UpdateType
    changes: Dict[str, Any]
    error: Optional[str] = None
    warnings: List[str] = None
    impact_score: float = 0.0  # 0.0 to 1.0, higher means more impact
    affected_files: List[str] = None
    semantic_changes: Dict[str, Any] = None
    health_impact: Optional[Dict[str, float]] = None  # Impact on health metrics

class UpdateThrottler:
    """Prevents too frequent updates to the same file"""
    def __init__(self, min_interval: int = 5):
        self.last_updates = {}
        self.min_interval = min_interval  # minimum seconds between updates
        
    def can_update(self, file_path: str) -> bool:
        now = datetime.now()
        if file_path in self.last_updates:
            if now - self.last_updates[file_path] < timedelta(seconds=self.min_interval):
                return False
        self.last_updates[file_path] = now
        return True

class SecurityChecker:
    """Checks for potential security issues in code changes"""
    SECURITY_PATTERNS = {
        'hardcoded_secrets': r'(?i)(password|secret|key|token|api_key)\s*=\s*[\'"][^\'"]+[\'"]',
        'sql_injection': r'(?i)execute\s*\(\s*.*\+.*\)',
        'command_injection': r'(?i)(os\.system|subprocess\.run|eval|exec)\s*\(',
        'unsafe_deserialization': r'(?i)(pickle\.loads|yaml\.load\s*\([^)])',
        'file_access': r'(?i)(open|file)\s*\([\'"][^\'"]+[\'"]'
    }
    
    @classmethod
    def check_security(cls, content: str) -> List[str]:
        issues = []
        for issue_type, pattern in cls.SECURITY_PATTERNS.items():
            if re.search(pattern, content):
                issues.append(f"Potential {issue_type} detected")
        return issues

class CircularDependencyChecker:
    """Checks for circular dependencies in the code"""
    def __init__(self, graph_manager):
        self.graph_manager = graph_manager
        
    def check_circular(self, new_graph: nx.DiGraph) -> List[List[str]]:
        """Returns list of circular dependency chains"""
        # Combine existing graph with new changes
        full_graph = self.graph_manager.export_graph()
        test_graph = nx.compose(full_graph, new_graph)
        
        try:
            cycles = list(nx.simple_cycles(test_graph))
            return cycles
        except Exception as e:
            logger.error(f"Error checking circular dependencies: {e}")
            return []

class PerformanceAnalyzer:
    """Analyzes potential performance impacts of changes"""
    def __init__(self):
        self.complexity_threshold = 10  # McCabe complexity threshold
        
    def analyze_performance(self, tree: ast.AST) -> List[str]:
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                # Check for nested loops
                if any(isinstance(child, (ast.For, ast.While)) for child in ast.walk(node)):
                    issues.append("Nested loop detected - potential O(n²) complexity")
                    
            elif isinstance(node, ast.ListComp):
                # Check for nested list comprehensions
                if any(isinstance(child, ast.ListComp) for child in ast.walk(node)):
                    issues.append("Nested list comprehension detected")
                    
            elif isinstance(node, ast.Call):
                # Check for potential memory issues
                if isinstance(node.func, ast.Name):
                    if node.func.id in ['range', 'list', 'dict', 'set']:
                        # Check if large collection is being created
                        if node.args and isinstance(node.args[0], ast.Num):
                            if node.args[0].n > 10000:
                                issues.append(f"Large collection creation: {node.func.id}({node.args[0].n})")
                                
        return issues

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, graph_manager, ts_analyzer):
        """Initialize the change handler"""
        self.graph_manager = graph_manager
        self.ts_analyzer = ts_analyzer
        self.update_queue = set()
        self.queue_lock = threading.Lock()
        self.file_hashes = {}  # Store file hashes to detect real changes
        self.backup_folder = Path("./backups")
        self.backup_folder.mkdir(exist_ok=True)
        self.throttler = UpdateThrottler()
        self.circular_checker = CircularDependencyChecker(graph_manager)
        self.performance_analyzer = PerformanceAnalyzer()
        
        # Initialize semantic managers
        self.semantic_manager = SemanticContextManager(Path("./semantic_context"))
        self.context_checker = SemanticContextChecker(self.semantic_manager)
        
        # Track health metrics
        self.last_health_score = None
        self.health_threshold = 0.7  # Minimum acceptable health score
        
        self.update_thread = threading.Thread(target=self._process_updates, daemon=True)
        self.update_thread.start()

    def _backup_file(self, file_path: str):
        """Create a backup of the file before updating"""
        try:
            backup_path = self.backup_folder / f"{Path(file_path).name}.{int(time.time())}.bak"
            with open(file_path, 'rb') as src, open(backup_path, 'wb') as dst:
                dst.write(src.read())
            return backup_path
        except Exception as e:
            logger.error(f"Error creating backup for {file_path}: {e}")
            return None
            
    def _restore_backup(self, backup_path: Path):
        """Restore file from backup"""
        try:
            original_name = backup_path.stem.rsplit('.', 1)[0]
            original_path = Path(original_name)
            with open(backup_path, 'rb') as src, open(original_path, 'wb') as dst:
                dst.write(src.read())
            logger.info(f"Restored backup for {original_path}")
        except Exception as e:
            logger.error(f"Error restoring backup {backup_path}: {e}")
            
    def _get_file_hash(self, file_path: str) -> str:
        """Get hash of file contents"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return None
            
    def _validate_update(self, file_path: str) -> UpdateValidation:
        """Validate if a file update should be processed"""
        try:
            # First, check semantic context
            with open(file_path, 'r', encoding='utf-8') as f:
                new_content = f.read()
                
            context_validation = self.context_checker.validate_change(file_path, new_content)
            if not context_validation.is_valid:
                return UpdateValidation(
                    False,
                    UpdateType.BREAKING,
                    {},
                    context_validation.error,
                    [],
                    1.0,
                    []
                )
                
            # Add semantic validation warnings
            warnings = list(context_validation.warnings)
            
            # Check if file still exists
            if not Path(file_path).exists():
                return UpdateValidation(
                    False,
                    UpdateType.BREAKING,
                    {},
                    "File no longer exists",
                    warnings,
                    1.0,
                    []
                )
                
            # Check update frequency
            if not self.throttler.can_update(file_path):
                return UpdateValidation(
                    False,
                    UpdateType.MINOR,
                    {},
                    "Update throttled - too frequent changes",
                    warnings,
                    0.0,
                    []
                )
                
            # Get old content from backup if available
            old_content = ""
            backup_files = list(self.backup_folder.glob(f"{Path(file_path).name}.*"))
            if backup_files:
                latest_backup = max(backup_files, key=lambda x: int(x.suffix[1:]))
                with open(latest_backup, 'r', encoding='utf-8') as f:
                    old_content = f.read()
                    
            # Use semantic context for update type and impact
            update_type = UpdateType.SEMANTIC if context_validation.impact_assessment["impact_score"] > 0.3 else UpdateType.MINOR
            
            return UpdateValidation(
                True,
                update_type,
                {"content_changed": bool(old_content != new_content)},
                None,
                warnings,
                context_validation.impact_assessment["impact_score"],
                list(context_validation.related_files),
                context_validation.context_data
            )
            
        except Exception as e:
            logger.error(f"Error validating update for {file_path}: {e}")
            return UpdateValidation(False, UpdateType.BREAKING, {}, str(e), [], 1.0, [])
            
    def _determine_update_type(self, old_content: str, new_content: str, semantic_changes: Dict) -> Tuple[UpdateType, Dict]:
        """Determine the type of update and its health impact"""
        # Get current health metrics
        health_before = self.semantic_manager.analyze_codebase_health()
        
        # Analyze changes
        security_issues = SecurityChecker.check_security(new_content)
        performance_impact = self.performance_analyzer.analyze_performance(ast.parse(new_content))
        circular_deps = self.circular_checker.check_circular(self.graph_manager.graph)
        
        # Get updated health metrics
        health_after = self.semantic_manager.analyze_codebase_health()
        
        # Calculate health impact
        health_impact = {
            'score_change': health_after['health_score'] - health_before['health_score'],
            'duplication_change': health_after['metrics']['duplication_rate'] - health_before['metrics']['duplication_rate'],
            'orphan_change': health_after['metrics']['orphan_rate'] - health_before['metrics']['orphan_rate'],
            'divergence_change': health_after['metrics']['divergence_rate'] - health_before['metrics']['divergence_rate']
        }
        
        # Determine update type based on all factors
        if security_issues:
            return UpdateType.SECURITY, health_impact
        elif circular_deps:
            return UpdateType.CIRCULAR, health_impact
        elif performance_impact > 0.5:  # High performance impact
            return UpdateType.PERFORMANCE, health_impact
        elif abs(health_impact['score_change']) > 0.1:  # Significant health change
            return UpdateType.HEALTH, health_impact
        elif semantic_changes:
            return UpdateType.SEMANTIC, health_impact
        else:
            return UpdateType.MINOR, health_impact
        
    def _calculate_impact_score(self, update_type: UpdateType, semantic_changes: Dict) -> float:
        """Calculate impact score based on update type and semantic changes"""
        base_scores = {
            UpdateType.SYNTAX_ONLY: 0.1,
            UpdateType.MINOR: 0.3,
            UpdateType.STRUCTURAL: 0.6,
            UpdateType.SEMANTIC: 0.7,
            UpdateType.BREAKING: 1.0,
            UpdateType.CIRCULAR: 0.9,
            UpdateType.SECURITY: 0.8,
            UpdateType.PERFORMANCE: 0.5,
            UpdateType.HEALTH: 0.8
        }
        
        base_score = base_scores.get(update_type, 0.5)
        
        # Adjust score based on semantic changes
        if semantic_changes:
            removed = len(semantic_changes.get("removed_relationships", []))
            new = len(semantic_changes.get("new_relationships", []))
            maintained = len(semantic_changes.get("maintained_relationships", []))
            
            if removed > 0:
                base_score += 0.2  # Breaking existing relationships is high impact
            if new > maintained:
                base_score += 0.1  # More new than maintained relationships
                
        return min(base_score, 1.0)
        
    def _get_affected_files(self, file_path: str, semantic_changes: Dict) -> List[str]:
        """Get list of files affected by the changes"""
        affected = set()
        
        # Add direct dependencies from graph
        for edge in self.graph_manager.graph.edges(file_path):
            affected.add(edge[1])
            
        # Add semantically related files
        if semantic_changes:
            affected.update(semantic_changes.get("removed_relationships", []))
            affected.update(semantic_changes.get("new_relationships", []))
            affected.update(semantic_changes.get("maintained_relationships", []))
            
        return list(affected)
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        file_path = event.src_path
        if not any(file_path.endswith(ext) for ext in ['.py', '.ts', '.tsx', '.js', '.jsx']):
            return
            
        with self.queue_lock:
            self.update_queue.add(file_path)
            
    def _process_file_update(self, file_path: str):
        """Process a single file update"""
        try:
            # Validate update
            validation = self._validate_update(file_path)
            if not validation.is_valid:
                logger.warning(f"Update validation failed for {file_path}: {validation.error}")
                return
                
            # Create backup
            backup_path = self._backup_file(file_path)
            
            # Update graph
            self.graph_manager.update_file(file_path)
            
            # Update semantic context
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.semantic_manager.update_context(
                file_path,
                content,
                {"last_modified": datetime.now().isoformat()}
            )
            
            # Log update details
            logger.info(f"Processed update for {file_path}")
            logger.info(f"Update type: {validation.update_type}")
            logger.info(f"Impact score: {validation.impact_score}")
            if validation.semantic_changes:
                logger.info("Semantic changes detected:")
                logger.info(f"- New relationships: {len(validation.semantic_changes['new_relationships'])}")
                logger.info(f"- Removed relationships: {len(validation.semantic_changes['removed_relationships'])}")
                
        except Exception as e:
            logger.error(f"Error processing update for {file_path}: {e}")
            if backup_path:
                self._restore_backup(backup_path)

    def _process_updates(self):
        """Process queued file updates"""
        while True:
            time.sleep(1)  # Wait for more changes to accumulate
            
            with self.queue_lock:
                current_updates = self.update_queue.copy()
                self.update_queue.clear()
                
            if current_updates:
                for file_path in current_updates:
                    self._process_file_update(file_path)
                    
class GraphUpdater:
    def __init__(self, graph_manager, watch_paths: list):
        """Initialize the graph updater"""
        self.graph_manager = graph_manager
        self.watch_paths = watch_paths
        self.ts_analyzer = TypeScriptAnalyzer()
        self.observer = Observer()
        self.handler = CodeChangeHandler(graph_manager, self.ts_analyzer)
        
    def start(self):
        """Start watching for file changes"""
        for path in self.watch_paths:
            self.observer.schedule(self.handler, path, recursive=True)
        self.observer.start()
        logger.info(f"Started watching {len(self.watch_paths)} paths for changes")
        
    def stop(self):
        """Stop watching for file changes"""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped watching for changes")
        
def main():
    """Test the graph updater"""
    from .graph_db import GraphDatabaseManager
    
    # Initialize components
    db = GraphDatabaseManager()
    watch_paths = ["."]  # Watch current directory
    updater = GraphUpdater(db, watch_paths)
    
    try:
        # Start watching for changes
        updater.start()
        
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping graph updater...")
        updater.stop()
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
