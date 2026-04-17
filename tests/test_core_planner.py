"""Unit tests for matadore.core.planner."""

from matadore.core.planner import _SECS_PER_ASSET, EngagementPlan, PlanLine, build_plan
from matadore.inputs.base import EngageTarget
from matadore.plugins import GitLeaks, Nmap, Nuclei


class TestPlanLine:
    def test_defaults(self):
        line = PlanLine(tag="DOMAIN", description="Will resolve example.com")
        assert line.asset_count == 1

    def test_custom_asset_count(self):
        line = PlanLine(tag="NETWORK", description="Will probe 254 hosts", asset_count=254)
        assert line.asset_count == 254


class TestEngagementPlan:
    def _make_plan(self, mode: str = "active", asset_counts: list[int] | None = None) -> EngagementPlan:
        target = EngageTarget(value="example.com", mode=mode, dry_run=True)
        plan = EngagementPlan(target=target)
        for count in asset_counts or [10]:
            plan.lines.append(PlanLine(tag="DOMAIN", description="desc", asset_count=count))
        return plan

    def test_total_assets_single_line(self):
        plan = self._make_plan(asset_counts=[5])
        assert plan.total_assets == 5

    def test_total_assets_multiple_lines(self):
        plan = self._make_plan(asset_counts=[10, 5, 0])
        assert plan.total_assets == 15

    def test_estimated_duration_active(self):
        plan = self._make_plan(mode="active", asset_counts=[1])
        assert "8" in plan.estimated_duration

    def test_estimated_duration_passive_is_faster(self):
        active_secs = 10 * _SECS_PER_ASSET["active"]
        passive_secs = 10 * _SECS_PER_ASSET["passive"]
        assert passive_secs < active_secs

    def test_estimated_duration_shows_minutes_for_large_scope(self):
        plan = self._make_plan(mode="active", asset_counts=[100])
        assert "min" in plan.estimated_duration

    def test_estimated_duration_shows_seconds_for_small_scope(self):
        plan = self._make_plan(mode="active", asset_counts=[1])
        assert "s" in plan.estimated_duration

    def test_show_does_not_raise(self, capsys):
        plan = self._make_plan()
        plan.show()
        out = capsys.readouterr().out
        assert "Total assets" in out

    def test_to_text_contains_target(self):
        plan = self._make_plan()
        text = plan.to_text()
        assert "example.com" in text

    def test_to_text_contains_total_assets(self):
        plan = self._make_plan(asset_counts=[7])
        text = plan.to_text()
        assert "7" in text

    def test_to_text_contains_mode(self):
        plan = self._make_plan(mode="stealth")
        text = plan.to_text()
        assert "stealth" in text

    def test_to_text_contains_proceed_line(self):
        plan = self._make_plan()
        text = plan.to_text()
        assert "proceed" in text.lower()

    def test_plugins_active_listed(self):
        plan = self._make_plan()
        plan.plugins_active = ["nmap", "nuclei"]
        text = plan.to_text()
        assert "nmap" in text
        assert "nuclei" in text


class TestBuildPlan:
    def test_domain_target(self):
        t = EngageTarget(value="example.com", dry_run=True)
        plan = build_plan(t)
        assert len(plan.lines) >= 1
        assert plan.lines[0].tag == "DOMAIN"
        assert "example.com" in plan.lines[0].description

    def test_network_target_counts_hosts(self):
        t = EngageTarget(value="192.168.1.0/24", type="network", dry_run=True)
        plan = build_plan(t)
        assert plan.lines[0].asset_count == 254

    def test_repo_target(self):
        t = EngageTarget(value="myorg/myrepo", type="repo", dry_run=True)
        plan = build_plan(t)
        assert plan.lines[0].tag == "REPO"

    def test_cloud_target(self):
        t = EngageTarget(value="my-account", type="cloud", dry_run=True, extra={"provider": "aws"})
        plan = build_plan(t)
        assert plan.lines[0].tag == "CLOUD"

    def test_unknown_type_does_not_raise(self):
        # Bypass EngageTarget validation to test planner resilience.
        t = EngageTarget(value="x", dry_run=True)
        object.__setattr__(t, "type", "unknown_type")
        plan = build_plan(t)
        assert plan.total_assets == 0

    def test_with_matching_plugins(self):
        t = EngageTarget(value="example.com", type="domain", dry_run=True)
        plan = build_plan(t, plugins=[Nmap(), Nuclei()])
        assert "nmap" in plan.plugins_active
        assert "nuclei" in plan.plugins_active
        assert len(plan.lines) == 3  # 1 input + 2 plugins

    def test_non_matching_plugins_excluded(self):
        t = EngageTarget(value="example.com", type="domain", dry_run=True)
        plan = build_plan(t, plugins=[GitLeaks()])
        assert plan.plugins_active == []
        assert len(plan.lines) == 1  # only input line

    def test_no_plugins(self):
        t = EngageTarget(value="example.com", dry_run=True)
        plan = build_plan(t, plugins=None)
        assert plan.plugins_active == []

    def test_plan_to_text_is_string(self):
        t = EngageTarget(value="example.com", dry_run=True)
        plan = build_plan(t)
        assert isinstance(plan.to_text(), str)
        assert len(plan.to_text()) > 0
