"""Errors raised by soplot, and the logging policy around them.

These replace a separate ``logerr`` package whose validation helper carried
three defects: one exception instance shared by every call site (built once, at
import time, as a default argument, then mutated by each use), an encoder whose
own failure path re-entered itself, and a ``print`` of the offending object's
whole state -- data frames included -- to stdout. Raising a plain exception
removes all three mechanisms rather than patching them.

Logging follows the library rule: soplot configures no sink and writes nowhere
by default. An error records itself once at DEBUG under loguru's ``soplot``
namespace, which :mod:`soplot` disables on import; an application that wants to
see it calls ``logger.enable("soplot")``.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

__all__ = ["FigureModifyError", "SoplotError", "UnexpectedTypeError"]


class SoplotError(Exception):
    """Base class for every error soplot raises.

    Args:
        message: What went wrong, in one line.
        hint: What the caller can change to fix it, where that is known.
        **context: Small values worth seeing beside the message, such as
            ``modifier=type(mdf).__name__``. Keep them descriptive -- they end
            up in the error text, so a frame or an array belongs here only as
            its shape or its type name, never as the data itself.
    """

    def __init__(self, message: str, *, hint: str | None = None, **context: Any) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.context: dict[str, Any] = context
        # depth=1 attributes the record to the line that raised, not to this file.
        logger.opt(depth=1).debug("{}: {}", type(self).__name__, self)

    def __str__(self) -> str:
        parts = [self.message]
        if self.context:
            parts.append(", ".join(f"{key}={value!r}" for key, value in self.context.items()))
        if self.hint:
            parts.append(f"hint: {self.hint}")
        return " | ".join(parts)


class UnexpectedTypeError(SoplotError, TypeError):
    """An argument is not of a type the builder can use.

    Also a :class:`TypeError`, so calling code that already guards against one
    keeps working.
    """


class FigureModifyError(SoplotError, RuntimeError):
    """A figure could not be modified after it was drawn."""
