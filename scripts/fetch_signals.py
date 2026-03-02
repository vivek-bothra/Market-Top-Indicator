#!/usr/bin/env python3
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

MARKETS = [
    {"ticker": "^GSPC", "name": "S&P 500", "region": "USA", "flag": "🇺🇸", "currency": "USD"},
    {"ticker": "^IXIC", "name": "NASDAQ Composite", "region": "USA", "flag": "🇺🇸", "currency": "USD"},
    {"ticker": "^RUT", "name": "Russell 2000", "region": "USA", "flag": "🇺🇸", "currency": "USD"},
    {"ticker": "^STOXX50E", "name": "Euro Stoxx 50", "region": "Eurozone", "flag": "🇪🇺", "currency": "EUR"},
    {"ticker": "^GDAXI", "name": "DAX", "region": "Germany", "flag": "🇩🇪", "currency": "EUR"},
    {"ticker": "^FTSE", "name": "FTSE 100", "region": "UK", "flag": "🇬🇧", "currency": "GBP"},
    {"ticker": "^FCHI", "name": "CAC 40", "region": "France", "flag": "🇫🇷", "currency": "EUR"},
    {"ticker": "^N225", "name": "Nikkei 225", "region": "Japan", "flag": "🇯🇵", "currency": "JPY"},
    {"ticker": "^HSI", "name": "Hang Seng", "region": "Hong Kong", "flag": "🇭🇰", "currency": "HKD"},
    {"ticker": "^AXJO", "name": "ASX 200", "region": "Australia", "flag": "🇦🇺", "currency": "AUD"},
    {"ticker": "^NSEI", "name": "NIFTY 50 (India Broad Proxy)", "region": "India", "flag": "🇮🇳", "currency": "INR"},
    {"ticker": "NIFTYSMLCAP250.NS", "name": "NIFTY Smallcap 250", "region": "India", "flag": "🇮🇳", "currency": "INR"},
    {"ticker": "^BVSP", "name": "Bovespa", "region": "Brazil", "flag": "🇧🇷", "currency": "BRL"},
]


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi_wilder(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = (-delta).clip(lower=0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(100)


def atr_wilder(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat([
        (high - low),
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def calculate_signal(df: pd.DataFrame) -> dict:
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    ema10 = ema(close, 10)
    ema20 = ema(close, 20)
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)
    macd_line = ema12 - ema26
    macd_signal = ema(macd_line, 9)
    rsi = rsi_wilder(close, 14)
    atr = atr_wilder(high, low, close, 14)

    signal_series = []
    for i in range(len(df)):
      if i < 52:
          signal_series.append("FLAT")
          continue
      is_long = ema10.iloc[i] > ema20.iloc[i] and macd_line.iloc[i] > macd_signal.iloc[i]
      is_watch = ema10.iloc[i] > ema20.iloc[i] and (macd_line.iloc[i] < macd_signal.iloc[i] or rsi.iloc[i] > 70)
      signal_series.append("LONG" if is_long else ("WATCH" if is_watch else "FLAT"))

    entry_date = None
    entry_price = None
    entry_atr = None
    prev_state = "FLAT"
    for i, state in enumerate(signal_series):
        if state == "LONG" and prev_state != "LONG":
            entry_date = df.index[i].strftime("%Y-%m-%d")
            entry_price = float(close.iloc[i])
            entry_atr = float(atr.iloc[i])
        prev_state = state

    current_state = signal_series[-1]
    current = float(close.iloc[-1])
    previous = float(close.iloc[-2]) if len(close) > 1 else current

    payload = {
        "signal": current_state,
        "current_price": round(current, 2),
        "weekly_change_pct": round(((current - previous) / previous) * 100, 2),
        "entry_date": None,
        "entry_price": None,
        "stop_loss": None,
        "return_pct": None,
        "ema_short": round(float(ema10.iloc[-1]), 2),
        "ema_long": round(float(ema20.iloc[-1]), 2),
        "rsi": round(float(rsi.iloc[-1]), 2),
        "macd_line": round(float(macd_line.iloc[-1]), 2),
        "macd_signal": round(float(macd_signal.iloc[-1]), 2),
        "atr": round(float(atr.iloc[-1]), 2),
        "sparkline": [round(float(v), 2) for v in close.tail(20).tolist()],
    }

    if current_state in {"LONG", "WATCH"} and entry_price is not None and entry_atr is not None:
        payload["entry_date"] = entry_date
        payload["entry_price"] = round(entry_price, 2)
        payload["stop_loss"] = round(entry_price - 2 * entry_atr, 2)
        payload["return_pct"] = round(((current - entry_price) / entry_price) * 100, 2)

    return payload


def fetch_ticker(ticker: str) -> pd.DataFrame:
    if ticker in {"^NSEI", "NIFTYSMLCAP250.NS"}:
        time.sleep(1)
    df = yf.download(ticker, auto_adjust=True, interval="1wk", period="2y", progress=False)
    if df.empty:
        raise ValueError(f"No data for {ticker}")
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
    df = df.ffill(limit=2).dropna()
    if len(df) < 52:
        raise ValueError(f"Insufficient weekly bars for {ticker}: {len(df)}")
    return df


def main() -> None:
    output = {"generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "source": "github-actions", "markets": []}

    summaries = []
    for meta in MARKETS:
        ticker = meta["ticker"]
        try:
            df = fetch_ticker(ticker)
            sig = calculate_signal(df)
            market = {**meta, **sig}
            output["markets"].append(market)
            summaries.append((ticker, market["signal"], market["current_price"], market["weekly_change_pct"]))
        except Exception as exc:
            print(f"ERROR {ticker}: {exc}")

    data_path = Path("data/signals.json")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    print("\nSummary")
    print("Ticker\tSignal\tPrice\tWeekly%")
    for ticker, signal, price, weekly in summaries:
        print(f"{ticker}\t{signal}\t{price}\t{weekly}")


if __name__ == "__main__":
    main()
