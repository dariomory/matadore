"""Matadore core -- the Brain.

Orchestrates the full engagement lifecycle:

- :mod:`~matadore.core.engine`   -- top-level ``engage()`` dispatch
- :mod:`~matadore.core.planner`  -- ``dry_run=True`` scope preview
- :mod:`~matadore.core.reasoner` -- LLM-powered adversarial analysis
- :mod:`~matadore.core.chainer`  -- kill chain and attack path construction
- :mod:`~matadore.core.streamer` -- async event generator for ``stream=True``
"""
