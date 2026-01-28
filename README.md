# 🇸🇬 S-REITs AI Dashboard

An automated dashboard for monitoring Singapore Real Estate Investment Trusts (S-REITs), featuring data-driven technical analysis and AI-powered market insights using Claude 3.5 Sonnet.


## 🚀 Features

- **Automated Data Fetching**: Retrieves historical price data via `yfinance` and scrapes fundamental metrics (Yield, P/NAV, Gearing)
- **Technical Analysis**: Computes RSI, trend indicators, and price changes to identify market movements.
- **AI Insights**: Integrates with **Anthropic's Claude 3.5 Sonnet** to generate:
  - Weekly market commentary.
  - Individual REIT investment perspectives.
  - Sector-specific outlooks (Industrial, Commercial, Healthcare, etc.).
- **Dynamic Dashboard**: Generates a clean, responsive `index.html` report with interactive data tables and AI summaries.
- **Telegram Integration**: Sends weekly automated updates to a designated Telegram channel/chat.
- **Cloud Automation**: Fully automated execution via **GitHub Actions** with weekly scheduled updates.

## 🛠️ Tech Stack

- **Language**: Python 3.11
- **Data Sources**: Yahoo Finance (yfinance), Beautiful Soup 4 (Web Scraping)
- **AI Engine**: Anthropic Claude API claude-sonnet-4-5-20250929
- **Automation**: GitHub Actions
- **deployment**: GitHub Pages
- **Notifications**: Telegram Bot API

## 📋 Prerequisites

- Python 3.11+
- Anthropic API Key (for AI insights)
- Telegram Bot Token & Chat ID (for notifications)

## ⚙️ Setup & Installation

1. **Clone the repository**:

    ```bash
    git clone https://github.com/agenticcycleos/Singapore-Reits.git
    cd Singapore-Reits/s_reits_dashboard
    ```

2. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

3. **Configure Environment Variables**:
    Create a `.env` file (or set in your environment):

    ```env
    ANTHROPIC_API_KEY=your_claude_api_key_here
    TELEGRAM_BOT_TOKEN=your_bot_token_here
    TELEGRAM_CHAT_ID=your_chat_id_here
    ```

4. **Configure REITs**:
    Modify `reits_config.json` to add or remove REIT tickers to track.

## 🏃 Usage

Run the main script to fetch data, generate the dashboard, and send notifications:

```bash
python main.py
```

The generated dashboard will be saved in `public/index.html`.

## 🤖 Automated Workflows

The project includes two primary GitHub Action workflows located in `.github/workflows/`:

1. **Update Dashboard (`update-dashboard.yml`)**:
    - Runs every Sunday at 02:00 UTC.
    - Installs dependencies, runs `main.py`.
    - Commits the updated `index.html` and deploys to GitHub Pages.
2. **Weekly Update (`weekly_update.yml`)**:
    - Specifically focused on triggered/scheduled notification tasks.

## 📄 License

[MIT License](LICENSE) (If applicable)

---
*Disclaimer: This tool is for informational purposes only and does not constitute financial advice.*
