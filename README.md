🤖 AI Crypto Market Analyst
An intelligent trading assistant that automates market analysis for Bitcoin (BTC) and Ethereum (ETH). This bot fetches live market data from Binance.US, calculates key technical indicators, and uses GPT-4o to interpret market structure based on strict institutional trading rules. It delivers hourly reports and high-probability trade signals directly to your Telegram.

✨ Features
📈 Automated Technical Analysis: Fetches real-time OHLCV data and calculates EMA 50/200 (4H trend context) and RSI 14 (1H momentum).

🧠 GPT-4o Powered Logic: Uses OpenAI's LLM to analyze market regime (Bullish/Bearish/Chop) and filter out low-quality setups.

📱 Instant Telegram Alerts: Sends formatted notifications for both active trade signals (with Entry, SL, TP) and "No Trade" market updates.

🛡️ Robust Error Handling: Includes dynamic column logic for pandas-ta compatibility and geo-blocking workarounds using ccxt.binanceus.

☁️ Cloud Ready: Optimized for scheduled execution via GitHub Actions or Cron jobs.

🛠️ Tech Stack
Language: Python 3.9+

Data Source: ccxt (Binance.US)

Analysis: pandas, pandas_ta, OpenAI API (GPT-4o)

Notifications: requests (Telegram Bot API)

🚀 Quick Start
Install dependencies:

Bash

pip install -r requirements.txt
Configure Environment: Create a .env file with your keys:

Ini, TOML

OPENAI_API_KEY=your_openai_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
Run the Bot:

Bash

python main.py
📊 Strategy Logic
The bot applies a rigid systematic framework before signaling a trade:

Bullish Regime: Price > EMA 50 > EMA 200 (4H Chart)

Bearish Regime: Price < EMA 50 < EMA 200 (4H Chart)

Momentum Filter: RSI must be between 30 and 70 (1H Chart) to avoid exhaustion.

