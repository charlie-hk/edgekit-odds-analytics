"""Remove the bookmaker margin (the "vig") from a set of decimal odds.

All functions take decimal odds for every outcome of ONE market (for example
home / draw / away) and return fair probabilities that sum to 1.
"""
from __future__ import annotations

from math import sqrt
from typing import Callable, Dict, List, Sequence


def implied(odds: Sequence[float]) -> List[float]:
    """Raw implied probabilities (1 / odds). They sum to more than 1 when the book has a margin."""
    if len(odds) < 2:
        raise ValueError("a market needs at least two outcomes")
    if any(o <= 1.0 for o in odds):
        raise ValueError("decimal odds must be greater than 1.0")
    return [1.0 / o for o in odds]


def overround(odds: Sequence[float]) -> float:
    """Bookmaker margin as a fraction, e.g. 0.045 means 4.5%."""
    return sum(implied(odds)) - 1.0


def multiplicative(odds: Sequence[float]) -> List[float]:
    """Scale every implied probability by the same factor (proportional method)."""
    q = implied(odds)
    s = sum(q)
    return [x / s for x in q]


def additive(odds: Sequence[float]) -> List[float]:
    """Subtract an equal share of the margin from every outcome.

    Can produce non-positive probabilities for long shots, in which case a
    ValueError is raised and another method should be used.
    """
    q = implied(odds)
    cut = (sum(q) - 1.0) / len(q)
    p = [x - cut for x in q]
    if min(p) <= 0.0:
        raise ValueError("additive method gives a non-positive probability for this market")
    return p


def power(odds: Sequence[float]) -> List[float]:
    """Find k so that sum(q_i ** k) == 1 and use p_i = q_i ** k.

    Takes proportionally more margin from long shots than the multiplicative
    method does, which matches the favourite-longshot bias seen in real markets.
    """
    q = implied(odds)
    if abs(sum(q) - 1.0) < 1e-12:
        return q
    lo, hi = 0.0, 200.0  # g(k) = sum(q**k) - 1 is decreasing in k
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if sum(x ** mid for x in q) > 1.0:
            lo = mid
        else:
            hi = mid
    k = (lo + hi) / 2.0
    p = [x ** k for x in q]
    t = sum(p)
    return [x / t for x in p]


def shin(odds: Sequence[float]) -> List[float]:
    """Shin's method: models the margin as protection against insider trading.

    Solves for the insider proportion z and returns the matching probabilities.
    """
    q = implied(odds)
    s = sum(q)
    if s <= 1.0:
        return [x / s for x in q]

    def probs(z: float) -> List[float]:
        return [(sqrt(z * z + 4.0 * (1.0 - z) * x * x / s) - z) / (2.0 * (1.0 - z)) for x in q]

    lo, hi = 0.0, 0.999999  # f(z) = sum(probs(z)) - 1 is decreasing in z
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if sum(probs(mid)) > 1.0:
            lo = mid
        else:
            hi = mid
    p = probs((lo + hi) / 2.0)
    t = sum(p)
    return [x / t for x in p]


METHODS: Dict[str, Callable[[Sequence[float]], List[float]]] = {
    "multiplicative": multiplicative,
    "additive": additive,
    "power": power,
    "shin": shin,
}


def devig(odds: Sequence[float], method: str = "power") -> List[float]:
    """Fair probabilities for one market using the chosen method."""
    try:
        fn = METHODS[method]
    except KeyError:
        raise ValueError(f"unknown method {method!r}; choose from {sorted(METHODS)}") from None
    return fn(odds)


def fair_odds(probabilities: Sequence[float]) -> List[float]:
    """Convert probabilities to fair decimal odds."""
    return [1.0 / p for p in probabilities]


def compare(odds: Sequence[float]) -> Dict[str, List[float]]:
    """Run every method; methods that cannot handle the market are skipped."""
    out: Dict[str, List[float]] = {}
    for name, fn in METHODS.items():
        try:
            out[name] = fn(odds)
        except ValueError:
            continue
    return out
