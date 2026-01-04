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
        
        # 4. Check for Entries
        alert_triggered = False
        message_buffer = [f"📊 <b>Gold Update</b> (${current_price:.2f})"]
        
        for name, price in fib_levels.items():
            # Debug print
            print(f"{name}: ${price:.2f}")
            
            if abs(current_price - price) <= threshold:
                alert_triggered = True
                message_buffer.append(f"🚨 <b>NEAR LEVEL: {name}</b>")
                message_buffer.append(f"Price: ${price:.2f}")

        # Always send a 'Daily Brief' if it's the first run, or just on alert
        # For now, we only send if near a level to avoid spam, 
        # BUT we append the range info if an alert is triggered.
        if alert_triggered:
            message_buffer.append(f"\nrange: ${swing_low:.0f} - ${swing_high:.0f}")
            full_msg = "\n".join(message_buffer)
            # Send HTML parse mode if you want bolding, or plain text
            # For simplicity in this function, we assume plain text usually
            # stripping tags or just sending as is:
            send_telegram_alert(full_msg.replace("<b>", "").replace("</b>", ""))

        else:
            print("No levels triggered.")
            # OPTIONAL: Uncomment below to verify it works even without levels
            # send_telegram_alert(f"Bot Alive. Gold: ${current_price:.2f}. Range: {swing_low}-{swing_high}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
