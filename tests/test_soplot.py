"""Tests for the plot builders and the helpers they were vendored from.

The plots are never displayed: matplotlib runs on the Agg backend and the
assertions read the declaration a builder returns, not pixels. Data is
synthetic and seeded, so a failure means the code changed, not the sample.
"""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import seaborn.objects as so

import soplot
from soplot import MDF, SO, Args, FigureModifyError, KwArgs, SoLayer, UnexpectedTypeError
from soplot._stats import Agg, get_iqr_bounds
from soplot._types import arg_initializer

# No display: the assertions read what a builder declares, never a rendered pixel.
matplotlib.use("Agg")

SEED = 20260914


@pytest.fixture
def frame() -> pd.DataFrame:
    """A frame with one tame column, one column carrying outliers, one label."""
    rng = np.random.default_rng(SEED)
    return pd.DataFrame(
        {
            "tame": rng.normal(3, 1, 120),
            "spiky": np.concatenate([rng.normal(3, 1, 118), [40.0, -40.0]]),
            "group": rng.choice(["a", "b"], 120),
        }
    )


def marks_of(plot: so.Plot) -> list[str]:
    """Names of the marks a plot declares, in order.

    Reads a private seaborn attribute on purpose: it is the only way to see a
    layer without drawing it. Kept in one place so a seaborn change breaks one
    function rather than every test.
    """
    return [type(layer["mark"]).__name__ for layer in plot._layers]


def stats_of(plot: so.Plot) -> list[object]:
    """The aggregation function of each layer, or None where there is no stat."""
    return [getattr(layer.get("stat"), "func", None) for layer in plot._layers]


class RecordingPlot:
    """Stands in for ``so.Plot`` and records which modifier method was called.

    ``modify_plot`` never inspects the plot it is given, so a recorder is
    enough -- and it pins the routing without depending on seaborn internals.
    """

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def _record(self, name: str):
        def method(*args, **kwargs):
            self.calls.append((name, kwargs or args))
            return self
        return method

    def __getattr__(self, name: str):
        if name in {"scale", "facet", "pair", "layout", "label", "limit", "share", "theme"}:
            return self._record(name)
        raise AttributeError(name)


# --------------------------------------------------------------------------
# arg_initializer -- the spread that every multi-feature builder depends on
# --------------------------------------------------------------------------

def test_args_entries_are_spread_one_per_slot():
    assert arg_initializer(Args("x", "y", "z"), "D", 3) == ["x", "y", "z"]


def test_last_args_entry_repeats_once_the_entries_run_out():
    assert arg_initializer(Args("x", "y"), "D", 4) == ["x", "y", "y", "y"]


def test_none_falls_back_to_the_default():
    assert arg_initializer(None, "D", 2) == ["D", "D"]
    assert arg_initializer(Args("x", None), "D", 2) == ["x", "D"]


def test_empty_args_falls_back_instead_of_raising():
    # Used to raise IndexError: the empty list was indexed before it was checked.
    assert arg_initializer(Args(), "D", 3) == ["D", "D", "D"]


@pytest.mark.parametrize("value", [True, "x", [1, 2], KwArgs(a=1)])
def test_a_non_args_value_is_replicated_not_discarded(value):
    # Used to be dropped and silently replaced by the default value.
    assert arg_initializer(value, "D", 3) == [value, value, value]


# --------------------------------------------------------------------------
# get_iqr_bounds -- whisker bounds, not bare Tukey fences
# --------------------------------------------------------------------------

def test_bounds_are_clipped_to_the_observed_range():
    data = np.arange(20.0)  # no outliers: both fences fall outside the data
    assert get_iqr_bounds(data) == (data.min(), data.max())


def test_an_outlier_is_left_outside_the_bounds():
    data = np.array([1.0, 1.1, 1.2, 1.3, 1.4, 9.0])
    lower, upper = get_iqr_bounds(data)
    assert upper < 9.0
    assert lower == data.min()


