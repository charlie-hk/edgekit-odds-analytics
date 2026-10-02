"""Arbitrage across bookmakers."""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple


def best_prices(books: Dict[str, Sequence[float]]) -> List[Tuple[float, str]]:
    """For every outcome index return (best odds, book name) across all books."""
    names = list(books)
    n = len(books[names[0]])
    if any(len(books[b]) != n for b in names):
        raise ValueError("every book must quote the same number of outcomes")
    best: List[Tuple[float, str]] = []
    for i in range(n):
        o, b = max(((books[b][i], b) for b in names), key=lambda t: t[0])
        best.append((o, b))
    return best


def arbitrage(best_odds: Sequence[float], bankroll: float = 100.0) -> Optional[dict]:
    """Return the stake split when buying every outcome at the best odds locks in a profit.

    Returns None when there is no arbitrage (the implied probabilities sum to 1 or more).
    """
    if any(o <= 1.0 for o in best_odds):
        raise ValueError("decimal odds must be greater than 1.0")
    inv = sum(1.0 / o for o in best_odds)
    if inv >= 1.0:
        return None
    payout = bankroll / inv
    return {
        "margin": 1.0 / inv - 1.0,
        "stakes": [bankroll * (1.0 / o) / inv for o in best_odds],
        "payout": payout,
        "profit": payout - bankroll,
    }
