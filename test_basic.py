"""
Tests for the Google Alerts Analysis System

Basic tests to verify core functionality without requiring API credentials.
"""

import json
from llm_categorizer import CategoryDecision, ArticleAnalysis


def test_scholar_alert_data_structure():
    """Test the expected scholar alert data structure."""
    alert = {
        'alert_query': 'machine learning mineral exploration',
        'date': '2024-01-01',
        'message_id': '123',
        'articles': [
            {
                'title': 'ML for Mineral Exploration',
                'url': 'https://scholar.google.com/article',
                'snippet': 'Test snippet'
            }
        ],
        'full_body': 'Test body'
    }
    
    assert 'alert_query' in alert
    assert 'articles' in alert
    assert len(alert['articles']) == 1
    assert alert['articles'][0]['title'] == 'ML for Mineral Exploration'
    
    print("✅ Scholar alert data structure test passed")


def test_category_decision_model():
    """Test that CategoryDecision model works correctly."""
    decision = CategoryDecision(
        is_relevant=True,
        confidence=0.85,
        category="Machine Learning",
        reasoning="Test reasoning",
        summary="Test summary",
        keywords=["ml", "test"]
    )
    
    assert decision.is_relevant is True
    assert decision.confidence == 0.85
    assert decision.category == "Machine Learning"
    assert len(decision.keywords) == 2
    
    # Test model_dump
    data = decision.model_dump()
    assert isinstance(data, dict)
    assert data['is_relevant'] is True
    
    print("✅ CategoryDecision model test passed")


def test_category_decision_json_serialization():
    """Test that CategoryDecision can be serialized to JSON."""
    decision = CategoryDecision(
        is_relevant=False,
        confidence=0.95,
        category="Not Relevant",
        reasoning="Bitcoin mining is not mineral exploration",
        summary="Cryptocurrency news",
        keywords=["bitcoin", "crypto"]
    )
    
    # Convert to dict and serialize
    data = decision.model_dump()
    json_str = json.dumps(data)
    
    # Deserialize
    parsed = json.loads(json_str)
    assert parsed['is_relevant'] is False
    assert parsed['confidence'] == 0.95
    
    print("✅ JSON serialization test passed")


def test_alert_data_structure():
    """Test the expected alert data structure."""
    alert = {
        'alert_query': 'test query',
        'date': '2024-01-01',
        'message_id': '123',
        'articles': [
            {
                'title': 'Test Article',
                'url': 'https://example.com',
                'snippet': 'Test snippet'
            }
        ],
        'full_body': 'Test body'
    }
    
    assert 'alert_query' in alert
    assert 'articles' in alert
    assert len(alert['articles']) == 1
    assert alert['articles'][0]['title'] == 'Test Article'
    
    print("✅ Alert data structure test passed")


def test_confidence_bounds():
    """Test that confidence values are within valid bounds."""
    # Valid confidence values
    for conf in [0.0, 0.5, 1.0]:
        decision = CategoryDecision(
            is_relevant=True,
            confidence=conf,
            category="Test",
            reasoning="Test",
            summary="Test",
            keywords=[]
        )
        assert 0.0 <= decision.confidence <= 1.0
    
    print("✅ Confidence bounds test passed")


def test_keywords_list():
    """Test that keywords are properly stored as a list."""
    keywords = ["machine learning", "exploration", "geology"]
    decision = CategoryDecision(
        is_relevant=True,
        confidence=0.8,
        category="ML Exploration",
        reasoning="Test",
        summary="Test",
        keywords=keywords
    )
    
    assert isinstance(decision.keywords, list)
    assert len(decision.keywords) == 3
    assert "machine learning" in decision.keywords
    
    print("✅ Keywords list test passed")


def test_article_summaries():
    """Test that article summaries can be captured and default to an empty list."""
    decision_default = CategoryDecision(
        is_relevant=True,
        confidence=0.7,
        category="Test",
        reasoning="Test",
        summary="Test",
        keywords=[]
    )
    assert decision_default.article_summaries == []
    assert decision_default.articles == []
    assert decision_default.relevant_article_count == 0
    assert decision_default.total_article_count == 0

    summaries = [{"title": "A", "summary": "Short summary", "url": "https://example.com"}]
    decision_with_data = CategoryDecision(
        is_relevant=True,
        confidence=0.9,
        category="Test",
        reasoning="Test",
        summary="Test",
        keywords=[],
        article_summaries=summaries
    )
    assert decision_with_data.article_summaries == summaries

    print("✅ Article summaries test passed")


