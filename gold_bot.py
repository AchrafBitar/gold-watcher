import os
import yfinance as yf
import requests

def send_telegram_alert(message):
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not bot_token or not chat_id:
        print("Error: Config missing.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}

    try:
        requests.post(url, json=payload)
        print(f"Alert sent: {message[:20]}...") 
    except Exception as e:
        print(f"Error sending msg: {e}")

def calculate_fib_levels(high, low):
    """
    Calculates Fibonacci Retracement levels between a High and Low.
    Returns a dict of {LevelName: Price}.
    """
    diff = high - low
    return {
        "Fib 0.236": high - (diff * 0.236),
        "Fib 0.382": high - (diff * 0.382),
        "Fib 0.500": high - (diff * 0.5), # The psychological half-back
        "Fib 0.618": high - (diff * 0.618), # The Golden Pocket
        "Fib 0.786": high - (diff * 0.786)
    }

def main():
    ticker = "GC=F" # Gold Futures (Reliable)
    threshold = 3.0  # Alert if within $3 of a level
    
    print(f"Analyzing {ticker} Market Structure...")

    try:
        gold = yf.Ticker(ticker)
        
        # 1. Fetch Data (Last 5 days to be safe, then slice last 2)
        hist = gold.history(period="5d")
        
        if len(hist) < 2:
            print("Not enough data for swing analysis.")
            return

        # Slice the last 2 trading days
        last_2_days = hist.tail(2)
        
        # 2. Identify Swing High and Low
        swing_high = last_2_days['High'].max()
        swing_low = last_2_days['Low'].min()
        current_price = hist['Close'].iloc[-1]
        
        # 3. Calculate Fibonacci Levels automatically
        fib_levels = calculate_fib_levels(swing_high, swing_low)
        
        print(f"Current: ${current_price:.2f}")
        print(f"2-Day Range: {swing_low:.1f} - {swing_high:.1f}")
        
        # ... (Inside main function, after calculating levels) ...
        
        # 4. Check for Entries
        alert_triggered = False
        message_buffer = [f"📊 <b>Gold Update</b>"]
        message_buffer.append(f"Price: ${current_price:.2f}")
        
        for name, price in fib_levels.items():
            if abs(current_price - price) <= threshold:
                alert_triggered = True
                message_buffer.append(f"🚨 <b>NEAR {name}</b>: ${price:.2f}")

        # 5. The Decision Logic
        if alert_triggered:
            # If we found a level, send the ALERT
            message_buffer.append(f"\nrange: ${swing_low:.1f} - ${swing_high:.1f}")
            full_msg = "\n".join(message_buffer)
            send_telegram_alert(full_msg.replace("<b>", "").replace("</b>", ""))
            
        else:
            # If NO level found, send the "NO TRADING" message
            # This ensures you get a notification every time the script runs.
            status_msg = (
                f"NO TRADING FOR NOW :)\n"
                f"Current: ${current_price:.2f}\n"
                f"(Range: {swing_low:.0f}-{swing_high:.0f})"
            )
            send_telegram_alert(status_msg)

    except Exception as e:
        print(f"Error: {e}")
