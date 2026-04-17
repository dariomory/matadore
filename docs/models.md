# Domain Models

Matadore's data layer is built entirely on [Pydantic](https://docs.pydantic.dev/) v2 models.
Every finding, attack path, and report object is fully typed and validated - the AI cannot
assert a claim without a verifiable `Evidence` reference.

![Domain model diagram](assets/models.png)

## Package layout

```
src/matadore/models/
├── finding.py      # Evidence, RawFinding, Vulnerability
├── attack_path.py  # AttackPath
├── report.py       # Report, Brief
├── events.py       # StreamEvent
└── audit.py        # AuditEntry, AuditLog
```

All models are re-exported from `matadore.models` so you can import from either location:

```python
from matadore.models import Evidence, Vulnerability, AttackPath, Report
```

## Models

::: matadore.models.finding
::: matadore.models.attack_path
::: matadore.models.report
::: matadore.models.events
::: matadore.models.audit
