"""Context service for warehouse quotes using a simple Model Context Protocol.

This implementation replaces the previous FAISS based Retrieval Augmented
Generation (RAG) layer.  The knowledge base is small enough to fit in memory, so
documents are loaded and searched with lightweight keyword matching.  Relevant
snippets are then injected directly into the LLM prompt.
"""

from typing import List, Dict, Optional
import json
from pathlib import Path
from datetime import datetime
import re

class RAGService:
    """Load knowledge snippets and return relevant context."""

    def __init__(self, knowledge_base_path: Optional[str] = None) -> None:
        self.knowledge_base_path = (
            Path(knowledge_base_path) if knowledge_base_path else Path(__file__).parent / "knowledge"
        )
        self.rag_doc_path = Path(__file__).parent.parent.parent.parent / "rag_document.txt"
        self.load_knowledge_base()
        
    def load_knowledge_base(self):
        """Load the knowledge base documents."""
        # Load JSON documents
        with open(self.knowledge_base_path / "warehouse_knowledge.json", "r") as f:
            self.documents = json.load(f)
            
        # Load and parse RAG document
        with open(self.rag_doc_path, "r") as f:
            rag_content = f.read()
            
        # Parse sections from RAG document
        sections = self._parse_rag_document(rag_content)
        
        # Combine both sources
        for section in sections:
            self.documents["documents"].append({
                "id": f"rag_{section['title'].lower().replace(' ', '_')}",
                "category": section["category"],
                "content": section["content"],
                "updated_at": datetime.utcnow().isoformat()
            })
            
        # Precompute lowercase tokens for simple matching
        for doc in self.documents["documents"]:
            doc["_tokens"] = self._tokenize(doc["content"])
        
    def _parse_rag_document(self, content: str) -> List[Dict]:
        """Parse RAG document into sections"""
        sections = []
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            # Main section (h1)
            if line.startswith('# '):
                if current_section:
                    sections.append({
                        "title": current_section,
                        "category": current_section.lower().replace(' ', '_'),
                        "content": '\n'.join(current_content)
                    })
                current_section = line[2:].strip()
                current_content = []
            # Subsection (h2)
            elif line.startswith('## '):
                if current_content:
                    sections.append({
                        "title": current_section + " - " + line[3:].strip(),
                        "category": current_section.lower().replace(' ', '_'),
                        "content": '\n'.join(current_content)
                    })
                current_content = []
            else:
                current_content.append(line)
                
        # Add last section
        if current_section and current_content:
            sections.append({
                "title": current_section,
                "category": current_section.lower().replace(' ', '_'),
                "content": '\n'.join(current_content)
            })
            
        return sections

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer that lowercases and splits on non-word characters."""
        return re.findall(r"\w+", text.lower())
            
    def get_relevant_context(self, query: str, k: int = 3) -> List[Dict]:
        """Retrieve relevant documents for a query using keyword matching."""
        tokens = self._tokenize(query)

        scored: List[Dict] = []
        for doc in self.documents["documents"]:
            score = sum(1 for t in tokens if t in doc.get("_tokens", []))
            if score:
                scored.append({**doc, "relevance_score": float(score)})

        scored.sort(key=lambda d: d["relevance_score"], reverse=True)
        return scored[:k]
        
    def get_rate_card_context(self, service_type: str, include_edge_cases: bool = True) -> List[Dict]:
        """Get relevant rate card information"""
        queries = [
            f"rate calculation {service_type}",
            f"pricing {service_type}",
            "rate card validation"
        ]
        
        if include_edge_cases:
            queries.append("edge cases handling")
            
        all_results = []
        for query in queries:
            results = self.get_relevant_context(query, k=2)
            all_results.extend(results)
            
        # Remove duplicates and sort by relevance
        seen = set()
        unique_results = []
        for doc in all_results:
            if doc["id"] not in seen:
                seen.add(doc["id"])
                unique_results.append(doc)
                
        return sorted(unique_results, key=lambda x: x["relevance_score"], reverse=True)[:4]
        
    def get_customer_service_guidelines(self, specific_topic: Optional[str] = None) -> List[Dict]:
        """Get customer service guidelines"""
        query = "customer service guidelines"
        if specific_topic:
            query += f" {specific_topic}"
            
        return self.get_relevant_context(query, k=2)
        
    def format_context_for_llm(self, documents: List[Dict], max_length: int = 2048) -> str:
        """Format retrieved documents for LLM prompt"""
        formatted = []
        current_length = 0
        
        for doc in sorted(documents, key=lambda x: x.get("relevance_score", 0), reverse=True):
            content = f"Category: {doc['category']}\n{doc['content']}"
            content_length = len(content)
            
            if current_length + content_length > max_length:
                # Truncate content to fit
                available_length = max_length - current_length
                if available_length > 100:  # Only add if we can include meaningful content
                    content = content[:available_length] + "..."
                    formatted.append(content)
                break
                
            formatted.append(content)
            current_length += content_length
            
        return "\n\n".join(formatted)
