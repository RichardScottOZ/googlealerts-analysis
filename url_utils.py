"""
URL Utility Module

Shared utilities for extracting and parsing URLs from Google Alert emails.
This module has no external dependencies beyond Python standard library.
"""

import re
from urllib.parse import unquote, urlparse, parse_qs
from typing import List


# Domains to exclude when extracting article URLs from emails
# (social media sharing links, Google actions, W3C standards, etc.)
EXCLUDE_DOMAINS = ['google', 'facebook', 'twitter', 'linkedin', 'youtube', 'w3.org']


def extract_actual_url(url: str) -> str:
    """
    Extract the actual URL from a Google redirect URL.
    
    Google Alert emails use redirect URLs like:
    https://www.google.com/url?...&url=<actual_url>&...
    
    This function extracts the actual destination URL.
    
    Args:
        url: Original URL (may be a Google redirect)
        
    Returns:
        Actual destination URL
        
    Examples:
        >>> extract_actual_url('https://www.google.com/url?url=https://example.com')
        'https://example.com'
        >>> extract_actual_url('https://example.com/article')
        'https://example.com/article'
    """
    # Check if this is a Google redirect URL
    if 'google.com/url' not in url:
        return url
    
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Extract the 'url' parameter which contains the actual destination
        if 'url' in params:
            actual_url = params['url'][0]
            return unquote(actual_url)
        
        # Fallback: try regex extraction
        match = re.search(r'[?&]url=([^&]+)', url)
        if match:
            return unquote(match.group(1))
    except (ValueError, KeyError, IndexError) as e:
        print(f"Warning: Could not extract URL from redirect: {e}")
        return url
    
    return url


def is_excluded_domain(url: str, exclude_domains: List[str] = None) -> bool:
    """
    Check if a URL is from an excluded domain.
    
    Args:
        url: URL to check
        exclude_domains: List of domain strings to exclude (optional, uses EXCLUDE_DOMAINS if None)
        
    Returns:
        True if URL is from an excluded domain
    """
    if exclude_domains is None:
        exclude_domains = EXCLUDE_DOMAINS
    
    url_lower = url.lower()
    return any(domain in url_lower for domain in exclude_domains)
