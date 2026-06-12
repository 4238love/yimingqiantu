let appState;

export function createArchiveView(context) {
    appState = context.appState;
    return { buildLifeArchiveMarkdown, exportLifeArchive };
}

function archiveLine(label, value) {
    if (Array.isArray(value)) return value.length ? label + '：' + value.join('、') : '';
    if (value && typeof value === 'object') return label + '：' + JSON.stringify(value, null, 2);
    return value || value === 0 ? label + '：' + String(value) : '';
}

function buildLifeArchiveMarkdown(state) {
    const chart = state.bazi_chart || {};
    const birth = state.birth_info || {};
    const goal = state.goal_progress || state.ending?.life_goal || {};
    const ending = state.ending || {};
    const lines = [];
    lines.push('# 一命千途 · 人生档案');
    lines.push('');
    lines.push('## 基本信息');
    [
        archiveLine('当前阶段', phaseLabel(state.phase)),
        archiveLine('出生时间', birth.datetime),
        archiveLine('开始年龄', state.start_age ? state.start_age + '岁' : ''),
        archiveLine('当前年龄', state.current_age ? state.current_age + '岁' : ''),
        archiveLine('当前年份', state.current_year),
        archiveLine('人生愿望', goal.title),
        archiveLine('愿望进度', goal.score || goal.percent ? (Number(goal.score || 0) + '/' + Number(goal.threshold || 0) + '（' + Number(goal.percent || 0) + '%）') : ''),
    ].filter(Boolean).forEach(line => lines.push('- ' + line));
    lines.push('');
    lines.push('## 命盘摘要');
    [
        archiveLine('四柱', [chart.year_pillar, chart.month_pillar, chart.day_pillar, chart.hour_pillar || '未知时柱'].filter(Boolean).join(' ')),
        archiveLine('日主', chart.day_master),
        archiveLine('身势', chart.day_strength),
        archiveLine('起运', chart.luck_start_label),
        archiveLine('喜用', chart.useful_elements || []),
        archiveLine('忌神', chart.unfavorable_elements || []),
        archiveLine('命盘关键词', state.chart_tags || []),
    ].filter(Boolean).forEach(line => lines.push('- ' + line));
    lines.push('');
    lines.push('## 当前状态');
    Object.entries(state.life_state || {}).forEach(([key, value]) => lines.push('- ' + key + '：' + value));
    const streakView = getStreakView(state);
    if (streakView.action) {
        lines.push('');
        lines.push('## 连续选择反馈');
        lines.push('- 当前惯性：' + streakView.label);
        lines.push('- 习惯优势：' + (streakView.bonus > 0 ? '后台推演 +' + streakView.bonus : '暂无'));
        lines.push('- 提醒：' + streakView.hint);
    }
    if (state.achievements?.length) {
        lines.push('');
        lines.push('## 解锁成就');
        state.achievements.forEach(item => lines.push('- ' + (item.title || '成就') + '：' + (item.description || '') + (item.unlocked_at ? '（' + item.unlocked_at + '）' : '')));
    }
    if (state.milestones?.length) {
        lines.push('');
        lines.push('## 人生里程碑');
        state.milestones.forEach(item => lines.push('- ' + (item.title || '里程碑') + '：' + (item.text || '')));
    }
    appendMemorySection(lines, '人生记忆', state.life_memories);
    appendMemorySection(lines, '关系记忆', state.relationship_memories);
    appendMemorySection(lines, '伏笔与回声', collectArchiveEchoes(state));
    appendMemorySection(lines, '遗憾与未竟线索', [...(state.regrets || []), ...(state.unresolved_threads || [])]);
    appendMemorySection(lines, '关键转折', state.turning_points);
    if (ending.title || ending.summary) {
        lines.push('');
        lines.push('## 结局');
        if (ending.title) lines.push('### ' + ending.title);
        if (ending.hidden_ending?.title) {
            lines.push('- 隐藏结局：' + ending.hidden_ending.title + '（' + (ending.hidden_ending.rarity || '隐藏') + '）');
            if (ending.hidden_ending.unlock_reason) lines.push('- 解锁条件：' + ending.hidden_ending.unlock_reason);
        }
        if (ending.summary) lines.push(ending.summary);
    }
    lines.push('');
    lines.push('## 叙事记录');
    (state.display_history || []).forEach((item, index) => {
        lines.push('');
        lines.push('### ' + String(index + 1).padStart(2, '0'));
        lines.push(String(item || '').trim());
    });
    lines.push('');
    return lines.join('\n');
}

function downloadTextFile(filename, text) {
    const blob = new Blob([text], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
}

function exportLifeArchive() {
    const state = appState.gameState;
    if (!state || state.phase === 'birth_input') return;
    const stamp = [state.current_year || 'unknown', state.current_age ? state.current_age + '岁' : ''].filter(Boolean).join('-');
    downloadTextFile('一命千途-人生档案-' + stamp + '.md', buildLifeArchiveMarkdown(state));
}

function appendMemorySection(lines, title, memories) {
    const list = Array.isArray(memories) ? memories.filter(Boolean).slice(-12) : [];
    if (!list.length) return;
    lines.push('');
    lines.push('## ' + title);
    list.forEach(item => {
        const age = item.age ? String(item.age) + '岁' + (item.half_label || '') : '';
        const titleText = item.title || item.type || '记忆';
        const text = item.text || item.summary || item.choice_text || '';
        const echo = item.echo_after_age ? '；预计' + item.echo_after_age + '岁后回响' : '';
        const affects = Array.isArray(item.affects) && item.affects.length ? '；影响：' + item.affects.join('、') : '';
        lines.push('- ' + [age, titleText].filter(Boolean).join(' · ') + '：' + text + echo + affects);
    });
}

function collectArchiveEchoes(state) {
    const records = [...(state.half_year_summaries || []), ...(state.annual_summaries || [])];
    const echoes = [];
    records.forEach(record => {
        if (record?.life_memory) echoes.push(record.life_memory);
        (record?.memory_echoes || []).forEach(item => echoes.push(item));
    });
    return echoes;
}
