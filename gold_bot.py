import os
import yfinance as yf
import requests
import pandas as pd
import numpy as np

def send_telegram_alert(message):
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")
    if not bot_token or not chat_id: return
    
    # We use HTML parsing for bold text
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try: requests.post(url, json=payload)
    except: pass

def calculate_rsi(series, period=14):
    """ Calculates the Relative Strength Index (Momentum) """
    delta = series.diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_fib_levels(high, low):
    """ Calculates the Golden Zone """
    diff = high - low
    return {
        "0.500": high - (diff * 0.5),      # Equilibrium
        "0.618": high - (diff * 0.618),    # Golden Pocket
    }

def main():
    ticker = "ETH-USD"
    threshold = 15.0 # Increased buffer for ETH volatility
    
    print(f"Running Expert Analysis on {ticker}...")

    try:
        # Fetch detailed data (15m intervals for the last 5 days)
        coin = yf.Ticker(ticker)
        # 15m interval is best for Day/Swing trading logic
        df = coin.history(period="5d", interval="15m")
        
        if len(df) < 50:
            print("Not enough data.")
            return

        # --- TECHNICAL ANALYSIS ---
        current_price = df['Close'].iloc[-1]
        
        # 1. Trend (50 Simple Moving Average)
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        # If Price > SMA, we are in an UPTREND (Look for Longs)
        trend = "BULLISH 🟢" if current_price > df['SMA_50'].iloc[-1] else "BEARISH 🔴"
        
        # 2. Momentum (RSI)
        df['RSI'] = calculate_rsi(df['Close'])
        rsi = df['RSI'].iloc[-1]
        
        # 3. Structure (Fibs of last 48h / ~192 candles)
        last_2_days = df.tail(192) 
        swing_high = last_2_days['High'].max()
        swing_low = last_2_days['Low'].min()
        fibs = calculate_fib_levels(swing_high, swing_low)
        
        # --- DECISION ENGINE ---
        signal = "WAIT ✋"
        reason = "Market is choppy."
        
        # Distance to Golden Zone
        dist_to_05 = abs(current_price - fibs["0.500"])
        dist_to_618 = abs(current_price - fibs["0.618"])
        in_zone = (dist_to_05 <= threshold) or (dist_to_618 <= threshold)

        # LOGIC TREE
        if in_zone:
            if "BULLISH" in trend and rsi < 70:
                signal = "BUY / LONG 🚀"
                reason = "Uptrend pullback to Golden Pocket."
            elif "BEARISH" in trend and rsi > 30:
                signal = "SELL / SHORT 📉"
                reason = "Downtrend rejection at Golden Pocket."
            else:
                signal = "WATCH 👀"
                reason = "In Zone, but Momentum (RSI) contradicts Trend."
        else:
            # Overbought/Oversold Checks
            if rsi > 75:
                signal = "TAKE PROFIT 💰"
                reason = "RSI is Overheated (>75)."
            elif rsi < 25:
                signal = "TAKE PROFIT 💰"
                reason = "RSI is Oversold (<25)."

        # --- TELEGRAM REPORT ---
        msg = [f"🧠 <b>ETH STRATEGY ADVISOR</b>"]
        msg.append(f"<b>SIGNAL: {signal}</b>")
        msg.append(f"---------------------------")
        msg.append(f"💎 Price: ${current_price:.2f}")
        msg.append(f"📈 Trend: {trend}")
        msg.append(f"⚡ RSI: {rsi:.1f}")
        msg.append(f"---------------------------")
        msg.append(f"🎯 <b>Logic:</b> {reason}")
        
        if in_zone:
             msg.append(f"📍 Fib Zone: ${fibs['0.618']:.2f} - ${fibs['0.500']:.2f}")

        full_msg = "\n".join(msg)
        
        # Send Alert
        send_telegram_alert(full_msg)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
