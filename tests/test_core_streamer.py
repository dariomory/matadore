"""Unit tests for matadore.core.streamer."""

import asyncio

import pytest

from matadore.core.streamer import SEVERITY_ORDER, Streamer
from matadore.models.events import StreamEvent


async def collect(streamer: Streamer) -> list[StreamEvent]:
    """Drain all events from a streamer into a list."""
    events = []
    async for event in streamer:
        events.append(event)
    return events


class TestSeverityOrder:
    def test_critical_is_highest(self):
        assert SEVERITY_ORDER["CRITICAL"] < SEVERITY_ORDER["HIGH"]

    def test_info_is_lowest(self):
        assert SEVERITY_ORDER["INFO"] > SEVERITY_ORDER["LOW"]

    def test_full_order(self):
        order = [SEVERITY_ORDER[k] for k in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")]
        assert order == sorted(order)


class TestStreamer:
    def test_default_not_halted(self):
        s = Streamer()
        assert s.halted is False

    def test_halt_sets_flag(self):
        s = Streamer()
        s.halt()
        assert s.halted is True

    def test_emit_and_consume_single_event(self):
        async def _run():
            s = Streamer()
            await s.emit(level="HIGH", description="SSH key found.", asset="repo/infra")
            await s.close()
            events = await collect(s)
            assert len(events) == 1
            assert events[0].level == "HIGH"
            assert events[0].description == "SSH key found."
            assert events[0].asset == "repo/infra"

        asyncio.run(_run())

    def test_emit_multiple_events(self):
        async def _run():
            s = Streamer()
            await s.emit(level="CRITICAL", description="Exposed .env", asset="api.example.com")
            await s.emit(level="HIGH", description="SSH open", asset="10.0.0.1")
            await s.emit(level="INFO", description="Subdomain found", asset="staging.example.com")
            await s.close()
            events = await collect(s)
            assert len(events) == 3

        asyncio.run(_run())

    def test_level_filtering_drops_below_min(self):
        async def _run():
            s = Streamer(min_level="HIGH")
            await s.emit(level="CRITICAL", description="critical")
            await s.emit(level="HIGH", description="high")
            await s.emit(level="MEDIUM", description="medium - should be dropped")
            await s.emit(level="INFO", description="info - should be dropped")
            await s.close()
            events = await collect(s)
            assert len(events) == 2
            assert {e.level for e in events} == {"CRITICAL", "HIGH"}

        asyncio.run(_run())

    def test_level_filtering_critical_only(self):
        async def _run():
            s = Streamer(min_level="CRITICAL")
            await s.emit(level="CRITICAL", description="only this")
            await s.emit(level="HIGH", description="dropped")
            await s.close()
            events = await collect(s)
            assert len(events) == 1
            assert events[0].level == "CRITICAL"

        asyncio.run(_run())

    def test_emit_after_halt_is_noop(self):
        async def _run():
            s = Streamer()
            await s.emit(level="INFO", description="before halt")
            s.halt()
            await s.emit(level="INFO", description="after halt - dropped")
            events = await collect(s)
            assert len(events) == 1
            assert events[0].description == "before halt"

        asyncio.run(_run())

    def test_halt_via_event_fn(self):
        async def _run():
            s = Streamer()
            await s.emit(level="CRITICAL", description="trigger halt")
            await s.emit(level="HIGH", description="may not arrive")
            await s.close()
            events = []
            async for event in s:
                events.append(event)
                event.halt()
            assert events[0].level == "CRITICAL"
            assert s.halted is True

        asyncio.run(_run())

    def test_event_halt_fn_is_bound(self):
        async def _run():
            s = Streamer()
            await s.emit(level="INFO", description="test")
            await s.close()
            async for event in s:
                assert event._halt_fn is not None
                break

        asyncio.run(_run())

    def test_level_uppercased(self):
        async def _run():
            s = Streamer()
            await s.emit(level="critical", description="lowercase level")
            await s.close()
            events = await collect(s)
            assert events[0].level == "CRITICAL"

        asyncio.run(_run())

    def test_sync_iter(self):
        loop = asyncio.new_event_loop()

        async def _produce(s: Streamer) -> None:
            await s.emit(level="HIGH", description="sync test")
            await s.close()

        s = Streamer()
        loop.run_until_complete(_produce(s))
        events = list(s.sync_iter(loop=loop))
        loop.close()

        assert len(events) == 1
        assert events[0].description == "sync test"

    def test_empty_stream_yields_nothing(self):
        async def _run():
            s = Streamer()
            await s.close()
            events = await collect(s)
            assert events == []

        asyncio.run(_run())

    def test_halt_on_empty_queue_does_not_raise(self):
        s = Streamer()
        s.halt()
        assert s.halted is True
