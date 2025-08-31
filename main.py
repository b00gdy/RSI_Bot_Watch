# main.py — RSI(14) daily alerts + debug pings

import os
import requests
from datetime import datetime, timezone

BINANCE_BASE = "https://api.binance.com"

# === CONFIG ===
SYMBOLS = [
    "BTCUSDT",  # Bitcoin
    "ETHUSDT",  # Ethereum
    "SOLUSDT",  # Solana
    "AVAXUSDT", # Avalanche
    "LINKUSDT", # Chainlink
    "BNBUSDT",  # Binance Coin
]

RSI_PERIOD = 14
RSI_THRESHOLD = 30.0
LOOKBACK = 200  # number of daily candles to fetch
ENABLE_STARTUP_PING = True  # send a quick "I'm alive" message each run for debugging

# Notifications (from GitHub Secrets)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")  # optional

def send_telegram(msg):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram secrets missing; skipping Telegram send.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, data=data, timeout=20)
        print(f"Telegram status: {r.status_code}")
    except Exception as e:
        print(f"Telegram send error: {e}")

def send_discord(msg):
    if not DISCORD_WEBHOOK_URL:
        return
    try:
        r = requests.post(DISCORD_WEBHOOK_URL, json={"content": msg}, timeout=20)
        print(f"Discord status: {r.status_code}")
    except Exception as e:
        print(f"Discord send error: {e}")

def notify(msg):
    print(msg)
    send_telegram(msg)
    send_discord(msg)

def rsi(values, period=14):
    if len(values) < period + 1:
        return []
    gains, losses = [], []
    for i in range(1, period + 1):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0.0))
        losses.append(abs(min(change, 0.0)))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period

    def calc_rsi(ag, al):
        if al == 0:
            return 100.0
        rs = ag / al
        return 100 - (100 / (1 + rs))

    rsis = [None] * period
    rsis.append(calc_rsi(avg_gain, avg_loss))
    for i in range(period + 1, len(values)):
        change = values[i] - values[i - 1]
        gain = max(change, 0.0)
        loss = abs(min(change, 0.0))
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rsis.append(calc_rsi(avg_gain, avg_loss))
    return rsis

def get_binance_klines(symbol, interval="1d", limit=LOOKBACK):
    url = f"https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def latest_rsi_cross_under(symbol):
    kl = get_binance_klines(symbol, "1d", LOOKBACK)
    closes = [float(c[4]) for c in kl]  # close price at index 4
    rsis = rsi(closes, RSI_PERIOD)
    if len(rsis) < 2:
        return None
    today_rsi = rsis[-1]
    yday_rsi = rsis[-2]
    if today_rsi is None or yday_rsi is None:
        return None
    crossed = yday_rsi >= RSI_THRESHOLD and today_rsi < RSI_THRESHOLD
    return {
        "symbol": symbol,
        "today_rsi": round(today_rsi, 2),
        "yday_rsi": round(yday_rsi, 2),
        "crossed": crossed,
    }

def main():
    print("Starting RSI check…")
    if ENABLE_STARTUP_PING:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        send_telegram(f"🤖 RSI bot run started at {now}")

    alerts = []
    for sym in SYMBOLS:
        try:
            res = latest_rsi_cross_under(sym)
            if not res:
                print(f"{sym}: insufficient data for RSI.")
                continue
            print(f"{sym} RSI today {res['today_rsi']} (yday {res['yday_rsi']})")
            if res["crossed"]:
                alerts.append(f"⚠️ *{sym}* RSI crossed *below {RSI_THRESHOLD}*: {res['today_rsi']}")
        except requests.HTTPError as e:
            print(f"{sym} HTTP error: {e}")
        except Exception as e:
            print(f"{sym} unexpected error: {e}")

    if alerts:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        msg = "🔔 RSI Alerts\n" + "\n".join(alerts) + f"\n\nTime: {now}"
        notify(msg)
    else:
        print("No crosses today.")

if __name__ == "__main__":
    main()