def test_wider_percentiles_widen_the_bounds(frame):
    narrow = get_iqr_bounds(frame["spiky"], (25.0, 75.0))
    wide = get_iqr_bounds(frame["spiky"], (10.0, 90.0))
    assert wide[0] < narrow[0]
    assert wide[1] > narrow[1]


def test_a_column_without_outliers_is_clipped_whatever_the_percentiles():
    # Both fences fall outside an even spread, so every pair returns min and max.
    data = np.arange(100.0)
    assert get_iqr_bounds(data, (10.0, 90.0)) == get_iqr_bounds(data) == (0.0, 99.0)


def test_a_constant_column_has_no_spread():
    data = np.full(10, 7.0)
    assert get_iqr_bounds(data) == (7.0, 7.0)


def test_agg_helpers_return_the_two_bounds(frame):
    lower, upper = get_iqr_bounds(frame["spiky"])
    assert Agg.lower_outlier_bound(frame["spiky"]) == lower
    assert Agg.upper_outlier_bound(frame["spiky"]) == upper


# --------------------------------------------------------------------------
# histogram
# --------------------------------------------------------------------------

def test_histogram_carries_both_the_bars_and_the_density(frame):
    assert marks_of(SO.histogram(data=frame, feature="tame")) == ["Bars", "Area"]


def test_histogram_without_a_kde_layer_is_bars_alone(frame):
    assert marks_of(SO.histogram(data=frame, feature="tame", kde_layer=None)) == ["Bars"]


def test_histogram_takes_the_kde_layer_it_is_given(frame):
    plot = SO.histogram(data=frame, feature="tame", kde_layer=SoLayer(so.Line(), so.KDE()))
    assert marks_of(plot) == ["Bars", "Line"]


# --------------------------------------------------------------------------
# outlier_box
# --------------------------------------------------------------------------

def test_outlier_box_draws_the_sample_and_five_reference_marks(frame):
    assert marks_of(SO.outlier_box(data=frame, feature="spiky")) == [
        "Dot", "Range", "Dash", "Dash", "Dash", "Dash",
    ]


def test_outlier_box_aggregates_with_the_whisker_bounds(frame):
    funcs = stats_of(SO.outlier_box(data=frame, feature="spiky"))
    assert Agg.upper_outlier_bound in funcs
    assert Agg.lower_outlier_bound in funcs
    assert "mean" in funcs
    assert "median" in funcs


def test_band_view_swaps_the_sample_for_a_band(frame):
    assert marks_of(SO.outlier_box(data=frame, feature="spiky", band_view=True))[0] == "Dash"


# --------------------------------------------------------------------------
# modify_plot
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("modifier", "expected"),
    [
        (MDF.Scale(x="log"), "scale"),
        (MDF.Facet(col="group"), "facet"),
        (MDF.Pair(x=["tame"]), "pair"),
        (MDF.Layout(size=(3, 3)), "layout"),
        (MDF.Label(title="t"), "label"),
        (MDF.Limit(x=(0, 4)), "limit"),
        (MDF.Share(x=True), "share"),
        (MDF.Theme({"axes.facecolor": "w"}), "theme"),
    ],
)
def test_each_modifier_reaches_its_own_plot_method(modifier, expected):
    recorder = RecordingPlot()
    SO.modify_plot(recorder, modifier)
    assert [name for name, _ in recorder.calls] == [expected]


def test_modifiers_are_applied_in_order():
    recorder = RecordingPlot()
    SO.modify_plot(recorder, MDF.Label(title="t"), MDF.Scale(x="log"), MDF.Limit(x=(0, 4)))
    assert [name for name, _ in recorder.calls] == ["label", "scale", "limit"]


def test_an_empty_placeholder_is_accepted_and_applies_nothing():
    # The multi-feature builders pass an empty KwArgs to mean "no modifier here".
    recorder = RecordingPlot()
    SO.modify_plot(recorder, KwArgs())
    assert recorder.calls == []


