"""Expected value and Kelly staking."""
from __future__ import annotations


def edge(prob: float, odds: float) -> float:
    """Expected profit per unit staked: prob * odds - 1. Positive means +EV."""
    if not 0.0 < prob < 1.0:
        raise ValueError("probability must be between 0 and 1")
    if odds <= 1.0:
        raise ValueError("decimal odds must be greater than 1.0")
    return prob * odds - 1.0


def kelly_fraction(prob: float, odds: float) -> float:
    """Full-Kelly fraction of bankroll (0 when there is no edge)."""
    e = edge(prob, odds)
    return max(e / (odds - 1.0), 0.0)


def kelly_stake(bankroll: float, prob: float, odds: float, fraction: float = 0.25) -> float:
    """Stake using a fraction of Kelly (default quarter Kelly, which is far less volatile)."""
    if bankroll < 0 or not 0.0 <= fraction <= 1.0:
        raise ValueError("bankroll must be >= 0 and fraction between 0 and 1")
    return bankroll * kelly_fraction(prob, odds) * fraction
