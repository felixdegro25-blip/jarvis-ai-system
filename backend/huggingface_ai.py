"""
Hugging Face AI Integration für JARVIS
Kostenlose KI direkt im Code
"""

import requests
import os
from typing import Optional
from datetime import datetime

class HuggingFaceAI:
    """Hugging Face Inference API Integration"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Hugging Face AI
        
        Get free API key from: https://huggingface.co/settings/tokens
        """
        self.api_key = api_key or os.getenv('HF_API_KEY')
        if not self.api_key:
            raise ValueError("❌ HF_API_KEY not set! Get it from https://huggingface.co/settings/tokens")
        
        self.base_url = "https://api-inference.huggingface.co/models"
        self.model = "mistralai/Mistral-7B-Instruct-v0.1"  # Kostenlos & schnell
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        
        print(f"🤖 Hugging Face AI initialized")
        print(f"   Model: {self.model}")
        print(f"   API Key: {self.api_key[:20]}...")
    
    async def generate_response(self, prompt: str, max_tokens: int = 200) -> dict:
        """
        Generate AI response from Hugging Face
        
        Args:
            prompt: User message
            max_tokens: Max response length
        
        Returns:
            dict with response, confidence, etc.
        """
        try:
            url = f"{self.base_url}/{self.model}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": 0.7,
                    "top_p": 0.95,
                }
            }
            
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if isinstance(result, list):
                generated_text = result[0].get('generated_text', '')
            else:
                generated_text = result.get('generated_text', '')
            
            # Entferne Prompt aus Response
            ai_response = generated_text.replace(prompt, '').strip()
            
            return {
                "status": "success",
                "response": ai_response,
                "confidence": 92.5,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }
        
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "response": "⏱️ Request timeout - model might be loading. Try again!",
                "confidence": 0,
                "error": "timeout"
            }
        except Exception as e:
            return {
                "status": "error",
                "response": f"❌ Error: {str(e)}",
                "confidence": 0,
                "error": str(e)
            }
    
    async def chat_with_context(self, user_message: str, context: list = None) -> dict:
        """
        Chat with context from previous messages
        
        Args:
            user_message: Current user message
            context: List of previous messages [{'role': 'user/ai', 'content': '...'}]
        
        Returns:
            AI response
        """
        # Build prompt with context
        prompt_parts = []
        
        if context:
            for msg in context[-5:]:  # Last 5 messages for context
                role = "User" if msg['role'] == 'user' else "JARVIS"
                prompt_parts.append(f"{role}: {msg['content']}")
        
        prompt_parts.append(f"User: {user_message}")
        prompt_parts.append("JARVIS:")
        
        full_prompt = "\n".join(prompt_parts)
        
        return await self.generate_response(full_prompt)
    
    async def extract_intent(self, message: str) -> dict:
        """
        Extract intent from user message (for PC control, tasks, etc.)
        
        Returns:
            intent, entities, confidence
        """
        prompt = f"""Analyze this command and extract the intent:
        
Command: {message}

Respond in JSON format:
{{
  "intent": "chat|shutdown|restart|open_app|create_task|set_reminder|set_alarm",
  "entities": {{}},
  "confidence": 0.0
}}

Only respond with valid JSON, no other text."""
        
        try:
            result = await self.generate_response(prompt)
            
            # Parse JSON from response
            import json
            response_text = result['response']
            
            # Extract JSON
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                intent_data = json.loads(json_str)
                return intent_data
        
        except Exception as e:
            print(f"❌ Intent extraction error: {e}")
        
        return {
            "intent": "chat",
            "entities": {},
            "confidence": 0.5
        }

# ============ SINGLETON INSTANCE ============
_ai_instance = None

def get_ai() -> HuggingFaceAI:
    """Get or create AI instance"""
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = HuggingFaceAI()
    return _ai_instance
