"""Properties that make the seeded historical valuation feel credible and smooth.

The series is an explicitly-labelled deterministic proxy (no live snapshot history
exists), but it must read like a finance chart: bounded day-to-day moves, trend
continuity, and no impossible V-shaped spikes — not random noise.
"""

from __future__ import annotations

import pytest

from skillsmarket.history import seeded_history, sparkline


def _daily_pct_moves(points: list[dict[str, float]]) -> list[float]:
    moves = []
    for prev, cur in zip(points, points[1:]):
        if prev["price"]:
            moves.append((cur["price"] - prev["price"]) / prev["price"] * 100.0)
    return moves


def test_history_anchors_to_current_price_and_is_positive():
    points = seeded_history("Python", 142.0, days=90)
    assert len(points) == 90
    assert points[-1]["price"] == 142.0
    assert points[-1]["day"] == 0
    assert points[0]["day"] == -89
    assert all(point["price"] > 0 for point in points)


def test_history_is_deterministic():
    a = seeded_history("Data Analysis", 187.5, days=90)
    b = seeded_history("Data Analysis", 187.5, days=90)
    assert a == b


@pytest.mark.parametrize(
    "name,price",
    [("Python", 142.0), ("Microsoft Excel", 78.0), ("Machine Learning", 205.0), ("Scheduling", 61.5)],
)
def test_daily_moves_are_bounded_no_impossible_spikes(name: str, price: float):
    """No single day should jump more than a credible amount (~2.5%)."""
    moves = _daily_pct_moves(seeded_history(name, price, days=90))
    assert moves
    assert max(abs(move) for move in moves) <= 2.5


@pytest.mark.parametrize(
    "name,price",
    [("Python", 142.0), ("Microsoft Excel", 78.0), ("Machine Learning", 205.0), ("Communication", 95.0)],
)
def test_series_is_smooth_few_direction_reversals(name: str, price: float):
    """A jagged random walk reverses direction almost every day (~45/90). A smooth,
    trend-continuous series should reverse far less often."""
    moves = _daily_pct_moves(seeded_history(name, price, days=90))
    reversals = sum(
        1 for prev, cur in zip(moves, moves[1:]) if prev != 0 and cur != 0 and (prev > 0) != (cur > 0)
    )
    assert reversals <= 16


def test_sparkline_still_short_and_anchored():
    spark = sparkline("Data Analysis", 200.0)
    assert 10 <= len(spark) <= 20
    assert spark[-1] == 200.0
