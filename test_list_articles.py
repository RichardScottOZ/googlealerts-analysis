"""
Tests for the list_articles.py script
"""

import json
import tempfile
import os
from pathlib import Path
from list_articles import parse_report_json, format_article_list, Article


def test_parse_empty_report():
    """Test parsing an empty report."""
    # Create temporary JSON file with empty results
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            'timestamp': '2024-01-01T00:00:00',
            'total_alerts': 0,
            'relevant_alerts': 0,
            'results': []
        }, f)
        temp_path = f.name
    
    try:
        articles = parse_report_json(temp_path, 'google_alerts')
        assert len(articles) == 0, "Should have no articles"
    finally:
        os.unlink(temp_path)
    
    print("✅ Empty report parsing test passed")


def test_parse_report_with_articles():
    """Test parsing a report with articles."""
    # Create sample report
    sample_report = {
        'timestamp': '2024-01-01T00:00:00',
        'total_alerts': 1,
        'relevant_alerts': 1,
        'results': [
            {
                'alert': {
                    'alert_query': 'machine learning exploration',
                    'date': '2024-01-01',
                    'articles': []
                },
                'decision': {
                    'is_relevant': True,
                    'confidence': 0.9,
                    'category': 'Machine Learning',
                    'reasoning': 'Relevant to ML in exploration',
                    'summary': 'ML articles',
                    'keywords': ['ml', 'exploration'],
                    'articles': [
                        {
                            'title': 'ML for Mineral Exploration',
                            'url': 'https://example.com/ml-mining',
                            'summary': 'Using ML in mineral exploration',
                            'is_relevant': True,
                            'relevance_reasoning': 'Directly relevant'
                        },
                        {
                            'title': 'Bitcoin Mining',
                            'url': 'https://example.com/bitcoin',
                            'summary': 'Cryptocurrency mining',
                            'is_relevant': False,
                            'relevance_reasoning': 'Not relevant to mineral exploration'
                        }
                    ],
                    'relevant_article_count': 1,
                    'total_article_count': 2
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_report, f)
        temp_path = f.name
    
    try:
        articles = parse_report_json(temp_path, 'google_alerts')
        assert len(articles) == 2, f"Should have 2 articles, got {len(articles)}"
        assert articles[0].title == 'ML for Mineral Exploration'
        assert articles[0].is_relevant is True
        assert articles[1].title == 'Bitcoin Mining'
        assert articles[1].is_relevant is False
        assert articles[0].source == 'google_alerts'
    finally:
        os.unlink(temp_path)
    
    print("✅ Report with articles parsing test passed")


def test_parse_legacy_format():
    """Test parsing reports in legacy format (without per-article analysis)."""
    sample_report = {
        'timestamp': '2024-01-01T00:00:00',
        'total_alerts': 1,
        'relevant_alerts': 1,
        'results': [
            {
                'alert': {
                    'alert_query': 'geology ML',
                    'date': '2024-01-02',
                    'articles': [
                        {
                            'title': 'Geology and Machine Learning',
                            'url': 'https://example.com/geo-ml',
                            'snippet': 'An article about geology and ML'
                        }
                    ]
                },
                'decision': {
                    'is_relevant': True,
                    'confidence': 0.85,
                    'category': 'ML',
                    'reasoning': 'Relevant',
                    'summary': 'Good article',
                    'keywords': ['geology', 'ml']
                }
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_report, f)
        temp_path = f.name
    
    try:
        articles = parse_report_json(temp_path, 'scholar_alerts')
        assert len(articles) == 1, f"Should have 1 article, got {len(articles)}"
        assert articles[0].title == 'Geology and Machine Learning'
        assert articles[0].source == 'scholar_alerts'
        assert articles[0].summary == 'An article about geology and ML'
    finally:
        os.unlink(temp_path)
    
    print("✅ Legacy format parsing test passed")


def test_article_sorting():
    """Test that articles are sorted chronologically."""
    articles = [
        Article(
            title='Article 1',
            url='https://example.com/1',
            summary='First',
            date='2024-01-01',
            source='google_alerts',
            alert_query='test',
            is_relevant=True
        ),
        Article(
            title='Article 2',
            url='https://example.com/2',
            summary='Second',
            date='2024-01-03',
            source='google_alerts',
            alert_query='test',
            is_relevant=True
        ),
        Article(
            title='Article 3',
            url='https://example.com/3',
            summary='Third',
            date='2024-01-02',
            source='scholar_alerts',
            alert_query='test',
            is_relevant=True
        )
    ]
    
    # Format (which sorts)
    output = format_article_list(articles, 'text', show_irrelevant=True)
    
    # Check that the newest (2024-01-03) comes first in output
    assert output.index('Article 2') < output.index('Article 3'), "Article 2 should come before Article 3"
    assert output.index('Article 3') < output.index('Article 1'), "Article 3 should come before Article 1"
    
    print("✅ Article sorting test passed")


def test_format_text_output():
    """Test text formatting."""
    articles = [
        Article(
            title='Test Article',
            url='https://example.com/test',
            summary='A test summary',
            date='2024-01-01',
            source='google_alerts',
            alert_query='test query',
            is_relevant=True,
            relevance_reasoning='Very relevant'
        )
    ]
    
    output = format_article_list(articles, 'text', show_irrelevant=True)
    
    assert 'Test Article' in output
    assert 'https://example.com/test' in output
    assert 'A test summary' in output
    assert 'test query' in output
    assert '✅' in output  # Relevance icon
    
    print("✅ Text formatting test passed")


def test_format_markdown_output():
    """Test markdown formatting."""
    articles = [
        Article(
            title='ML Article',
            url='https://example.com/ml',
            summary='Machine learning article',
            date='2024-01-01',
            source='scholar_alerts',
            alert_query='ml exploration',
            is_relevant=True
        )
    ]
    
    output = format_article_list(articles, 'markdown', show_irrelevant=True)
    
    assert '# Chronological Article List' in output
    assert '## 1. ML Article' in output
    assert 'https://example.com/ml' in output
    assert 'Machine learning article' in output
    assert '🎓 Scholar Alert' in output
    assert '✅' in output
    
    print("✅ Markdown formatting test passed")


def test_format_json_output():
    """Test JSON formatting."""
    articles = [
        Article(
            title='JSON Test',
            url='https://example.com/json',
            summary='JSON test summary',
            date='2024-01-01',
            source='google_alerts',
            alert_query='json test',
            is_relevant=False,
            relevance_reasoning='Not relevant'
        )
    ]
    
    output = format_article_list(articles, 'json', show_irrelevant=True)
    
    # Parse JSON to verify it's valid
    parsed = json.loads(output)
    assert len(parsed) == 1
    assert parsed[0]['title'] == 'JSON Test'
    assert parsed[0]['url'] == 'https://example.com/json'
    assert parsed[0]['is_relevant'] is False
    assert parsed[0]['source'] == 'google_alerts'
    
    print("✅ JSON formatting test passed")


def test_filter_irrelevant_articles():
    """Test filtering of non-relevant articles."""
    articles = [
        Article(
            title='Relevant',
            url='https://example.com/1',
            summary='Relevant article',
            date='2024-01-01',
            source='google_alerts',
            alert_query='test',
            is_relevant=True
        ),
        Article(
            title='Not Relevant',
            url='https://example.com/2',
            summary='Not relevant article',
            date='2024-01-02',
            source='google_alerts',
            alert_query='test',
            is_relevant=False
        )
    ]
    
    # Without show_irrelevant flag
    output = format_article_list(articles, 'text', show_irrelevant=False)
    assert 'Relevant' in output
    assert 'Not Relevant' not in output
    
    # With show_irrelevant flag
    output_all = format_article_list(articles, 'text', show_irrelevant=True)
    assert 'Relevant' in output_all
    assert 'Not Relevant' in output_all
    
    print("✅ Irrelevant article filtering test passed")


def test_nonexistent_file():
    """Test handling of non-existent files."""
    articles = parse_report_json('/nonexistent/file.json', 'google_alerts')
    assert len(articles) == 0, "Should return empty list for non-existent file"
    
    print("✅ Non-existent file handling test passed")


def test_invalid_json_file():
    """Test handling of invalid JSON."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_path = f.name
    
    try:
        articles = parse_report_json(temp_path, 'google_alerts')
        assert len(articles) == 0, "Should return empty list for invalid JSON"
    finally:
        os.unlink(temp_path)
    
    print("✅ Invalid JSON handling test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Tests for list_articles.py")
    print("=" * 60)
    print()
    
    try:
        test_parse_empty_report()
        test_parse_report_with_articles()
        test_parse_legacy_format()
        test_article_sorting()
        test_format_text_output()
        test_format_markdown_output()
        test_format_json_output()
        test_filter_irrelevant_articles()
        test_nonexistent_file()
        test_invalid_json_file()
        
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
        import traceback
        traceback.print_exc()
        print("=" * 60)
        return False


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
