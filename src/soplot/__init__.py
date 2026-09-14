"""Repeatable seaborn.objects plots.

A plot is declared as objects -- a ``SoLayer`` per mark, an ``MDF`` per
modifier -- instead of as a long call, so the declaration can be stored, passed
around and replayed. The builders on :class:`SO` turn those declarations into
``seaborn.objects`` plots.

Nothing here is drawn on import, and nothing is logged: the package calls
``logger.disable("soplot")`` below, because configuring logging is the
application's business, not a library's. To see the records, the application
calls ``logger.enable("soplot")``.
"""

from loguru import logger

from soplot._errors import FigureModifyError, SoplotError, UnexpectedTypeError
from soplot._types import AkwArgs, Args, KwArgs
from soplot.soplot import MDF, SO, SoLayer, SoPlot, add_barlabel

__all__ = [
    "MDF",
    "SO",
    "AkwArgs",
    "Args",
    "FigureModifyError",
    "KwArgs",
    "SoLayer",
    "SoPlot",
    "SoplotError",
    "UnexpectedTypeError",
    "add_barlabel",
]

logger.disable("soplot")
