import math
import os

import pytest

from edgekit import (METHODS, arbitrage, best_prices, clv, compare, devig, edge, fair_odds,
                     implied, kelly_fraction, kelly_stake, overround)
from edgekit.scan import read_csv, scan

TWO_WAY = [1.50, 2.80]
THREE_WAY = [2.10, 3.40, 3.60]
HEAVY = [1.20, 5.00]


@pytest.mark.parametrize("odds", [TWO_WAY, THREE_WAY, HEAVY])
@pytest.mark.parametrize("method", list(METHODS))
def test_probabilities_sum_to_one(odds, method):
    p = devig(odds, method)
    assert math.isclose(sum(p), 1.0, abs_tol=1e-9)
    assert all(0.0 < x < 1.0 for x in p)


def test_overround_and_implied():
    assert math.isclose(overround([1.90, 1.90]), 2 / 1.90 - 1)
    assert math.isclose(sum(implied([2.0, 2.0])), 1.0)


def test_symmetric_market_is_fifty_fifty_for_every_method():
    for method in METHODS:
        assert devig([1.90, 1.90], method) == pytest.approx([0.5, 0.5])


def test_multiplicative_is_proportional():
    q = implied(THREE_WAY)
    p = devig(THREE_WAY, "multiplicative")
    assert p == pytest.approx([x / sum(q) for x in q])


def test_power_and_shin_give_favourite_more_than_multiplicative():
    # favourite-longshot bias: more margin is taken from the long shot
    m = devig(HEAVY, "multiplicative")[0]
    assert devig(HEAVY, "power")[0] > m
    assert devig(HEAVY, "shin")[0] > m


def test_power_solves_its_own_equation():
    p = devig(THREE_WAY, "power")
    q = implied(THREE_WAY)
    k = math.log(p[0]) / math.log(q[0])
    assert sum(x ** k for x in q) == pytest.approx(1.0, abs=1e-9)


def test_no_margin_market_is_unchanged():
    p = devig([2.0, 2.0], "power")
    assert p == pytest.approx([0.5, 0.5])


def test_fair_odds_round_trip():
    p = devig(TWO_WAY, "power")
    assert [1 / o for o in fair_odds(p)] == pytest.approx(p)


def test_compare_runs_all_methods_on_normal_markets():
    assert set(compare(THREE_WAY)) == set(METHODS)


def test_invalid_input():
    with pytest.raises(ValueError):
        devig([1.0, 2.0])
    with pytest.raises(ValueError):
        devig([2.0])
    with pytest.raises(ValueError):
        devig([2.0, 2.0], "nope")


def test_edge_and_kelly():
    assert edge(0.5, 2.1) == pytest.approx(0.05)
    assert kelly_fraction(0.55, 2.0) == pytest.approx(0.10)
    assert kelly_fraction(0.40, 2.0) == 0.0
    assert kelly_stake(1000, 0.55, 2.0, 0.25) == pytest.approx(25.0)


def test_arbitrage_found_and_balanced():
    r = arbitrage([2.10, 2.10], 100)
    assert r is not None and r["profit"] > 0
    assert sum(r["stakes"]) == pytest.approx(100)
    # every outcome pays the same
    assert r["stakes"][0] * 2.10 == pytest.approx(r["stakes"][1] * 2.10)
    assert r["stakes"][0] * 2.10 == pytest.approx(r["payout"])


def test_no_arbitrage():
    assert arbitrage([1.90, 1.90]) is None


def test_best_prices_picks_highest_per_outcome():
    best = best_prices({"a": [1.9, 2.0], "b": [1.8, 2.2]})
    assert best == [(1.9, "a"), (2.2, "b")]


def test_clv():
    assert clv(2.10, [2.0, 2.0], 0) == pytest.approx(0.05)
    assert clv(1.90, [2.0, 2.0], 0) == pytest.approx(-0.05)


def test_scan_sample_csv():
    path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_odds.csv")
    res = scan(read_csv(path), sharp="SharpBook", min_edge=0.01)
    assert res["value"], "expected at least one +EV price in the sample data"
    assert all(r["edge"] >= 0.01 for r in res["value"])
    assert any(r["event"].startswith("Sample Darts") for r in res["arbs"])
