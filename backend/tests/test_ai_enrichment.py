import asyncio

from backend.app import ai_enrichment


def test_no_ai_enrichment_adapter_is_noop(monkeypatch):
    monkeypatch.setattr(ai_enrichment.openai_client, 'is_text_ai_enabled', lambda *args, **kwargs: False)

    adapter = ai_enrichment.adapter_for_session({'player_id': 'no_ai'})

    assert isinstance(adapter, ai_enrichment.NoAiEnrichmentAdapter)
    assert asyncio.run(adapter.enrich_chart_analysis({}, {})) is None
    assert asyncio.run(adapter.enrich_prelude({}, {})) is None
