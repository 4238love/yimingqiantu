import json
from pathlib import Path

from backend.app import game_logic


def test_state_schema_required_keys_match_new_session():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    session = game_logic._new_session('schema_player')

    missing = sorted(set(schema['required']) - set(session))

    assert missing == []


def test_state_schema_documents_mvp_life_state_fields():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    life_state = schema['definitions']['lifeState']['properties']

    assert set(life_state) == {
        '健康', '心智', '情绪', '学识', '事业', '财富',
        '家庭', '感情', '社交', '名望', '福德', '压力',
    }


def test_state_schema_start_age_minimum_is_six():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))

    assert schema['properties']['start_age']['minimum'] == 6


def test_state_schema_parses_and_tracks_annual_summary_metadata():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    annual_item = schema['properties']['annual_summaries']['items']['properties']

    assert {
        'age',
        'year',
        'half',
        'half_label',
        'summary',
        'state_effect',
        'focuses',
        'main_focus',
        'roll_event',
        'roll_modifiers',
        'state_before',
        'state_after',
        'luck_cycle',
        'annual_cycle',
        'monthly_cycles',
        'gm_narrative',
        'gm_state_update_suggestion',
        'long_term_impact',
        'memory_tags',
    } <= set(annual_item)


def test_state_schema_tracks_flowing_month_and_half_year_fields():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    properties = schema['properties']
    cycle_properties = schema['definitions']['pillarCycle']['properties']
    half_item = properties['half_year_summaries']['items']['properties']

    assert {
        'monthly_cycles',
        'current_half',
        'current_half_label',
        'current_monthly_cycles',
        'half_year_summaries',
    } <= set(properties)
    assert {'month', 'month_name', 'half', 'age_start_months', 'age_end_months', 'age_start_label', 'age_end_label'} <= set(cycle_properties)
    assert {'half', 'half_label', 'monthly_cycles'} <= set(half_item)


def test_state_schema_tracks_stage_systems_and_ending_archive():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    properties = schema['properties']
    half_item = properties['half_year_summaries']['items']['properties']
    ending_props = properties['ending']['anyOf'][1]['properties']

    assert {'current_stage', 'life_systems', 'ending_reason', 'ending_codex'} <= set(properties)
    assert {'stage_event', 'stage_label', 'life_systems_after', 'relationships_after'} <= set(half_item)
    assert {'reason', 'dimensions', 'achievements', 'regrets', 'key_turning_points', 'life_systems', 'relationships', 'hidden_ending', 'hidden_endings', 'codex_unlocks', 'codex_progress'} <= set(ending_props)


def test_state_schema_tracks_life_goal_fields():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    properties = schema['properties']
    half_item = properties['half_year_summaries']['items']['properties']
    ending_props = properties['ending']['anyOf'][1]['properties']

    assert {'life_goals', 'active_life_goal_id', 'goal_progress'} <= set(properties)
    assert {'goal_progress_before', 'goal_progress_after'} <= set(half_item)
    assert {'life_goal', 'life_goal_achieved'} <= set(ending_props)


def test_state_schema_tracks_achievements_and_milestones():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    properties = schema['properties']
    half_item = properties['half_year_summaries']['items']['properties']
    ending_props = properties['ending']['anyOf'][1]['properties']

    assert {'achievements', 'latest_achievements', 'milestones'} <= set(properties)
    assert {'new_achievements', 'milestone'} <= set(half_item)
    assert {'achievements_unlocked', 'milestones'} <= set(ending_props)


def test_state_schema_documents_luck_start_fields_on_chart():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    chart_properties = schema['definitions']['baziChart']['properties']

    assert {'luck_start_label', 'luck_start_months'} <= set(chart_properties)


def test_state_schema_documents_bazi_analysis_fields():
    schema = json.loads(Path('backend/app/state.schema.json').read_text(encoding='utf-8'))
    analysis = schema['definitions']['baziAnalysis']['properties']

    assert {
        'five_element_balance',
        'day_master_status',
        'useful_elements',
        'unfavorable_elements',
        'ten_god_focus',
        'luck_cycle_themes',
        'life_topics',
        'suitable_directions',
        'high_risk_fields',
        'chart_tags',
        'source',
    } <= set(analysis)
