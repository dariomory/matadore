"""Models for real-time streaming events emitted during an engagement."""

from __future__ import annotations

from typing import Callable

from pydantic import BaseModel


class StreamEvent(BaseModel):
    """A single finding or status event emitted during ``stream=True`` mode.

    Attributes:
        level: Severity label — ``"CRITICAL"``, ``"HIGH"``, ``"MEDIUM"``,
            ``"LOW"``, or ``"INFO"``.
        description: Human-readable description of what was found or observed.
        asset: The asset that triggered this event (URL, IP, file path, etc.).
        _halt: Internal callable to stop the engagement early.
    """

    level: str
    description: str
    asset: str = ""

    model_config = {"arbitrary_types_allowed": True}

    _halt_fn: Callable[[], None] | None = None

    def halt(self) -> None:
        """Stop the running engagement immediately.

        Safe to call from inside a ``for event in m.engage(..., stream=True)``
        loop — the generator will stop after this event is yielded.
        """
        if self._halt_fn is not None:
            self._halt_fn()
