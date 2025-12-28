"""
Test script to verify Google Scholar alert URL parsing.
This validates the fix for Scholar redirect URL extraction.
"""

import re
from url_utils import extract_actual_url, is_excluded_domain


def test_scholar_url_extraction():
    """Test that Scholar URLs are correctly extracted."""
    test_cases = [
        # (input_url, expected_output, should_be_excluded)
        (
            "https://scholar.google.com/scholar_url?url=https://arxiv.org/abs/2312.12345",
            "https://arxiv.org/abs/2312.12345",
            False
        ),
        (
            "https://scholar.googleusercontent.com/scholar?q=cache:abc&url=https://www.nature.com/articles/s41586-023-12345",
            "https://www.nature.com/articles/s41586-023-12345",
            False
        ),
        (
            "https://www.google.com/url?url=https://example.com/article&ct=ga",
            "https://example.com/article",
            False
        ),
        (
            "https://direct-article-url.com/paper",
            "https://direct-article-url.com/paper",
            False
        ),
        (
            "https://scholar.google.com/citations?user=abc123",
            "https://scholar.google.com/citations?user=abc123",
            True  # Should be excluded as it's not an article
        ),
    ]
    
    print("Testing Scholar URL extraction...")
    print("=" * 70)
    
    all_passed = True
    for i, (input_url, expected, should_exclude) in enumerate(test_cases, 1):
        actual = extract_actual_url(input_url)
        excluded = is_excluded_domain(actual)
        
        passed = (actual == expected) and (excluded == should_exclude)
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"\nTest {i}: {status}")
        print(f"  Input:    {input_url[:60]}...")
        print(f"  Expected: {expected}")
        print(f"  Actual:   {actual}")
        print(f"  Excluded: {excluded} (expected: {should_exclude})")
        
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


def test_scholar_alert_parsing():
    """Test parsing of a complete Scholar alert email."""
    # Simulate Scholar alert HTML structure
    mock_scholar_html = """
    <html>
    <body>
    <table>
    <tr>
    <td>
    <h3><a href="https://scholar.google.com/scholar_url?url=https://arxiv.org/abs/2401.12345">
    Machine Learning for Mineral Exploration: A Comprehensive Review
    </a></h3>
    <div>J Doe, A Smith - arXiv preprint arXiv:2401.12345, 2024</div>
    <div>This paper presents a comprehensive review of machine learning techniques...</div>
    </td>
    </tr>
    <tr>
    <td>
    <h3><a href="https://scholar.google.com/scholar_url?url=https://www.sciencedirect.com/science/article/pii/S0169136824000123">
    Deep Learning for Geophysical Data Analysis
    </a></h3>
    <div>B Johnson - Journal of Applied Geophysics, 2024</div>
    <div>We propose a novel deep learning approach for analyzing geophysical data...</div>
    </td>
    </tr>
    <tr>
    <td>
    <a href="https://scholar.google.com/citations?view_op=view_citation">View citation</a>
    </td>
    </tr>
    </table>
    </body>
    </html>
    """
    
    print("\n\nTesting Scholar alert HTML parsing...")
    print("=" * 70)
    
    # Extract links
    link_pattern = re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.DOTALL)
    matches = link_pattern.findall(mock_scholar_html)
    
    articles = []
    for url, content in matches:
        # Extract actual URL
        actual_url = extract_actual_url(url)
        
        # Check if it's an article (not excluded)
        if actual_url.startswith('http') and not is_excluded_domain(actual_url):
            # Extract title (simple text extraction)
            title = re.sub(r'<[^>]+>', '', content).strip()
            if title:
                articles.append({
                    'title': title,
                    'url': actual_url
                })
    
    print(f"\nExtracted {len(articles)} article(s):")
    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['title'][:60]}")
        print(f"   {article['url']}")
    
    print("\n" + "=" * 70)
    
    # Verify we got the right articles
    expected_count = 2
    if len(articles) == expected_count:
        print(f"✅ Correctly extracted {expected_count} articles")
        return True
    else:
        print(f"❌ Expected {expected_count} articles, got {len(articles)}")
        return False


if __name__ == '__main__':
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Google Scholar URL Parsing Tests" + " " * 20 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    test1_passed = test_scholar_url_extraction()
    test2_passed = test_scholar_alert_parsing()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"URL Extraction Tests: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"HTML Parsing Tests:   {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print()
    
    if test1_passed and test2_passed:
        print("🎉 All tests passed! Scholar URL extraction is working correctly.")
        exit(0)
    else:
        print("❌ Some tests failed. Please review the output above.")
        exit(1)
