"""Matadore scanner plugins.

Built-in plugins wrap best-in-class open-source tools.  Matadore doesn't
re-implement what nmap, nuclei, and trivy already do well - it reasons over
their output.

Usage::

    from matadore.plugins import Nmap, Nuclei, Trivy, GitLeaks, ScoutSuite

    m = Matadore(
        model="gpt-4o",
        plugins=[Nmap(), Nuclei(), Trivy(), GitLeaks()],
    )

Write your own::

    from matadore.plugins import BasePlugin
    from matadore.models import RawFinding

    class MyScanner(BasePlugin):
        name = "my-scanner"

        def run(self, target: str) -> list[RawFinding]:
            ...
"""

from matadore.plugins.base import BasePlugin, PluginContext, PluginResult
from matadore.plugins.gitleaks import GitLeaks
from matadore.plugins.nmap import Nmap
from matadore.plugins.nuclei import Nuclei
from matadore.plugins.scoutsuite import ScoutSuite
from matadore.plugins.trivy import Trivy

__all__ = [
    "BasePlugin",
    "GitLeaks",
    "Nmap",
    "Nuclei",
    "PluginContext",
    "PluginResult",
    "ScoutSuite",
    "Trivy",
]
