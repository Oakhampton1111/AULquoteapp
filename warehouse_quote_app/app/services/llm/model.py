"""
FLAN-T5 model service for warehouse quote processing.
"""

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from typing import Dict, List, Optional, Union
import json
from pathlib import Path

class WarehouseLLM:
    def __init__(self, model_name: str = "google/flan-t5-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load rate card templates and prompts
        self.templates_path = Path(__file__).parent / "templates"
        self.load_templates()
        
    def load_templates(self):
        """Load prompt templates and examples"""
        with open(self.templates_path / "prompts.json", "r") as f:
            self.templates = json.load(f)
            
    def generate_response(
        self,
        input_text: str,
        max_length: int = 512,
        template_key: str = "general",
        context: Optional[Dict] = None
    ) -> str:
        """Generate response using FLAN-T5"""
        # Get template and format with context
        template = self.templates[template_key]
        if context:
            template = template.format(**context)
            
        # Combine template and input
        prompt = f"{template}\nUser: {input_text}\nAssistant:"
        
        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            early_stopping=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response.strip()
    
    def extract_rate_info(self, conversation_history: List[Dict]) -> Dict:
        """Extract rate-relevant information from conversation"""
        # Format conversation history
        formatted_history = "\n".join([
            f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
            for msg in conversation_history
        ])
        
        # Use specific template for rate extraction
        response = self.generate_response(
            formatted_history,
            template_key="rate_extraction",
            max_length=256
        )
        
        try:
            # Response should be JSON format
            rate_info = json.loads(response)
            return rate_info
        except json.JSONDecodeError:
            return {}
            
    def validate_rate_card(self, rate_card: Dict) -> Dict[str, Union[bool, List[str]]]:
        """Validate rate card configuration"""
        rate_card_str = json.dumps(rate_card, indent=2)
        response = self.generate_response(
            rate_card_str,
            template_key="rate_validation",
            max_length=512
        )
        
        try:
            validation_result = json.loads(response)
            return validation_result
        except json.JSONDecodeError:
            return {
                "valid": False,
                "errors": ["Failed to parse validation response"]
            }
            
    def suggest_rate_improvements(self, rate_card: Dict, historical_data: List[Dict]) -> List[str]:
        """Suggest improvements for rate card based on historical data"""
        context = {
            "rate_card": json.dumps(rate_card, indent=2),
            "historical_data": json.dumps(historical_data, indent=2)
        }
        
        response = self.generate_response(
            "",
            template_key="rate_improvement",
            context=context,
            max_length=1024
        )
        
        try:
            suggestions = json.loads(response)
            return suggestions if isinstance(suggestions, list) else []
        except json.JSONDecodeError:
            return []
