#!/usr/bin/env python3
"""
Article List Generator - Helper Script

This script reads the default JSON outputs from Google Alerts and Google Scholar analysis
and generates a chronological list of articles with summaries and URLs.
"""

import json
import argparse
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class Article:
    """Data class to hold article information."""
    
    def __init__(
        self,
        title: str,
        url: str,
        summary: str,
        date: str,
        source: str,
        alert_query: str,
        is_relevant: bool,
        relevance_reasoning: str = ""
    ):
        self.title = title
        self.url = url
        self.summary = summary
        self.date = date
        self.source = source  # 'google_alerts' or 'scholar_alerts'
        self.alert_query = alert_query
        self.is_relevant = is_relevant
        self.relevance_reasoning = relevance_reasoning
    
    def get_date_for_sorting(self) -> datetime:
        """Convert date string to datetime for sorting."""
        try:
            # Try common date formats
            for fmt in [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S.%f',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%dT%H:%M:%S.%f%z'
            ]:
                try:
                    return datetime.strptime(self.date.split('+')[0].split('Z')[0], fmt)
                except ValueError:
                    continue
            # If all formats fail, return epoch time
            return datetime.fromtimestamp(0)
        except Exception:
            return datetime.fromtimestamp(0)
    
    def __repr__(self):
        return f"Article(title={self.title[:30]}..., date={self.date}, source={self.source})"


def parse_report_json(file_path: str, source_type: str) -> List[Article]:
    """
    Parse a report JSON file and extract all articles.
    
    Args:
        file_path: Path to the JSON report file
        source_type: Either 'google_alerts' or 'scholar_alerts'
        
    Returns:
        List of Article objects
    """
    articles = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Warning: File not found: {file_path}")
        return articles
    except json.JSONDecodeError as e:
        print(f"⚠️  Warning: Invalid JSON in {file_path}: {e}")
        return articles
    
    # Extract articles from results
    results = data.get('results', [])
    
    for result in results:
        alert = result.get('alert', {})
        decision = result.get('decision', {})
        
        alert_query = alert.get('alert_query', 'Unknown Query')
        alert_date = alert.get('date', 'Unknown Date')
        
        # Get analyzed articles from decision
        analyzed_articles = decision.get('articles', [])
        
        if analyzed_articles:
            # Use the per-article analysis
            for article_data in analyzed_articles:
                article = Article(
                    title=article_data.get('title', 'No Title'),
                    url=article_data.get('url', ''),
                    summary=article_data.get('summary', ''),
                    date=alert_date,
                    source=source_type,
                    alert_query=alert_query,
                    is_relevant=article_data.get('is_relevant', False),
                    relevance_reasoning=article_data.get('relevance_reasoning', '')
                )
                articles.append(article)
        else:
            # Fallback to raw articles from alert (older format)
            raw_articles = alert.get('articles', [])
            for article_data in raw_articles:
                article = Article(
                    title=article_data.get('title', 'No Title'),
                    url=article_data.get('url', ''),
                    summary=article_data.get('snippet', ''),
                    date=alert_date,
                    source=source_type,
                    alert_query=alert_query,
                    is_relevant=decision.get('is_relevant', False),
                    relevance_reasoning=decision.get('reasoning', '')
                )
                articles.append(article)
    
    return articles


