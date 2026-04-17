"""Unit tests for matadore.plugins.base."""

import pytest

from matadore.models.finding import RawFinding
from matadore.plugins.base import BasePlugin, PluginContext, PluginResult


class ConcretePlugin(BasePlugin):
    """Minimal concrete plugin for testing."""

    name = "test-plugin"
    supported_types = {"domain", "network"}

    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        return PluginResult(
            plugin=self.name,
            target=target,
            findings=[RawFinding(plugin=self.name, asset=target, raw="test output")],
        )


class WildcardPlugin(BasePlugin):
    """Plugin that accepts all target types (supported_types=None)."""

    name = "wildcard"

    def run(self, target: str, ctx: PluginContext) -> PluginResult:
        return PluginResult(plugin=self.name, target=target)


class TestBasePlugin:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            BasePlugin()

    def test_concrete_plugin_runs(self):
        p = ConcretePlugin()
        ctx = PluginContext()
        result = p.run("example.com", ctx)
        assert result.plugin == "test-plugin"
        assert result.target == "example.com"
        assert len(result.findings) == 1

    def test_supports_matching_type(self):
        p = ConcretePlugin()
        assert p.supports("domain") is True
        assert p.supports("network") is True

    def test_supports_non_matching_type(self):
        p = ConcretePlugin()
        assert p.supports("cloud") is False
        assert p.supports("repo") is False

    def test_wildcard_supports_all_types(self):
        p = WildcardPlugin()
        for t in ("domain", "network", "repo", "github_org", "cloud", "docker_registry"):
            assert p.supports(t) is True

    def test_repr(self):
        p = ConcretePlugin()
        assert "ConcretePlugin" in repr(p)
        assert "test-plugin" in repr(p)

    def test_async_run_delegates_to_sync(self):
        import asyncio

        p = ConcretePlugin()
        ctx = PluginContext()
        result = asyncio.run(p.run_async("example.com", ctx))
        assert result.target == "example.com"


class TestPluginContext:
    def test_defaults(self):
        ctx = PluginContext()
        assert ctx.mode == "active"
        assert ctx.dry_run is False
        assert ctx.extra == {}

    def test_custom_values(self):
        ctx = PluginContext(mode="stealth", dry_run=True, extra={"timeout": 30})
        assert ctx.mode == "stealth"
        assert ctx.dry_run is True
        assert ctx.extra["timeout"] == 30


class TestPluginResult:
    def test_defaults(self):
        r = PluginResult(plugin="nmap", target="10.0.0.1")
        assert r.findings == []
        assert r.skipped is False
        assert r.skip_reason == ""

    def test_skipped_result(self):
        r = PluginResult(plugin="nmap", target="10.0.0.1", skipped=True, skip_reason="dry_run")
        assert r.skipped is True
        assert r.skip_reason == "dry_run"
