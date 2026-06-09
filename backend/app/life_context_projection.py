from __future__ import annotations

from typing import Any

from . import action_guide, half_year_resolution


def refresh_current_context(session: dict[str, Any], action_summaries: dict[str, str] | None = None) -> dict[str, Any]:
    """Refresh player-facing life context and advisory artifacts.

    Interface:
    - safe to call after any authoritative state mutation;
    - deterministic cycles, stage, life systems and goal progress stay behind
      the half-year resolution Module;
    - advisory action_guides and current_life projection are owned here.
    """
    half_year_resolution.refresh_authoritative_context(session)
    if session.get('current_age') is not None:
        session['action_guides'] = action_guide.build_decision_support(session, action_summaries)
    else:
        session['action_guides'] = []
    return build_current_life_projection(session)


def build_current_life_projection(session: dict[str, Any]) -> dict[str, Any]:
    """Build the display projection consumed by frontends and AI enrichment."""
    current_life = half_year_resolution.build_current_life_projection(session)
    current_life['行动预览'] = session.get('action_guides', [])
    session['current_life'] = current_life
    return current_life
