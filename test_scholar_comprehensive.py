"""
Comprehensive test for Google Scholar alert parsing with various HTML formats.
"""

import re
from url_utils import extract_actual_url, is_excluded_domain


def test_scholar_html_variations():
    """Test various real-world Scholar alert HTML structures."""
    
    test_cases = [
        # Test case 1: Standard Scholar alert with h3 tags
        {
            'name': 'Standard h3 format',
            'html': '''
                <h3>
                    <a href="https://scholar.google.com/scholar_url?url=https://www.mdpi.com/2076-3417/14/1/123">
                        Deep Learning Applications in Mineral Exploration
                    </a>
                </h3>
            ''',
            'expected_urls': ['https://www.mdpi.com/2076-3417/14/1/123']
        },
        # Test case 2: Multiple articles with different URL formats
        {
            'name': 'Multiple articles',
            'html': '''
                <div>
                    <h3><a href="https://scholar.google.com/scholar_url?url=https://arxiv.org/abs/2401.01234">Article 1</a></h3>
                    <h3><a href="https://scholar.google.com/scholar_url?url=https://doi.org/10.1234/example.2024.01">Article 2</a></h3>
                    <a href="https://scholar.google.com/citations">View citations</a>
                </div>
            ''',
            'expected_urls': [
                'https://arxiv.org/abs/2401.01234',
                'https://doi.org/10.1234/example.2024.01'
            ]
        },
        # Test case 3: Scholar with HTML entities and encoded URLs
        {
            'name': 'Encoded URLs',
            'html': '''
                <a href="https://scholar.google.com/scholar_url?url=https%3A%2F%2Fwww.nature.com%2Farticles%2Fs41598-024-12345-6">
                    Encoded URL Article
                </a>
            ''',
            'expected_urls': ['https://www.nature.com/articles/s41598-024-12345-6']
        },
        # Test case 4: Mixed regular and Scholar URLs
        {
            'name': 'Mixed Google and Scholar URLs',
            'html': '''
                <div>
                    <a href="https://www.google.com/url?url=https://example.com/regular-alert">Regular Alert</a>
                    <a href="https://scholar.google.com/scholar_url?url=https://sciencedirect.com/scholar-article">Scholar Alert</a>
                </div>
            ''',
            'expected_urls': [
                'https://example.com/regular-alert',
                'https://sciencedirect.com/scholar-article'
            ]
        },
        # Test case 5: Scholar with nested HTML
        {
            'name': 'Nested HTML structure',
            'html': '''
                <table>
                    <tr>
                        <td>
                            <div>
                                <h3>
                                    <a href="https://scholar.google.com/scholar_url?url=https://journals.sagepub.com/article123">
                                        <div><b>Machine Learning in Geoscience</b></div>
                                    </a>
                                </h3>
                            </div>
                        </td>
                    </tr>
                </table>
            ''',
            'expected_urls': ['https://journals.sagepub.com/article123']
        },
    ]
    
    print("\n\nTesting Scholar HTML Variations...")
    print("=" * 70)
    
    all_passed = True
    link_pattern = re.compile(r'<a[^>]+href=["\']([^"\']+)["\']', re.DOTALL)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print("-" * 70)
        
        # Extract all hrefs
        urls = link_pattern.findall(test_case['html'])
        
        # Process URLs
        extracted_urls = []
        for url in urls:
            actual_url = extract_actual_url(url)
            if actual_url.startswith('http') and not is_excluded_domain(actual_url):
                extracted_urls.append(actual_url)
        
        # Check results
        expected = test_case['expected_urls']
        passed = set(extracted_urls) == set(expected)
        
        print(f"  Expected {len(expected)} URL(s), got {len(extracted_urls)}")
        for j, url in enumerate(extracted_urls, 1):
            status = "✅" if url in expected else "❌"
            print(f"    {status} {j}. {url[:60]}...")
        
        if not passed:
            print(f"  ❌ FAILED")
            if set(extracted_urls) != set(expected):
                missing = set(expected) - set(extracted_urls)
                extra = set(extracted_urls) - set(expected)
                if missing:
                    print(f"     Missing: {missing}")
                if extra:
                    print(f"     Extra: {extra}")
            all_passed = False
        else:
            print(f"  ✅ PASSED")
    
    print("\n" + "=" * 70)
    return all_passed


def test_edge_cases():
    """Test edge cases and potential issues."""
    
    print("\n\nTesting Edge Cases...")
    print("=" * 70)
    
    edge_cases = [
        {
            'name': 'URL with multiple parameters (URL-encoded, as Google does it)',
            'url': 'https://scholar.google.com/scholar_url?url=https%3A%2F%2Fexample.com%2Farticle%3Fid%3D123%26param%3Dvalue&ct=ga',
            'expected': 'https://example.com/article?id=123&param=value',
            'should_exclude': False
        },
        {
            'name': 'Scholar URL without url parameter',
            'url': 'https://scholar.google.com/scholar?q=search+terms',
            'expected': 'https://scholar.google.com/scholar?q=search+terms',
            'should_exclude': True
        },
        {
            'name': 'Empty URL',
            'url': '',
            'expected': '',
            'should_exclude': False
        },
        {
            'name': 'Non-http URL',
            'url': 'ftp://example.com/file',
            'expected': 'ftp://example.com/file',
            'should_exclude': False
        },
        {
            'name': 'Scholar with special characters in URL',
            'url': 'https://scholar.google.com/scholar_url?url=https://example.com/article%20with%20spaces',
            'expected': 'https://example.com/article with spaces',
            'should_exclude': False
        },
    ]
    
    all_passed = True
    for i, test in enumerate(edge_cases, 1):
        if test['url']:
            actual = extract_actual_url(test['url'])
            excluded = is_excluded_domain(actual) if actual.startswith('http') else False
        else:
            actual = test['url']
            excluded = False
        
        passed = (actual == test['expected']) and (excluded == test['should_exclude'])
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"\nTest {i}: {test['name']} - {status}")
        if not passed:
            print(f"  Expected: {test['expected']}")
            print(f"  Actual:   {actual}")
            print(f"  Excluded: {excluded} (expected: {test['should_exclude']})")
            all_passed = False
    
    print("\n" + "=" * 70)
    return all_passed


if __name__ == '__main__':
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 10 + "Comprehensive Google Scholar Parsing Tests" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")
    
    test1_passed = test_scholar_html_variations()
    test2_passed = test_edge_cases()
    
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"HTML Variations Tests: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Edge Cases Tests:      {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print()
    
    if test1_passed and test2_passed:
        print("🎉 All comprehensive tests passed!")
        print("   Scholar URL parsing is robust and production-ready.")
        exit(0)
    else:
        print("❌ Some tests failed. Please review the output above.")
        exit(1)
