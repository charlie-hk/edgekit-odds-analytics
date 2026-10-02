"""Command line interface: python -m edgekit <command>."""
from __future__ import annotations

import argparse
import sys

from . import arbitrage, clv, compare, devig, edge, fair_odds, kelly_stake, overround
from .scan import read_csv, scan


def _pct(x: float) -> str:
    return f"{x * 100:.2f}%"


def cmd_devig(a) -> int:
    print(f"overround: {_pct(overround(a.odds))}")
    results = compare(a.odds) if a.method == "all" else {a.method: devig(a.odds, a.method)}
    for name, p in results.items():
        fo = ", ".join(f"{x:.3f}" for x in fair_odds(p))
        print(f"{name:<15} " + "  ".join(_pct(x) for x in p) + f"   fair odds: {fo}")
    return 0


def cmd_ev(a) -> int:
    p = devig(a.sharp, a.method)[a.outcome]
    o = a.odds
    e = edge(p, o)
    print(f"fair probability: {_pct(p)}   price: {o}   EV: {_pct(e)}")
    print(f"stake ({a.kelly:g} Kelly, bankroll {a.bankroll:g}): {kelly_stake(a.bankroll, p, o, a.kelly):.2f}")
    return 0


def cmd_arb(a) -> int:
    r = arbitrage(a.odds, a.bankroll)
    if not r:
        print("no arbitrage at these prices")
        return 0
    print(f"arbitrage margin: {_pct(r['margin'])}   locked profit: {r['profit']:.2f} on {a.bankroll:g}")
    for i, s in enumerate(r["stakes"]):
        print(f"  outcome {i}: odds {a.odds[i]}  stake {s:.2f}")
    return 0


def cmd_clv(a) -> int:
    print(f"CLV: {_pct(clv(a.bet_odds, a.closing, a.outcome, a.method))}")
    return 0


def cmd_scan(a) -> int:
    res = scan(read_csv(a.csv), a.sharp, a.method, a.min_edge, a.bankroll, a.kelly)
    print(f"+EV prices: {len(res['value'])}   arbitrage: {len(res['arbs'])}")
    for r in res["value"]:
        print(f"  {r['event']} | {r['market']} | {r['outcome']} @ {r['odds']} ({r['book']})  "
              f"fair {_pct(r['fair_prob'])}  EV {_pct(r['edge'])}  stake {r['stake']:.2f}")
    for r in res["arbs"]:
        legs = "; ".join(f"{l['outcome']} @ {l['odds']} ({l['book']}) stake {l['stake']:.2f}" for l in r["legs"])
        print(f"  ARB {r['event']} | {r['market']}  margin {_pct(r['margin'])}  profit {r['profit']:.2f}  [{legs}]")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="edgekit", description="Odds analytics: devig, EV, arbitrage, CLV.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("devig", help="remove the margin from one market")
    d.add_argument("odds", type=float, nargs="+")
    d.add_argument("--method", default="all", choices=["all", "multiplicative", "additive", "power", "shin"])
    d.set_defaults(fn=cmd_devig)

    e = sub.add_parser("ev", help="expected value of a price against a sharp market")
    e.add_argument("--sharp", type=float, nargs="+", required=True, help="sharp odds for all outcomes")
    e.add_argument("--outcome", type=int, required=True, help="index of the outcome you want to bet (0-based)")
    e.add_argument("--odds", type=float, required=True, help="the price you can get")
    e.add_argument("--method", default="power")
    e.add_argument("--bankroll", type=float, default=1000.0)
    e.add_argument("--kelly", type=float, default=0.25)
    e.set_defaults(fn=cmd_ev)

    r = sub.add_parser("arb", help="stake split for an arbitrage")
    r.add_argument("odds", type=float, nargs="+", help="best odds for every outcome")
    r.add_argument("--bankroll", type=float, default=100.0)
    r.set_defaults(fn=cmd_arb)

    c = sub.add_parser("clv", help="closing line value of a bet")
    c.add_argument("--bet-odds", type=float, required=True)
    c.add_argument("--closing", type=float, nargs="+", required=True)
    c.add_argument("--outcome", type=int, required=True)
    c.add_argument("--method", default="power")
    c.set_defaults(fn=cmd_clv)

    s = sub.add_parser("scan", help="scan a CSV of odds (event,market,outcome,book,odds)")
    s.add_argument("csv")
    s.add_argument("--sharp", required=True, help="name of the sharp reference book in the CSV")
    s.add_argument("--method", default="power")
    s.add_argument("--min-edge", type=float, default=0.01)
    s.add_argument("--bankroll", type=float, default=1000.0)
    s.add_argument("--kelly", type=float, default=0.25)
    s.set_defaults(fn=cmd_scan)

    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
