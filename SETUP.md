# Setup Guide

This guide will help you set up the Google Alerts Analysis system.

## Prerequisites

- Python 3.8 or higher
- Gmail account with Google Alerts configured
- OpenAI API account OR Google Cloud account (for Gemini)

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Gmail API Access

#### A. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Name it (e.g., "Gmail Alerts Analyzer")
4. Click "Create"

#### B. Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on it and press "Enable"

#### C. Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" user type
   - Fill in required fields (App name, user support email)
   - Add your email as a test user
   - Save
4. Back to credentials creation:
   - Application type: "Desktop app"
   - Name it (e.g., "Gmail Alerts Analyzer")
   - Click "Create"
5. Download the credentials JSON file
6. Rename it to `credentials.json`
7. Move it to the project root directory

### 3. Set Up LLM API Keys

#### Option A: OpenAI (Recommended for simplicity)

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API keys section
4. Click "Create new secret key"
5. Copy the key (you won't see it again!)
6. Add credits to your account if needed

#### Option B: Google Gemini (Free tier available)

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with Google account
3. Click "Get API Key"
4. Create or select a project
5. Copy the API key

#### Option C: OpenRouter (Access to multiple models)

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up or log in
3. Navigate to [Keys](https://openrouter.ai/keys)
4. Click "Create Key"
5. Copy the API key
6. Add credits to your account

OpenRouter provides access to many models including:
- GPT-4, GPT-4o, GPT-4o-mini (OpenAI)
- Claude 3.5 Sonnet, Claude 3 Opus (Anthropic)
- Llama 3.1 70B, 405B (Meta)
- And many more open-source models

### 4. Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your keys:

For OpenAI:
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
```

For Gemini:
```env
GEMINI_API_KEY=AIzaxxxxxxxxxxxxx
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash
```

For OpenRouter:
```env
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxx
LLM_PROVIDER=openrouter
LLM_MODEL=openai/gpt-4o-mini
LLM_MODEL=allenai/olmo-3.1-32b-think:free
LLM_MODE=moonshotai/kimi-k2:free
# Or try: anthropic/claude-3.5-sonnet, meta-llama/llama-3.1-70b-instruct
```
```

3. Adjust other settings:
```env
MAX_EMAILS_TO_PROCESS=10
DAYS_BACK=7
```

### 5. Set Up Google Alerts

If you don't have Google Alerts set up yet:

1. Go to [Google Alerts](https://www.google.com/alerts)
2. Create alerts for topics like:
   - "machine learning mineral exploration"
   - "AI mining geology"
   - "remote sensing mineral deposits"
   - "predictive modeling mining"
   - "geoscience data science"
3. Set delivery to your Gmail address
4. Choose frequency (e.g., "At most once a day")

### 6. First Run

Run the analyzer:
```bash
python analyze_alerts.py
```

**On first run:**
1. A browser window will open
2. Select your Google account
3. You'll see a warning "Google hasn't verified this app"
   - Click "Advanced" → "Go to [App name] (unsafe)"
4. Grant permission to read Gmail
5. The authentication token will be saved in `token.pickle`

Subsequent runs will use the saved token.

## Verification

After setup, you should see output like:
```
🔍 Fetching Google Alerts from the last 7 days...
✅ Found 5 Google Alerts

🤖 Categorizing alerts using openai (gpt-4o-mini)...

[1/5] Processing: machine learning mineral exploration...
  ✅ Relevant: True (confidence: 0.89)
  📁 Category: Machine Learning - Exploration
  📝 Summary: Article discusses new ML techniques for mineral discovery...

...

📊 Generating report...
✅ Report saved to: report.md

📈 Summary: 3/5 alerts relevant
```

## Troubleshooting

### "credentials.json not found"
- Ensure you've downloaded and renamed the OAuth credentials file
- Place it in the project root directory

### "OPENAI_API_KEY not found in environment"
- Check that `.env` file exists (copy from `.env.example`)
- Verify the key is correctly formatted
- Restart terminal/reload environment

### "No Google Alerts found"
- Make sure you have Google Alerts set up
- Try increasing `DAYS_BACK` in `.env`
- Check alerts are delivered to the Gmail account you authenticated with

### OAuth Error: "Access blocked: This app's request is invalid"
- Make sure you added yourself as a test user in OAuth consent screen
- Try recreating the OAuth credentials

### API Rate Limits
- OpenAI has rate limits based on your tier
- Gemini has generous free tier limits
- Consider reducing `MAX_EMAILS_TO_PROCESS` if hitting limits

## Next Steps

Once setup is complete:

1. Run regular analyses (daily/weekly)
2. Review the generated reports
3. Adjust categorization by modifying prompts in `llm_categorizer.py`
4. Set up automated runs with cron/Task Scheduler
5. Integrate with GitHub Issues workflow

## Security Notes

- Never commit `credentials.json` or `token.pickle` to git (they're in .gitignore)
- Never commit `.env` with real API keys to git
- Rotate API keys periodically
- Use separate API keys for development and production

## Cost Monitoring

Monitor your API usage:
- OpenAI: [Usage Dashboard](https://platform.openai.com/usage)
- Gemini: [Google Cloud Console](https://console.cloud.google.com/)

With GPT-4o-mini or Gemini Flash, costs are typically < $0.01 per 10 alerts.
