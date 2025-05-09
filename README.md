# Market-Top-Indicator
This system aims to:  Identify Market Tops: Detect when the market might reverse from an uptrend.  Protect Capital: Exit positions using indicator-based signals and a stop-loss.  It combines trend-following, momentum, and overbought indicators with risk management
Strategy Rules

Entry (Long Position):

10-week EMA > 20-week EMA (uptrend).

MACD line > signal line (bullish momentum).

Exit (Close Position):

10-week EMA < 20-week EMA (trend reversal).

AND either:

MACD line < signal line (bearish momentum), OR

RSI > 70 (overbought).

Stop-Loss:

Set at 2x ATR below the entry price, calculated at entry.

How It Works

Entry: You enter a long position when the market shows a strong uptrend confirmed by both EMA and MACD.

Exit: You exit when a potential market top is signaled by an EMA crossover, with confirmation from MACD or RSI.

Risk Management: The ATR-based stop-loss protects against sudden drops, adapting to market volatility.

results - https://in.tradingview.com/chart/SPX/oaWQMXXV-Market-Top-Detection-and-Capital-Protection-System/
