# settings for the config.py

# data
xauusd_data = "XAUUSD_M15_202207110100_202610022345.csv"
server_hours_ahead_of_NY = 7 # Time zone in MT5 is UTC+2 or 3, it is 7 hours ahead of NY

# Pricing rules and indicators
ema_fast = 50 # shorter EMA candle
ema_slow = 200 # longer EMA candle
rsi_length = 7 # RSI
rsi_ma_length = 14 # RSI Moving average

# signals
overbought = 70
oversold = 30 

# trade rules
candle_look_back = 10 # candles back to find the stop (lowest low / highest high), 10 candles = 2.5 hours
reward_ratio = 2.0 # target = entry +/- (reward_ratio x risk) # risk = entry - stop

# development period: build and tune rules here
dev_start = '2022-07-11'
dev_end = '2025-06-30'

# locked test period: run once with final rules
test_start = '2025-07-01'
test_end = '2026-10-02'

# ---------------------------------------------------------------------------
# Where the parameter values come from (honest version)
# ---------------------------------------------------------------------------
# None of these numbers are derived from theory. They are conventions or
# starting values, to be tested for sensitivity once the backtest works.
#
# EMA 50 / 200: famous from DAILY charts (~a quarter / ~a trading year,
#   the "golden cross"). Studied academically: Brock, Lakonishok & LeBaron
#   (1992, Journal of Finance) found MA rules had predictive power on
#   historical Dow data; Sullivan, Timmermann & White (1999, Journal of
#   Finance) showed much of that weakens once data snooping is accounted for.
#   On 15-minute candles the numbers mean something different:
#   EMA 50 ~ 12.5 hours, EMA 200 ~ 50 hours (~2 trading days).
#   My justification is the timescale: a ~half-day trend line vs a
#   ~two-day trend line, the fast one about 4x shorter.
#
# RSI length 7: a faster, noisier variant of Wilder's original default of
#   14 (from his 1978 book introducing RSI). Shorter = reacts quicker, more
#   false signals. Chosen to time pullbacks on a short timeframe.
# RSI MA length 14: smoothing for the persistence filter; should match the
#   RSI MA setting on my chart so backtest signals match what I see.
#
# SWING_LOOKBACK = 10: a simple starting rule. 10 x 15 min = 2.5 hours,
#   roughly the length of an intraday pullback, so the lowest low of that
#   window approximates the pullback's bottom. It widens a little in
#   volatile periods (bigger candles = wider window range).
#   Alternatives to test: ATR-based stops (stop = k x Average True Range,
#   scales directly with volatility) or true swing detection (a low lower
#   than N candles on each side; more chart-like but confirmed N candles late).
#
# ---------------------------------------------------------------------------