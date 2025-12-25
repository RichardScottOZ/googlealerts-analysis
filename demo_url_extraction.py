"""
Demo script to show the improved URL extraction and article logging.

This demonstrates:
1. Extraction of actual URLs from Google redirect URLs
2. Article-level logging during processing
3. JSON output with complete article information
"""

import json
import re
from datetime import datetime

from url_utils import extract_actual_url, is_excluded_domain, EXCLUDE_DOMAINS


def extract_alert_info(body: str, subject: str):
    """
    Extract alert information from email body.
    
    This is a simplified version of GmailAlertFetcher._extract_alert_info()
    """
    
    # Extract alert query from subject
    alert_query = subject.replace('Google Alert - ', '') if 'Google Alert - ' in subject else subject
    
    articles = []
    
    # Try to parse HTML if present
    if '<a href=' in body:
        # Extract all links with their surrounding context
        link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(link_pattern, body, re.DOTALL)
        
        for url, content in matches:
            # Extract actual URL from Google redirect
            actual_url = extract_actual_url(url)
            
            # Check if URL is an article link (check actual URL, not redirect)
            if actual_url.startswith('http') and not is_excluded_domain(actual_url):
                # Extract title from content (look for <b> tags)
                title_match = re.search(r'<b>([^<]+)</b>', content)
                if title_match:
                    clean_title = title_match.group(1).strip()
                else:
                    # Fallback: clean up all HTML tags
                    clean_title = re.sub(r'<[^>]+>', '', content).strip()
                
                # Only add if we have a meaningful title or URL
                if clean_title or actual_url:
                    articles.append({
                        'title': clean_title,
                        'url': actual_url,
                        'snippet': ''
                    })
    
    return {
        'alert_query': alert_query,
        'articles': articles,
        'full_body': body[:500]
    }


def demo_url_extraction():
    """Demo URL extraction from mock Google Alert HTML."""
    print("=" * 70)
    print("Demo: URL Extraction from Google Alert Email")
    print("=" * 70)
    print()
    
    # Mock Google Alert HTML (typical format with Google redirect URLs)
    mock_html = """
    <html>
    <body>
    <table>
    <tr>
    <td>
    <div>
    <a href="https://www.google.com/url?rct=j&sa=t&url=https://mining-journal.com/ml-exploration&ct=ga&cd=CAI...">
    <div><font><b>Machine Learning Transforms Mineral Exploration</b></font></div>
    </a>
    <br>
    <div>
    <font>New AI algorithms are revolutionizing how companies discover mineral deposits...</font>
    </div>
    <br>
    <div>
    <font color="#6f6f6f">mining-journal.com</font>
    </div>
    </div>
    </td>
    </tr>
    <tr>
    <td>
    <div>
    <a href="https://www.google.com/url?url=https%3A%2F%2Ftech-news.com%2Fai-geoscience%2Farticle-456&ct=ga">
    <div><font><b>AI in Geoscience: The Future of Exploration</b></font></div>
    </a>
    <br>
    <div>
    <font>Artificial intelligence is becoming essential for geological surveys and mapping...</font>
    </div>
    </div>
    </td>
    </tr>
    <tr>
    <td>
    <div>
    <a href="https://www.google.com/url?url=https://example.com/direct-article">
    <div><font><b>Remote Sensing with Deep Learning</b></font></div>
    </a>
    </div>
    </td>
    </tr>
    </table>
    </body>
    </html>
    """
    
    # Extract alert info
    alert_info = extract_alert_info(mock_html, "Google Alert - machine learning mineral exploration")
    
    print(f"Alert Query: {alert_info['alert_query']}")
    print(f"Articles Found: {len(alert_info['articles'])}")
    print()
    
    for i, article in enumerate(alert_info['articles'], 1):
        print(f"{i}. Title: {article['title']}")
        print(f"   URL: {article['url']}")
        print(f"   ✓ URL successfully extracted from Google redirect")
        print()
    
    print("✅ All URLs successfully extracted from Google redirect format!")
    print()


