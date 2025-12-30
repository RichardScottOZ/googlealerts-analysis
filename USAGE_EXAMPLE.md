# Usage Example for list_articles.py

This document demonstrates how to use the `list_articles.py` helper script to view articles from Google Alerts and Scholar Alerts analysis in chronological order.

## Prerequisites

First, run the analysis scripts to generate the JSON reports:

```bash
# Analyze Google Alerts
python analyze_alerts.py

# Analyze Google Scholar Alerts
python analyze_scholar_alerts.py
```

This will create `report.json` and `scholar_report.json` files.

## Basic Usage

### View All Relevant Articles

```bash
python list_articles.py
```

This displays all relevant articles from both Google Alerts and Scholar Alerts in chronological order (newest first).

### Include Non-Relevant Articles

```bash
python list_articles.py --show-all
```

Shows all articles, including those marked as not relevant to mineral exploration ML.

## Output Formats

### Plain Text (Default)

```bash
python list_articles.py
```

Output format:
```
================================================================================
CHRONOLOGICAL ARTICLE LIST
================================================================================
Total Articles: 4
================================================================================

1. ✅ Deep Learning Transforms Copper Exploration in Chile
   [Google Alert] | Date: 2024-12-28
   Alert Query: machine learning mineral exploration
   URL: https://example.com/ml-copper-chile
   Summary: New deep learning algorithms achieve 85% accuracy...
   Relevance: Directly relevant to ML applications in mineral exploration

--------------------------------------------------------------------------------
```

### Markdown Format

```bash
python list_articles.py --format markdown --output articles.md
```

Creates a markdown file with formatted sections and clickable links.

### JSON Format

```bash
python list_articles.py --format json --output articles.json
```

Creates a machine-readable JSON file with all article data.

## Filtering Options

### Show Only Google Alerts

```bash
python list_articles.py --google-alerts-only
```

### Show Only Scholar Alerts

```bash
python list_articles.py --scholar-alerts-only
```

### Custom Input Files

```bash
python list_articles.py \
  --google-alerts path/to/custom_report.json \
  --scholar-alerts path/to/custom_scholar_report.json
```

## Advanced Options

### Generate Separate Outputs

Create separate files for Google Alerts and Scholar Alerts:

```bash
python list_articles.py --separate --output articles.txt
```

This creates:
- `articles_google.txt` - Google Alerts only
- `articles_scholar.txt` - Scholar Alerts only

Works with any format:

```bash
python list_articles.py --separate --format markdown --output articles.md
# Creates: articles_google.md and articles_scholar.md
```

## Example Workflow

1. Run analyses:
```bash
python analyze_alerts.py
python analyze_scholar_alerts.py
```

2. Quick review of relevant articles:
```bash
python list_articles.py
```

3. Generate comprehensive markdown report:
```bash
python list_articles.py --show-all --format markdown --output full_articles.md
```

4. Export data for further processing:
```bash
python list_articles.py --format json --output articles.json
```

## Tips

- By default, only relevant articles are shown (those marked as relevant to mineral exploration ML)
- Articles are always sorted by date, newest first
- The script provides helpful feedback about how many articles were found from each source
- If a report file is missing, the script continues and processes available files
- You can combine most flags (e.g., `--show-all --google-alerts-only --format markdown`)
