"""
LLM Categorizer Module

This module uses LLMs (OpenAI GPT or Google Gemini) to categorize Google Alerts
and determine if they are relevant to the mineral-exploration-machine-learning repository.
"""

import os
from typing import List, Dict, Any, Literal
from pydantic import BaseModel
import json

# Optional imports - these will be imported dynamically based on provider
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False


class CategoryDecision(BaseModel):
    """Model for categorization decision."""
    is_relevant: bool
    confidence: float  # 0.0 to 1.0
    category: str
    reasoning: str
    summary: str
    keywords: List[str]


class LLMCategorizer:
    """Categorizes content using LLM APIs."""
    
    def __init__(
        self,
        provider: Literal["openai", "gemini"] = "openai",
        model: str = None,
        api_key: str = None
    ):
        """
        Initialize LLM Categorizer.
        
        Args:
            provider: LLM provider (openai or gemini)
            model: Model name (e.g., gpt-4o-mini, gemini-1.5-flash)
            api_key: API key for the provider
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        
        # Set default models
        if model is None:
            if provider == "openai":
                self.model = "gpt-4o-mini"
            else:
                self.model = "gemini-1.5-flash"
        else:
            self.model = model
        
        self._initialize_client()
    
    def _get_api_key(self) -> str:
        """Get API key from environment."""
        if self.provider == "openai":
            key = os.getenv('OPENAI_API_KEY')
            if not key:
                raise ValueError("OPENAI_API_KEY not found in environment")
            return key
        else:
            key = os.getenv('GEMINI_API_KEY')
            if not key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            return key
    
    def _initialize_client(self) -> None:
        """Initialize the LLM client."""
        if self.provider == "openai":
            if not HAS_OPENAI:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            if not HAS_GEMINI:
                raise ImportError(
                    "Google Generative AI package not installed. "
                    "Install with: pip install google-generativeai"
                )
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
    
    def categorize_alert(self, alert_data: Dict[str, Any]) -> CategoryDecision:
        """
        Categorize a Google Alert.
        
        Args:
            alert_data: Alert information dictionary
            
        Returns:
            CategoryDecision with relevance determination
        """
        prompt = self._build_categorization_prompt(alert_data)
        
        try:
            if self.provider == "openai":
                response = self._call_openai(prompt)
            else:
                response = self._call_gemini(prompt)
            
            return self._parse_response(response)
            
        except Exception as e:
            print(f"Error during categorization: {e}")
            return CategoryDecision(
                is_relevant=False,
                confidence=0.0,
                category="error",
                reasoning=f"Error during categorization: {str(e)}",
                summary="Could not categorize due to error",
                keywords=[]
            )
    
    def _build_categorization_prompt(self, alert_data: Dict[str, Any]) -> str:
        """Build the prompt for LLM categorization."""
        articles_text = ""
        for i, article in enumerate(alert_data.get('articles', []), 1):
            articles_text += f"\n{i}. Title: {article.get('title', 'N/A')}\n"
            articles_text += f"   URL: {article.get('url', 'N/A')}\n"
            if article.get('snippet'):
                articles_text += f"   Snippet: {article.get('snippet', '')}\n"
        
        prompt = f"""You are an expert in mineral exploration and machine learning. Your task is to analyze Google Alert articles and determine if they are relevant to a GitHub repository about machine learning applications in mineral exploration.

The repository (https://github.com/RichardScottOZ/mineral-exploration-machine-learning) focuses on:
- Machine learning techniques applied to mineral exploration
- Geoscience data analysis using ML/AI
- Remote sensing and geophysical data processing
- Predictive modeling for mineral deposits
- Geological mapping with ML
- Exploration targeting using data science
- Mining industry AI applications

Google Alert Query: {alert_data.get('alert_query', 'Unknown')}
Date: {alert_data.get('date', 'Unknown')}

Articles in this alert:
{articles_text}

Analyze these articles and provide:
1. Is this relevant to the mineral-exploration-machine-learning repository? (true/false)
2. Confidence level (0.0 to 1.0)
3. Category (e.g., "Machine Learning - Exploration", "Remote Sensing", "Geophysics", "Mining Technology", "Not Relevant")
4. Brief reasoning for your decision
5. A one-sentence summary of the alert content
6. Key keywords (2-5 words)

Respond in JSON format:
{{
    "is_relevant": boolean,
    "confidence": float,
    "category": "string",
    "reasoning": "string",
    "summary": "string",
    "keywords": ["keyword1", "keyword2", ...]
}}"""
        
        return prompt
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert in mineral exploration and machine learning. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API."""
        response = self.client.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "response_mime_type": "application/json"
            }
        )
        return response.text
    
    def _parse_response(self, response_text: str) -> CategoryDecision:
        """Parse LLM response into CategoryDecision."""
        try:
            data = json.loads(response_text)
            return CategoryDecision(**data)
        except Exception as e:
            print(f"Error parsing response: {e}")
            print(f"Response: {response_text}")
            # Return a default decision
            return CategoryDecision(
                is_relevant=False,
                confidence=0.0,
                category="parse_error",
                reasoning=f"Could not parse LLM response: {str(e)}",
                summary="Response parsing failed",
                keywords=[]
            )
    
    def batch_categorize(self, alerts: List[Dict[str, Any]]) -> List[CategoryDecision]:
        """
        Categorize multiple alerts.
        
        Args:
            alerts: List of alert data dictionaries
            
        Returns:
            List of CategoryDecision objects
        """
        results = []
        for i, alert in enumerate(alerts, 1):
            print(f"Categorizing alert {i}/{len(alerts)}...")
            decision = self.categorize_alert(alert)
            results.append(decision)
        return results


if __name__ == '__main__':
    # Test the categorizer
    from dotenv import load_dotenv
    load_dotenv()
    
    # Test data
    test_alert = {
        'alert_query': 'machine learning mineral exploration',
        'date': '2024-01-15',
        'articles': [
            {
                'title': 'AI Revolution in Copper Exploration',
                'url': 'https://example.com/article1',
                'snippet': 'New machine learning algorithms help discover copper deposits faster...'
            }
        ]
    }
    
    categorizer = LLMCategorizer(provider="openai")
    decision = categorizer.categorize_alert(test_alert)
    
    print(f"\nRelevant: {decision.is_relevant}")
    print(f"Confidence: {decision.confidence}")
    print(f"Category: {decision.category}")
    print(f"Summary: {decision.summary}")
    print(f"Keywords: {', '.join(decision.keywords)}")
