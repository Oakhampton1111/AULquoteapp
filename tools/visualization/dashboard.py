"""
Knowledge Graph Visualization Dashboard
Provides interactive visualization and analysis of the code knowledge graph
"""

import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from pathlib import Path
import sys
import json
from typing import Dict, List, Any
import pandas as pd

# Add tools directory to path
tools_dir = Path(__file__).parent.parent
sys.path.append(str(tools_dir))

from db.graph_db import GraphDatabaseManager

def create_graph_visualization(graph: nx.DiGraph) -> go.Figure:
    """Create an interactive graph visualization using Plotly"""
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_text = []
    
    pos = nx.spring_layout(graph)
    
    for edge in graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.append(edge[2].get('edge_type', 'unknown'))
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        text=edge_text,
        mode='lines'
    )
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    
    for node, data in graph.nodes(data=True):
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"Name: {node}<br>Type: {data.get('node_type', 'unknown')}")
        # Color by node type
        if data.get('node_type') == 'class':
            node_color.append('#1f77b4')  # blue
        elif data.get('node_type') == 'function':
            node_color.append('#2ca02c')  # green
        else:
            node_color.append('#d62728')  # red
            
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        text=node_text,
        marker=dict(
            size=10,
            color=node_color,
            line_width=2
        )
    )
    
    # Create the figure
    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title='Code Knowledge Graph',
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20,l=5,r=5,t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )
    )
    
    return fig

def display_statistics(stats: Dict[str, Any]):
    """Display database statistics"""
    st.subheader("Knowledge Graph Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Nodes", stats['node_count'])
        st.metric("Total Relationships", stats['relationship_count'])
        
    with col2:
        st.subheader("Node Types")
        for node_type, count in stats['node_types'].items():
            st.metric(node_type or 'unknown', count)
            
    st.subheader("Relationship Types")
    for rel_type, count in stats['relationship_types'].items():
        st.metric(rel_type or 'unknown', count)
        
def display_dead_code(dead_code: List[str]):
    """Display dead code analysis"""
    st.subheader("Dead Code Analysis")
    
    if dead_code:
        st.warning(f"Found {len(dead_code)} potentially dead code nodes")
        for node in dead_code:
            st.code(node, language="python")
    else:
        st.success("No dead code detected")
        
def display_duplicates(duplicates: List[Dict[str, Any]]):
    """Display code duplication analysis"""
    st.subheader("Code Duplication Analysis")
    
    if duplicates:
        st.warning(f"Found {len(duplicates)} potential code duplicates")
        df = pd.DataFrame(duplicates)
        st.dataframe(df)
    else:
        st.success("No code duplicates detected")
        
def main():
    """Main dashboard application"""
    st.set_page_config(
        page_title="Code Knowledge Graph Dashboard",
        page_icon="🧊",
        layout="wide"
    )
    
    st.title("Code Knowledge Graph Dashboard")
    
    # Initialize database connection
    db = GraphDatabaseManager()
    
    try:
        # Create a sample graph for testing if no graph exists
        if not Path("code_knowledge_graph.graphml").exists():
            graph = nx.DiGraph()
            graph.add_node("main", node_type="function")
            graph.add_node("helper", node_type="function")
            graph.add_edge("main", "helper", edge_type="CALLS")
            nx.write_graphml(graph, "code_knowledge_graph.graphml")
        
        # Load the graph
        graph = nx.read_graphml("code_knowledge_graph.graphml")
        
        # Import to database
        db.import_networkx_graph(graph)
        
        # Get statistics
        stats = db.get_statistics()
        display_statistics(stats)
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["Graph Visualization", "Dead Code", "Duplicates"])
        
        with tab1:
            st.subheader("Knowledge Graph Visualization")
            fig = create_graph_visualization(graph)
            st.plotly_chart(fig, use_container_width=True)
            
        with tab2:
            dead_code = db.find_dead_code()
            display_dead_code(dead_code)
            
        with tab3:
            duplicates = db.find_duplicates()
            display_duplicates(duplicates)
            
    except Exception as e:
        st.error(f"Error: {e}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
