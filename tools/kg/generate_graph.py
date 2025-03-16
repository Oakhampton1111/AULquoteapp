"""
Knowledge Graph Generation Script
Generates an optimized knowledge graph for the AUL Quote App
"""

import logging
from pathlib import Path
import networkx as nx
from datetime import datetime
import json
import os
import time
from enum import Enum
from typing import Any

from .kg_generator import build_knowledge_graph, InterfaceType
from .config.kg_config import PROJECT_ROOT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def _json_default(obj: Any) -> Any:
    """Custom JSON encoder for handling special types"""
    if isinstance(obj, InterfaceType):
        return obj.name
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')

def prepare_graph_for_export(graph: nx.DiGraph) -> nx.DiGraph:
    """
    Prepare graph for GraphML export by converting non-compatible data types
    """
    def serialize_value(value: Any) -> Any:
        if isinstance(value, (str, int, float, bool)):
            return value
        elif value is None:
            return ""
        else:
            try:
                return json.dumps(value)
            except:
                return str(value)

    # Create a new graph for the serialized data
    new_graph = nx.DiGraph()
    
    # Process nodes
    for node, data in graph.nodes(data=True):
        serialized_data = {k: serialize_value(v) for k, v in data.items()}
        new_graph.add_node(node, **serialized_data)
    
    # Process edges
    for u, v, data in graph.edges(data=True):
        serialized_data = {k: serialize_value(v) for k, v in data.items()}
        new_graph.add_edge(u, v, **serialized_data)
    
    return new_graph

def generate_knowledge_graph() -> None:
    """Generate and save the knowledge graph"""
    start_time = time.time()
    logger.info("Starting knowledge graph generation...")
    
    try:
        # Build the graph
        graph = build_knowledge_graph(PROJECT_ROOT)
        
        # Prepare graph for export
        export_graph = prepare_graph_for_export(graph)
        
        # Generate timestamp for versioning
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save both GraphML and JSON versions
        graphml_path = PROJECT_ROOT / f"code_knowledge_graph_{timestamp}.graphml"
        json_path = PROJECT_ROOT / f"code_knowledge_graph_{timestamp}.json"
        
        # Save as GraphML
        nx.write_graphml(export_graph, graphml_path)
        
        # Convert to JSON-compatible format
        json_data = {
            'nodes': [{'id': n, **d} for n, d in graph.nodes(data=True)],
            'edges': [{'source': u, 'target': v, **d} for u, v, d in graph.edges(data=True)],
            'metadata': {
                'generated_at': timestamp,
                'node_count': graph.number_of_nodes(),
                'edge_count': graph.number_of_edges(),
                'health_issues': graph.graph.get('health_issues', {})
            }
        }
        
        # Save as JSON with custom encoder
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=_json_default)
        
        # Log statistics
        num_nodes = graph.number_of_nodes()
        num_edges = graph.number_of_edges()
        duration = time.time() - start_time
        
        logger.info(f"Knowledge graph generated successfully:")
        logger.info(f"- Nodes: {num_nodes}")
        logger.info(f"- Edges: {num_edges}")
        logger.info(f"- Duration: {duration:.2f} seconds")
        logger.info(f"- GraphML Output: {graphml_path}")
        logger.info(f"- JSON Output: {json_path}")
        
    except Exception as e:
        logger.error(f"Error generating knowledge graph: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    generate_knowledge_graph()