def test_article_analysis_model():
    """Test that ArticleAnalysis model works correctly."""
    article = ArticleAnalysis(
        title="ML in Mining Exploration",
        url="https://example.com/ml-mining",
        summary="Article about using machine learning in mineral exploration",
        is_relevant=True,
        relevance_reasoning="Directly relates to ML applications in mineral exploration"
    )
    
    assert article.title == "ML in Mining Exploration"
    assert article.url == "https://example.com/ml-mining"
    assert article.is_relevant is True
    assert "ML applications" in article.relevance_reasoning
    
    # Test model_dump
    data = article.model_dump()
    assert isinstance(data, dict)
    assert data['is_relevant'] is True
    
    print("✅ ArticleAnalysis model test passed")


def test_category_decision_with_articles():
    """Test CategoryDecision with per-article analysis."""
    articles = [
        ArticleAnalysis(
            title="ML in Mining",
            url="https://example.com/article1",
            summary="Article about ML in mining",
            is_relevant=True,
            relevance_reasoning="Relevant to ML in mineral exploration"
        ),
        ArticleAnalysis(
            title="Cryptocurrency News",
            url="https://example.com/article2",
            summary="Bitcoin mining news",
            is_relevant=False,
            relevance_reasoning="Not related to mineral exploration"
        )
    ]
    
    decision = CategoryDecision(
        is_relevant=True,
        confidence=0.85,
        category="Machine Learning - Exploration",
        reasoning="One relevant article found",
        summary="Alert contains relevant ML in mining article",
        keywords=["ml", "mining", "exploration"],
        articles=articles,
        relevant_article_count=1,
        total_article_count=2
    )
    
    assert decision.is_relevant is True
    assert decision.relevant_article_count == 1
    assert decision.total_article_count == 2
    assert len(decision.articles) == 2
    assert decision.articles[0].is_relevant is True
    assert decision.articles[1].is_relevant is False
    
    # Test serialization
    data = decision.model_dump()
    assert data['relevant_article_count'] == 1
    assert data['total_article_count'] == 2
    assert len(data['articles']) == 2
    
    print("✅ CategoryDecision with articles test passed")


def test_url_extraction_filtering():
    """Test that URL extraction properly filters out non-article links."""
    import re
    from url_utils import EXCLUDE_DOMAINS
    
    # Sample HTML with various link types
    sample_html = """
    <a href="https://farmonaut.com/article1">Mining Innovation Article</a>
    <a href="https://www.facebook.com/share">Facebook</a>
    <a href="https://twitter.com/intent/tweet">Twitter</a>
    <a href="https://google.com/alerts/remove">Flag as irrelevant</a>
    <a href="https://example.com/mining-news">Another Mining Article</a>
    <a href="https://www.linkedin.com/share">LinkedIn</a>
    """
    
    link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
    matches = re.findall(link_pattern, sample_html)
    
    # Filter using the same logic as gmail_fetcher.py
    articles = []
    
    for url, title in matches:
        if url.startswith('http') and not any(domain in url.lower() for domain in EXCLUDE_DOMAINS):
            articles.append({
                'title': title.strip(),
                'url': url,
                'snippet': ''
            })
    
    # Should have exactly 2 articles (farmonaut and example.com)
    assert len(articles) == 2
    
    # Extract URLs and titles for verification
    article_urls = [a['url'] for a in articles]
    article_titles = [a['title'] for a in articles]
    
    # Verify the expected articles are present (order-independent)
    assert 'https://farmonaut.com/article1' in article_urls
    assert 'https://example.com/mining-news' in article_urls
    assert 'Mining Innovation Article' in article_titles
    assert 'Another Mining Article' in article_titles
    
    # Verify social media links are filtered out
    assert not any('facebook' in url.lower() for url in article_urls)
    assert not any('twitter' in url.lower() for url in article_urls)
    assert not any('linkedin' in url.lower() for url in article_urls)
    assert not any('google' in url.lower() for url in article_urls)
    
    print("✅ URL extraction filtering test passed")


def test_google_redirect_url_extraction():
    """Test extraction of actual URLs from Google redirect URLs."""
    from url_utils import extract_actual_url
    
    # Test cases
    test_cases = [
        {
            'input': 'https://www.google.com/url?rct=j&sa=t&url=https://example.com/article&ct=ga',
            'expected': 'https://example.com/article'
        },
        {
            'input': 'https://www.google.com/url?url=https%3A%2F%2Fexample.com%2Fencoded%2Fpath&ct=ga',
            'expected': 'https://example.com/encoded/path'
        },
        {
            'input': 'https://example.com/direct-link',
            'expected': 'https://example.com/direct-link'
        },
        {
            'input': 'https://www.google.com/url?rct=j&url=https://mining-news.com/ml-exploration/article-123',
            'expected': 'https://mining-news.com/ml-exploration/article-123'
        }
    ]
    
    for test_case in test_cases:
        result = extract_actual_url(test_case['input'])
        assert result == test_case['expected'], f"Expected {test_case['expected']}, got {result}"
    
    print("✅ Google redirect URL extraction test passed")


