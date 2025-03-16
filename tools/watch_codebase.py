"""
Start the codebase watcher for real-time health and dependency analysis
"""

import os
import sys
import logging
from pathlib import Path

# Add tools directory to Python path
tools_dir = Path(__file__).parent
if str(tools_dir) not in sys.path:
    sys.path.append(str(tools_dir))

from kg.file_watcher import CodeWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    # Get the project root directory (where this script is located)
    root_dir = Path(__file__).parent.parent.absolute()
    context_dir = root_dir / "semantic_context"
    
    # Create context directory if it doesn't exist
    context_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Starting watcher for {root_dir}")
    logger.info(f"Using configuration from tools/kg/KNOWLEDGE_GRAPH_CONFIG.md")
    logger.info(f"Context directory: {context_dir}")
    
    # Start the watcher
    watcher = CodeWatcher(str(root_dir), str(context_dir))
    try:
        watcher.start()
        logger.info("Watcher started successfully")
        logger.info("Monitoring the following directories:")
        for dir in watcher.INCLUDED_DIRS:
            logger.info(f"  - {os.path.join(root_dir, dir)}")
    except Exception as e:
        logger.error(f"Failed to start watcher: {e}")
        raise

if __name__ == "__main__":
    main()
