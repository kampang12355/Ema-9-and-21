import ccxt
import time
import datetime
import requests
import pandas as pd

# === KONFIGURASI ===
TELEGRAM_TOKEN = '7428494687:AAE2vjVmDVtWDr-neM9-gmj_Pea4NT9_Vc4'
CHAT_ID = '7066460655'
PAIR = 'BTC/USDT'
TIMEFRAME = '1m'
RR = 2.1
FIBO_LEVEL = 0.57

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload)

def get_data():
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(PAIR, timeframe=TIMEFRAME, limit=100)
    df = pd.DataFrame(ohlcv, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    return df

def check_signal(df):
    df['EMA9'] = df['close'].ewm(span=9).mean()
    df['EMA21'] = df['close'].ewm(span=21).mean()

    # EMA Cross + Market Structure
    if df['EMA9'].iloc[-2] < df['EMA21'].iloc[-2] and df['EMA9'].iloc[-1] > df['EMA21'].iloc[-1]:
        swing_low = min(df['low'][-5:])
        entry = df['close'].iloc[-1]
        sl = swing_low
        tp = entry + (entry - sl) * RR
        retrace = entry - (entry - sl) * FIBO_LEVEL
        return True, entry, sl, tp, retrace
    return False, None, None, None, None

# === MAIN LOOP ===
send_telegram("🤖 Bot aktif 24/7 dan memantau sinyal...")

while True:
    try:
        df = get_data()
        signal, entry, sl, tp, retrace = check_signal(df)
        if signal:
            send_telegram(
                f"📈 BUY Signal {PAIR}\n"
                f"Entry: {entry:.2f}\n"
                f"SL: {sl:.2f}\n"
                f"TP: {tp:.2f}\n"
                f"Fibo (0.57): {retrace:.2f}"
            )
            time.sleep(60)
        else:
            print("📉 Tidak ada sinyal.")
        time.sleep(10)
    except Exception as e:
        print(f"❌ Error: {e}")
        time.sleep(10)
