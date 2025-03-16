"""
Knowledge Graph Generator
Builds a knowledge graph focusing on interfaces and semantic relationships
"""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple
import networkx as nx
from sentence_transformers import SentenceTransformer
import json
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import logging
import os
import matplotlib.pyplot as plt
import torch

from .config.kg_config import (
    get_high_priority_paths,
    should_exclude_path,
    get_relationship_config,
    get_code_health_rules,
    get_domain_group,
    get_interface_type,
    PROJECT_ROOT,
    DomainGroup,
    InterfaceType,
    INTERFACE_DEFINITIONS
)

logger = logging.getLogger(__name__)

# Define directories to include in knowledge graph generation
INCLUDED_DIRS = [
    'frontend/src/components',
    'frontend/src/api',
    'frontend/src/services',
    'warehouse_quote_app/app',
    'warehouse_quote_app/app/services',
    'warehouse_quote_app/app/models'
]

# Define directories and patterns to exclude
EXCLUDED_PATTERNS = [
    r'.*\.git.*',
    r'.*\.venv.*',
    r'.*__pycache__.*',
    r'.*\.pytest_cache.*',
    r'.*\.mypy_cache.*',
    r'.*\.vscode.*',
    r'.*\.idea.*',
    r'.*\.DS_Store.*',
    r'.*\.env.*',
    r'.*node_modules.*',
    r'.*\.(test|spec)\.(ts|tsx|js|jsx|py)$',  # Test files
    r'.*/tests/.*',
    r'.*/scripts/.*',
    r'.*/migrations/.*',
    r'.*/deployment/.*'
]

@dataclass
class CodeNode:
    """Represents a node in the code knowledge graph"""
    name: str
    type: str
    file: str
    line_number: int
    docstring: Optional[str] = None
    interface_type: Optional[InterfaceType] = None
    domain_group: Optional[DomainGroup] = None
    semantic_group: Optional[str] = None
    content: Optional[str] = None

@dataclass
class CodeEdge:
    """Represents an edge in the code knowledge graph"""
    source: str
    target: str
    type: str
    weight: float = 1.0
    properties: Optional[Dict] = None

class InterfaceAnalyzer(ast.NodeVisitor):
    """Analyzes interface definitions and implementations"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.interfaces: Dict[str, CodeNode] = {}
        self.implementations: Dict[str, CodeNode] = {}
        self.edges: List[CodeEdge] = []
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Process class definitions to identify interfaces and implementations"""
        # Check if this is an interface
        is_interface = any(
            base.id.endswith('Interface')
            for base in node.bases
            if isinstance(base, ast.Name)
        )
        
        if is_interface:
            self.interfaces[node.name] = CodeNode(
                name=node.name,
                type='interface',
                file=self.file_path,
                line_number=node.lineno,
                docstring=ast.get_docstring(node),
                interface_type=get_interface_type(self.file_path),
                domain_group=get_domain_group(self.file_path),
                content=self._get_node_content(node)
            )
        else:
            # Check if this class implements any interfaces
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id in self.interfaces:
                    self.implementations[node.name] = CodeNode(
                        name=node.name,
                        type='class',
                        file=self.file_path,
                        line_number=node.lineno,
                        docstring=ast.get_docstring(node),
                        interface_type=get_interface_type(self.file_path),
                        domain_group=get_domain_group(self.file_path),
                        content=self._get_node_content(node)
                    )
                    
                    self.edges.append(CodeEdge(
                        source=node.name,
                        target=base.id,
                        type='implements_interface',
                        weight=2.0
                    ))
        
        self.generic_visit(node)
        
    def _get_node_content(self, node: ast.AST) -> str:
        """Extract the content of a node"""
        return ast.unparse(node)

