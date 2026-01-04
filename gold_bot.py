import os
import yfinance as yf
import requests

def send_telegram_alert(message):
    """
    Sends a message to a Telegram chat using bot credentials 
    from environment variables.
    """
    bot_token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("CHAT_ID")

    if not bot_token or not chat_id:
        print("Error: BOT_TOKEN or CHAT_ID environment variables are not set.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print(f"Alert sent: {message}")
        else:
            print(f"Failed to send alert. Status: {response.status_code}, Response: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def main():
    # Configuration
    ticker = "GC=F"
    key_levels = [2550, 2600, 2650]
    threshold = 2.0  # Range within which to alert (e.g., +/- $2)

    print(f"Fetching data for {ticker}...")
    
    try:
        # Fetch data
        gold = yf.Ticker(ticker)
        # Using 'fast_info' is often faster for current price than .history
        current_price = gold.fast_info.last_price 

        # If fast_info fails or is None, fallback to history
        if not current_price:
            data = gold.history(period="1d")
            if not data.empty:
                current_price = data['Close'].iloc[-1]
            else:
                print("Error: Could not retrieve price data.")
                return

        print(f"Current Gold Price: ${current_price:.2f}")

        # Check levels
        for level in key_levels:
            if abs(current_price - level) <= threshold:
                msg = (f"⚠️ Gold Price Alert!\n"
                       f"Current Price: ${current_price:.2f}\n"
                       f"Near Key Level: {level}")
                send_telegram_alert(msg)
                
    except Exception as e:
        print(f"An error occurred during execution: {e}")

if __name__ == "__main__":
    main()
