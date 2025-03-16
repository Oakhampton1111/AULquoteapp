"""
TypeScript Code Analyzer
Parses TypeScript files and extracts code structure for knowledge graph generation
"""

import ast_parser
from typing import Dict, List, Any, Optional
import json
import subprocess
import tempfile
import os
from pathlib import Path
import logging
import networkx as nx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TypeScriptAnalyzer:
    def __init__(self):
        """Initialize the TypeScript analyzer"""
        self.ensure_typescript_tools()
        
    def ensure_typescript_tools(self):
        """Ensure TypeScript compiler and parser are installed"""
        try:
            # Check if TypeScript is installed
            subprocess.run(["tsc", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.info("Installing TypeScript...")
            subprocess.run(["npm", "install", "-g", "typescript"], check=True)
            
        # Install required npm packages if not present
        packages = ["@typescript-eslint/parser", "@typescript-eslint/typescript-estree"]
        for package in packages:
            try:
                subprocess.run(
                    ["npm", "list", "-g", package],
                    capture_output=True,
                    check=True
                )
            except subprocess.CalledProcessError:
                logger.info(f"Installing {package}...")
                subprocess.run(["npm", "install", "-g", package], check=True)
                
    def parse_typescript(self, file_path: str) -> Dict[str, Any]:
        """Parse TypeScript file and return AST"""
        # Create a temporary JavaScript file for parsing
        with tempfile.NamedTemporaryFile(suffix='.js', delete=False) as temp_js:
            # Compile TypeScript to JavaScript
            subprocess.run(
                ["tsc", "--target", "ES2020", "--module", "commonjs", file_path],
                check=True
            )
            
            # Get the compiled JS file path
            js_path = str(Path(file_path).with_suffix('.js'))
            
            # Parse the JavaScript file
            with open(js_path, 'r') as f:
                js_content = f.read()
                
            # Clean up the compiled JS file
            os.unlink(js_path)
            
            # Parse JavaScript AST
            cmd = [
                "npx",
                "@typescript-eslint/parser",
                "--ecma-version",
                "2020",
                "--source-type",
                "module",
                js_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
            
    def extract_nodes_and_edges(self, ast: Dict[str, Any], file_path: str) -> nx.DiGraph:
        """Extract nodes and edges from TypeScript AST"""
        graph = nx.DiGraph()
        
        def process_node(node: Dict[str, Any], parent: Optional[str] = None):
            """Process an AST node and extract relevant information"""
            node_type = node.get("type")
            
            if node_type == "ClassDeclaration":
                name = node["id"]["name"]
                node_id = f"{file_path}:{name}"
                graph.add_node(
                    node_id,
                    node_type="class",
                    name=name,
                    file_path=file_path,
                    language="typescript"
                )
                
                # Process class methods
                for member in node.get("body", {}).get("body", []):
                    if member["type"] == "MethodDefinition":
                        method_name = member["key"]["name"]
                        method_id = f"{node_id}.{method_name}"
                        graph.add_node(
                            method_id,
                            node_type="method",
                            name=method_name,
                            file_path=file_path,
                            language="typescript"
                        )
                        graph.add_edge(node_id, method_id, edge_type="DEFINES")
                        
            elif node_type == "FunctionDeclaration":
                name = node["id"]["name"]
                node_id = f"{file_path}:{name}"
                graph.add_node(
                    node_id,
                    node_type="function",
                    name=name,
                    file_path=file_path,
                    language="typescript"
                )
                
            elif node_type == "CallExpression":
                if "callee" in node:
                    callee = node["callee"]
                    if callee["type"] == "Identifier":
                        called_name = callee["name"]
                        if parent:
                            graph.add_edge(parent, f"{file_path}:{called_name}", edge_type="CALLS")
                            
            # Process imports
            elif node_type == "ImportDeclaration":
                source = node["source"]["value"]
                for specifier in node.get("specifiers", []):
                    if specifier["type"] == "ImportSpecifier":
                        imported_name = specifier["imported"]["name"]
                        local_name = specifier["local"]["name"]
                        graph.add_node(
                            f"{file_path}:{local_name}",
                            node_type="import",
                            name=local_name,
                            imported_name=imported_name,
                            source=source,
                            file_path=file_path,
                            language="typescript"
                        )
                        
            # Recursively process child nodes
            for key, value in node.items():
                if isinstance(value, dict):
                    process_node(value, parent)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            process_node(item, parent)
                            
        process_node(ast)
        return graph
        
    def analyze_file(self, file_path: str) -> nx.DiGraph:
        """Analyze a TypeScript file and return a knowledge graph"""
        try:
            ast = self.parse_typescript(file_path)
            return self.extract_nodes_and_edges(ast, file_path)
        except Exception as e:
            logger.error(f"Error analyzing TypeScript file {file_path}: {e}")
            return nx.DiGraph()
            
def main():
    """Test the TypeScript analyzer"""
    analyzer = TypeScriptAnalyzer()
    
    # Test with a sample TypeScript file
    test_ts = """
    import { Component } from '@angular/core';
    
    class TestClass {
        constructor() {}
        
        testMethod() {
            console.log('test');
        }
    }
    
    function testFunction() {
        const test = new TestClass();
        test.testMethod();
    }
    """
    
    with tempfile.NamedTemporaryFile(suffix='.ts', mode='w', delete=False) as f:
        f.write(test_ts)
        test_file = f.name
        
    try:
        graph = analyzer.analyze_file(test_file)
        print(f"Nodes: {list(graph.nodes(data=True))}")
        print(f"Edges: {list(graph.edges(data=True))}")
    finally:
        os.unlink(test_file)

if __name__ == "__main__":
    main()
