# Quick Start Guide

Get up and running with Google Alerts Analysis in 5 minutes!

## Option 1: Demo Mode (No Setup Required)

Run the demo to see how the system works:

```bash
pip install pydantic python-dotenv
python demo.py
```

This will:
- Generate mock Google Alerts data
- Show how categorization works
- Create sample reports (demo_report.md and demo_report.json)

## Option 2: Full Setup (Real Gmail Integration)

### Prerequisites
- Python 3.8+
- Gmail account with Google Alerts
- OpenAI, Gemini, or OpenRouter API key

### 5-Minute Setup

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Configure API key:**
```bash
cp .env.example .env
nano .env  # or use your favorite editor
```

Add your OpenAI API key (or Gemini/OpenRouter):
```env
OPENAI_API_KEY=sk-proj-xxxxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# Or for OpenRouter:
# OPENROUTER_API_KEY=sk-or-xxxxx
# LLM_PROVIDER=openrouter
# LLM_MODEL=anthropic/claude-3.5-sonnet
```

**3. Set up Gmail API:**
- Go to https://console.cloud.google.com/
- Create a project and enable Gmail API
- Create OAuth credentials (Desktop app)
- Download as `credentials.json` in project root

See [SETUP.md](SETUP.md) for detailed instructions.

**4. Run the analyzer:**
```bash
python analyze_alerts.py
```

On first run, authenticate with Google. Subsequent runs will be automatic.

## Common Commands

```bash
# Basic usage (uses .env settings)
python analyze_alerts.py

# Process last 14 days
python analyze_alerts.py --days 14

# Use Gemini instead of OpenAI
python analyze_alerts.py --provider gemini

# Use OpenRouter with multiple model options
python analyze_alerts.py --provider openrouter --model anthropic/claude-3.5-sonnet

# Generate JSON report
python analyze_alerts.py --format json --output results.json

# Process more emails
python analyze_alerts.py --max-emails 20

# Custom model
python analyze_alerts.py --provider openai --model gpt-4
```

## Understanding the Output

After running, you'll get two reports:

**1. Main Report** (default: `report.md`)
- Human-readable markdown format
- Customizable with `--output` and `--format` flags

**2. JSON Report** (`report.json`)
- **Always generated automatically**
- Machine-readable structured data
- Perfect for programmatic processing, automation, and integration

### Report Contents

✅ **Relevant Alerts** - Articles about ML in mineral exploration
- Category (e.g., "Machine Learning - Exploration")
- Confidence score (0.0 to 1.0)
- Summary of the content
- Links to articles
- Keywords extracted

❌ **Non-Relevant Alerts** - Articles not related to the topic
- Reasoning for exclusion

## What Gets Categorized as Relevant?

Alerts about:
- ✅ Machine learning in mineral exploration
- ✅ AI for geology and geoscience
- ✅ Remote sensing for mining
- ✅ Predictive modeling for deposits
- ✅ Data science in exploration
- ❌ Cryptocurrency mining (Bitcoin, etc.)
- ❌ General tech news unrelated to minerals
- ❌ Financial mining stocks (unless ML-related)

## Cost Estimate

Using GPT-4o-mini or Gemini Flash:
- **10 alerts**: ~$0.01
- **100 alerts**: ~$0.10
- **Daily run (10 alerts)**: ~$0.30/month

Both providers have free tiers that may cover your usage.

## Troubleshooting

### "credentials.json not found"
Download OAuth credentials from Google Cloud Console.

### "OPENAI_API_KEY not found"
Create and populate the `.env` file from `.env.example`.

### "No Google Alerts found"
- Set up Google Alerts at https://www.google.com/alerts
- Try increasing `--days` parameter
- Check you're using the correct Gmail account

### OAuth Issues
Delete `token.pickle` and re-authenticate.

## Next Steps

1. ✅ Run demo to understand output format
2. ✅ Set up real Gmail API access
3. ✅ Run first analysis
4. 📝 Review the report
5. 🔄 Schedule regular runs (cron/Task Scheduler)
6. 🎯 Customize categorization criteria if needed

## Need Help?

- Full setup instructions: [SETUP.md](SETUP.md)
- Detailed README: [README.md](README.md)
- Issues: https://github.com/RichardScottOZ/googlealerts-analysis/issues

---

**Pro Tips:**
- Start with demo mode to understand the system
- Use GPT-4o-mini for cost-effectiveness
- Run weekly to batch process alerts
- Review confidence scores - higher is more reliable
