"""Async event streaming for real-time engagement output.

When ``m.engage(target, stream=True)`` is called the engine feeds findings
into a :class:`Streamer` as they arrive.  The caller iterates over the
yielded :class:`~matadore.models.events.StreamEvent` objects and can stop
the scan early by calling :meth:`~matadore.models.events.StreamEvent.halt`.

Typical usage inside the engine::

    streamer = Streamer()

    async def _run():
        async for asset in input_handler.resolve_async(target):
            result = await plugin.run_async(asset, ctx)
            for finding in result.findings:
                await streamer.emit(
                    level="HIGH",
                    description=finding.raw[:120],
                    asset=finding.asset,
                )

    asyncio.run(_run())

Caller-facing usage::

    for event in m.engage("mydomain.com", stream=True):
        print(f"[{event.level}] {event.description}")
        if "prod-db" in event.asset:
            event.halt()
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from typing import Any

from matadore.models.events import StreamEvent

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


class Streamer:
    """Async producer/consumer bridge for streaming engagement events.

    The engine calls :meth:`emit` as findings arrive; the caller iterates
    via :meth:`sync_iter` (blocking) or :meth:`__aiter__` (async).

    Args:
        min_level: Minimum severity level to emit.  Events below this
            threshold are silently dropped.  One of ``"CRITICAL"``,
            ``"HIGH"``, ``"MEDIUM"``, ``"LOW"``, ``"INFO"``.
        max_queue: Maximum number of buffered events before ``emit``
            blocks.  Prevents unbounded memory growth on slow consumers.
    """

    def __init__(self, min_level: str = "INFO", max_queue: int = 256) -> None:
        self._min_rank = SEVERITY_ORDER.get(min_level.upper(), 4)
        self._queue: asyncio.Queue[StreamEvent | None] = asyncio.Queue(maxsize=max_queue)
        self._halted = False

    @property
    def halted(self) -> bool:
        """``True`` after :meth:`halt` has been called."""
        return self._halted

    def halt(self) -> None:
        """Signal the streamer to stop after the current event.

        Safe to call from any thread or coroutine.
        """
        self._halted = True
        try:
            self._queue.put_nowait(None)
        except asyncio.QueueFull:
            pass

    async def emit(
        self,
        level: str,
        description: str,
        asset: str = "",
        **extra: Any,
    ) -> None:
        """Emit a single event into the stream.

        Dropped silently when the level is below ``min_level`` or after
        :meth:`halt` has been called.

        Args:
            level: Severity -- ``"CRITICAL"``, ``"HIGH"``, ``"MEDIUM"``,
                ``"LOW"``, or ``"INFO"``.
            description: Human-readable finding description.
            asset: Asset that triggered this event.
            **extra: Reserved for future structured metadata.
        """
        if self._halted:
            return
        rank = SEVERITY_ORDER.get(level.upper(), 4)
        if rank > self._min_rank:
            return

        event = StreamEvent(level=level.upper(), description=description, asset=asset)
        event._halt_fn = self.halt
        await self._queue.put(event)

    async def close(self) -> None:
        """Signal end-of-stream to the consumer.

        Call this once the engine has finished producing events.
        """
        await self._queue.put(None)

    async def __aiter__(self) -> AsyncIterator[StreamEvent]:
        """Async iterator -- yields events until the stream is closed."""
        while True:
            event = await self._queue.get()
            if event is None:
                break
            yield event
            if self._halted:
                break

    def sync_iter(self, loop: asyncio.AbstractEventLoop | None = None) -> Iterator[StreamEvent]:
        """Blocking iterator for use in synchronous caller code.

        This is what the public ``for event in m.engage(..., stream=True)``
        loop calls under the hood.

        Args:
            loop: Event loop to use.  Creates a new one if not provided.

        Yields:
            :class:`~matadore.models.events.StreamEvent` objects as they
            arrive.
        """
        _loop = loop or asyncio.new_event_loop()

        async def _next() -> StreamEvent | None:
            return await self._queue.get()

        while True:
            event = _loop.run_until_complete(_next())
            if event is None:
                break
            yield event
            if self._halted:
                break
