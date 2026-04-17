"""Dry-run planner -- shows exactly what an engagement will touch before
any active scanning begins.

Matches the README example output::

    plan = m.engage("mydomain.com", dry_run=True)
    plan.show()
    # [DOMAIN]   Will resolve and enumerate: mydomain.com + 14 discovered subdomains
    # [NETWORK]  Will probe: 192.168.1.12, 192.168.1.45 (skipping .0/broadcast)
    # [REPO]     Will clone (read-only): myorg/myrepo @ HEAD
    # [CLOUD]    Will call: ec2:DescribeInstances, s3:ListBuckets (read-only IAM)
    #
    # Total assets in scope: 31
    # Estimated duration: ~4 min (active mode)
    # Run m.engage("mydomain.com") to proceed.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from matadore.inputs import REGISTRY
from matadore.inputs.base import EngageTarget
from matadore.plugins.base import BasePlugin, PluginContext

# Rough seconds-per-asset estimates by mode, used for duration estimates.
_SECS_PER_ASSET: dict[str, float] = {
    "passive": 2.0,
    "active": 8.0,
    "stealth": 20.0,
}


@dataclass
class PlanLine:
    """A single line in the dry-run plan output.

    Attributes:
        tag: Uppercase label shown in brackets, e.g. ``"DOMAIN"``.
        description: Human-readable action description.
        asset_count: Estimated number of concrete assets this line covers.
    """

    tag: str
    description: str
    asset_count: int = 1


@dataclass
class EngagementPlan:
    """Dry-run plan for a single ``engage()`` call.

    Produced by :func:`build_plan` when ``dry_run=True``.  Callers print
    this with :meth:`show` or inspect it programmatically.

    Attributes:
        target: The parsed engagement target.
        lines: Ordered plan lines, one per input handler / plugin pair.
        plugins_active: Names of the plugins that would run.
    """

    target: EngageTarget
    lines: list[PlanLine] = field(default_factory=list)
    plugins_active: list[str] = field(default_factory=list)

    @property
    def total_assets(self) -> int:
        """Total estimated asset count across all plan lines."""
        return sum(line.asset_count for line in self.lines)

    @property
    def estimated_duration(self) -> str:
        """Human-readable estimated scan duration string."""
        secs = self.total_assets * _SECS_PER_ASSET.get(self.target.mode, 8.0)
        if secs < 60:
            return f"~{int(secs)}s"
        minutes = secs / 60
        return f"~{int(minutes)} min"

    def show(self) -> None:
        """Print the plan to stdout in the README-style format."""
        print(self._render())

    def to_text(self) -> str:
        """Return the plan as a plain-text string."""
        return self._render()

    def _render(self) -> str:
        rendered_lines = []
        for line in self.lines:
            rendered_lines.append(f"[{line.tag}]  {line.description}")

        rendered_lines.append("")
        rendered_lines.append(f"Total assets in scope: {self.total_assets}")
        rendered_lines.append(
            f"Estimated duration: {self.estimated_duration} ({self.target.mode} mode)"
        )

        if self.plugins_active:
            rendered_lines.append(f"Plugins: {', '.join(self.plugins_active)}")

        rendered_lines.append(
            f"Run m.engage({self.target.value!r}) to proceed."
        )
        return "\n".join(rendered_lines)


def build_plan(
    target: EngageTarget,
    plugins: list[BasePlugin] | None = None,
) -> EngagementPlan:
    """Build a dry-run :class:`EngagementPlan` for *target*.

    Resolves the correct input handler from :data:`~matadore.inputs.REGISTRY`,
    calls :meth:`~matadore.inputs.base.BaseInput.describe` to produce the
    human-readable action lines, and lists which plugins would run.

    Args:
        target: The parsed engagement target.  Must have ``dry_run=True``
            (enforced by the engine before calling this function).
        plugins: Optional list of plugin instances to include in the plan.
            When ``None`` no plugin lines are added.

    Returns:
        A fully populated :class:`EngagementPlan`.
    """
    plan = EngagementPlan(target=target)

    handler_cls = REGISTRY.get(target.type)
    if handler_cls is None:
        plan.lines.append(
            PlanLine(
                tag=target.type.upper(),
                description=f"Unknown target type -- no handler registered for {target.type!r}",
                asset_count=0,
            )
        )
        return plan

    handler = handler_cls()

    # Resolve dry-run assets to get an accurate count.
    dry_target = EngageTarget(
        value=target.value,
        type=target.type,
        mode=target.mode,
        dry_run=True,
        extra=target.extra,
    )
    try:
        assets = handler.resolve(dry_target)
        asset_count = len(assets)
    except NotImplementedError:
        asset_count = 1

    plan.lines.append(
        PlanLine(
            tag=target.type.upper(),
            description=handler.describe(target),
            asset_count=asset_count,
        )
    )

    # Add active plugins that support this target type.
    ctx = PluginContext(mode=target.mode, dry_run=True)
    active_plugins: list[str] = []
    for plugin in plugins or []:
        if plugin.supports(target.type):
            active_plugins.append(plugin.name)
            try:
                result = plugin.run(target.value, ctx)
                desc = result.skip_reason or f"Would run {plugin.name} against {target.value}"
            except NotImplementedError:
                desc = f"Would run {plugin.name} against {target.value}"

            plan.lines.append(
                PlanLine(
                    tag=plugin.name.upper(),
                    description=desc,
                    asset_count=0,
                )
            )

    plan.plugins_active = active_plugins
    return plan
