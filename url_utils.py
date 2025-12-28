"""
URL Utility Module

Shared utilities for extracting and parsing URLs from Google Alert emails.
This module has no external dependencies beyond Python standard library.
"""

import re
from urllib.parse import unquote, urlparse, parse_qs
from typing import List


# Domains to exclude when extracting article URLs from emails
# (social media sharing links, Google actions, etc.)
EXCLUDE_DOMAINS = ['google', 'facebook', 'twitter', 'linkedin', 'youtube']


def extract_actual_url(url: str) -> str:
    """
    Extract the actual URL from a Google redirect URL.
    
    Google Alert emails use redirect URLs like:
    https://www.google.com/url?...&url=<actual_url>&...
    
    Google Scholar Alert emails use redirect URLs like:
    https://scholar.google.com/scholar_url?url=<actual_url>&...
    https://scholar.googleusercontent.com/scholar?...&url=<actual_url>&...
    
    This function extracts the actual destination URL.
    
    Args:
        url: Original URL (may be a Google redirect)
        
    Returns:
        Actual destination URL
        
    Examples:
        >>> extract_actual_url('https://www.google.com/url?url=https://example.com')
        'https://example.com'
        >>> extract_actual_url('https://scholar.google.com/scholar_url?url=https://arxiv.org/abs/123')
        'https://arxiv.org/abs/123'
        >>> extract_actual_url('https://example.com/article')
        'https://example.com/article'
    """
    # Check if this is a Google redirect URL (regular or Scholar)
    if not ('google.com/url' in url or 'scholar.google' in url):
        return url
    
    try:
        # Use regex to extract the url parameter value more robustly
        # This handles cases where the actual URL contains & characters
        match = re.search(r'[?&]url=([^&]+(?:&[^=&]+)*)', url)
        if match:
            # Get everything after url= until we hit another parameter (like &ct=, &sa=, etc.)
            # We need to find the end of the URL, which is either:
            # 1. Another Google parameter (&ct=, &sa=, &rct=, etc.)
            # 2. End of string
            url_part = url[url.find('url=') + 4:]
            
            # Find where the actual URL ends (before Google's tracking parameters)
            # Common Google tracking parameters
            google_params = ['&ct=', '&sa=', '&rct=', '&cd=', '&usg=', '&ved=', '&q=']
            end_pos = len(url_part)
            
            for param in google_params:
                pos = url_part.find(param)
                if pos != -1 and pos < end_pos:
                    end_pos = pos
            
            actual_url = url_part[:end_pos]
            return unquote(actual_url)
        
        # Fallback: try parse_qs (works for simple cases)
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        if 'url' in params:
            actual_url = params['url'][0]
            return unquote(actual_url)
            
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
