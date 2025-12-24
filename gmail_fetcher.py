"""
Gmail Alert Fetcher Module

This module handles authentication and fetching of Google Alerts from Gmail.
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import re


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailAlertFetcher:
    """Fetches Google Alerts from Gmail account."""
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        """
        Initialize Gmail Alert Fetcher.
        
        Args:
            credentials_file: Path to OAuth credentials file
            token_file: Path to store/load authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        
    def authenticate(self) -> None:
        """Authenticate with Gmail API."""
        creds = None
        
        # Load token if it exists
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        
    def get_alert_statistics(self, days_back: int = None) -> Dict[str, int]:
        """
        Get statistics about Google Alert emails.
        
        Note: Uses Gmail API's resultSizeEstimate which provides an approximate count.
        For very large mailboxes, the count may not be exact but is sufficient for
        general inbox visibility.
        
        Args:
            days_back: Number of days to search back (None for all time)
            
        Returns:
            Dictionary with 'total', 'unread', and 'read' counts (approximate)
        """
        if not self.service:
            self.authenticate()
        
        # Build query for Google Alerts emails
        base_query = 'from:googlealerts-noreply@google.com'
        
        if days_back:
            search_date = datetime.now() - timedelta(days=days_back)
            date_str = search_date.strftime('%Y/%m/%d')
            base_query += f' after:{date_str}'
        
        try:
            # Get total count
            total_results = self.service.users().messages().list(
                userId='me',
                q=base_query,
                maxResults=1  # We just need the count
            ).execute()
            
            total_count = total_results.get('resultSizeEstimate', 0)
            
            # Get unread count
            unread_query = base_query + ' is:unread'
            unread_results = self.service.users().messages().list(
                userId='me',
                q=unread_query,
                maxResults=1  # We just need the count
            ).execute()
            
            unread_count = unread_results.get('resultSizeEstimate', 0)
            
            return {
                'total': total_count,
                'unread': unread_count,
                'read': total_count - unread_count
            }
            
        except Exception as e:
            print(f"Error getting alert statistics: {e}")
            return {
                'total': 0,
                'unread': 0,
                'read': 0
            }
    
    def fetch_google_alerts(self, days_back: int = 7, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch Google Alerts emails from Gmail.
        
        Args:
            days_back: Number of days to search back
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of alert dictionaries with title, link, snippet, and date
        """
        if not self.service:
            self.authenticate()
        
        # Calculate date for query
        search_date = datetime.now() - timedelta(days=days_back)
        date_str = search_date.strftime('%Y/%m/%d')
        
        # Search for Google Alerts emails
        query = f'from:googlealerts-noreply@google.com after:{date_str}'
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print(f"No Google Alerts found in the last {days_back} days.")
                return []
            
            alerts = []
            for message in messages:
                alert_data = self._parse_alert_message(message['id'])
                if alert_data:
                    alerts.append(alert_data)
            
            return alerts
            
        except Exception as e:
            print(f"Error fetching Google Alerts: {e}")
            return []
    
    def _parse_alert_message(self, message_id: str) -> Dict[str, Any]:
        """
        Parse a Google Alert email message.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary with alert information
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
            
            # Extract body
            body = self._get_email_body(message['payload'])
            
            # Parse alert information from body
            alert_info = self._extract_alert_info(body, subject)
            alert_info['date'] = date
            alert_info['message_id'] = message_id
            
            return alert_info
            
        except Exception as e:
            print(f"Error parsing message {message_id}: {e}")
            return None
    
    def _get_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from message payload."""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        else:
            if 'body' in payload and 'data' in payload['body']:
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def _extract_alert_info(self, body: str, subject: str) -> Dict[str, Any]:
        """
        Extract alert information from email body.
        
        Args:
            body: Email body text
            subject: Email subject line
            
        Returns:
            Dictionary with title, links, and snippets
        """
        # Extract alert query from subject (e.g., "Google Alert - machine learning")
        alert_query = subject.replace('Google Alert - ', '') if 'Google Alert - ' in subject else subject
        
        # Extract URLs and surrounding text
        url_pattern = r'https?://[^\s<>"\')]+[^\s<>"\'.,;:!?)\]]'
        urls = re.findall(url_pattern, body)
        
        # Extract snippets around URLs (simple approach)
        # In real Google Alerts, each article has title, snippet, and URL
        # This is a simplified parser
        articles = []
        
        # Try to parse HTML if present
        if '<a href=' in body:
            # HTML parsing - extract links and titles
            link_pattern = r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]+)</a>'
            matches = re.findall(link_pattern, body)
            for url, title in matches:
                if url.startswith('http') and 'google' not in url.lower():
                    articles.append({
                        'title': title.strip(),
                        'url': url,
                        'snippet': ''
                    })
        
        # Fallback: use plain URLs found
        if not articles:
            for url in urls:
                if 'google' not in url.lower():
                    articles.append({
                        'title': '',
                        'url': url,
                        'snippet': ''
                    })
        
        return {
            'alert_query': alert_query,
            'articles': articles,
            'full_body': body[:500]  # Keep first 500 chars for context
        }


if __name__ == '__main__':
    # Test the fetcher
    fetcher = GmailAlertFetcher()
    fetcher.authenticate()
    alerts = fetcher.fetch_google_alerts(days_back=7, max_results=5)
    
    print(f"Found {len(alerts)} Google Alerts")
    for i, alert in enumerate(alerts, 1):
        print(f"\n{i}. Alert Query: {alert['alert_query']}")
        print(f"   Date: {alert['date']}")
        print(f"   Articles: {len(alert['articles'])}")
