"""
Semantic Context Manager for code analysis and understanding
"""

import ast
import json
import logging
import os
import re
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed

import networkx as nx
import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from .analysis.code_analysis import (
    calculate_duplication_rate,
    calculate_orphan_rate,
    calculate_divergence_rate,
    calculate_health_score
)
from .config.health_config import get_code_health_rules
from .config.kg_config import InterfaceType
from .config.health_config import get_cache_paths

@dataclass
class SemanticContext:
    """Holds semantic information about a code component."""
    embedding: Optional[np.ndarray] = None
    summary: Optional[str] = None
    docstring: Optional[str] = None
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)

@dataclass
class CodeComponent:
    """Represents a code component with its semantic context."""
    path: str
    content: str
    name: str
    semantic_context: Optional[SemanticContext] = None
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    interface: Optional[Any] = None
    implementation: Optional[Any] = None

class SemanticContextManager:
    """Manages semantic context for code analysis"""
    
    def __init__(self, root_path: str):
        """Initialize the semantic context manager."""
        self.root_path = Path(root_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.components: Dict[str, CodeComponent] = {}
        self.rules = get_code_health_rules()
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Initialize model with proper error handling
        try:
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model.to(device)
        except Exception as e:
            self.logger.error(f"Failed to initialize model: {str(e)}")
            raise
            
        self.batch_size = 32
        self.exclude_patterns = [
            r'.*\.git.*',
            r'.*\.venv.*',
            r'.*__pycache__.*',
            r'.*\.pytest_cache.*',
            r'.*\.mypy_cache.*',
            r'.*\.vscode.*',
            r'.*\.idea.*',
            r'.*\.DS_Store.*',
            r'.*\.env.*',
            r'.*node_modules.*'
        ]
        
        # Initialize cache with versioning
        self.cache_version = "1.0"
        self.embedding_cache = self._load_embedding_cache()
        self.embedding_cache_file = get_cache_paths()['embeddings']
        
        # Initialize thread pool for parallel processing
        self.max_workers = min(32, (os.cpu_count() or 1) + 4)
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Track progress
        self.progress_callback = None
        
    def __del__(self):
        """Cleanup resources when the object is deleted."""
        try:
            self.cleanup()
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f"Error during cleanup in __del__: {str(e)}")

    def cleanup(self):
        """Cleanup resources."""
        try:
            if hasattr(self, 'executor'):
                self.executor.shutdown(wait=True)
            if hasattr(self, 'embedding_cache'):
                self._save_embedding_cache(self.embedding_cache)
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def set_progress_callback(self, callback: callable):
        """Set callback for progress updates."""
        self.progress_callback = callback
    
    def _update_progress(self, current: int, total: int, message: str):
        """Update progress through callback if set."""
        if self.progress_callback:
            self.progress_callback(current, total, message)
    
    def load_context(self) -> None:
        """Load semantic context from files."""
        self.logger.info("Loading semantic context...")
        
        # Define supported file extensions
        supported_extensions = {'.py', '.ts', '.tsx', '.jsx', '.js'}
        
        # Use the same included directories as the knowledge graph
        included_dirs = [
            'frontend/src/components',  # React/TypeScript UI components
            'frontend/src/api',         # API client code
            'frontend/src/services',    # Frontend services
            'warehouse_quote_app/app',  # Backend core app
            'warehouse_quote_app/app/services',  # Backend services
            'warehouse_quote_app/app/models'     # Backend data models
        ]
        
        # Find all supported files
        code_files = []
        for root, _, files in os.walk(self.root_path):
            # Skip excluded directories
            if any(re.match(pattern, root) for pattern in self.exclude_patterns):
                continue
                
            # Check if this directory is included
            rel_path = os.path.relpath(root, self.root_path).replace('\\', '/')
            if not any(rel_path.startswith(included) for included in included_dirs):
                continue
                
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext not in supported_extensions:
                    continue
                    
                file_path = os.path.join(root, file)
                if any(re.match(pattern, file_path) for pattern in self.exclude_patterns):
                    continue
                    
                code_files.append(file_path)
        
        total_files = len(code_files)
        self._update_progress(0, total_files, "Finding code files")
        self.logger.info(f"Found {total_files} code files to analyze")
        
        # Load files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as file_executor:
            futures = []
            for file_path in code_files:
                future = file_executor.submit(self._load_file, file_path)
                futures.append((file_path, future))
            
            # Process results as they complete
            for i, (file_path, future) in enumerate(futures):
                try:
                    component = future.result()
                    if component:
                        rel_path = os.path.relpath(file_path, self.root_path)
                        self.components[rel_path] = component
                except Exception as e:
                    self.logger.error(f"Error loading file {file_path}: {str(e)}")
                self._update_progress(i + 1, total_files, f"Loading file {i + 1}/{total_files}")
        
        # Process components in parallel
        self._update_progress(0, len(self.components), "Computing embeddings")
        self.process_components(list(self.components.values()))
        
        self.logger.info(f"Loaded {len(self.components)} components")
        self._update_progress(len(self.components), len(self.components), "Finished loading context")
    
    def _load_file(self, file_path: str) -> Optional[CodeComponent]:
        """Load a single file with validation."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validate content
            if not content.strip():
                self.logger.warning(f"Empty file: {file_path}")
                return None
                
            # Basic syntax check
            try:
                ast.parse(content)
            except SyntaxError as e:
                self.logger.error(f"Syntax error in {file_path}: {str(e)}")
                return None
            
            component = CodeComponent(
                path=file_path,
                content=content,
                name=os.path.splitext(os.path.basename(file_path))[0]
            )
            
            # Initialize semantic context
            component.semantic_context = SemanticContext()
            
            return component
            
        except Exception as e:
            self.logger.error(f"Error loading file {file_path}: {str(e)}")
            return None
    
    def _load_embedding_cache(self) -> Dict[str, torch.Tensor]:
        """Load embeddings from cache file."""
        import builtins  # Explicitly import builtins to ensure 'open' is available
        
        try:
            cache_path = get_cache_paths()['embeddings']
            if cache_path.exists():
                with builtins.open(str(cache_path), 'rb') as f:
                    cache = torch.load(f)
                self.logger.info(f"Loaded {len(cache)} embeddings from cache")
                return cache
            return {}
        except Exception as e:
            self.logger.error(f"Failed to load embedding cache: {str(e)}")
            return {}

    def _save_embedding_cache(self, embeddings: Dict[str, torch.Tensor]) -> None:
        """Save embeddings to cache file."""
        import builtins  # Explicitly import builtins to ensure 'open' is available
        
        try:
            cache_path = get_cache_paths()['embeddings']
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with builtins.open(str(cache_path), 'wb') as f:
                torch.save(embeddings, f)
                
            self.logger.info(f"Saved {len(embeddings)} embeddings to cache")
        except Exception as e:
            self.logger.error(f"Failed to save embedding cache: {str(e)}")

    def compute_embeddings_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Compute embeddings for a batch of texts with error handling."""
        if not texts:
            return []
            
        try:
            # Encode all texts in a single batch
            with torch.no_grad():
                embeddings = self.model.encode(
                    texts,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to compute embeddings batch: {str(e)}")
            return [None] * len(texts)

    def process_components(self, components: List[CodeComponent]) -> None:
        """Process components in parallel with improved error handling."""
        if not components:
            return
            
        try:
            # Group components by batch size
            batches = [
                components[i:i + self.batch_size]
                for i in range(0, len(components), self.batch_size)
            ]
            
            # Process batches in parallel
            futures = []
            for batch in batches:
                future = self.executor.submit(self._process_component_batch, batch)
                futures.append(future)
            
            # Wait for all batches to complete
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    self.logger.error(f"Batch processing failed: {str(e)}")
                    
        except Exception as e:
            self.logger.error(f"Failed to process components: {str(e)}")
            raise

    def _process_component_batch(self, components: List[CodeComponent]) -> None:
        """Process a batch of components."""
        try:
            # Extract texts for embedding
            texts = []
            for comp in components:
                text = self._prepare_text_for_embedding(comp)
                texts.append(text)
            
            # Compute embeddings
            embeddings = self.compute_embeddings_batch(texts)
            
            # Update components with embeddings
            for comp, embedding in zip(components, embeddings):
                if embedding is not None:
                    if not comp.semantic_context:
                        comp.semantic_context = SemanticContext()
                    comp.semantic_context.embedding = embedding
                    
                    # Update cache
                    cache_key = self._get_cache_key(comp)
                    self.embedding_cache[cache_key] = torch.tensor(embedding)
                    
        except Exception as e:
            self.logger.error(f"Failed to process component batch: {str(e)}")
            raise

    def _prepare_text_for_embedding(self, component: CodeComponent) -> str:
        """Prepare component text for embedding computation."""
        text_parts = []
        
        # Add component name
        if component.name:
            text_parts.append(component.name)
        
        # Add docstring if available
        if (component.semantic_context and 
            component.semantic_context.docstring):
            text_parts.append(component.semantic_context.docstring)
        
        # Add content with basic cleaning
        if component.content:
            # Remove comments
            content = re.sub(r'#.*$', '', component.content, flags=re.MULTILINE)
            # Remove empty lines
            content = '\n'.join(
                line for line in content.split('\n')
                if line.strip()
            )
            text_parts.append(content)
        
        return ' '.join(text_parts)

    def _get_cache_key(self, component: CodeComponent) -> str:
        """Generate a unique cache key for a component."""
        content_hash = hash(component.content)
        return f"{component.path}:{content_hash}"

    def analyze_codebase_health(self, root_dir: str = ".") -> Dict[str, Any]:
        """Analyze the health of the codebase."""
        if not self.components:
            return {
                "health_score": 100.0,
                "metrics": {
                    "duplication_rate": 0.0,
                    "orphan_rate": 0.0,
                    "divergence_rate": 0.0
                },
                "issues": []
            }
        
        # Create analysis context
        embeddings = torch.tensor([comp.semantic_context.embedding for comp in self.components.values()], dtype=torch.float32)
        context = AnalysisContext(
            embeddings=embeddings,
            components=list(self.components.values()),
            rules=self.rules
        )
        
        # Calculate metrics
        metrics = [
            calculate_duplication_rate(context),
            calculate_orphan_rate(context),
            calculate_divergence_rate(context)
        ]
        
        # Log metrics
        for metric in metrics:
            self.logger.info(f"{metric.name}: {metric.value:.2f}% (threshold: {metric.threshold:.2f}%)")
        
        # Identify specific issues
        issues = self._identify_issues()
        self.logger.info(f"Found {len(issues)} potential issues")
        
        # Calculate overall health score
        health_score = calculate_health_score(metrics)
        
        return {
            "health_score": health_score,
            "metrics": {metric.name: metric.value for metric in metrics},
            "issues": issues
        }

    def _identify_issues(self) -> List[Dict[str, Any]]:
        """Identify specific issues in the codebase with optimized tensor operations."""
        issues = []
        
        # Convert all embeddings to tensors once
        embeddings = []
        valid_components = []
        for comp in self.components.values():
            if comp.semantic_context and isinstance(comp.semantic_context.embedding, (np.ndarray, list)):
                embeddings.append(comp.semantic_context.embedding)
                valid_components.append(comp)
        
        if not valid_components:
            return []
            
        # Convert to tensor
        embeddings_tensor = torch.tensor(embeddings, dtype=torch.float32)
        
        # Normalize embeddings
        embeddings_tensor = torch.nn.functional.normalize(embeddings_tensor, p=2, dim=1)
        
        # Compute all pairwise similarities at once
        similarities = torch.mm(embeddings_tensor, embeddings_tensor.t())
        
        # Find duplicates
        duplicate_mask = (similarities > 0.85).triu(diagonal=1)
        for i, comp1 in enumerate(valid_components):
            duplicates = []
            duplicate_indices = duplicate_mask[i].nonzero().squeeze(1)
            for j in duplicate_indices:
                duplicates.append(valid_components[j].path)
            
            if duplicates:
                issues.append({
                    "type": "duplication",
                    "component": comp1.path,
                    "related_components": duplicates,
                    "impact": len(duplicates) / len(valid_components)
                })
        
        # Find orphans (components with low max similarity to others)
        max_similarities, _ = similarities.max(dim=1)
        orphan_mask = max_similarities < self.rules['orphan']['threshold']
        for i, is_orphan in enumerate(orphan_mask):
            if is_orphan:
                issues.append({
                    "type": "orphaned",
                    "component": valid_components[i].path,
                    "impact": 1 - float(max_similarities[i])
                })
        
        # Find divergent components (low average similarity)
        avg_similarities = similarities.mean(dim=1)
        divergent_mask = avg_similarities < self.rules['divergence']['threshold']
        for i, is_divergent in enumerate(divergent_mask):
            if is_divergent:
                issues.append({
                    "type": "divergent",
                    "component": valid_components[i].path,
                    "impact": 1 - float(avg_similarities[i])
                })
        
        return issues

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on identified issues"""
        recommendations = []
        
        # Count issue types
        issue_counts = {
            "duplication": 0,
            "orphaned": 0,
            "divergent": 0
        }
        
        for issue in self._identify_issues():
            issue_counts[issue["type"]] += 1
        
        # Generate specific recommendations
        if issue_counts["duplication"] > 0:
            recommendations.append(
                f"Found {issue_counts['duplication']} instances of potential code duplication. "
                "Consider refactoring into shared utilities or base classes."
            )
            
        if issue_counts["orphaned"] > 0:
            recommendations.append(
                f"Found {issue_counts['orphaned']} potentially orphaned components. "
                "Review these components for proper integration or removal."
            )
            
        if issue_counts["divergent"] > 0:
            recommendations.append(
                f"Found {issue_counts['divergent']} components that diverge significantly "
                "from the codebase patterns. Consider standardizing their implementation."
            )
            
        # Add general recommendations if needed
        if sum(issue_counts.values()) > 5:
            recommendations.append(
                "Consider implementing a systematic code review process to maintain "
                "consistency and reduce technical debt."
            )
            
        return recommendations

    def _setup_logging(self) -> None:
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def update_file_context(self, file_path: str) -> None:
        """Update semantic context for a single file."""
        try:
            if not os.path.exists(file_path):
                self.logger.warning(f"File not found: {file_path}")
                return
                
            # Remove old context if it exists
            rel_path = os.path.relpath(file_path, self.root_path)
            if rel_path in self.components:
                del self.components[rel_path]
                
            # Load and process the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            component = CodeComponent(
                path=rel_path,
                content=content,
                name=os.path.basename(file_path)
            )
            
            # Generate embedding
            try:
                embedding = self.model.encode([content], show_progress_bar=False)[0]
                component.semantic_context = SemanticContext(embedding=embedding)
            except Exception as e:
                self.logger.error(f"Failed to generate embedding for {file_path}: {str(e)}")
                
            # Store the component
            self.components[rel_path] = component
            self.logger.info(f"Updated context for {rel_path}")
            
        except Exception as e:
            self.logger.error(f"Error updating context for {file_path}: {str(e)}")
