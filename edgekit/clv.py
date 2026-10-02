"""Closing line value: did you beat the market's final fair price?"""
from __future__ import annotations

from typing import Sequence

from .devig import devig


def clv(bet_odds: float, closing_odds: Sequence[float], outcome: int, method: str = "power") -> float:
    """CLV as a fraction. 0.03 means your price was 3% better than the devigged closing price.

    `closing_odds` are the closing decimal odds of ALL outcomes of the market (from a sharp book);
    `outcome` is the index of the outcome you bet.
    """
    if bet_odds <= 1.0:
        raise ValueError("decimal odds must be greater than 1.0")
    p_close = devig(closing_odds, method)[outcome]
    return bet_odds * p_close - 1.0
