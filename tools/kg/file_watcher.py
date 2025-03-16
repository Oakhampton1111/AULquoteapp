"""
Real-time file watcher for code health and dependency analysis
"""

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from pathlib import Path
import logging
from typing import Set, Optional, Dict, Any
import threading
import queue
import os
import re
from datetime import datetime

from .semantic_context_manager import SemanticContextManager
from .cleanup.code_health_manager import CodeHealthManager

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self, root_dir: str, context_dir: str):
        super().__init__()
        self.root_dir = Path(root_dir)
        self.context_dir = Path(context_dir)
        self.semantic_manager = SemanticContextManager(self.context_dir)
        self.health_manager = CodeHealthManager(self.semantic_manager)
        self.change_queue = queue.Queue()
        self.changed_files: Set[Path] = set()
        self.last_analysis_time = 0
        self.analysis_cooldown = 5  # seconds
        self.running = True
        self.analysis_thread = threading.Thread(target=self._process_changes, daemon=True)
        self.analysis_thread.start()
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if not self._should_process_file(file_path):
            return
            
        logger.debug(f"File modified: {file_path}")
        self.change_queue.put(("modified", file_path))
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if not self._should_process_file(file_path):
            return
            
        logger.debug(f"File created: {file_path}")
        self.change_queue.put(("created", file_path))
        
    def on_deleted(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if not self._should_process_file(file_path):
            return
            
        logger.debug(f"File deleted: {file_path}")
        self.change_queue.put(("deleted", file_path))
        
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if the file should be processed based on extension and location"""
        try:
            if not os.path.exists(file_path) or os.path.isdir(file_path):
                return False
                
            # Convert to relative path for easier checking
            try:
                rel_path = str(file_path.relative_to(self.root_dir)).replace('\\', '/')
            except ValueError:
                # File is outside of root directory
                return False
                
            # Skip excluded patterns
            for pattern in CodeWatcher.EXCLUDED_PATTERNS:
                if re.match(pattern, rel_path):
                    return False
                    
            # Only process files in included directories
            for included in CodeWatcher.INCLUDED_DIRS:
                included = included.replace('\\', '/')
                if included in rel_path:
                    # Only process Python and TypeScript operational files
                    if file_path.suffix in ['.py', '.ts', '.tsx'] and not file_path.name.startswith('__'):
                        return True
                        
            return False
            
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {str(e)}")
            return False
        
    def _process_changes(self):
        """Process file changes in a separate thread"""
        while self.running:
            try:
                # Wait for changes to accumulate
                time.sleep(self.analysis_cooldown)
                
                # Process all pending changes
                changed = False
                while not self.change_queue.empty():
                    try:
                        change_type, file_path = self.change_queue.get_nowait()
                        self.changed_files.add(file_path)
                        changed = True
                    except queue.Empty:
                        break
                    
                if changed:
                    current_time = time.time()
                    if current_time - self.last_analysis_time > self.analysis_cooldown:
                        self._analyze_changes()
                        self.changed_files.clear()
                        self.last_analysis_time = current_time
                    
            except Exception as e:
                logger.error(f"Error processing changes: {e}")
                
    def _analyze_changes(self):
        """Analyze the accumulated changes"""
        try:
            if not self.changed_files:
                return
                
            logger.info(f"Analyzing {len(self.changed_files)} changed files...")
            
            # Ensure semantic manager has initial context
            if not self.semantic_manager.components:
                logger.info("Loading initial semantic context...")
                self.semantic_manager.load_context()
            
            # Update semantic context for changed files
            for file_path in self.changed_files:
                try:
                    if os.path.exists(file_path):
                        logger.info(f"Updating context for {file_path}")
                        self.semantic_manager.update_file_context(str(file_path))
                except Exception as e:
                    logger.error(f"Error updating context for {file_path}: {str(e)}")
            
            # Analyze code health
            try:
                health_report = self.health_manager.analyze_codebase(str(self.root_dir))
                
                # Save health report
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = os.path.join(self.root_dir, f"code_health_report_{timestamp}.json")
                
                if health_report:
                    self.health_manager.save_report(health_report, report_path)
                    logger.info(f"Health analysis completed. Report saved to: {report_path}")
                    
                    # Log health score and any critical issues
                    score = health_report.get('health_score', 0.0)
                    logger.info(f"Health Score: {score:.2f}%")
                    
                    if 'issues' in health_report:
                        critical_issues = [i for i in health_report['issues'] 
                                        if i.get('severity') in ['high', 'critical']]
                        if critical_issues:
                            logger.warning("Critical issues found:")
                            for issue in critical_issues:
                                logger.warning(f"- {issue.get('type')}: {issue.get('details')}")
                
            except Exception as e:
                logger.error(f"Error analyzing code health: {str(e)}")
                import traceback
                logger.debug(traceback.format_exc())
            
            # Clear the changed files set
            self.changed_files.clear()
            
        except Exception as e:
            logger.error(f"Error during analysis: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            
    def stop(self):
        """Stop the analysis thread"""
        self.running = False
        if self.analysis_thread.is_alive():
            self.analysis_thread.join(timeout=1.0)


class CodeWatcher:
    """Watches codebase for changes and triggers analysis."""
    
    # Directories to watch - aligned with knowledge graph config
    INCLUDED_DIRS = [
        'frontend/src/components',  # React/TypeScript UI components
        'frontend/src/api',         # API client code
        'frontend/src/services',    # Frontend services
        'warehouse_quote_app/app',  # Backend core app
        'warehouse_quote_app/app/services',  # Backend services
        'warehouse_quote_app/app/models'     # Backend data models
    ]
    
    # Patterns to exclude - aligned with knowledge graph config
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
    
    def __init__(self, root_dir: str, context_dir: Optional[str] = None):
        self.root_dir = Path(root_dir).resolve()  # Use absolute path
        self.context_dir = Path(context_dir).resolve() if context_dir else self.root_dir / "semantic_context"
        self.context_dir.mkdir(parents=True, exist_ok=True)  # Ensure context directory exists
        
        logger.info(f"Initializing CodeWatcher for {self.root_dir}")
        logger.info(f"Using context directory: {self.context_dir}")
        
        self.event_handler = CodeChangeHandler(str(self.root_dir), str(self.context_dir))
        self.observer = Observer()
        
    def start(self):
        """Start watching for file changes"""
        try:
            self.observer.schedule(self.event_handler, str(self.root_dir), recursive=True)
            self.observer.start()
            logger.info(f"Started watching {self.root_dir}")
            
            # Run until interrupted
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
            self.stop()
        except Exception as e:
            logger.error(f"Error in watcher: {e}", exc_info=True)
            self.stop()
            raise
            
    def stop(self):
        """Stop watching for file changes"""
        logger.info("Stopping watcher...")
        self.event_handler.stop()
        self.observer.stop()
        self.observer.join()
        logger.info("Watcher stopped")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python file_watcher.py <root_dir> [context_dir]")
        sys.exit(1)
        
    root_dir = sys.argv[1]
    context_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    watcher = CodeWatcher(root_dir, context_dir)
    watcher.start()