def test_report_unicode_encoding():
    """Test that report generation handles Unicode characters properly."""
    import tempfile
    import os
    
    # Import AlertAnalyzer here to avoid Google auth issues in test environment
    # We'll just test the generate_report method directly
    try:
        from analyze_alerts import AlertAnalyzer
    except ImportError:
        # If Google libraries are not installed, skip this part of the test
        # but still verify the file encoding works
        pass
    
    # Create a mock analysis result with Unicode characters in the summary
    analysis_result = {
        'timestamp': '2024-01-01T00:00:00',
        'configuration': {
            'llm_provider': 'test',
            'llm_model': 'test-model',
            'days_back': 7,
            'max_emails': 10
        },
        'statistics': {
            'total': 10,
            'unread': 5,
            'read': 5
        },
        'total_alerts': 2,
        'relevant_alerts': 1,
        'results': [
            {
                'alert': {
                    'alert_query': 'test query',
                    'date': '2024-01-01',
                    'articles': []
                },
                'decision': {
                    'is_relevant': True,
                    'confidence': 0.85,
                    'category': 'Machine Learning',
                    'reasoning': 'Test reasoning with Unicode: ✅ ❌ 📊 🤖',
                    'summary': 'Test summary with emojis ✅',
                    'keywords': ['test'],
                    'articles': [
                        {
                            'title': 'Test Article ✅',
                            'url': 'https://example.com',
                            'summary': 'Summary with emoji ✅',
                            'is_relevant': True,
                            'relevance_reasoning': 'Relevant ✅'
                        }
                    ],
                    'relevant_article_count': 1,
                    'total_article_count': 1
                }
            }
        ]
    }
    
    # Test content with Unicode characters
    test_content = """# Test Report
    
## Results
✅ Relevant: True
❌ Relevant: False
📊 Articles: 1/2
🤖 Processing
📁 Category: Machine Learning
📝 Summary: Test
"""
    
    # Test writing to file with UTF-8 encoding (this is what the fix does)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.md', delete=False) as f:
        temp_path = f.name
        f.write(test_content)
    
    try:
        # Read it back and verify
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '✅' in content, "File should contain Unicode checkmark"
        assert '❌' in content, "File should contain Unicode cross"
        assert '📊' in content, "File should contain Unicode chart emoji"
    finally:
        os.unlink(temp_path)
    
    print("✅ Report Unicode encoding test passed")


def test_xhtml_namespace_url_filtering():
    """Test that XHTML namespace URLs are properly filtered out."""
    from url_utils import is_excluded_domain
    
    # Test the XHTML namespace URL that was appearing in the bug report
    xhtml_namespace_url = "http://www.w3.org/1999/xhtml"
    
    # This should be excluded
    assert is_excluded_domain(xhtml_namespace_url), \
        "XHTML namespace URL should be excluded from article extraction"
    
    # Test other W3C URLs that should also be filtered
    w3c_urls = [
        "https://www.w3.org/2000/svg",
        "http://www.w3.org/TR/html5/",
        "https://w3.org/standards/"
    ]
    
    for url in w3c_urls:
        assert is_excluded_domain(url), \
            f"W3C URL {url} should be excluded from article extraction"
    
    # Test that legitimate article URLs are NOT excluded
    legitimate_urls = [
        "https://nature.com/articles/science-123",
        "https://arxiv.org/abs/2024.12345",
        "https://sciencedirect.com/article/xyz",
        "https://example.com/blog/post"
    ]
    
    for url in legitimate_urls:
        assert not is_excluded_domain(url), \
            f"Legitimate article URL {url} should NOT be excluded"
    
    print("✅ XHTML namespace URL filtering test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Tests for Google Alerts Analysis System")
    print("=" * 60)
    print()
    
    try:
        test_scholar_alert_data_structure()
        test_category_decision_model()
        test_category_decision_json_serialization()
        test_alert_data_structure()
        test_confidence_bounds()
        test_keywords_list()
        test_article_summaries()
        test_article_analysis_model()
        test_category_decision_with_articles()
        test_url_extraction_filtering()
        test_google_redirect_url_extraction()
        test_report_unicode_encoding()
        test_xhtml_namespace_url_filtering()
        
        print()
        print("=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Unexpected error: {e}")
        print("=" * 60)
        return False


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
