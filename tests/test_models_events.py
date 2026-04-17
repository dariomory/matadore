"""Unit tests for matadore.models.events."""

import pytest
from pydantic import ValidationError

from matadore.models.events import StreamEvent


class TestStreamEvent:
    def test_create_minimal(self):
        e = StreamEvent(level="INFO", description="Subdomain discovered.")
        assert e.level == "INFO"
        assert e.description == "Subdomain discovered."
        assert e.asset == ""

    def test_create_with_asset(self):
        e = StreamEvent(level="CRITICAL", description="Exposed .env file.", asset="https://api.example.com/.env")
        assert e.asset == "https://api.example.com/.env"

    def test_missing_level_raises(self):
        with pytest.raises(ValidationError):
            StreamEvent(description="something")  # type: ignore[call-arg]

    def test_missing_description_raises(self):
        with pytest.raises(ValidationError):
            StreamEvent(level="HIGH")  # type: ignore[call-arg]

    def test_halt_without_fn_is_noop(self):
        e = StreamEvent(level="HIGH", description="SSH key found.")
        # Should not raise even though no _halt_fn is set
        e.halt()

    def test_halt_calls_fn(self):
        called = []

        e = StreamEvent(level="CRITICAL", description="prod-db exposed.")
        e._halt_fn = lambda: called.append(True)
        e.halt()

        assert called == [True]