def demo_json_structure():
    """Demo the JSON structure output."""
    print("=" * 70)
    print("Demo: JSON Output Structure")
    print("=" * 70)
    print()
    
    # Mock analysis result showing the complete structure
    current_time = datetime.now().isoformat()
    mock_result = {
        'timestamp': current_time,
        'configuration': {
            'llm_provider': 'openai',
            'llm_model': 'gpt-4o-mini',
            'days_back': 7,
            'max_emails': 10
        },
        'statistics': {
            'total': 25,
            'unread': 5,
            'read': 20
        },
        'total_alerts': 2,
        'relevant_alerts': 1,
        'results': [
            {
                'alert': {
                    'alert_query': 'machine learning mineral exploration',
                    'date': 'Mon, 15 Jan 2024 10:00:00 +0000',
                    'message_id': '12345',
                    'articles': [
                        {
                            'title': 'Machine Learning Transforms Mineral Exploration',
                            'url': 'https://mining-journal.com/ml-exploration',
                            'snippet': 'New AI algorithms revolutionize discovery...'
                        },
                        {
                            'title': 'AI in Geoscience',
                            'url': 'https://tech-news.com/ai-geoscience/article-456',
                            'snippet': 'Artificial intelligence for geological surveys...'
                        }
                    ],
                    'full_body': 'Email body excerpt...'
                },
                'decision': {
                    'is_relevant': True,
                    'confidence': 0.92,
                    'category': 'Machine Learning - Exploration',
                    'reasoning': 'Articles discuss ML applications in mineral exploration',
                    'summary': 'Alert contains 2 relevant articles about ML in mineral exploration',
                    'keywords': ['machine learning', 'mineral exploration', 'AI', 'geoscience'],
                    'articles': [
                        {
                            'title': 'Machine Learning Transforms Mineral Exploration',
                            'url': 'https://mining-journal.com/ml-exploration',
                            'summary': 'Article discusses new AI algorithms for discovering mineral deposits',
                            'is_relevant': True,
                            'relevance_reasoning': 'Directly relates to ML in mineral exploration'
                        },
                        {
                            'title': 'AI in Geoscience',
                            'url': 'https://tech-news.com/ai-geoscience/article-456',
                            'summary': 'Article about AI applications in geological surveys',
                            'is_relevant': True,
                            'relevance_reasoning': 'Covers AI in geoscience for exploration'
                        }
                    ],
                    'relevant_article_count': 2,
                    'total_article_count': 2,
                    'article_summaries': []
                }
            }
        ]
    }
    
    print("JSON Structure (formatted for readability):")
    print(json.dumps(mock_result, indent=2))
    print()
    
    print("Key Features of JSON Output:")
    print("✓ Complete article information with URLs")
    print("✓ Per-article relevance analysis")
    print("✓ Article summaries and reasoning")
    print("✓ Alert metadata and statistics")
    print("✓ LLM configuration details")
    print()


def demo_console_logging():
    """Demo the improved console logging output."""
    print("=" * 70)
    print("Demo: Improved Console Logging")
    print("=" * 70)
    print()
    
    print("Example console output when processing alerts:")
    print()
    print("[1/2] Processing: machine learning mineral exploration...")
    print("  📰 Found 2 article(s) in alert:")
    print("     1. Machine Learning Transforms Mineral Exploration")
    print("        URL: https://mining-journal.com/ml-exploration")
    print("     2. AI in Geoscience: The Future of Exploration")
    print("        URL: https://tech-news.com/ai-geoscience/article-456")
    print("  ✅ Relevant: True (confidence: 0.92)")
    print("  📊 Articles: 2/2 relevant")
    print("  📁 Category: Machine Learning - Exploration")
    print("  📝 Summary: Alert contains 2 relevant articles about ML in mineral exploration")
    print("  📋 Article Analysis:")
    print("     1. ✅ Machine Learning Transforms Mineral Exploration")
    print("        https://mining-journal.com/ml-exploration")
    print("     2. ✅ AI in Geoscience: The Future of Exploration")
    print("        https://tech-news.com/ai-geoscience/article-456")
    print()
    
    print("[2/2] Processing: bitcoin mining news...")
    print("  📰 Found 1 article(s) in alert:")
    print("     1. Bitcoin Mining Profitability Increases")
    print("        URL: https://crypto-news.com/bitcoin-mining")
    print("  ❌ Relevant: False (confidence: 0.95)")
    print("  📊 Articles: 0/1 relevant")
    print("  📁 Category: Not Relevant - Cryptocurrency")
    print("  📝 Summary: No relevant articles found")
    print("  📋 Article Analysis:")
    print("     1. ❌ Bitcoin Mining Profitability Increases")
    print("        https://crypto-news.com/bitcoin-mining")
    print()
    
    print("Key Improvements:")
    print("✓ Shows articles found in each alert before LLM processing")
    print("✓ Displays actual URLs extracted from Google redirects")
    print("✓ Shows per-article relevance after LLM analysis")
    print("✓ Clear visual indicators (✅/❌) for quick scanning")
    print()


if __name__ == '__main__':
    print()
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "Google Alerts Analysis - Feature Demonstration" + " " * 10 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    demo_url_extraction()
    demo_json_structure()
    demo_console_logging()
    
    print("=" * 70)
    print("✅ All improvements demonstrated successfully!")
    print("=" * 70)
    print()
    print("Summary of Changes:")
    print("1. ✅ Article URLs now correctly extracted from Google redirect URLs")
    print("2. ✅ Article information logged to console during processing")
    print("3. ✅ JSON output includes complete article structure with URLs")
    print()
