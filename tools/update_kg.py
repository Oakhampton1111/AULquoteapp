"""
Update Knowledge Graph
"""

import sys
from pathlib import Path

# Add tools directory to Python path
tools_dir = Path(__file__).parent
if str(tools_dir) not in sys.path:
    sys.path.append(str(tools_dir))

from kg.generate_graph import generate_knowledge_graph

if __name__ == "__main__":
    generate_knowledge_graph()
