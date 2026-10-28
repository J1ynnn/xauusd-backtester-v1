# Ideas to Test

Expansions, strategy variants, robustness checks and machine-learning directions for the backtester.

## Rules for testing any idea

1. Run the **baseline** backtest first, so there is something to compare against.
2. Change **one thing at a time**.
3. Decide on the development period (before July 2025); confirm on the locked test period only once.
4. Record the result, even if the idea fails. A failed idea is still a finding.

Every variant tested on the same data raises the risk of **overfitting**: finding something that worked by luck. A few well-reasoned tests are better than many small tweaks.

---

## Findings so far

- **Trend filter too strict.** The original rule "EMA50 > EMA200 **and** close > EMA50" left only 2 buys and 1 sell in about four years. Oversold pullbacks (RSI(7) and its MA both below 30) almost always push price below EMA50, so the setup and the filter nearly contradicted each other. The baseline now uses EMA50 vs EMA200 only.
- **Development-period baseline (before costs):** 223 trades, 33.6% win rate, +2R, max drawdown −23R. Buys +16R, sells −14R.

---

## A. Strategy variants

| ID | Idea | Why | What to measure |
|---|---|---|---|
| A1 | **Linger rule**: require RSI below 30 for at least N candles before the cross back | A longer stay may mean a real pullback rather than a one-candle spike | Win rate and expectancy for N = 1 (baseline), 2, 3, 5; watch the trade count |
| A2 | **Softer price filter**: buys only when close > EMA200 | A pullback below EMA50 is normal; below EMA200 may mean the trend is breaking | Trades kept vs removed, and whether the removed ones were mostly losers |
| A3 | **Stop placement**: lookbacks of 5, 10, 15, 20; ATR-based stops; a minimum stop distance | Volatility changed a lot as gold rose from ~$1,750 to ~$4,100; tiny stops can look unrealistically easy to win | Look for a broad plateau of similar results, not one sharp best value |
| A4 | **Reward ratio**: 1.5R, 2R, 3R | Higher targets win less often but pay more. Breakeven win rate = 1 / (1 + R): 40%, 33.3%, 25% | Expectancy in R, not win rate alone |
| A5 | **Time-based exit**: close after a maximum number of candles | A pullback trade that hasn't worked within a few hours may be a failed idea | Expectancy and average trade duration |
| A6 | **Session filter**: only London/New York hours | Busier markets may give cleaner moves; quiet hours have wider spreads | Results split by hour of day *before* adding the filter |
| A7 | **News avoidance**: skip signals near major US releases (CPI, jobs report, FOMC) | News can jump straight through stops | Needs a calendar of release dates |
| A8 | **Breakeven stop**: move the stop to entry once +1R in profit | Turns some losers into scratches, but also some winners | More complex to backtest correctly |

---

## B. Robustness: is the result real, or luck?

- **B1. Train/test split by date.** Choose settings on the development period, report the locked test period once. Never shuffle time-series data.
- **B2. Random-entry baseline.** Same stop/target rules, random entries, repeated many times. Does the strategy beat the spread of random results?
- **B3. Buy-and-hold comparison.** Gold roughly doubled in this period, so a strategy that mostly buys could look good just because gold went up.
- **B4. Confidence intervals.** Standard error = √(p(1 − p) / n); rough 95% range = p ± 2 × SE. Optional: binomial test against the 33.3% breakeven (`scipy.stats.binomtest`).
- **B5. Trading costs.** Subtract the spread on every trade, then test with 2× costs. If the edge disappears, it was too thin to trust.
- **B6. Other instruments.** Same rules and broker on silver, major indices, EURUSD. Working across markets is stronger evidence than more gold history.
- **B7. Results by year and market condition.** Did it only work in certain periods?
- **B8. Monte Carlo on trade order.** Shuffle the order of trade results many times and look at the range of worst drawdowns.
- **B9. Exit precision with M1 data.** When the stop and target fall inside one M15 candle, check the 1-minute candles to see which was hit first, instead of assuming a loss.
- **B10. No-edge test with simulated prices.** Generate artificial price paths (e.g. geometric Brownian motion) with the same volatility, and run the unchanged strategy. If it "profits" on random data too, the real-data result may be luck.

### Execution realism

- **Gap rule:** if a candle *opens* beyond the stop, exit at the open (losses larger than 1R; common after weekends and news).
- **Slippage:** subtract a few points on every stop exit, and test 2× as well.

---

## C. Machine-learning directions

### C1. ML filter on the signals (meta-labeling)

From Marcos López de Prado, *Advances in Financial Machine Learning* (2018). The rules generate candidate trades; a model predicts which ones to take. The rule-based system is the **baseline** the model must beat.

- **Label (y):** 1 if the trade won, 0 if it lost
- **Features (X)**, measured at entry using only past data:
  - RSI, RSI MA, number of candles RSI spent below 30
  - distance of price from EMA50 / EMA200 (divided by ATR, to be comparable across price levels)
  - EMA50 − EMA200 gap (trend strength)
  - recent volatility (ATR), tick volume, spread
  - hour of day, day of week
- **Models:** logistic regression first (simple, interpretable), then a decision tree or random forest (scikit-learn)

### C2. More training examples (triple-barrier labeling)

About 350 signals is little data for ML. Instead, label **every candle**: "if I entered here with this stop and a 2R target, would the target be hit before the stop (within a time limit)?" This gives tens of thousands of examples. Neighbouring candles overlap in time, so their labels are not independent.

### C3. Regime detection

Cluster market conditions (trending, ranging, volatile) from features like volatility and EMA slope, then check whether the strategy only works in some regimes.

### C4. News sentiment

Score headlines with a language model and add the score as a feature. Timestamps must be exact, or future information leaks in.

### How to evaluate any model

- **Walk-forward validation:** always train on the past and test on the future (scikit-learn `TimeSeriesSplit`). Never a random split.
- **Main metric: precision.** Of the trades the model says to take, how many win. That *is* the win rate of the filtered strategy.
- **Accuracy can mislead:** if most setups lose, "never trade" scores highly.
- **Compare** against the unfiltered rules on the same test period.
- A model that does **not** beat the baseline is a valid, reportable result.

### Leakage checklist

- Every feature uses `.shift(1)` or only data up to the entry candle
- No feature uses the trade's outcome, exit time or later prices
- Indicators calculated before the train/test split use only past values (EMA and RSI do)

---

## D. Engineering

- **Settings sweep:** loop over a dictionary of settings, run the backtest for each, collect results in one table (choose on development data only).
- **Record settings with results:** save each run's settings next to its results, so every result can be traced back.
- **Tests:** check indicators against hand-calculated values, and run a truncation test (results before a cut-off must not change when later data is removed) to prove there is no lookahead.