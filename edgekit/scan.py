"""Scan a CSV of odds for +EV prices and arbitrage.

CSV columns: event, market, outcome, book, odds  (decimal odds).
Bring your own odds data from a feed you are licensed to use.
"""
from __future__ import annotations

import csv
from collections import OrderedDict
from typing import Dict, List

from .arb import arbitrage, best_prices
from .devig import devig
from .ev import edge, kelly_stake


def read_csv(path: str) -> Dict[tuple, Dict[str, Dict[str, float]]]:
    """Group rows into {(event, market): {book: {outcome: odds}}}."""
    groups: Dict[tuple, Dict[str, Dict[str, float]]] = OrderedDict()
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = (row["event"].strip(), row["market"].strip())
            groups.setdefault(key, OrderedDict()).setdefault(row["book"].strip(), OrderedDict())[
                row["outcome"].strip()
            ] = float(row["odds"])
    return groups


def scan(groups, sharp: str, method: str = "power", min_edge: float = 0.01,
         bankroll: float = 1000.0, kelly: float = 0.25) -> Dict[str, List[dict]]:
    """Return {'value': [...], 'arbs': [...]} for every grouped market."""
    value: List[dict] = []
    arbs: List[dict] = []
    for (event, market), books in groups.items():
        if sharp not in books:
            continue
        outcomes = list(books[sharp])
        complete = {b: [q[o] for o in outcomes] for b, q in books.items() if all(o in q for o in outcomes)}
        if sharp not in complete:
            continue
        fair = devig(complete[sharp], method)
        for book, odds in complete.items():
            if book == sharp:
                continue
            for i, o in enumerate(outcomes):
                e = edge(fair[i], odds[i])
                if e >= min_edge:
                    value.append({"event": event, "market": market, "outcome": o, "book": book,
                                  "odds": odds[i], "fair_prob": fair[i], "edge": e,
                                  "stake": kelly_stake(bankroll, fair[i], odds[i], kelly)})
        if len(complete) >= 2:
            best = best_prices(complete)
            a = arbitrage([b[0] for b in best], bankroll)
            if a:
                arbs.append({"event": event, "market": market,
                             "legs": [{"outcome": outcomes[i], "book": best[i][1], "odds": best[i][0],
                                       "stake": a["stakes"][i]} for i in range(len(outcomes))],
                             "margin": a["margin"], "profit": a["profit"]})
    value.sort(key=lambda r: r["edge"], reverse=True)
    arbs.sort(key=lambda r: r["margin"], reverse=True)
    return {"value": value, "arbs": arbs}
