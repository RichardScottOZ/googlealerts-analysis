"""
Tests for date range functionality.

This test verifies that the date range parameters work correctly
when fetching alerts from a specific historical period.
"""

from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from gmail_fetcher import GmailAlertFetcher


def test_date_range_query_google_alerts():
    """Test that date range creates correct Gmail query for Google Alerts."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_messages_list = Mock()
    
    # Track the query that was used
    captured_query = None
    
    def capture_query(**kwargs):
        nonlocal captured_query
        captured_query = kwargs.get('q', '')
        return Mock(execute=Mock(return_value={'messages': []}))
    
    mock_messages_list.side_effect = capture_query
    mock_service.users().messages().list = mock_messages_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message to avoid actual parsing
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Fetch with date range: 280 to 250 days ago
        alerts = fetcher.fetch_google_alerts(
            days_back=250,
            max_results=10,
            days_back_start=280
        )
    
    # Verify the query includes both after: and before:
    assert 'from:googlealerts-noreply@google.com' in captured_query, "Query should include sender"
    assert 'after:' in captured_query, "Query should include after: clause"
    assert 'before:' in captured_query, "Query should include before: clause"
    
    # Extract dates from query
    # Query format: "from:... after:YYYY/MM/DD before:YYYY/MM/DD"
    parts = captured_query.split()
    after_date = None
    before_date = None
    
    for part in parts:
        if part.startswith('after:'):
            after_date = part.replace('after:', '')
        elif part.startswith('before:'):
            before_date = part.replace('before:', '')
    
    assert after_date is not None, "Should have after: date"
    assert before_date is not None, "Should have before: date"
    
    # Verify dates are approximately correct (within 1 day tolerance for timezone/timing)
    expected_after = datetime.now() - timedelta(days=280)
    expected_before = datetime.now() - timedelta(days=250)
    
    after_parsed = datetime.strptime(after_date, '%Y/%m/%d')
    before_parsed = datetime.strptime(before_date, '%Y/%m/%d')
    
    # Check dates are within reasonable range
    assert abs((after_parsed - expected_after).days) <= 1, "After date should be ~280 days ago"
    assert abs((before_parsed - expected_before).days) <= 1, "Before date should be ~250 days ago"
    assert after_parsed < before_parsed, "After date should be earlier than before date"
    
    print("✅ Date range query test for Google Alerts passed")


def test_date_range_query_scholar_alerts():
    """Test that date range creates correct Gmail query for Scholar Alerts."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_messages_list = Mock()
    
    # Track the query that was used
    captured_query = None
    
    def capture_query(**kwargs):
        nonlocal captured_query
        captured_query = kwargs.get('q', '')
        return Mock(execute=Mock(return_value={'messages': []}))
    
    mock_messages_list.side_effect = capture_query
    mock_service.users().messages().list = mock_messages_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message to avoid actual parsing
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Fetch with date range: 280 to 250 days ago
        alerts = fetcher.fetch_scholar_alerts(
            days_back=250,
            max_results=10,
            days_back_start=280
        )
    
    # Verify the query includes both after: and before:
    assert 'from:scholaralerts-noreply@google.com' in captured_query, "Query should include sender"
    assert 'after:' in captured_query, "Query should include after: clause"
    assert 'before:' in captured_query, "Query should include before: clause"
    
    print("✅ Date range query test for Scholar Alerts passed")


def test_backward_compatibility_no_start_date():
    """Test that fetching without days_back_start still works (backward compatibility)."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_messages_list = Mock()
    
    # Track the query that was used
    captured_query = None
    
    def capture_query(**kwargs):
        nonlocal captured_query
        captured_query = kwargs.get('q', '')
        return Mock(execute=Mock(return_value={'messages': []}))
    
    mock_messages_list.side_effect = capture_query
    mock_service.users().messages().list = mock_messages_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message to avoid actual parsing
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Fetch without date range (backward compatible mode)
        alerts = fetcher.fetch_google_alerts(
            days_back=7,
            max_results=10
        )
    
    # Verify the query only includes after: (not before:)
    assert 'from:googlealerts-noreply@google.com' in captured_query, "Query should include sender"
    assert 'after:' in captured_query, "Query should include after: clause"
    assert 'before:' not in captured_query, "Query should NOT include before: clause (backward compatible)"
    
    print("✅ Backward compatibility test (no start date) passed")


def test_invalid_date_range_ignored():
    """Test that invalid date range (start < end) is ignored."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_messages_list = Mock()
    
    # Track the query that was used
    captured_query = None
    
    def capture_query(**kwargs):
        nonlocal captured_query
        captured_query = kwargs.get('q', '')
        return Mock(execute=Mock(return_value={'messages': []}))
    
    mock_messages_list.side_effect = capture_query
    mock_service.users().messages().list = mock_messages_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message to avoid actual parsing
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Fetch with invalid date range (start=200 < end=250)
        # This should be ignored and treated as normal days_back
        alerts = fetcher.fetch_google_alerts(
            days_back=250,
            max_results=10,
            days_back_start=200  # Invalid: start should be > end
        )
    
    # Verify the query does NOT include before: (invalid range ignored)
    assert 'from:googlealerts-noreply@google.com' in captured_query, "Query should include sender"
    assert 'after:' in captured_query, "Query should include after: clause"
    assert 'before:' not in captured_query, "Query should NOT include before: clause (invalid range)"
    
    print("✅ Invalid date range handling test passed")


def test_statistics_with_date_range():
    """Test that statistics method supports date range."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_list = Mock()
    
    captured_queries = []
    
    def capture_query(**kwargs):
        captured_queries.append(kwargs.get('q', ''))
        return Mock(execute=Mock(return_value={'resultSizeEstimate': 100}))
    
    mock_list.side_effect = capture_query
    mock_service.users().messages().list = mock_list
    fetcher.service = mock_service
    
    # Get statistics with date range
    stats = fetcher.get_alert_statistics(
        days_back=250,
        days_back_start=280,
        alert_type='google'
    )
    
    # Should have made 2 queries (total and unread)
    assert len(captured_queries) >= 2, "Should make at least 2 queries"
    
    # Check first query includes date range
    first_query = captured_queries[0]
    assert 'after:' in first_query, "Query should include after: clause"
    assert 'before:' in first_query, "Query should include before: clause"
    
    print("✅ Statistics with date range test passed")


def run_all_tests():
    """Run all date range tests."""
    print("=" * 60)
    print("Running Date Range Tests for Gmail Fetcher")
    print("=" * 60)
    print()
    
    try:
        test_date_range_query_google_alerts()
        test_date_range_query_scholar_alerts()
        test_backward_compatibility_no_start_date()
        test_invalid_date_range_ignored()
        test_statistics_with_date_range()
        
        print()
        print("=" * 60)
        print("✅ All date range tests passed!")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print()
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Unexpected error: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
