# main.py
# Runs in GitHub Actions. Checks RSI(14) daily for selected symbols on Binance
# and sends a Telegram (or Discord) alert when RSI crosses below 30.

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

# Notifications (set as GitHub Secrets in the Actions workflow settings)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")  # optional


def rsi(values, period=14):
    """Wilder's RSI computed from a list of closing prices."""
    if len(values) < period + 1:
        return []

    gains, losses = [], []
    for i in range(1, period + 1):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0.0))
        lo

