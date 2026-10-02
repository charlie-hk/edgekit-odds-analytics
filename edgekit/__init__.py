"""EdgeKit: devig, expected value, Kelly, arbitrage and closing line value for decimal odds."""
from .arb import arbitrage, best_prices
from .clv import clv
from .devig import METHODS, compare, devig, fair_odds, implied, overround
from .ev import edge, kelly_fraction, kelly_stake

__all__ = ["METHODS", "arbitrage", "best_prices", "clv", "compare", "devig", "edge",
           "fair_odds", "implied", "kelly_fraction", "kelly_stake", "overround"]
__version__ = "0.1.0"
