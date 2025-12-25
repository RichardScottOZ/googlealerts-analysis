"""
LLM Categorizer Module

This module uses LLMs (OpenAI GPT, Google Gemini, or OpenRouter) to categorize Google Alerts
and determine if they are relevant to the mineral-exploration-machine-learning repository.
"""

import os
from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field
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


class ArticleAnalysis(BaseModel):
    """Model for per-article analysis."""
    title: str
    url: str
    summary: str
    is_relevant: bool
    relevance_reasoning: str = ""


class CategoryDecision(BaseModel):
    """Model for categorization decision."""
    is_relevant: bool  # True if any article is relevant
    confidence: float  # 0.0 to 1.0 - average of relevant article confidences
    category: str
    reasoning: str
    summary: str  # Summary of the overall alert
    keywords: List[str]
    article_summaries: List[Dict[str, str]] = Field(default_factory=list)  # Deprecated, kept for backward compatibility
    articles: List[ArticleAnalysis] = Field(default_factory=list)  # New per-article analysis
    relevant_article_count: int = 0
    total_article_count: int = 0


class LLMCategorizer:
    """Categorizes content using LLM APIs."""
    
    def __init__(
        self,
        provider: Literal["openai", "gemini", "openrouter"] = "openai",
        model: str = None,
        api_key: str = None
    ):
        """
        Initialize LLM Categorizer.
        
        Args:
            provider: LLM provider (openai, gemini, or openrouter)
            model: Model name (e.g., gpt-4o-mini, gemini-1.5-flash, anthropic/claude-3.5-sonnet)
            api_key: API key for the provider
        """
        self.provider = provider
        self.api_key = api_key or self._get_api_key()
        
        # Set default models
        if model is None:
            if provider == "openai":
                self.model = "gpt-4o-mini"
            elif provider == "gemini":
                self.model = "gemini-1.5-flash"
            else:  # openrouter
                self.model = "openai/gpt-4o-mini"
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
        elif self.provider == "gemini":
            key = os.getenv('GEMINI_API_KEY')
            if not key:
                raise ValueError("GEMINI_API_KEY not found in environment")
            return key
        else:  # openrouter
            key = os.getenv('OPENROUTER_API_KEY')
            if not key:
                raise ValueError("OPENROUTER_API_KEY not found in environment")
            return key
    
    def _initialize_client(self) -> None:
        """Initialize the LLM client."""
        if self.provider == "openai":
            if not HAS_OPENAI:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
            self.client = openai.OpenAI(api_key=self.api_key)
        elif self.provider == "gemini":
            if not HAS_GEMINI:
                raise ImportError(
                    "Google Generative AI package not installed. "
                    "Install with: pip install google-generativeai"
                )
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        else:  # openrouter
            if not HAS_OPENAI:
                raise ImportError(
                    "OpenAI package required for OpenRouter. Install with: pip install openai"
                )
            # OpenRouter uses OpenAI-compatible API
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url="https://openrouter.ai/api/v1"
            )
    
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
            elif self.provider == "gemini":
                response = self._call_gemini(prompt)
            else:  # openrouter
                response = self._call_openrouter(prompt)
            
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
        article_count = 0
        for article in alert_data.get('articles', []):
            url = article.get('url', '')
            # Skip articles without URLs
            if not url or url == 'N/A':
                continue
            article_count += 1
            title = article.get('title', '') or 'N/A'
            articles_text += f"\n{article_count}. Title: {title}\n"
            articles_text += f"   URL: {url}\n"
            if article.get('snippet'):
                articles_text += f"   Snippet: {article.get('snippet', '')}\n"
        
        prompt = f"""You are an expert in mineral exploration and machine learning. Your task is to analyze EACH article in this Google Alert INDIVIDUALLY and determine if it is relevant to a GitHub repository about machine learning applications in mineral exploration.

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

CRITICAL INSTRUCTIONS:
1. Analyze EACH article individually - do NOT summarize the entire alert email
2. For EACH article, determine if it is relevant to the repository topic
3. The overall alert is only relevant if at least ONE article is relevant
4. You MUST analyze the actual article content/title/URL - not the alert email itself
5. Use the EXACT URLs provided - do not modify or invent URLs
6. If a title is missing, create a brief descriptive title based on the URL or snippet
7. Skip articles that have no valid URL

For each article, provide:
- The exact title (or inferred title if missing)
- The exact URL from the list above
- A one-sentence summary of what the article is about
- Whether it is relevant (true/false) to ML in mineral exploration
- Brief reasoning for the relevance decision

Respond in JSON format:
{{
    "articles": [
        {{
            "title": "exact or inferred title",
            "url": "exact URL from above",
            "summary": "one-sentence summary of article content",
            "is_relevant": true/false,
            "relevance_reasoning": "brief explanation of why relevant or not"
        }},
        ...
    ],
    "relevant_article_count": number of relevant articles,
    "total_article_count": total number of articles analyzed,
    "is_relevant": true if ANY article is relevant (relevant_article_count > 0),
    "confidence": average confidence for relevant articles (0.0 to 1.0),
    "category": "Machine Learning - Exploration" or "Remote Sensing" or "Geophysics" or "Mining Technology" or "Not Relevant",
    "reasoning": "brief overall reasoning based on relevant articles",
    "summary": "summary of relevant articles only (or 'No relevant articles' if none)",
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
    
    def _call_openrouter(self, prompt: str) -> str:
        """Call OpenRouter API."""
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
    
    def _parse_response(self, response_text: str) -> CategoryDecision:
        """Parse LLM response into CategoryDecision."""
        try:
            data = json.loads(response_text)
            
            # Convert articles list to ArticleAnalysis objects
            articles_data = data.pop('articles', [])
            articles = []
            for article in articles_data:
                # Handle both old format (with is_relevant) and ensure compatibility
                articles.append(ArticleAnalysis(
                    title=article.get('title', ''),
                    url=article.get('url', ''),
                    summary=article.get('summary', ''),
                    is_relevant=article.get('is_relevant', False),
                    relevance_reasoning=article.get('relevance_reasoning', '')
                ))
            
            # Calculate counts if not provided
            total_count = len(articles)
            relevant_count = sum(1 for a in articles if a.is_relevant)
            
            # Build the CategoryDecision with the converted articles
            return CategoryDecision(
                is_relevant=data.get('is_relevant', relevant_count > 0),
                confidence=data.get('confidence', 0.0),
                category=data.get('category', 'Unknown'),
                reasoning=data.get('reasoning', ''),
                summary=data.get('summary', ''),
                keywords=data.get('keywords', []),
                article_summaries=data.get('article_summaries', []),  # Keep for backward compatibility
                articles=articles,
                relevant_article_count=data.get('relevant_article_count', relevant_count),
                total_article_count=data.get('total_article_count', total_count)
            )
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
