"""Argument containers used to declare a plot before it is built.

The plot builders in this package take their configuration as objects rather
than as loose ``*args`` / ``**kwargs``, so a layer or a modifier can be stored,
passed around and replayed into seaborn later. These containers were previously
imported from a separate ``argin`` package; only the surface soplot actually
uses is kept here, so the package installs on its own.
"""

from __future__ import annotations

from typing import Any

__all__ = ["AkwArgs", "Args", "KwArgs", "arg_initializer"]


class Args(list):
    """A positional-argument list, distinguishable from a plain ``list``.

    The distinction is load-bearing: :func:`arg_initializer` reads an ``Args``
    as one entry per subplot, and any other value as a single setting meant for
    every subplot. ``Args(so.Bars(), so.Hist())`` holds two marks; ``[1, 2]``
    stays one value.
    """

    def __init__(self, *args: Any) -> None:
        super().__init__(args)


class KwArgs(dict):
    """A keyword-argument mapping, distinguishable from a plain ``dict``.

    Note that ``KwArgs(...) | {...}`` returns a plain ``dict`` -- PEP 584 does
    not preserve the subclass -- so callers merging defaults with overrides wrap
    the result again: ``KwArgs(**(defaults | overrides))``.
    """


class AkwArgs:
    """Positional and keyword arguments captured together to be replayed later.

    Subclasses add no behaviour; they name the call the arguments are destined
    for. ``SoPlot(data=df, x="tip")`` is later splatted into seaborn as
    ``so.Plot(*param.args, **param.kwargs)``.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = Args(*args)
        self.kwargs = KwArgs(**kwargs)

    def __repr__(self) -> str:
        parts = [repr(a) for a in self.args]
        parts += [f"{k}={v!r}" for k, v in self.kwargs.items()]
        return f"{type(self).__qualname__}({', '.join(parts)})"


def arg_initializer(parameter: Any, default_value: Any, replicate_number: int) -> Args:
    """Spread ``parameter`` over ``replicate_number`` subplots.

    An ``Args`` is read entry by entry; once its entries run out the last one
    repeats, so a single entry configures every subplot. An entry that is
    ``None`` falls back to ``default_value``. Any other value -- a scalar, a
    plain ``list``, a ``KwArgs`` -- is one setting repeated for every subplot.
    ``None`` and an empty ``Args`` both fall back to ``default_value``.

    Args:
        parameter: What the caller supplied, or ``None``.
        default_value: Stands in wherever the caller supplied nothing.
        replicate_number: How many subplots are being configured.

    Returns:
        An ``Args`` of exactly ``replicate_number`` entries.
    """
    if parameter is None or (isinstance(parameter, Args) and not parameter):
        return Args(*[default_value] * replicate_number)

    if not isinstance(parameter, Args):
        return Args(*[parameter] * replicate_number)

    last = len(parameter) - 1
    spread = Args()
    for index in range(replicate_number):
        value = parameter[min(index, last)]
        spread.append(default_value if value is None else value)
    return spread