class SemanticAnalyzer:
    """Analyzes semantic relationships between code elements"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
        self.relationship_config = get_relationship_config()
        
    def analyze_semantic_relationships(
            self,
            graph: nx.DiGraph,
            min_similarity: float = 0.7
        ) -> List[CodeEdge]:
        """
        Analyze semantic relationships between nodes
        
        Args:
            graph: Knowledge graph
            min_similarity: Minimum cosine similarity threshold
            
        Returns:
            List of semantic relationship edges
        """
        edges = []
        nodes = list(graph.nodes(data=True))
        
        # Pre-compute embeddings with batching for efficiency
        self._precompute_embeddings(nodes)
        
        # Analyze relationships between nodes
        for i, (node1, data1) in enumerate(nodes[:-1]):
            for node2, data2 in nodes[i+1:]:
                if self._should_analyze_relationship(data1, data2):
                    relationship = self._analyze_node_relationship(
                        node1, data1, node2, data2, min_similarity
                    )
                    if relationship:
                        edges.append(relationship)
        
        return edges
        
    def _precompute_embeddings(self, nodes: List[tuple]) -> None:
        """Pre-compute embeddings for all nodes in batches"""
        batch_size = 32
        texts = []
        node_ids = []
        
        for node, data in nodes:
            if node not in self.embeddings_cache:
                text = self._get_node_text(data)
                if text:
                    texts.append(text)
                    node_ids.append(node)
                
            if len(texts) >= batch_size:
                embeddings = self.model.encode(texts)
                for node_id, embedding in zip(node_ids, embeddings):
                    self.embeddings_cache[node_id] = embedding
                texts = []
                node_ids = []
                
        if texts:  # Handle remaining texts
            embeddings = self.model.encode(texts)
            for node_id, embedding in zip(node_ids, embeddings):
                self.embeddings_cache[node_id] = embedding
                
    def _should_analyze_relationship(
            self,
            data1: Dict,
            data2: Dict
        ) -> bool:
        """Determine if two nodes should be analyzed for relationships"""
        # Skip if nodes are in different domain groups
        if (data1.get('domain_group') != data2.get('domain_group')):
            return False
            
        # Skip if nodes are of incompatible types
        incompatible_types = self.relationship_config.get('incompatible_types', [])
        if (data1.get('type'), data2.get('type')) in incompatible_types:
            return False
            
        return True
        
    def _analyze_node_relationship(
            self,
            node1: str,
            data1: Dict,
            node2: str,
            data2: Dict,
            min_similarity: float
        ) -> Optional[CodeEdge]:
        """Analyze relationship between two nodes"""
        # Get embeddings
        emb1 = self.embeddings_cache.get(node1)
        emb2 = self.embeddings_cache.get(node2)
        
        if emb1 is None or emb2 is None:
            return None
            
        # Calculate similarity
        similarity = float(cosine_similarity([emb1], [emb2])[0][0])
        
        if similarity >= min_similarity:
            relationship_type = self._determine_relationship_type(
                data1, data2, similarity
            )
            return CodeEdge(
                source=node1,
                target=node2,
                type=relationship_type,
                weight=similarity,
                properties={
                    'similarity_score': similarity,
                    'relationship_confidence': self._calculate_confidence(
                        similarity, data1, data2
                    )
                }
            )
        return None
        
    def _get_node_text(self, data: Dict) -> Optional[str]:
        """Get text representation of a node for embedding"""
        texts = []
        if data.get('docstring'):
            texts.append(data['docstring'])
        if data.get('name'):
            texts.append(data['name'])
        if data.get('content'):
            texts.append(data['content'])
        return ' '.join(texts) if texts else None
        
    def _determine_relationship_type(
            self,
            data1: Dict,
            data2: Dict,
            similarity: float
        ) -> str:
        """Determine the type of relationship between nodes"""
        if similarity > 0.9:
            return 'highly_related'
        elif similarity > 0.8:
            return 'moderately_related'
        return 'weakly_related'
        
    def _calculate_confidence(
            self,
            similarity: float,
            data1: Dict,
            data2: Dict
        ) -> float:
        """Calculate confidence score for the relationship"""
        # Base confidence on similarity
        confidence = similarity
        
        # Adjust based on available metadata
        if data1.get('docstring') and data2.get('docstring'):
            confidence *= 1.2
        if data1.get('content') and data2.get('content'):
            confidence *= 1.1
            
        return min(confidence, 1.0)

class CodeHealthAnalyzer:
    """Analyzes code health issues"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.rules = get_code_health_rules()
        self.model = SentenceTransformer(model_name)
        self.embeddings_cache = {}
        self.health_metrics = defaultdict(list)
        
    def analyze_health(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """
        Analyze code health issues in the graph
        
        Args:
            graph: Knowledge graph
            
        Returns:
            Dict containing health metrics and issues
        """
        self.health_metrics.clear()
        
        # Find code duplicates
        duplicate_issues = self.find_code_duplicates(dict(graph.nodes(data=True)))
        self.health_metrics['duplicates'].extend(duplicate_issues)
        
        # Find interface divergence
        divergence_issues = self.find_interface_divergence(graph)
        self.health_metrics['divergence'].extend(divergence_issues)
        
        # Find orphaned components
        orphan_issues = self._find_orphans(graph)
        self.health_metrics['orphans'].extend(orphan_issues)
        
        # Calculate overall health score
        health_score = self._calculate_health_score()
        
        return {
            'health_score': health_score,
            'metrics': dict(self.health_metrics),
            'recommendations': self._generate_recommendations()
        }
        
    def find_code_duplicates(
            self,
            nodes: Dict[str, Dict]
        ) -> List[Dict[str, Any]]:
        """
        Find potential code duplicates
        
        Args:
            nodes: Dictionary of node data
            
        Returns:
            List of duplicate code issues
        """
        issues = []
        processed = set()
        
        for name1, data1 in nodes.items():
            if not self._should_check_duplication(name1):
                continue
                
            content1 = data1.get('content', '')
            if not content1 or name1 in processed:
                continue
                
            emb1 = self._get_embedding(content1)
            if emb1 is None:
                continue
                
            for name2, data2 in nodes.items():
                if (name1 == name2 or
                    name2 in processed or
                    not self._should_check_duplication(name2)):
                    continue
                    
                content2 = data2.get('content', '')
                if not content2:
                    continue
                    
                emb2 = self._get_embedding(content2)
                if emb2 is None:
                    continue
                    
                similarity = float(cosine_similarity([emb1], [emb2])[0][0])
                
                if similarity > self.rules['duplicate_threshold']:
                    issues.append({
                        'type': 'duplicate',
                        'severity': 'high' if similarity > 0.9 else 'medium',
                        'nodes': [name1, name2],
                        'similarity': similarity,
                        'files': [data1.get('file', ''), data2.get('file', '')]
                    })
                    processed.add(name2)
                    
            processed.add(name1)
            
        return issues
        
    def find_interface_divergence(self, graph: nx.DiGraph) -> List[Dict[str, Any]]:
        """Find implementations that have diverged from their interfaces"""
        issues = []
        
        for node, data in graph.nodes(data=True):
            if data.get('type') == 'implementation':
                interface_name = data.get('implements')
                if interface_name and interface_name in graph:
                    interface_data = graph.nodes[interface_name]
                    drift = self.calculate_interface_drift(interface_data, data)
                    
                    if drift > self.rules['drift_threshold']:
                        issues.append({
                            'type': 'divergence',
                            'severity': 'high' if drift > 0.8 else 'medium',
                            'implementation': node,
                            'interface': interface_name,
                            'drift_score': drift,
                            'file': data.get('file', '')
                        })
                        
        return issues
        
    def calculate_interface_drift(
            self,
            interface_node: Dict,
            implementation_node: Dict
        ) -> float:
        """
        Calculate interface drift between interface and implementation
        
        Args:
            interface_node: Interface node data
            implementation_node: Implementation node data
            
        Returns:
            Drift score between 0 and 1
        """
        interface_methods = self._extract_methods(interface_node.get('content', ''))
        impl_methods = self._extract_methods(implementation_node.get('content', ''))
        
        # Check method signature drift
        signature_drift = self._calculate_signature_drift(
            interface_methods,
            impl_methods
        )
        
        # Check semantic drift
        semantic_drift = self._calculate_semantic_drift(
            interface_node,
            implementation_node
        )
        
        # Weighted combination
        return 0.6 * signature_drift + 0.4 * semantic_drift
        
    def _find_orphans(self, graph: nx.DiGraph) -> List[Dict[str, Any]]:
        """Find orphaned components"""
        issues = []
        
        for node, data in graph.nodes(data=True):
            if not self._should_check_orphan(node):
                continue
                
            # Check incoming and outgoing edges
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            
            if in_degree + out_degree == 0:
                issues.append({
                    'type': 'orphan',
                    'severity': 'medium',
                    'node': node,
                    'file': data.get('file', '')
                })
                
        return issues
        
    def _calculate_health_score(self) -> float:
        """Calculate overall health score"""
        total_weight = 0
        weighted_score = 0
        
        # Calculate weighted scores for each metric type
        for metric_type, issues in self.health_metrics.items():
            weight = self.rules.get(f'{metric_type}_weight', 1.0)
            severity_counts = {
                'high': sum(1 for i in issues if i['severity'] == 'high'),
                'medium': sum(1 for i in issues if i['severity'] == 'medium')
            }
            
            # Calculate metric score (0 to 1, higher is better)
            if not issues:
                metric_score = 1.0
            else:
                metric_score = 1.0 - (
                    (severity_counts['high'] * 0.8 +
                     severity_counts['medium'] * 0.4) /
                    len(issues)
                )
                
            weighted_score += metric_score * weight
            total_weight += weight
            
        return weighted_score / total_weight if total_weight > 0 else 1.0
        
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on health metrics"""
        recommendations = []
        
        # Handle duplicates
        if self.health_metrics['duplicates']:
            high_severity = sum(
                1 for i in self.health_metrics['duplicates']
                if i['severity'] == 'high'
            )
            if high_severity > 0:
                recommendations.append(
                    f"Critical: Found {high_severity} instances of high-similarity "
                    "code duplication. Consider extracting shared functionality "
                    "into reusable components."
                )
                
        # Handle divergence
        if self.health_metrics['divergence']:
            high_drift = sum(
                1 for i in self.health_metrics['divergence']
                if i['drift_score'] > 0.8
            )
            if high_drift > 0:
                recommendations.append(
                    f"Warning: {high_drift} implementations have significantly "
                    "diverged from their interfaces. Review and align them with "
                    "their interface contracts."
                )
                
        # Handle orphans
        if self.health_metrics['orphans']:
            recommendations.append(
                f"Found {len(self.health_metrics['orphans'])} orphaned "
                "components. Consider removing unused code or properly "
                "integrating these components."
            )
            
        return recommendations
        
    def _get_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get or compute embedding for text"""
        if text not in self.embeddings_cache:
            try:
                self.embeddings_cache[text] = self.model.encode(text)
            except Exception as e:
                logger.error(f"Error computing embedding: {e}")
                return None
        return self.embeddings_cache[text]
        
    def _extract_methods(self, content: str) -> Dict[str, Dict]:
        """Extract method signatures and bodies"""
        methods = {}
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    methods[node.name] = {
                        'args': [arg.arg for arg in node.args.args],
                        'returns': self._get_return_type(node),
                        'body': ast.get_source_segment(content, node)
                    }
        except Exception as e:
            logger.error(f"Error parsing content: {e}")
        return methods
        
    def _get_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if present"""
        if node.returns:
            return ast.unparse(node.returns)
        return None
        
    def _calculate_signature_drift(
            self,
            interface_methods: Dict[str, Dict],
            impl_methods: Dict[str, Dict]
        ) -> float:
        """Calculate method signature drift"""
        if not interface_methods:
            return 0.0
            
        total_drift = 0.0
        for name, interface_method in interface_methods.items():
            if name not in impl_methods:
                total_drift += 1.0
                continue
                
            impl_method = impl_methods[name]
            
            # Compare arguments
            arg_diff = set(interface_method['args']) ^ set(impl_method['args'])
            arg_drift = len(arg_diff) / max(
                len(interface_method['args']),
                len(impl_method['args'])
            ) if interface_method['args'] or impl_method['args'] else 0.0
            
            # Compare return types
            return_drift = (
                1.0 if interface_method['returns'] != impl_method['returns']
                else 0.0
            )
            
            total_drift += (arg_drift + return_drift) / 2
            
        return total_drift / len(interface_methods)
        
    def _calculate_semantic_drift(
            self,
            interface_node: Dict,
            implementation_node: Dict
        ) -> float:
        """Calculate semantic drift between interface and implementation"""
        interface_text = interface_node.get('docstring', '')
        impl_text = implementation_node.get('docstring', '')
        
        if not interface_text or not impl_text:
            return 0.0
            
        interface_emb = self._get_embedding(interface_text)
        impl_emb = self._get_embedding(impl_text)
        
        if interface_emb is None or impl_emb is None:
            return 0.0
            
        similarity = float(cosine_similarity([interface_emb], [impl_emb])[0][0])
        return 1.0 - similarity
        
    def _should_check_duplication(self, name: str) -> bool:
        """Check if a node should be checked for duplication"""
        excluded_patterns = self.rules.get('exclude_from_duplication', [])
        return not any(re.match(pattern, name) for pattern in excluded_patterns)
        
    def _should_check_orphan(self, name: str) -> bool:
        """Check if a component should be checked for orphan status"""
        excluded_patterns = self.rules.get('exclude_from_orphan_check', [])
        return not any(re.match(pattern, name) for pattern in excluded_patterns)

class TypeScriptAnalyzer:
    """Analyzes TypeScript/TSX files"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.nodes: Dict[str, CodeNode] = {}
        self.edges: List[CodeEdge] = []
        
    def analyze(self, content: str) -> None:
        """Analyze TypeScript/TSX content"""
        # Extract imports
        imports = self._extract_imports(content)
        
        # Extract exports (interfaces, types, classes, etc.)
        exports = self._extract_exports(content)
        
        # Extract JSDoc comments
        docs = self._extract_docs(content)
        
        # Create nodes for each export
        for export_name, export_type in exports.items():
            node = CodeNode(
                name=export_name,
                type=export_type,
                file=self.file_path,
                line_number=1,  # Actual line numbers would require more parsing
                docstring=docs.get(export_name, ""),
                interface_type=self._get_interface_type(export_type),
                domain_group=get_domain_group(self.file_path)
            )
            self.nodes[export_name] = node
            
        # Create edges for imports
        for imp in imports:
            edge = CodeEdge(
                source=Path(self.file_path).stem,
                target=imp,
                type="imports"
            )
            self.edges.append(edge)
            
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        imports = []
        import_pattern = r'import\s+(?:{[^}]*}|\*\s+as\s+\w+|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        
        for match in re.finditer(import_pattern, content):
            imports.append(match.group(1))
            
        return imports
        
    def _extract_exports(self, content: str) -> Dict[str, str]:
        """Extract exported declarations"""
        exports = {}
        patterns = [
            (r'export\s+interface\s+(\w+)', 'interface'),
            (r'export\s+type\s+(\w+)', 'type'),
            (r'export\s+class\s+(\w+)', 'class'),
            (r'export\s+const\s+(\w+)', 'const'),
            (r'export\s+function\s+(\w+)', 'function'),
            (r'export\s+enum\s+(\w+)', 'enum')
        ]
        
        for pattern, type_ in patterns:
            for match in re.finditer(pattern, content):
                exports[match.group(1)] = type_
                
        return exports
        
    def _extract_docs(self, content: str) -> Dict[str, str]:
        """Extract JSDoc comments"""
        docs = {}
        doc_pattern = r'/\*\*[\s\S]*?\*/\s*export\s+(?:interface|type|class|const|function|enum)\s+(\w+)'
        
        for match in re.finditer(doc_pattern, content):
            doc = match.group(0)
            name = match.group(1)
            # Clean up doc comment
            doc = re.sub(r'/\*\*|\*/|^\s*\*', '', doc, flags=re.MULTILINE)
            docs[name] = doc.strip()
            
        return docs
        
    def _get_interface_type(self, export_type: str) -> Optional[InterfaceType]:
        """Map export type to interface type"""
        type_map = {
            'interface': InterfaceType.DATA_MODEL,
            'type': InterfaceType.DATA_MODEL,
            'class': InterfaceType.SERVICE_INTERFACE,
            'function': InterfaceType.API_CONTRACT
        }
        return type_map.get(export_type)

def build_knowledge_graph(root_dir: Path = PROJECT_ROOT) -> nx.DiGraph:
    """Build knowledge graph from codebase
    
    Args:
        root_dir: Root directory to start graph generation from
        
    Returns:
        nx.DiGraph: Generated knowledge graph
    """
    graph = nx.DiGraph()
    
    # Initialize analyzers
    interface_analyzer = InterfaceAnalyzer(str(root_dir))
    semantic_analyzer = SemanticAnalyzer()
    health_analyzer = CodeHealthAnalyzer()
    
    # Get high priority paths to process
    priority_paths = get_high_priority_paths()
    
    # Process high priority paths first
    for path in priority_paths:
        if path.exists():
            process_path(path, graph, interface_analyzer)
    
    # Process remaining paths that aren't excluded
    for path in root_dir.rglob("*"):
        if should_process_path(path, priority_paths):
            process_path(path, graph, interface_analyzer)
    
    # Add semantic relationships
    semantic_edges = semantic_analyzer.analyze_semantic_relationships(graph)
    for edge in semantic_edges:
        graph.add_edge(
            edge.source,
            edge.target,
            edge_type=edge.type,
            weight=edge.weight,
            properties=edge.properties
        )
    
    # Analyze code health
    health_issues = health_analyzer.analyze_health(graph)
    
    # Add health metadata to graph
    graph.graph['health_issues'] = health_issues
            
    return graph

def should_process_path(path: Path, priority_paths: List[Path] = None) -> bool:
    """
    Determine if a path should be processed
    
    Args:
        path: Path to check
        priority_paths: List of high priority paths
        
    Returns:
        bool: True if path should be processed
    """
    # Skip if already processed as priority
    if priority_paths and path in priority_paths:
        return False
        
    # Skip directories
    if not path.is_file():
        return False
        
    # Get relative path for pattern matching
    try:
        rel_path = str(path.relative_to(PROJECT_ROOT)).replace('\\', '/')
    except ValueError:
        return False
        
    # Skip excluded patterns
    for pattern in EXCLUDED_PATTERNS:
        if re.match(pattern, rel_path):
            return False
            
    # Only process files in included directories
    for included in INCLUDED_DIRS:
        included = included.replace('\\', '/')
        if included in rel_path:
            # Only process Python and TypeScript operational files
            if path.suffix in ['.py', '.ts', '.tsx'] and not path.name.startswith('__'):
                return True
                
    return False

def process_path(path: Path, graph: nx.DiGraph, analyzer: InterfaceAnalyzer) -> None:
    """Process a path and add nodes/edges to graph"""
    if path.is_file():
        process_file(graph, path)

def process_file(graph: nx.DiGraph, file_path: Path) -> None:
    """Process a single file and add its nodes and edges to the graph"""
    try:
        file_path_str = str(file_path)
        
        # Process Python files
        if file_path_str.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST and extract interfaces
            tree = ast.parse(content)
            analyzer = InterfaceAnalyzer(str(file_path))
            analyzer.visit(tree)
            
            # Add nodes and edges
            for node in analyzer.interfaces.values():
                graph.add_node(node.name, **node.__dict__)
            for node in analyzer.implementations.values():
                graph.add_node(node.name, **node.__dict__)
            for edge in analyzer.edges:
                graph.add_edge(edge.source, edge.target, **edge.__dict__)
                
        # Process TypeScript/TSX files
        elif file_path_str.endswith(('.ts', '.tsx')):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Use TypeScript analyzer
            ts_analyzer = TypeScriptAnalyzer(str(file_path))
            ts_analyzer.analyze(content)
            
            # Add nodes and edges
            for node in ts_analyzer.nodes.values():
                graph.add_node(node.name, **node.__dict__)
            for edge in ts_analyzer.edges:
                graph.add_edge(edge.source, edge.target, **edge.__dict__)
                
    except Exception as e:
        logger.error(f"Error processing {file_path}: {str(e)}")
        raise

def main():
    """Main entry point for knowledge graph generation"""
    logger.info("Starting knowledge graph generation...")
    
    # Initialize graph
    G = nx.DiGraph()
    
    # Define paths to analyze
    app_paths = [
        os.path.join(PROJECT_ROOT, "warehouse_quote_app"),
        os.path.join(PROJECT_ROOT, "tools"),
        os.path.join(PROJECT_ROOT, "tests")
    ]
    
    # Process each path
    for path in app_paths:
        if not os.path.exists(path):
            logger.warning(f"Path does not exist: {path}")
            continue
            
        logger.info(f"Processing path: {path}")
        for root, dirs, files in os.walk(path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(re.match(pattern, d) for pattern in EXCLUDED_PATTERNS)]
            
            # Process Python files
            for file in files:
                if file.endswith(('.py', '.ts', '.js')):
                    file_path = os.path.join(root, file)
                    if any(re.match(pattern, file_path) for pattern in EXCLUDED_PATTERNS):
                        continue
                        
                    try:
                        process_file(G, file_path)
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {str(e)}")
                        continue
    
    # Save graph
    logger.info(f"Generated graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    # Save as GraphML
    graphml_path = os.path.join(PROJECT_ROOT, "code_knowledge_graph.graphml")
    nx.write_graphml(G, graphml_path)
    logger.info(f"Saved GraphML to {graphml_path}")
    
    # Save as JSON for easier debugging
    json_path = os.path.join(PROJECT_ROOT, "code_knowledge_graph.json")
    json_graph = nx.node_link_data(G)
    with open(json_path, 'w') as f:
        json.dump(json_graph, f, indent=2)
    logger.info(f"Saved JSON to {json_path}")
    
    # Generate visualization
    try:
        plt.figure(figsize=(20, 20))
        pos = nx.spring_layout(G)
        nx.draw(G, pos, with_labels=True, node_color='lightblue', 
               node_size=1500, font_size=8, font_weight='bold')
        plt.savefig(os.path.join(PROJECT_ROOT, 'code_knowledge_graph.png'))
        plt.close()
        logger.info("Saved visualization to code_knowledge_graph.png")
    except Exception as e:
        logger.warning(f"Could not save graph visualization: {str(e)}")

if __name__ == "__main__":
    main()
