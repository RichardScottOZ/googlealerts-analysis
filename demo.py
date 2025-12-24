"""
Example/Demo Script

This script demonstrates the Google Alerts Analysis system with mock data.
Run this to see how the system works without needing Gmail/API setup.
"""

import json
from datetime import datetime
from llm_categorizer import CategoryDecision


def create_mock_alerts():
    """Create mock Google Alert data for demonstration."""
    return [
        {
            'alert_query': 'machine learning mineral exploration',
            'date': 'Mon, 18 Dec 2024 10:30:00 +0000',
            'message_id': 'mock_001',
            'articles': [
                {
                    'title': 'AI-Powered Copper Discovery in Chile Using Deep Learning',
                    'url': 'https://example.com/ai-copper-discovery',
                    'snippet': 'Researchers developed new deep learning algorithms that improved copper deposit prediction accuracy by 40%...'
                },
                {
                    'title': 'Neural Networks Transform Mineral Exploration',
                    'url': 'https://example.com/neural-networks-exploration',
                    'snippet': 'Mining companies are adopting ML techniques for geological mapping and target generation...'
                }
            ],
            'full_body': 'Sample email body content...'
        },
        {
            'alert_query': 'remote sensing geology',
            'date': 'Tue, 19 Dec 2024 09:15:00 +0000',
            'message_id': 'mock_002',
            'articles': [
                {
                    'title': 'Satellite Imagery Analysis for Gold Exploration',
                    'url': 'https://example.com/satellite-gold',
                    'snippet': 'New hyperspectral remote sensing techniques identify alteration zones indicative of gold mineralization...'
                }
            ],
            'full_body': 'Sample email body content...'
        },
        {
            'alert_query': 'bitcoin mining news',
            'date': 'Wed, 20 Dec 2024 14:20:00 +0000',
            'message_id': 'mock_003',
            'articles': [
                {
                    'title': 'Bitcoin Price Surges to New High',
                    'url': 'https://example.com/bitcoin-price',
                    'snippet': 'Cryptocurrency markets see significant gains as Bitcoin mining difficulty increases...'
                }
            ],
            'full_body': 'Sample email body content...'
        }
    ]


def create_mock_decisions():
    """Create mock categorization decisions."""
    return [
        CategoryDecision(
            is_relevant=True,
            confidence=0.92,
            category="Machine Learning - Exploration",
            reasoning="Directly discusses deep learning applications in copper deposit prediction and ML for geological mapping, which are core topics for the repository.",
            summary="AI and deep learning techniques show significant improvements in copper discovery and geological mapping for mineral exploration.",
            keywords=["machine learning", "deep learning", "copper", "exploration", "geological mapping"]
        ),
        CategoryDecision(
            is_relevant=True,
            confidence=0.85,
            category="Remote Sensing",
            reasoning="Remote sensing and hyperspectral analysis are important ML application areas in mineral exploration, directly relevant to repository topics.",
            summary="Hyperspectral remote sensing techniques using satellite imagery for identifying gold mineralization zones.",
            keywords=["remote sensing", "hyperspectral", "satellite", "gold", "exploration"]
        ),
        CategoryDecision(
            is_relevant=False,
            confidence=0.95,
            category="Not Relevant - Cryptocurrency",
            reasoning="This is about cryptocurrency Bitcoin mining, not physical mineral exploration. Despite the word 'mining', it's completely unrelated to geological or mineral exploration.",
            summary="Bitcoin cryptocurrency price movements and blockchain mining difficulty.",
            keywords=["bitcoin", "cryptocurrency", "blockchain"]
        )
    ]


def generate_demo_report():
    """Generate a demonstration report."""
    alerts = create_mock_alerts()
    decisions = create_mock_decisions()
    
    # Create results
    results = []
    for alert, decision in zip(alerts, decisions):
        results.append({
            'alert': alert,
            'decision': decision.model_dump()
        })
    
    # Create analysis result
    analysis_result = {
        'timestamp': datetime.now().isoformat(),
        'configuration': {
            'llm_provider': 'openai (demo mode)',
            'llm_model': 'gpt-4o-mini',
            'days_back': 7,
            'max_emails': 10
        },
        'statistics': {
            'total': 15,
            'unread': 5,
            'read': 10
        },
        'total_alerts': len(alerts),
        'relevant_alerts': sum(1 for d in decisions if d.is_relevant),
        'results': results
    }
    
    return analysis_result


