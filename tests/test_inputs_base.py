"""Unit tests for matadore.inputs.base."""

import pytest

from matadore.inputs.base import BaseInput, EngageTarget, ResolvedAsset


class ConcreteInput(BaseInput):
    target_type = "domain"

    def resolve(self, target: EngageTarget) -> list[ResolvedAsset]:
        return [ResolvedAsset(asset=target.value, asset_type="domain")]


class TestEngageTarget:
    def test_defaults(self):
        t = EngageTarget(value="example.com")
        assert t.type == "domain"
        assert t.mode == "active"
        assert t.dry_run is False
        assert t.stream is False
        assert t.extra == {}

    def test_all_valid_types_accepted(self):
        for typ in ("domain", "network", "repo", "github_org", "cloud", "docker_registry"):
            t = EngageTarget(value="x", type=typ)
            assert t.type == typ

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="Unknown target type"):
            EngageTarget(value="x", type="foobar")

    def test_all_valid_modes_accepted(self):
        for mode in ("passive", "active", "stealth"):
            t = EngageTarget(value="x", mode=mode)
            assert t.mode == mode

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="Unknown scan mode"):
            EngageTarget(value="x", mode="aggressive")

    def test_extra_forwarded(self):
        t = EngageTarget(value="my-account", type="cloud", extra={"provider": "gcp"})
        assert t.extra["provider"] == "gcp"

    def test_dry_run_flag(self):
        t = EngageTarget(value="x", dry_run=True)
        assert t.dry_run is True


class TestResolvedAsset:
    def test_create_minimal(self):
        a = ResolvedAsset(asset="192.168.1.1", asset_type="ip")
        assert a.asset == "192.168.1.1"
        assert a.asset_type == "ip"
        assert a.metadata == {}

    def test_create_with_metadata(self):
        a = ResolvedAsset(asset="example.com", asset_type="domain", metadata={"ttl": 300})
        assert a.metadata["ttl"] == 300


class TestBaseInput:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BaseInput()  # type: ignore[abstract]

    def test_concrete_resolve(self):
        inp = ConcreteInput()
        t = EngageTarget(value="example.com")
        assets = inp.resolve(t)
        assert len(assets) == 1
        assert assets[0].asset == "example.com"

    def test_async_resolve_delegates_to_sync(self):
        import asyncio

        inp = ConcreteInput()
        t = EngageTarget(value="example.com")
        assets = asyncio.run(inp.resolve_async(t))
        assert assets[0].asset == "example.com"

    def test_describe_default(self):
        inp = ConcreteInput()
        t = EngageTarget(value="example.com")
        desc = inp.describe(t)
        assert "example.com" in desc

    def test_repr(self):
        inp = ConcreteInput()
        assert "ConcreteInput" in repr(inp)
        assert "domain" in repr(inp)
