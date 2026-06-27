"""Deterministic seeded historical valuation for skills.

There is no live snapshot history in this demo, so we synthesise a reproducible
backtest series per skill. It is explicitly a *seeded historical proxy*, not live
history — callers must label it as such in the UI.

The series is built to read like a credible finance chart rather than random
noise: a gentle seeded trend plus a few low-frequency harmonics (fractal-style
sum of sines with decaying amplitude). That gives trend continuity and bounded
day-to-day moves with no impossible V-shaped spikes, while staying 100%
deterministic and anchored to today's price.
"""

from __future__ import annotations

import math
from typing import Any, Callable

# Harmonic / trend shape constants. Tuned so daily moves stay < ~1% (well within a
# credible band) and the path keeps a clear direction instead of zig-zagging.
_OCTAVES = 3
_BASE_FREQ = 0.8        # fundamental: <1 full cycle across the whole window
_FREQ_MULT = 2.0        # each harmonic doubles in frequency…
_PERSISTENCE = 0.38     # …and shrinks in amplitude, so lows dominate the trend
_BASE_AMP = 0.05        # ~5% fundamental swing
_MAX_TREND = 0.11       # gentle drift across the window: ±11%


def _seed(name: str) -> int:
    return sum(ord(char) * (index + 1) for index, char in enumerate(name)) + 7


def _rng(seed: int) -> Callable[[], float]:
    """A tiny deterministic LCG yielding floats in [0, 1)."""
    state = seed % 2147483647 or 1

    def nxt() -> float:
        nonlocal state
        state = (state * 48271) % 2147483647
        return state / 2147483647.0

    return nxt


def _shape(seed: int, days: int) -> Callable[[int], float]:
    """Return level(offset) in fractional units (e.g. 0.06 == +6%).

    A signed linear trend plus decaying harmonics. Smooth by construction: the
    derivative of each low-frequency sine is small, so consecutive days move only
    a fraction of a percent and the line never spikes.
    """
    rng = _rng(seed)
    phases = [rng() * 2.0 * math.pi for _ in range(_OCTAVES)]
    jitter = [0.9 + rng() * 0.2 for _ in range(_OCTAVES)]  # mild per-skill variation
    trend_total = (rng() - 0.5) * 2.0 * _MAX_TREND  # some rise, some fall, some flat
    span = max(1, days - 1)

    def level(offset: int) -> float:
        x = offset / span  # 0 (oldest) -> 1 (today)
        value = trend_total * (x - 1.0)  # ends at 0 today; trend carried backwards
        amp, freq = _BASE_AMP, _BASE_FREQ
        for k in range(_OCTAVES):
            value += amp * math.sin(2.0 * math.pi * freq * jitter[k] * x + phases[k])
            amp *= _PERSISTENCE
            freq *= _FREQ_MULT
        return value

    return level


def seeded_history(name: str, current_price: float, days: int = 90) -> list[dict[str, float]]:
    """Daily price points ending exactly at ``current_price`` (day 0 = today)."""
    level = _shape(_seed(name), days)
    last_level = level(days - 1)
    points: list[dict[str, float]] = []
    for offset in range(days):
        factor = 1.0 + (level(offset) - last_level)
        price = max(1.0, round(current_price * factor, 2))
        day = -(days - 1 - offset)  # oldest negative -> 0 today
        points.append({"day": day, "price": price})
    # Anchor exactly to today's price regardless of rounding.
    if points:
        points[-1]["price"] = round(current_price, 2)
    return points


def history_stats(points: list[dict[str, float]], current_price: float) -> dict[str, Any]:
    prices = [point["price"] for point in points]
    high = max(prices)
    low = min(prices)
    first = prices[0]

    def _pct(old: float) -> float:
        return round((current_price - old) / old * 100, 1) if old else 0.0

    price_30 = prices[-31] if len(prices) >= 31 else first
    change_30d = _pct(price_30)
    change_90d = _pct(first)
    if change_30d > 1.5:
        trend = "uptrend"
    elif change_30d < -1.5:
        trend = "downtrend"
    else:
        trend = "rangebound"
    return {
        "high": round(high, 2),
        "low": round(low, 2),
        "first": round(first, 2),
        "last": round(current_price, 2),
        "change_30d": change_30d,
        "change_90d": change_90d,
        "trend": trend,
    }


def sparkline(name: str, current_price: float, points: int = 20) -> list[float]:
    """A short, downsampled series for inline sparklines."""
    history = seeded_history(name, current_price, days=90)
    step = max(1, len(history) // points)
    sampled = [history[index]["price"] for index in range(0, len(history), step)]
    if sampled[-1] != round(current_price, 2):
        sampled.append(round(current_price, 2))
    return sampled[-points:]


def source_badges(skill: dict[str, Any]) -> list[str]:
    """Honest source attribution badges for a skill row."""
    provenance = skill.get("provenance", "seeded")
    if provenance == "real_proxy":
        # Priced from the live MyCareersFuture salary sweep.
        return ["MyCareersFuture", "live"]
    rows = skill.get("source_rows") or []
    derived_mcf = any(str(row).startswith("mcf") for row in rows)
    return [("MyCareersFuture" if derived_mcf else "Catalogue"), "seeded"]


def attach_market_extras(market: dict[str, Any]) -> dict[str, Any]:
    """Add sparkline + 30d change + source badges to each skill row."""
    for skill in market.get("skills", []):
        price = float(skill.get("price", 0.0))
        spark = sparkline(skill["name"], price)
        skill["spark"] = spark
        old = spark[0] if spark else price
        skill["change_30d"] = round((price - old) / old * 100, 1) if old else 0.0
        skill["source_badges"] = source_badges(skill)
    return market
