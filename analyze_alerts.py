"""
Google Alerts Analysis - Main Script

This script orchestrates the fetching of Google Alerts from Gmail and their
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
from llm_categorizer import LLMCategorizer, CategoryDecision


class AlertAnalyzer:
    """Main orchestrator for Google Alerts analysis."""
    
    def __init__(
        self,
        llm_provider: str = "openai",
        llm_model: str = None,
        days_back: int = 7,
        max_emails: int = 10
    ):
        """
        Initialize Alert Analyzer.
        
        Args:
            llm_provider: LLM provider (openai or gemini)
            llm_model: Model name
            days_back: Days to search back for alerts
            max_emails: Maximum number of emails to process
        """
        self.days_back = days_back
        self.max_emails = max_emails
        
        # Initialize components
        self.gmail_fetcher = GmailAlertFetcher()
        self.categorizer = LLMCategorizer(provider=llm_provider, model=llm_model)
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run the complete analysis pipeline.
        
        Returns:
            Dictionary with analysis results
        """
        print(f"🔍 Fetching Google Alerts from the last {self.days_back} days...")
        
        # Fetch alerts from Gmail
        alerts = self.gmail_fetcher.fetch_google_alerts(
            days_back=self.days_back,
            max_results=self.max_emails
        )
        
        if not alerts:
            print("No alerts found.")
            return {
                'timestamp': datetime.now().isoformat(),
                'total_alerts': 0,
                'relevant_alerts': 0,
                'results': []
            }
        
        print(f"✅ Found {len(alerts)} Google Alerts\n")
        
        # Categorize alerts
        print(f"🤖 Categorizing alerts using {self.categorizer.provider} ({self.categorizer.model})...\n")
        
        results = []
        for i, alert in enumerate(alerts, 1):
            print(f"[{i}/{len(alerts)}] Processing: {alert['alert_query'][:50]}...")
            
            decision = self.categorizer.categorize_alert(alert)
            
            result = {
                'alert': alert,
                'decision': decision.model_dump()
            }
            results.append(result)
            
            # Print summary
            relevance_icon = "✅" if decision.is_relevant else "❌"
            print(f"  {relevance_icon} Relevant: {decision.is_relevant} (confidence: {decision.confidence:.2f})")
            print(f"  📁 Category: {decision.category}")
            print(f"  📝 Summary: {decision.summary}\n")
        
        # Compile final results
        relevant_count = sum(1 for r in results if r['decision']['is_relevant'])
        
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'configuration': {
                'llm_provider': self.categorizer.provider,
                'llm_model': self.categorizer.model,
                'days_back': self.days_back,
                'max_emails': self.max_emails
            },
            'total_alerts': len(alerts),
            'relevant_alerts': relevant_count,
            'results': results
        }
        
        return analysis_result
    
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
            "# Google Alerts Analysis Report",
            "",
            f"**Generated:** {analysis_result['timestamp']}",
            f"**LLM Provider:** {analysis_result['configuration']['llm_provider']} ({analysis_result['configuration']['llm_model']})",
            f"**Period:** Last {analysis_result['configuration']['days_back']} days",
            "",
            "## Summary",
            "",
            f"- **Total Alerts Processed:** {analysis_result['total_alerts']}",
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
                    f"**Category:** {decision['category']}",
                    f"**Confidence:** {decision['confidence']:.2f}",
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
        else:
            report_lines.append("*No relevant alerts found.*")
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
                    f"**Category:** {decision['category']} | **Confidence:** {decision['confidence']:.2f}",
                    f"**Reasoning:** {decision['reasoning']}",
                    ""
                ])
        
        return "\n".join(report_lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze Google Alerts for mineral exploration ML relevance"
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
        help='Days back to search (default: from .env or 7)'
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
        default='report.md',
        help='Output file path (default: report.md)'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration from args or env
    llm_provider = args.provider or os.getenv('LLM_PROVIDER', 'openai')
    llm_model = args.model or os.getenv('LLM_MODEL')
    days_back = args.days or int(os.getenv('DAYS_BACK', '7'))
    max_emails = args.max_emails or int(os.getenv('MAX_EMAILS_TO_PROCESS', '10'))
    
    try:
        # Initialize analyzer
        analyzer = AlertAnalyzer(
            llm_provider=llm_provider,
            llm_model=llm_model,
            days_back=days_back,
            max_emails=max_emails
        )
        
        # Run analysis
        results = analyzer.analyze()
        
        # Generate report
        print(f"\n📊 Generating report...")
        report = analyzer.generate_report(results, output_format=args.format)
        
        # Save report
        with open(args.output, 'w') as f:
            f.write(report)
        
        print(f"✅ Report saved to: {args.output}")
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