def format_article_list(
    articles: List[Article],
    format_type: str = 'text',
    show_irrelevant: bool = False
) -> str:
    """
    Format the article list for display.
    
    Args:
        articles: List of Article objects
        format_type: 'text', 'markdown', or 'json'
        show_irrelevant: Whether to include non-relevant articles
        
    Returns:
        Formatted string
    """
    if not articles:
        return "No articles found.\n"
    
    # Filter by relevance if requested
    if not show_irrelevant:
        articles = [a for a in articles if a.is_relevant]
    
    # Sort by date (newest first)
    articles.sort(key=lambda x: x.get_date_for_sorting(), reverse=True)
    
    if format_type == 'json':
        # JSON output
        article_dicts = []
        for article in articles:
            article_dicts.append({
                'title': article.title,
                'url': article.url,
                'summary': article.summary,
                'date': article.date,
                'source': article.source,
                'alert_query': article.alert_query,
                'is_relevant': article.is_relevant,
                'relevance_reasoning': article.relevance_reasoning
            })
        return json.dumps(article_dicts, indent=2, ensure_ascii=False)
    
    elif format_type == 'markdown':
        # Markdown output
        lines = [
            "# Chronological Article List",
            "",
            f"**Total Articles:** {len(articles)}",
            ""
        ]
        
        for i, article in enumerate(articles, 1):
            relevance_icon = "✅" if article.is_relevant else "❌"
            source_label = "🔍 Google Alert" if article.source == 'google_alerts' else "🎓 Scholar Alert"
            
            lines.extend([
                f"## {i}. {article.title}",
                "",
                f"{relevance_icon} **Relevant:** {article.is_relevant}",
                f"{source_label} | **Date:** {article.date}",
                f"**Alert Query:** {article.alert_query}",
                "",
                f"**URL:** {article.url}",
                ""
            ])
            
            if article.summary:
                lines.extend([
                    f"**Summary:** {article.summary}",
                    ""
                ])
            
            if article.relevance_reasoning:
                lines.extend([
                    f"**Relevance:** {article.relevance_reasoning}",
                    ""
                ])
            
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    else:
        # Plain text output
        lines = [
            "=" * 80,
            "CHRONOLOGICAL ARTICLE LIST",
            "=" * 80,
            f"Total Articles: {len(articles)}",
            "=" * 80,
            ""
        ]
        
        for i, article in enumerate(articles, 1):
            relevance_icon = "✅" if article.is_relevant else "❌"
            source_label = "[Google Alert]" if article.source == 'google_alerts' else "[Scholar Alert]"
            
            lines.extend([
                f"{i}. {relevance_icon} {article.title}",
                f"   {source_label} | Date: {article.date}",
                f"   Alert Query: {article.alert_query}",
                f"   URL: {article.url}"
            ])
            
            if article.summary:
                lines.append(f"   Summary: {article.summary}")
            
            if article.relevance_reasoning:
                lines.append(f"   Relevance: {article.relevance_reasoning}")
            
            lines.append("")
            lines.append("-" * 80)
            lines.append("")
        
        return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate chronological list of articles from analysis reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List relevant articles from both sources
  python list_articles.py
  
  # Include non-relevant articles
  python list_articles.py --show-all
  
  # Output in markdown format
  python list_articles.py --format markdown --output articles.md
  
  # Only show Google Alerts (not Scholar)
  python list_articles.py --google-alerts-only
  
  # Only show Scholar Alerts
  python list_articles.py --scholar-alerts-only
  
  # Custom input files
  python list_articles.py --google-alerts my_report.json --scholar-alerts my_scholar.json
        """
    )
    
    parser.add_argument(
        '--google-alerts',
        type=str,
        default='report.json',
        help='Path to Google Alerts JSON report (default: report.json)'
    )
    parser.add_argument(
        '--scholar-alerts',
        type=str,
        default='scholar_report.json',
        help='Path to Google Scholar Alerts JSON report (default: scholar_report.json)'
    )
    parser.add_argument(
        '--google-alerts-only',
        action='store_true',
        help='Only show articles from Google Alerts'
    )
    parser.add_argument(
        '--scholar-alerts-only',
        action='store_true',
        help='Only show articles from Scholar Alerts'
    )
    parser.add_argument(
        '--format',
        choices=['text', 'markdown', 'json'],
        default='text',
        help='Output format (default: text)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Output file path (default: print to stdout)'
    )
    parser.add_argument(
        '--show-all',
        action='store_true',
        help='Show both relevant and non-relevant articles'
    )
    parser.add_argument(
        '--separate',
        action='store_true',
        help='Generate separate outputs for each source (requires --output with extension)'
    )
    
    args = parser.parse_args()
    
    # Collect articles
    all_articles = []
    google_articles = []
    scholar_articles = []
    
    # Parse Google Alerts
    if not args.scholar_alerts_only:
        if Path(args.google_alerts).exists():
            print(f"📖 Reading Google Alerts from: {args.google_alerts}")
            google_articles = parse_report_json(args.google_alerts, 'google_alerts')
            all_articles.extend(google_articles)
            print(f"   Found {len(google_articles)} articles")
        else:
            print(f"⚠️  Google Alerts file not found: {args.google_alerts}")
    
    # Parse Scholar Alerts
    if not args.google_alerts_only:
        if Path(args.scholar_alerts).exists():
            print(f"📖 Reading Scholar Alerts from: {args.scholar_alerts}")
            scholar_articles = parse_report_json(args.scholar_alerts, 'scholar_alerts')
            all_articles.extend(scholar_articles)
            print(f"   Found {len(scholar_articles)} articles")
        else:
            print(f"⚠️  Scholar Alerts file not found: {args.scholar_alerts}")
    
    if not all_articles:
        print("\n❌ No articles found in any report files.")
        print("\nPlease ensure you have run:")
        print("  python analyze_alerts.py")
        print("  python analyze_scholar_alerts.py")
        return 1
    
    print(f"\n✅ Total articles collected: {len(all_articles)}")
    
    # Generate output
    if args.separate and args.output:
        # Generate separate outputs
        output_path = Path(args.output)
        stem = output_path.stem
        suffix = output_path.suffix
        parent = output_path.parent
        
        if google_articles:
            google_output = parent / f"{stem}_google{suffix}"
            google_content = format_article_list(google_articles, args.format, args.show_all)
            with open(google_output, 'w', encoding='utf-8') as f:
                f.write(google_content)
            print(f"✅ Google Alerts articles saved to: {google_output}")
        
        if scholar_articles:
            scholar_output = parent / f"{stem}_scholar{suffix}"
            scholar_content = format_article_list(scholar_articles, args.format, args.show_all)
            with open(scholar_output, 'w', encoding='utf-8') as f:
                f.write(scholar_content)
            print(f"✅ Scholar Alerts articles saved to: {scholar_output}")
    else:
        # Generate combined output
        output = format_article_list(all_articles, args.format, args.show_all)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"✅ Articles saved to: {args.output}")
        else:
            print("\n" + "=" * 80)
            print(output)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
