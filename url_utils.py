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
    
    Google Scholar Alert emails use redirect URLs like:
    https://scholar.google.com/scholar_url?url=<actual_url>&...
    https://scholar.googleusercontent.com/scholar?...&url=<actual_url>&...
    
    Note: Google properly URL-encodes the destination URL in the 'url' parameter,
    so parse_qs handles it correctly even when the destination URL contains
    query parameters with & characters.
    
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
        parsed = urlparse(url)
        
        # Use parse_qs - it handles URL-encoded parameters correctly
        # Google properly encodes the 'url' parameter, so this works for URLs
        # with query parameters, special characters, etc.
        params = parse_qs(parsed.query, keep_blank_values=True)
        
        if 'url' in params and params['url']:
            actual_url = params['url'][0]
            return unquote(actual_url)
        
        # Fallback: Manual regex extraction for edge cases where parse_qs fails
        # This pattern matches url= followed by content until we hit a known Google parameter
        # Pattern looks for &param= where param doesn't contain 'url' to avoid false matches
        match = re.search(r'[?&]url=([^&]+(?:&(?!ct=|sa=|rct=|cd=|usg=|ved=|q=)[^&]+)*)', url)
        if match:
            actual_url = match.group(1)
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
