"""Outlier bounds for the box and histogram builders.

Ported from a separate ``matstat`` package so soplot installs on its own. Only
the surface soplot calls is kept: ``get_percentile_of_scores`` stayed behind,
and with it the ``scipy`` dependency it was the sole reason for.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np

__all__ = ["Agg", "get_iqr_bounds"]


def get_iqr_bounds(
    vector1d: Any, percentiles: Sequence[float] = (25.0, 75.0)
) -> tuple[float, float]:
    """Return the lower and upper whisker bound of ``vector1d``.

    Tukey's fences (``Q1 - 1.5 * IQR`` and ``Q3 + 1.5 * IQR``) clipped to the
    observed minimum and maximum -- matplotlib's whisker convention, not the
    bare fences. The clipping is the point: a bound drawn on a plot should sit
    on a value the sample actually reaches, so a fence that runs past the data
    is pulled back to the last observation.

    Args:
        vector1d: One-dimensional array-like of numbers.
        percentiles: The two percentiles bracketing the interquartile range.

    Returns:
        ``(lower_bound, upper_bound)``.
    """
    q1, q3 = np.percentile(vector1d, percentiles)
    iqr = q3 - q1
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)
    lower_bound = lower_bound if lower_bound >= min(vector1d) else min(vector1d)
    upper_bound = upper_bound if upper_bound <= max(vector1d) else max(vector1d)
    return lower_bound, upper_bound


class Agg:
    """Aggregation functions shaped for ``seaborn.objects.Agg(...)``.

    Each takes the values of one group and returns a single number, which is
    what ``so.Agg`` expects of a callable.
    """

    @staticmethod
    def lower_outlier_bound(data: Any) -> float:
        """Return the lower whisker bound of ``data``."""
        return get_iqr_bounds(data)[0]

    @staticmethod
    def upper_outlier_bound(data: Any) -> float:
        """Return the upper whisker bound of ``data``."""
        return get_iqr_bounds(data)[1]
