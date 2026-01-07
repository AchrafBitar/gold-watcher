import os
import time
import logging
import requests
import ccxt
import pandas as pd
import pandas_ta as ta
from openai import OpenAI
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not all([OPENAI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
    logger.error("Missing environment variables. Please check your GitHub Secrets or .env file.")
    exit(1)

# Initialize OpenAI client (Standard)
client = OpenAI(api_key=OPENAI_API_KEY)

def get_market_data(symbol: str) -> str:
    """Fetches market data and calculates indicators."""
    try:
        exchange = ccxt.binance()
        
        def fetch_process(timeframe, limit):
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df

        logger.info(f"Fetching data for {symbol}...")
        df_4h = fetch_process('4h', 300)
        df_1h = fetch_process('1h', 300)

        # Calculate Indicators
        df_4h.ta.ema(length=50, append=True)
        df_4h.ta.ema(length=200, append=True)
        df_1h.ta.rsi(length=14, append=True)

        # Dynamic Column Logic
        rsi_col = 'RSI_14' if 'RSI_14' in df_1h.columns else 'RSI'
        ema50_col = 'EMA_50' if 'EMA_50' in df_4h.columns else 'EMA_50.0'
        ema200_col = 'EMA_200' if 'EMA_200' in df_4h.columns else 'EMA_200.0'
        
        # Fallback search
        if rsi_col not in df_1h.columns:
             cols = [c for c in df_1h.columns if c.startswith('RSI')]
             if cols: rsi_col = cols[0]
        if ema50_col not in df_4h.columns:
             cols = [c for c in df_4h.columns if c.startswith('EMA_50')]
             if cols: ema50_col = cols[0]
        if ema200_col not in df_4h.columns:
             cols = [c for c in df_4h.columns if c.startswith('EMA_200')]
             if cols: ema200_col = cols[0]

        last_4h = df_4h.iloc[-2] # Last completed candle
        last_1h = df_1h.iloc[-2]
        current_price = df_1h.iloc[-1]['close'] # Live price

        data_string = (
            f"Market Data for {symbol}:\n"
            f"Current Price: {current_price}\n"
            f"4H Chart (Context):\n"
            f"  - EMA 50: {last_4h[ema50_col]:.2f}\n"
            f"  - EMA 200: {last_4h[ema200_col]:.2f}\n"
            f"  - Close: {last_4h['close']}\n"
            f"1H Chart (Trigger):\n"
            f"  - RSI (14): {last_1h[rsi_col]:.2f}\n"
            f"  - Close: {last_1h['close']}"
        )
        return data_string

    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        return None

def analyze_market(data_string: str) -> str:
    """Sends data to OpenAI for analysis."""
    system_prompt = """
    You are a Senior Systematic Market Analyst. Your job is to filter trades based on INSTITUTIONAL RULES.
    STRICT LOGIC:
    1. MARKET REGIME (4H):
       - BULLISH: Price > EMA 50 > EMA 200
       - BEARISH: Price < EMA 50 < EMA 200
       - CHOP (NO TRADE): Any other configuration.
    2. MOMENTUM (1H):
       - LONG: RSI must NOT be < 30.
       - SHORT: RSI must NOT be > 70.
    OUTPUT FORMAT:
    Start response strictly with "🔴 STATUS: NO TRADE" or "🟢 STATUS: TRADE ACTIVE".
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o", # You can also use "gpt-4o-mini" to save money
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": data_string}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return None

def send_telegram_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
        logger.info("Telegram notification sent!")
    except Exception as e:
        logger.error(f"Error sending Telegram alert: {e}")

def main():
    symbols = ["BTC/USDT", "ETH/USDT"]
    logger.info(f"Starting Scheduled Analysis for {symbols}...")
    
    for symbol in symbols:
        logger.info(f"Analyzing {symbol}...")
        market_data = get_market_data(symbol)
        if not market_data: continue
        
        analysis_result = analyze_market(market_data)
        if not analysis_result: continue

        if "🟢 STATUS: TRADE ACTIVE" in analysis_result:
            send_telegram_alert(f"Signal for {symbol}:\n{analysis_result}")
        else:
            logger.info(f"No trade active for {symbol}.")

    logger.info("Analysis complete.")

if __name__ == "__main__":
    main()
