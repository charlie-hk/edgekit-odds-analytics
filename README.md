# EdgeKit

Odds analytics in pure Python (no dependencies), plus an interactive dashboard.

- **Devig**: remove the bookmaker margin with four methods (multiplicative, additive, power, Shin)
- **Expected value and Kelly staking**
- **Arbitrage**: best prices across books and the stake split that locks in a profit
- **Closing line value (CLV)**: did you beat the market's final fair price?
- **CSV scanner**: scan a file of odds for +EV prices and arbitrage

> EdgeKit works on odds you give it. It does not scrape bookmakers. Use a data feed you are licensed to use.
> It is an educational tool, not betting advice, and it cannot predict results or promise profit.

## Install

```bash
pip install .            # or just run it from this folder
python -m edgekit --help
```

## Command line

```bash
# Remove the margin from one market (all methods)
python -m edgekit devig 1.90 2.05

# Is 2.10 on outcome 0 a good price against a sharp line?
python -m edgekit ev --sharp 1.95 1.95 --outcome 0 --odds 2.10 --bankroll 1000 --kelly 0.25

# Stake split for an arbitrage
python -m edgekit arb 2.10 2.05 --bankroll 1000

# Closing line value
python -m edgekit clv --bet-odds 2.10 --closing 2.00 2.00 --outcome 0

# Scan a CSV (event,market,outcome,book,odds)
python -m edgekit scan examples/sample_odds.csv --sharp SharpBook
```

## Python

```python
from edgekit import devig, edge, kelly_stake, arbitrage, clv

p = devig([2.10, 3.40, 3.60], method="shin")      # fair probabilities
e = edge(p[0], 2.18)                              # expected profit per unit staked
stake = kelly_stake(1000, p[0], 2.18, fraction=0.25)
arb = arbitrage([2.10, 2.10], bankroll=100)       # None when there is no arbitrage
```

## Methods

| Method | Idea | Notes |
|---|---|---|
| multiplicative | scale every implied probability by the same factor | simple, favours long shots |
| additive | subtract an equal share of the margin | can fail on heavy favourites |
| power | find k with sum(q^k) = 1 | takes more margin from long shots |
| shin | models the margin as insider-trading protection | equals additive for two outcomes |

## Dashboard

`docs/index.html` is a single-file dashboard that runs the same maths in the browser
(open it directly, or serve `docs/` with GitHub Pages).

## Tests

```bash
pip install pytest
pytest
```
