"""
Google Scholar Alerts Analysis - Main Script

This script orchestrates the fetching of Google Scholar Alerts from Gmail and their
categorization using LLMs to determine relevance to mineral exploration ML.
"""

import os
import sys
import argparse
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from gmail_fetcher import GmailAlertFetcher
from llm_categorizer import LLMCategorizer, CategoryDecision, ArticleAnalysis


# Console output formatting constants
TITLE_TRUNCATE_LENGTH = 60
URL_TRUNCATE_LENGTH = 80


class ScholarAlertAnalyzer:
    """Main orchestrator for Google Scholar Alerts analysis."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = None,
        days_back: int = 7,
        max_emails: int = 10,
        days_back_start: int = None
    ):
        """
        Initialize Scholar Alert Analyzer.
        
        Args:
            llm_provider: LLM provider (openai or gemini)
            llm_model: Model name
            days_back: Days to search back for alerts (end of range, closest to now)
            max_emails: Maximum number of emails to process
            days_back_start: Optional start of date range (furthest from now)
        """
        self.days_back = days_back
        self.max_emails = max_emails
        self.days_back_start = days_back_start
        
        # Initialize components
        self.gmail_fetcher = GmailAlertFetcher()
        self.categorizer = LLMCategorizer(provider=llm_provider, model=llm_model)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline.
        
        Returns:
            Dictionary with analysis results
        """
        if self.days_back_start and self.days_back_start > self.days_back:
            print(f"🔍 Fetching Google Scholar Alerts from {self.days_back_start} to {self.days_back} days ago...")
        else:
            print(f"🔍 Fetching Google Scholar Alerts from the last {self.days_back} days...")
        
        # Get alert statistics
        stats = self.gmail_fetcher.get_alert_statistics(
            days_back=self.days_back,
            alert_type='scholar',
            days_back_start=self.days_back_start
        )
        
        if self.days_back_start and self.days_back_start > self.days_back:
            print(f"📊 Google Scholar Alerts statistics ({self.days_back_start} to {self.days_back} days ago):")
        else:
            print(f"📊 Google Scholar Alerts statistics (last {self.days_back} days):")
        print(f"   Total: {stats['total']}")
        print(f"   Unread: {stats['unread']}")
        print(f"   Read: {stats['read']}")
        print()
        
        # Fetch alerts from Gmail
        alerts = self.gmail_fetcher.fetch_scholar_alerts(
            days_back=self.days_back,
            max_results=self.max_emails,
            days_back_start=self.days_back_start
        )
        
        if not alerts:
            print("No alerts found.")
            return {
                'timestamp': datetime.now().isoformat(),
                'total_alerts': 0,
                'relevant_alerts': 0,
                'statistics': stats,
                'results': []
            }
        
        print(f"✅ Processing {len(alerts)} Google Scholar Alerts\n")
        
        # Categorize alerts
        print(f"🤖 Categorizing alerts using {self.categorizer.provider} ({self.categorizer.model})...\n")
        
        results = []
        for i, alert in enumerate(alerts, 1):
            print(f"[{i}/{len(alerts)}] Processing: {alert['alert_query'][:50]}...")
            
            # Log articles found in the alert
            articles = alert.get('articles', [])
            if articles:
                print(f"  📰 Found {len(articles)} article(s) in alert:")
                for j, article in enumerate(articles, 1):
                    title = article.get('title', 'No title')
                    url = article.get('url', 'No URL')
                    print(f"     {j}. {title[:TITLE_TRUNCATE_LENGTH]}")
                    print(f"        URL: {url[:URL_TRUNCATE_LENGTH]}")
            
            decision = self.categorizer.categorize_alert(alert)
            
            result = {
                'alert': alert,
                'decision': decision.model_dump()
            }
            results.append(result)
            
            # Print summary with per-article stats
            relevance_icon = "✅" if decision.is_relevant else "❌"
            print(f"  {relevance_icon} Relevant: {decision.is_relevant} (confidence: {decision.confidence:.2f})")
            print(f"  📊 Articles: {decision.relevant_article_count}/{decision.total_article_count} relevant")
            print(f"  📁 Category: {decision.category}")
            print(f"  📝 Summary: {decision.summary}")
            
            # Log analyzed articles with relevance status
            if decision.articles:
                print(f"  📋 Article Analysis:")
                for j, analyzed_article in enumerate(decision.articles, 1):
                    article_icon = "✅" if analyzed_article.is_relevant else "❌"
                    print(f"     {j}. {article_icon} {analyzed_article.title[:TITLE_TRUNCATE_LENGTH]}")
                    print(f"        {analyzed_article.url[:URL_TRUNCATE_LENGTH]}")
            print()  # Empty line between alerts
        
        # Compile final results
        relevant_count = sum(1 for r in results if r['decision']['is_relevant'])
        
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'llm_provider': self.categorizer.provider,
                'llm_model': self.categorizer.model,
                'days_back': self.days_back,
                'days_back_start': self.days_back_start,
                'max_emails': self.max_emails
            },
            'statistics': stats,
            'total_alerts': len(alerts),
            'relevant_alerts': relevant_count,
            'results': results
        }
        
        return analysis_result
    
    @staticmethod
    def _is_result_relevant(result: Dict[str, Any]) -> bool:
        """Check if a result has at least one relevant article."""
        decision = result.get('decision', {})
        return decision.get('is_relevant', False) and decision.get('relevant_article_count', 0) > 0
    
    def generate_report(self, analysis_result: Dict[str, Any], output_format: str = "markdown") -> str:
        """
        Generate a formatted report of the analysis.
        
        Args:
            analysis_result: Results from analyze()
            output_format: Format (markdown or json)
            
        Returns:
            Formatted report string
        """
        if output_format == "json":
            return json.dumps(analysis_result, indent=2)
        
        # Markdown report
        report_lines = [
            "# Google Scholar Alerts Analysis Report",
            "",
            f"**Generated:** {analysis_result['timestamp']}",
            f"**LLM Provider:** {analysis_result['configuration']['llm_provider']} ({analysis_result['configuration']['llm_model']})",
            f"**Period:** Last {analysis_result['configuration']['days_back']} days",
            "",
            "## Email Statistics",
            "",
            f"- **Total Google Scholar Alerts (in period):** {analysis_result['statistics']['total']}",
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
        
        # Add relevant alerts (only alerts with at least one relevant article)
        relevant_results = [r for r in analysis_result['results'] if self._is_result_relevant(r)]
        
        if relevant_results:
            for i, result in enumerate(relevant_results, 1):
                alert = result['alert']
                decision_data = result['decision']
                
                # Get article stats
                relevant_count = decision_data.get('relevant_article_count', 0)
                total_count = decision_data.get('total_article_count', 0)
                
                report_lines.extend([
                    f"### {i}. {alert['alert_query']}",
                    "",
                    f"**Category:** {decision_data['category']}",
                    f"**Confidence:** {decision_data['confidence']:.2f}",
                    f"**Date:** {alert['date']}",
                    f"**Relevant Articles:** {relevant_count}/{total_count}",
                    "",
                    f"**Summary:** {decision_data['summary']}",
                    "",
                    f"**Keywords:** {', '.join(decision_data.get('keywords', []))}",
                    "",
                    f"**Overall Reasoning:** {decision_data['reasoning']}",
                    ""
                ])

                # Display articles with per-article analysis
                articles = decision_data.get('articles', [])
                if articles:
                    report_lines.append("**Articles:**")
                    report_lines.append("")
                    
                    for j, article in enumerate(articles, 1):
                        title = article.get('title', 'No title')
                        url = article.get('url', '')
                        summary = article.get('summary', '')
                        is_relevant = article.get('is_relevant', False)
                        relevance_reasoning = article.get('relevance_reasoning', '')
                        
                        # Relevance indicator
                        relevance_icon = "✅" if is_relevant else "❌"
                        
                        if url and title and title != 'No title':
                            report_lines.append(f"{j}. {relevance_icon} [{title}]({url})")
                        elif url:
                            report_lines.append(f"{j}. {relevance_icon} {url}")
                        else:
                            report_lines.append(f"{j}. {relevance_icon} {title}")
                        
                        if summary:
                            report_lines.append(f"   - **Summary:** {summary}")
                        if relevance_reasoning:
                            report_lines.append(f"   - **Relevance:** {relevance_reasoning}")
                        report_lines.append("")
                else:
                    # Fallback to raw articles from alert if no analyzed articles
                    report_lines.append("**Articles:**")
                    report_lines.append("")
                    for j, article in enumerate(alert.get('articles', []), 1):
                        title = article.get('title', 'No title')
                        url = article.get('url', '')
                        if url and title and title != 'No title':
                            report_lines.append(f"{j}. [{title}]({url})")
                        elif url:
                            report_lines.append(f"{j}. {url}")
                    report_lines.append("")
                
                report_lines.append("")
        else:
            report_lines.append("*No relevant alerts found.*")
            report_lines.append("")
        
        # Add non-relevant alerts section (alerts with no relevant articles)
        non_relevant_results = [r for r in analysis_result['results'] if not self._is_result_relevant(r)]
        
        if non_relevant_results:
            report_lines.extend([
                "## Non-Relevant Alerts",
                ""
            ])
            
            for i, result in enumerate(non_relevant_results, 1):
                alert = result['alert']
                decision = result['decision']
                total_count = decision.get('total_article_count', 0)
                
                report_lines.extend([
                    f"### {i}. {alert['alert_query']}",
                    f"**Category:** {decision['category']} | **Confidence:** {decision['confidence']:.2f}",
                    f"**Articles Analyzed:** {total_count} (none relevant)",
                    f"**Reasoning:** {decision['reasoning']}",
                    ""
                ])
        
        return "\n".join(report_lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Google Scholar Alerts for mineral exploration ML relevance"
    )
    parser.add_argument(
        '--provider',
        choices=['openai', 'gemini', 'openrouter'],
        default=None,
        help='LLM provider (default: from .env or openai)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=None,
        help='LLM model name (default: gpt-4o-mini for OpenAI, gemini-1.5-flash for Gemini, openai/gpt-4o-mini for OpenRouter)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=None,
        help='Days back to search - end of range, closest to now (default: from .env or 7)'
    )
    parser.add_argument(
        '--days-start',
        type=int,
        default=None,
        help='Optional: Start of date range in days back (furthest from now). Use with --days to create a range. Example: --days-start 280 --days 250 searches emails from 280 to 250 days ago'
    )
    parser.add_argument(
        '--max-emails',
        type=int,
        default=None,
        help='Maximum emails to process (default: from .env or 10)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='scholar_report.md',
        help='Output file path (default: scholar_report.md)'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Start date in YYYY-MM-DD format (overrides days_back)'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='End date in YYYY-MM-DD format'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration from args or env
    llm_provider = args.provider or os.getenv('LLM_PROVIDER', 'openai')
    llm_model = args.model or os.getenv('LLM_MODEL')
    days_back = args.days or int(os.getenv('DAYS_BACK', '7'))
    days_back_start = args.days_start or (int(os.getenv('DAYS_BACK_START')) if os.getenv('DAYS_BACK_START') else None)
    max_emails = args.max_emails or int(os.getenv('MAX_EMAILS_TO_PROCESS', '10'))
    
    try:
        # Initialize analyzer
        analyzer = ScholarAlertAnalyzer(
            llm_provider=llm_provider,
            llm_model=llm_model,
            days_back=days_back,
            days_back_start=days_back_start,
            max_emails=max_emails
        )
        
        # Run analysis
        results = analyzer.analyze()
        
        # Generate report
        print(f"\n📊 Generating report...")
        report = analyzer.generate_report(results, output_format=args.format)
        
        # Save report
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Report saved to: {args.output}")
        
        # Always save machine-readable JSON report (unless already saved)
        # Normalize paths to handle './scholar_report.json', '../scholar_report.json', etc.
        output_path = os.path.abspath(args.output)
        report_json_path = os.path.abspath('scholar_report.json')
        
        if not (output_path == report_json_path and args.format == 'json'):
            try:
                # Reuse existing JSON report if available, otherwise generate it
                json_report = report if args.format == 'json' else analyzer.generate_report(results, output_format='json')
                with open('scholar_report.json', 'w', encoding='utf-8') as f:
                    f.write(json_report)
                print(f"✅ Machine-readable report saved to: scholar_report.json")
            except (IOError, OSError) as e:
                print(f"⚠️  Warning: Could not save scholar_report.json: {e}")
        
        print(f"\n📈 Summary: {results['relevant_alerts']}/{results['total_alerts']} alerts relevant")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("\nPlease ensure you have:")
        print("1. Created a .env file with API keys (see .env.example)")
        print("2. Downloaded credentials.json from Google Cloud Console")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
