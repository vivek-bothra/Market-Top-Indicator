# Testing Checklist

## Data Fetching
- [ ] All 13 markets load with valid data (>52 bars each)
- [ ] CORS fallback chain works (test by blocking corsproxy.io in DevTools)
- [ ] v7 CSV fallback parses correctly
- [ ] Rate limiting: fetches in batches of 3 with 500ms delay
- [ ] sessionStorage cache: second page load skips fetch (verify in Network tab)
- [ ] signals.json primary path: if data/signals.json present, Yahoo fetch skipped
- [ ] "LIVE DATA" vs "CACHED" badge displays correctly

## Signal Logic
- [ ] EMA values stabilise after warm-up period (first 52 bars not used)
- [ ] MACD line = EMA12 - EMA26 (verify against TradingView manually for ^GSPC)
- [ ] RSI uses Wilder's smoothing (not simple EMA)
- [ ] ATR uses Wilder's smoothing
- [ ] LONG signal fires only when BOTH EMA_short > EMA_long AND MACD > signal
- [ ] WATCH fires when uptrend but momentum weakening
- [ ] FLAT fires when EMA_short < EMA_long
- [ ] Entry date/price recorded at first LONG bar (not current bar if already LONG)
- [ ] Stop loss = entry_price - 2×ATR_at_entry (not current ATR)
- [ ] Return % correct: (current - entry) / entry × 100

## UI / UX
- [ ] All 13 market cards render
- [ ] Signal badges correct color (LONG=lime, WATCH=amber, FLAT=muted red outline)
- [ ] LONG/WATCH use 2px left border with tint backgrounds; FLAT uses dim 1px border
- [ ] Sparklines render at 100×36 with 2px stroke and subtle gradient fill
- [ ] FLAT cards don't show entry/stop/return rows
- [ ] Filter bar: LONG/WATCH/FLAT/ALL filters work correctly
- [ ] Filter count badges update correctly
- [ ] Loading skeleton shows during fetch
- [ ] Error card state shows with ↻ RETRY button
- [ ] RETRY button re-fetches only that market

## Responsive
- [ ] Desktop 1280px: 3-4 column grid
- [ ] Tablet 768px: 2 columns
- [ ] Mobile 375px: sparkline moves below price and indicators expand on tap
- [ ] Header stays readable at all sizes
- [ ] Filter bar wraps cleanly on mobile

## GitHub Pages
- [ ] Renders from file:// with no console errors
- [ ] Renders on GitHub Pages (no 404s, no mixed content)
- [ ] Google Fonts load (IBM Plex Mono 400/500/700)
- [ ] GitHub Actions workflow YAML is valid
- [ ] Python script runs: pip install yfinance pandas numpy && python scripts/fetch_signals.py
- [ ] signals.json generated with all 13 markets
- [ ] Actions workflow commits signals.json back to repo

## Cross-browser
- [ ] Chrome latest
- [ ] Firefox latest
- [ ] Safari (check SVG sparkline rendering)
