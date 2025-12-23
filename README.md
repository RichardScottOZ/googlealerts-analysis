# Google Alerts Analysis for Mineral Exploration ML

Automatically categorize Google Alerts to determine their relevance to the [mineral-exploration-machine-learning](https://github.com/RichardScottOZ/mineral-exploration-machine-learning) repository using AI-powered analysis.

This tool fetches Google Alerts from Gmail and uses LLMs (OpenAI GPT-4/GPT-4o-mini, Google Gemini, or OpenRouter) to intelligently categorize them, providing summaries and relevance scores for mineral exploration machine learning applications.

## Features

- 🔍 **Gmail Integration**: Automatically fetches Google Alerts from your Gmail account
- 🤖 **AI-Powered Categorization**: Uses GPT-4o-mini, Gemini, or OpenRouter to analyze content relevance
- 📊 **Detailed Reports**: Generates markdown or JSON reports with summaries and insights
- 🎯 **Smart Filtering**: Identifies articles relevant to ML in mineral exploration
- 📝 **Keyword Extraction**: Extracts key terms from each alert
- ⚡ **Flexible Configuration**: Support for multiple LLM providers and customizable parameters

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/RichardScottOZ/googlealerts-analysis.git
cd googlealerts-analysis
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Google Gmail API**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Gmail API
   - Create OAuth 2.0 credentials (Desktop application)
   - Download the credentials as `credentials.json` and place it in the project root

4. **Configure API keys**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
- For OpenAI: Get key from [OpenAI Platform](https://platform.openai.com/api-keys)
- For Gemini: Get key from [Google AI Studio](https://aistudio.google.com/app/apikey)
- For OpenRouter: Get key from [OpenRouter](https://openrouter.ai/keys)

## Configuration

Edit the `.env` file to customize:

```env
# Choose your LLM provider
LLM_PROVIDER=openai  # Options: openai, gemini, openrouter

# Choose your model
LLM_MODEL=gpt-4o-mini  # OpenAI: gpt-4o-mini, gpt-4, gpt-4o
                       # Gemini: gemini-1.5-flash, gemini-1.5-pro
                       # OpenRouter: openai/gpt-4o-mini, anthropic/claude-3.5-sonnet, meta-llama/llama-3.1-70b-instruct

# API Keys
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here

# Processing parameters
MAX_EMAILS_TO_PROCESS=10  # Maximum number of alerts to process
DAYS_BACK=7               # How many days back to search
```

## Usage

### Basic Usage

Run with default settings (from .env):
```bash
python analyze_alerts.py
```

### Advanced Usage

```bash
# Use Gemini instead of OpenAI
python analyze_alerts.py --provider gemini

# Use OpenRouter with Claude
python analyze_alerts.py --provider openrouter --model anthropic/claude-3.5-sonnet

# Process last 14 days with specific model
python analyze_alerts.py --days 14 --model gpt-4

# Specify maximum emails and output format
python analyze_alerts.py --max-emails 20 --format json --output results.json

# Full custom configuration
python analyze_alerts.py \
  --provider openai \
  --model gpt-4o-mini \
  --days 7 \
  --max-emails 10 \
  --output report.md \
  --format markdown
```

### Command Line Arguments

- `--provider`: LLM provider (`openai`, `gemini`, or `openrouter`)
- `--model`: Specific model name
- `--days`: Number of days back to search for alerts
- `--max-emails`: Maximum number of alerts to process
- `--output`: Output file path (default: `report.md`)
- `--format`: Output format (`markdown` or `json`)

## First Run

On first run, you'll be prompted to authenticate with Google:
1. A browser window will open
2. Select your Google account
3. Grant permission to read Gmail
4. A token will be saved for future runs

## Output

The tool generates a report with:

### Markdown Report (`report.md`)
- Summary statistics
- Relevant alerts with detailed analysis
- Article links and summaries
- Categorization reasoning
- Keywords and confidence scores

Example output:
```markdown
# Google Alerts Analysis Report

## Summary
- **Total Alerts Processed:** 10
- **Relevant to mineral-exploration-machine-learning:** 7
- **Relevance Rate:** 70.0%

## Relevant Alerts

### 1. Machine Learning in Copper Exploration
**Category:** Machine Learning - Exploration
**Confidence:** 0.92
**Summary:** New ML algorithms improve copper deposit prediction accuracy...
**Keywords:** machine learning, copper, exploration, predictive modeling
```

### JSON Report
Full structured data for programmatic processing:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "total_alerts": 10,
  "relevant_alerts": 7,
  "results": [...]
}
```

## Project Structure

```
googlealerts-analysis/
├── analyze_alerts.py      # Main orchestrator script
├── gmail_fetcher.py       # Gmail API integration
├── llm_categorizer.py     # LLM categorization logic
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## How It Works

1. **Fetch**: Connects to Gmail API and retrieves Google Alerts emails
2. **Parse**: Extracts article titles, URLs, and content from emails
3. **Analyze**: Sends each alert to LLM with context about the mineral-exploration-machine-learning repo
4. **Categorize**: LLM determines relevance, confidence, and provides reasoning
5. **Report**: Generates formatted report with all findings

## Relevance Criteria

The LLM evaluates alerts based on relevance to:
- Machine learning in mineral exploration
- Geoscience data analysis with ML/AI
- Remote sensing and geophysical data processing
- Predictive modeling for mineral deposits
- Geological mapping with ML
- Exploration targeting using data science
- Mining industry AI applications

## Troubleshooting

### Gmail Authentication Issues
- Ensure `credentials.json` is in the project root
- Delete `token.pickle` and re-authenticate if issues persist

### API Key Errors
- Verify API keys in `.env` file
- Check API key has sufficient quota/credits

### No Alerts Found
- Verify you have Google Alerts set up in Gmail
- Check the `DAYS_BACK` parameter - increase if needed
- Confirm alerts are from `googlealerts-noreply@google.com`

## Cost Considerations

- **OpenAI GPT-4o-mini**: Very cost-effective (~$0.15 per 1M input tokens)
- **Google Gemini Flash**: Also cost-effective with generous free tier
- Each alert typically uses 500-1000 tokens

For 10 alerts/day:
- Daily cost: < $0.01 with GPT-4o-mini or Gemini Flash
- Monthly cost: < $0.30

## Contributing

Contributions welcome! Areas for improvement:
- Better email parsing for different alert formats
- Additional categorization criteria
- Integration with GitHub Issues/Projects
- Web UI for results viewing
- Scheduled automated runs

## License

MIT License - feel free to use and modify for your needs.

## Related Projects

- [mineral-exploration-machine-learning](https://github.com/RichardScottOZ/mineral-exploration-machine-learning) - The repository this tool helps curate content for