def generate_demo_markdown_report(analysis_result):
    """Generate markdown report from demo data."""
    report_lines = [
        "# Google Alerts Analysis Report (DEMO)",
        "",
        f"**Generated:** {analysis_result['timestamp']}",
        f"**LLM Provider:** {analysis_result['configuration']['llm_provider']}",
        f"**Period:** Last {analysis_result['configuration']['days_back']} days",
        "",
        "## Email Statistics",
        "",
        f"- **Total Google Alerts (in period):** {analysis_result['statistics']['total']}",
        f"- **Unread:** {analysis_result['statistics']['unread']}",
        f"- **Read:** {analysis_result['statistics']['read']}",
        "",
        "## Analysis Summary",
        "",
        f"- **Alerts Processed:** {analysis_result['total_alerts']}",
        f"- **Relevant to mineral-exploration-machine-learning:** {analysis_result['relevant_alerts']}",
        f"- **Relevance Rate:** {(analysis_result['relevant_alerts'] / max(analysis_result['total_alerts'], 1) * 100):.1f}%",
        "",
        "## Relevant Alerts",
        ""
    ]
    
    # Add relevant alerts
    relevant_results = [r for r in analysis_result['results'] if r['decision']['is_relevant']]
    
    if relevant_results:
        for i, result in enumerate(relevant_results, 1):
            alert = result['alert']
            decision = result['decision']
            
            report_lines.extend([
                f"### {i}. {alert['alert_query']}",
                "",
                f"**Category:** {decision['category']}  ",
                f"**Confidence:** {decision['confidence']:.2f}  ",
                f"**Date:** {alert['date']}",
                "",
                f"**Summary:** {decision['summary']}",
                "",
                f"**Keywords:** {', '.join(decision['keywords'])}",
                "",
                f"**Reasoning:** {decision['reasoning']}",
                "",
                "**Articles:**",
                ""
            ])
            
            for j, article in enumerate(alert['articles'], 1):
                title = article.get('title', 'No title')
                url = article.get('url', '')
                if url and title and title != 'No title':
                    report_lines.append(f"{j}. [{title}]({url})")
                elif url:
                    report_lines.append(f"{j}. {url}")
            
            report_lines.append("")
    
    # Add non-relevant alerts section
    non_relevant_results = [r for r in analysis_result['results'] if not r['decision']['is_relevant']]
    
    if non_relevant_results:
        report_lines.extend([
            "## Non-Relevant Alerts",
            ""
        ])
        
        for i, result in enumerate(non_relevant_results, 1):
            alert = result['alert']
            decision = result['decision']
            
            report_lines.extend([
                f"### {i}. {alert['alert_query']}",
                f"**Category:** {decision['category']} | **Confidence:** {decision['confidence']:.2f}  ",
                f"**Reasoning:** {decision['reasoning']}",
                ""
            ])
    
    report_lines.extend([
        "---",
        "",
        "*This is a demonstration report with mock data. Run `python analyze_alerts.py` with real Gmail API setup to analyze actual Google Alerts.*"
    ])
    
    return "\n".join(report_lines)


def main():
    """Run the demo."""
    print("=" * 70)
    print("Google Alerts Analysis - DEMONSTRATION MODE")
    print("=" * 70)
    print()
    print("This demo shows how the system works with mock data.")
    print("To analyze real alerts, set up Gmail API and run analyze_alerts.py")
    print()
    
    print("🔍 Generating demo alerts...")
    analysis_result = generate_demo_report()
    
    print(f"✅ Generated {analysis_result['total_alerts']} mock alerts\n")
    print("🤖 Mock categorization results:\n")
    
    # Print summary for each alert
    for i, result in enumerate(analysis_result['results'], 1):
        alert = result['alert']
        decision = result['decision']
        
        relevance_icon = "✅" if decision['is_relevant'] else "❌"
        print(f"[{i}/{analysis_result['total_alerts']}] {alert['alert_query']}")
        print(f"  {relevance_icon} Relevant: {decision['is_relevant']} (confidence: {decision['confidence']:.2f})")
        print(f"  📁 Category: {decision['category']}")
        print(f"  📝 Summary: {decision['summary']}")
        print()
    
    # Generate reports
    print("📊 Generating demo reports...\n")
    
    # Markdown report
    markdown_report = generate_demo_markdown_report(analysis_result)
    with open('demo_report.md', 'w') as f:
        f.write(markdown_report)
    print("✅ Markdown report saved to: demo_report.md")
    
    # JSON report
    with open('demo_report.json', 'w') as f:
        json.dump(analysis_result, f, indent=2)
    print("✅ JSON report saved to: demo_report.json")
    
    print()
    print(f"📈 Demo Summary: {analysis_result['relevant_alerts']}/{analysis_result['total_alerts']} alerts relevant")
    print()
    print("=" * 70)
    print("Next Steps:")
    print("1. Review demo_report.md to see the report format")
    print("2. Set up real Gmail API access (see SETUP.md)")
    print("3. Run: python analyze_alerts.py")
    print("=" * 70)


if __name__ == '__main__':
    main()
