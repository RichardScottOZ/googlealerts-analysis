"""
Tests for Gmail API pagination functionality.

This test verifies that the fetcher correctly handles pagination when
fetching more than 500 emails (Gmail API's per-request limit).
"""

from unittest.mock import Mock, MagicMock, patch
from gmail_fetcher import GmailAlertFetcher


def test_pagination_single_page():
    """Test fetching less than 500 emails (single page)."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_messages_list = Mock()
    
    # Simulate a single page with 50 messages
    mock_messages_list.return_value.execute.return_value = {
        'messages': [{'id': f'msg_{i}'} for i in range(50)],
        # No nextPageToken means no more pages
    }
    
    mock_service.users().messages().list = mock_messages_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message to avoid actual parsing
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Fetch 50 emails (should be a single request)
        alerts = fetcher.fetch_google_alerts(days_back=7, max_results=50)
    
    # Verify results
    assert len(alerts) == 50, f"Expected 50 alerts, got {len(alerts)}"
    assert mock_messages_list.call_count == 1, "Should make exactly one API call"
    
    print("✅ Single page pagination test passed")


def test_pagination_multiple_pages():
    """Test fetching more than 500 emails (multiple pages)."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    
    # Track calls to verify pagination
    call_count = 0
    
    def mock_list_execute(**kwargs):
        nonlocal call_count
        call_count += 1
        
        # First call: return 500 messages with a nextPageToken
        if call_count == 1:
            return {
                'messages': [{'id': f'msg_{i}'} for i in range(500)],
                'nextPageToken': 'token_page_2'
            }
        # Second call: return 500 more messages with another nextPageToken
        elif call_count == 2:
            return {
                'messages': [{'id': f'msg_{i}'} for i in range(500, 1000)],
                'nextPageToken': 'token_page_3'
            }
        # Third call: return remaining 200 messages without nextPageToken
        elif call_count == 3:
            return {
                'messages': [{'id': f'msg_{i}'} for i in range(1000, 1200)],
                # No nextPageToken - this is the last page
            }
    
    # Create a mock that returns our custom responses
    mock_list = Mock()
    mock_list.return_value.execute = mock_list_execute
    mock_service.users().messages().list = mock_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message to avoid actual parsing
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Fetch 1200 emails (should require 3 requests: 500 + 500 + 200)
        alerts = fetcher.fetch_google_alerts(days_back=7, max_results=1200)
    
    # Verify results
    assert len(alerts) == 1200, f"Expected 1200 alerts, got {len(alerts)}"
    assert call_count == 3, f"Should make exactly 3 API calls, made {call_count}"
    
    # Verify that pageToken was used in subsequent calls
    calls = mock_list.call_args_list
    assert len(calls) == 3, "Should have 3 calls recorded"
    
    # First call should not have pageToken
    first_call_kwargs = calls[0][1] if calls[0][1] else calls[0][0][0] if calls[0][0] else {}
    assert 'pageToken' not in first_call_kwargs, "First call should not have pageToken"
    
    # Second and third calls should have pageToken
    for i, expected_token in [(1, 'token_page_2'), (2, 'token_page_3')]:
        call_kwargs = calls[i][1] if calls[i][1] else {}
        assert 'pageToken' in call_kwargs, f"Call {i+1} should have pageToken"
        assert call_kwargs['pageToken'] == expected_token, f"Call {i+1} should have token {expected_token}"
    
    print("✅ Multiple page pagination test passed")


def test_pagination_exactly_500():
    """Test fetching exactly 500 emails (boundary case)."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_messages_list = Mock()
    
    # Simulate exactly 500 messages without nextPageToken
    mock_messages_list.return_value.execute.return_value = {
        'messages': [{'id': f'msg_{i}'} for i in range(500)],
        # No nextPageToken
    }
    
    mock_service.users().messages().list = mock_messages_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Fetch exactly 500 emails
        alerts = fetcher.fetch_google_alerts(days_back=7, max_results=500)
    
    # Verify results
    assert len(alerts) == 500, f"Expected 500 alerts, got {len(alerts)}"
    assert mock_messages_list.call_count == 1, "Should make exactly one API call"
    
    print("✅ Boundary case (500) pagination test passed")


def test_pagination_scholar_alerts():
    """Test that Scholar alerts also implement pagination correctly."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    
    call_count = 0
    
    def mock_list_execute(**kwargs):
        nonlocal call_count
        call_count += 1
        
        # First call: return 500 messages with nextPageToken
        if call_count == 1:
            return {
                'messages': [{'id': f'scholar_msg_{i}'} for i in range(500)],
                'nextPageToken': 'scholar_token_page_2'
            }
        # Second call: return 300 more messages
        elif call_count == 2:
            return {
                'messages': [{'id': f'scholar_msg_{i}'} for i in range(500, 800)],
            }
    
    mock_list = Mock()
    mock_list.return_value.execute = mock_list_execute
    mock_service.users().messages().list = mock_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test scholar', 'articles': []}
        
        # Fetch 800 Scholar alerts (should require 2 requests: 500 + 300)
        alerts = fetcher.fetch_scholar_alerts(days_back=7, max_results=800)
    
    # Verify results
    assert len(alerts) == 800, f"Expected 800 alerts, got {len(alerts)}"
    assert call_count == 2, f"Should make exactly 2 API calls, made {call_count}"
    
    print("✅ Scholar alerts pagination test passed")


def test_pagination_no_more_results():
    """Test that pagination stops when there are no more results."""
    fetcher = GmailAlertFetcher()
    
    # Mock the Gmail service
    mock_service = Mock()
    mock_messages_list = Mock()
    
    # Simulate only 100 messages available (less than requested)
    mock_messages_list.return_value.execute.return_value = {
        'messages': [{'id': f'msg_{i}'} for i in range(100)],
        # No nextPageToken
    }
    
    mock_service.users().messages().list = mock_messages_list
    fetcher.service = mock_service
    
    # Mock _parse_alert_message
    with patch.object(fetcher, '_parse_alert_message') as mock_parse:
        mock_parse.return_value = {'alert_query': 'test', 'articles': []}
        
        # Request 1000 emails but only 100 available
        alerts = fetcher.fetch_google_alerts(days_back=7, max_results=1000)
    
    # Verify results
    assert len(alerts) == 100, f"Expected 100 alerts (all available), got {len(alerts)}"
    assert mock_messages_list.call_count == 1, "Should make only one API call (no more results)"
    
    print("✅ No more results pagination test passed")


def run_all_tests():
    """Run all pagination tests."""
    print("=" * 60)
    print("Running Pagination Tests for Gmail Fetcher")
    print("=" * 60)
    print()
    
    try:
        test_pagination_single_page()
        test_pagination_multiple_pages()
        test_pagination_exactly_500()
        test_pagination_scholar_alerts()
        test_pagination_no_more_results()
        
        print()
        print("=" * 60)
        print("✅ All pagination tests passed!")
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
