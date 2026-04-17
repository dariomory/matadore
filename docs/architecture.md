# Architecture

![High-level architecture](assets/architecture.png)

## Overview

Matadore is structured in five distinct layers:

| Layer | Package | Responsibility |
|---|---|---|
| Entry points | `cli.py`, `__init__.py` | CLI and SDK surface |
| Core / Brain | `core/` | Orchestration, LLM reasoning, kill chain construction |
| Inputs | `inputs/` | Expand targets into concrete scannable assets |
| Plugins | `plugins/` | Wrappers over best-in-class scanning tools |
| Models | `models/` | Typed Pydantic domain objects with mandatory Evidence |
| State | `state/` | Caching and diff scanning (SQLite / DuckDB) |
| Report | `report/` | Assembly, narrative brief, and multi-format export |

## Core -- The Brain

The `core/` package drives the full engagement lifecycle:

- **`engine.py`** -- top-level `engage()` orchestration
- **`planner.py`** -- `dry_run=True` scope preview
- **`reasoner.py`** -- LLM-powered adversarial analysis via [LiteLLM](https://github.com/BerriAI/litellm)
- **`chainer.py`** -- kill chain and attack path construction
- **`streamer.py`** -- async event generator for `stream=True` mode

`asyncio` is used throughout the mapping phase so 100 IPs scan in parallel, not in sequence.

## Plugins -- The Eyes

Matadore does not re-implement what nmap, nuclei, and trivy already do well -- it reasons over their output.

| Plugin | Tool | Target types |
|---|---|---|
| `Nmap` | [nmap](https://nmap.org/) | `domain`, `network` |
| `Nuclei` | [projectdiscovery/nuclei](https://github.com/projectdiscovery/nuclei) | `domain`, `network` |
| `Trivy` | [aquasecurity/trivy](https://github.com/aquasecurity/trivy) | `docker_registry`, `repo` |
| `GitLeaks` | [gitleaks](https://github.com/gitleaks/gitleaks) | `repo`, `github_org` |
| `ScoutSuite` | [nccgroup/ScoutSuite](https://github.com/nccgroup/ScoutSuite) | `cloud` |

Extend with your own scanner by subclassing `BasePlugin`.

## State and Caching

| Backend | Package | Best for |
|---|---|---|
| `SQLiteStore` | stdlib only | Local single-user engagements |
| `DuckDBStore` | requires `pip install duckdb` | Team-shared, persistent across operators |

Matadore caches `AssetSnapshot` records keyed by `(engagement_id, asset)`.
On repeated scans only assets whose checksum changed are re-processed.

## Domain Model

See the [Domain Models](models.md) page for the full Pydantic model diagram.
