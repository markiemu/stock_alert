import yfinance as yf
import mysql.connector
import csv
from datetime import datetime

# --- Connect to the MySQL database ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Add your password if you have one
    database="stock_alert_db"
)
cursor = db.cursor()

# --- Create alerts table if not exists ---
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_alerts (
        id INT AUTO_INCREMENT PRIMARY KEY,
        symbol VARCHAR(10),
        threshold FLOAT,
        email VARCHAR(255)
    )
""")

# --- Fetch all alerts ---
cursor.execute("SELECT symbol, threshold, email FROM stock_alerts")
stocks = cursor.fetchall()
print("🔎 Monitoring the following stocks:")
for symbol, threshold, email in stocks:
    print(f" - {symbol}: alert below {threshold}")

# --- Function to fetch stock price from Yahoo Finance ---
def fetch_stock_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period='1d')
    if not data.empty:
        return data['Close'].iloc[-1]
    else:
        raise ValueError("No data found for symbol: {}".format(symbol))

# --- Create or overwrite alert_results.csv for frontend use ---
with open("alert_results.csv", mode="w", newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Timestamp", "Symbol", "CurrentPrice", "Threshold", "Status"])  # Header row

    # --- Check each stock ---
    for symbol, threshold, email in stocks:
        try:
            price = fetch_stock_price(symbol)
            print(f"{symbol}: Current = {price}, Threshold = {threshold}")

            if price < threshold:
                status = "⚠️ ALERT"
                print(f"⚠️ {symbol} dropped below threshold!")
            else:
                status = "✅ OK"

            # Log the result to CSV
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), symbol, round(price, 2), threshold, status])

        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")

# --- Cleanup ---
cursor.close()
db.close()
