# RSI Alerts (Free) — GitHub Actions + Telegram

This repo checks **daily RSI(14)** for the symbols you choose (Binance symbols like `BTCUSDT`, `ETHUSDT`) and sends a **Telegram** (or optional Discord) alert when RSI **crosses below 30**. It runs every 15 minutes for free using **GitHub Actions**.

---

## Quick Start (Step-by-Step)

1. **Create a Telegram Bot (free)**
   - In Telegram, search for **@BotFather** → start → send `/newbot` → follow prompts → copy your **bot token**.
   - Start a chat with your new bot and send any message once.
   - Get your **chat ID** quickly by forwarding any message from that chat to **@JsonDumpBot**, or use Telegram's `getUpdates` (optional).

2. **Create a GitHub Repo**
   - Make a new repository on GitHub (public or private).

3. **Upload these three files**
   - `main.py`
   - `.github/workflows/rsi-alerts.yml`
   - `README.md` (this file)

4. **Add GitHub Secrets (Repo → Settings → Secrets and variables → Actions)**
   - `TELEGRAM_BOT_TOKEN` = token from BotFather
   - `TELEGRAM_CHAT_ID` = your numeric chat ID
   - *(Optional)* `DISCORD_WEBHOOK_URL` = a Discord incoming webhook URL

5. **Edit your symbols**
   - Open `main.py` and change the `SYMBOLS` list, e.g.:
     ```python
     SYMBOLS = ["BTCUSDT", "SOLUSDT", "AVAXUSDT"]
     ```

6. **Trigger the workflow**
   - Go to **Actions** tab → select **rsi-alerts** → click **Run workflow** (or wait for the 15-minute scheduler).
   - You should see logs in Actions, and alerts on Telegram if any symbol just crossed below 30.

7. **Optional tweaks**
   - Change schedule: in `.github/workflows/rsi-alerts.yml`, edit `cron` (e.g., `0 * * * *` for hourly).
   - Set `RSI_THRESHOLD` or timeframe (e.g., use `"4h"` in `get_binance_klines`).
   - Add Discord by setting `DISCORD_WEBHOOK_URL` secret.

---

## Notes
- Uses Binance **public** candles (no key required). Works even if you trade on another exchange.
- Sends an alert **only on a fresh cross** (yesterday >= 30, today < 30) to avoid spam.
- All times in alerts are **UTC**.

---

## Troubleshooting
- **No messages on Telegram?** Ensure you sent at least one message to your bot, and the **chat ID** is correct.
- **Actions failed?** Open the Actions log and look for network or syntax errors.
- **Symbols wrong?** Use Binance tickers (e.g., `BTCUSDT`, `ETHUSDT`, `SOLUSDT`).

Enjoy!