def test_an_empty_theme_is_not_applied():
    recorder = RecordingPlot()
    SO.modify_plot(recorder, MDF.Theme())
    assert recorder.calls == []


def test_a_foreign_modifier_is_refused(frame):
    with pytest.raises(UnexpectedTypeError) as caught:
        SO.modify_plot(so.Plot(frame, x="tame"), "not a modifier")
    assert "str" in str(caught.value)


def test_the_error_is_also_a_type_error(frame):
    # Calling code that already guards against TypeError keeps working.
    with pytest.raises(TypeError):
        SO.modify_plot(so.Plot(frame, x="tame"), 42)


def test_modify_plot_leaves_the_original_plot_alone(frame):
    plot = so.Plot(frame, x="tame")
    modified = SO.modify_plot(plot, MDF.Scale(x="log"))
    assert modified is not plot
    assert plot._scales == {}


# --------------------------------------------------------------------------
# add_layers
# --------------------------------------------------------------------------

def test_layers_are_added_in_order(frame):
    plot = SO.add_layers(so.Plot(frame, x="tame"), SoLayer(so.Bars(), so.Hist()), SoLayer(so.Dot()))
    assert marks_of(plot) == ["Bars", "Dot"]


def test_a_missing_layer_is_skipped(frame):
    plot = SO.add_layers(so.Plot(frame, x="tame"), None, SoLayer(so.Dot()))
    assert marks_of(plot) == ["Dot"]


# --------------------------------------------------------------------------
# feature / subfigure pairing
# --------------------------------------------------------------------------

def test_compare_plot_refuses_fewer_subfigures_than_features(frame):
    # Zipping used to stop at the shorter side: the third plot was dropped in
    # silence. Losing a plot without a word is worse than failing.
    figure = plt.figure()
    with pytest.raises(ValueError):
        SO.compare_plot(
            data=frame,
            variable="tame",
            features=["spiky", "tame", "group"],
            sub_figures=figure.subfigures(1, 2),
            layers=Args(Args(SoLayer(so.Dot()))),
        )
    plt.close(figure)


def test_multi_outlier_box_refuses_fewer_subfigures_than_features(frame):
    figure = plt.figure()
    with pytest.raises(ValueError):
        SO.multi_outlier_box(
            data=frame,
            features=["spiky", "tame", "spiky"],
            sub_figures=figure.subfigures(1, 2),
        )
    plt.close(figure)


def test_matching_counts_are_drawn(frame):
    figure = plt.figure()
    SO.multi_outlier_box(
        data=frame, features=["spiky", "tame"], sub_figures=figure.subfigures(1, 2)
    )
    assert all(subfigure.axes for subfigure in figure.subfigs)
    plt.close(figure)


# --------------------------------------------------------------------------
# add_barlabel
# --------------------------------------------------------------------------

def test_every_bar_gets_a_label(frame):
    figure = plt.figure()
    so.Plot(frame, x="group").add(so.Bar(), so.Hist()).on(figure).plot(pyplot=True)
    labelled = soplot.add_barlabel(figure)
    assert labelled is figure
    assert sum(len(axes.texts) for axes in figure.axes) == 2
    plt.close(figure)


def test_a_figure_that_cannot_be_labelled_raises_and_keeps_the_cause():
    class NotAFigure:
        pass

    with pytest.raises(FigureModifyError) as caught:
        soplot.add_barlabel(NotAFigure())
    assert isinstance(caught.value.__cause__, AttributeError)


# --------------------------------------------------------------------------
# the package surface
# --------------------------------------------------------------------------

def test_star_import_exposes_exactly_the_declared_names():
    namespace: dict[str, object] = {}
    exec("from soplot import *", namespace)
    assert sorted(n for n in namespace if not n.startswith("__")) == sorted(soplot.__all__)


@pytest.mark.parametrize("name", ["so", "np", "arg_initializer", "Agg", "get_iqr_bounds"])
def test_internal_names_stay_inside(name):
    assert not hasattr(soplot, name)
