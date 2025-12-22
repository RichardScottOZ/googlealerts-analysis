"""
Tests for the Google Alerts Analysis System

Basic tests to verify core functionality without requiring API credentials.
"""

import json
from llm_categorizer import CategoryDecision


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
    
    assert decision.is_relevant == True
    assert decision.confidence == 0.85
    assert decision.category == "Machine Learning"
    assert len(decision.keywords) == 2
    
    # Test model_dump
    data = decision.model_dump()
    assert isinstance(data, dict)
    assert data['is_relevant'] == True
    
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
    assert parsed['is_relevant'] == False
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


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Tests for Google Alerts Analysis System")
    print("=" * 60)
    print()
    
    try:
        test_category_decision_model()
        test_category_decision_json_serialization()
        test_alert_data_structure()
        test_confidence_bounds()
        test_keywords_list()
        
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
