import matplotlib.pyplot as plt

import config
import data_loader
import indicators
import signals
import backtest
import metrics

#create a clean data only in dev time data
def get_trades(start, end):
    raw_data = data_loader.load_data(config.xauusd_data)
    with_indicator = indicators.add_indicators(raw_data)
    with_signals = signals.add_signals(with_indicator)
    dev_data = with_signals.loc[start : end]
    tested_data = backtest.run_backtest(dev_data)
    return tested_data

#Save a chart of cumulative R over time.
def plot_equity_curve(trades, path):
    equity = metrics.equity_curve(trades)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(trades['time_of_exit'], equity, linewidth=2)
    ax.axhline(0, color='grey', linewidth=1)                # breakeven line
    ax.set_title("Equity curve: development period (before costs)")
    ax.set_xlabel("Exit date")
    ax.set_ylabel("Cumulative R")
    ax.grid(alpha=0.3)

    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)

if __name__ == '__main__':
    dev_trade = get_trades(config.dev_start, config.dev_end)
    
    print(metrics.create_summary(dev_trade).round(3))
    print(metrics.direction_breakdown(dev_trade))
    print(metrics.year_breakdown(dev_trade))

    plot_equity_curve(dev_trade, 'equity_curve.png')
    print("Chart saved as equity_curve.png")