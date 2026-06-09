import { escapeHtml } from './view_helpers.js?v=arch-modules-20260608';

let appState;
let DOMElements;

export function createChartView(context) {
    appState = context.appState;
    DOMElements = context.DOMElements;
    return { renderChart };
}

const elementLabels = { wood: '木', fire: '火', earth: '土', metal: '金', water: '水' };

const tenGodLabels = { year: '年干', month: '月干', day: '日干', hour: '时干' };

function renderChart() {
    const chart = appState.gameState?.bazi_chart || {};
    const birth = appState.gameState?.birth_info || {};
    const cycles = appState.gameState?.luck_cycles || [];
    const analysis = appState.gameState?.bazi_analysis || {};
    const lifeTopics = appState.gameState?.life_topics || analysis.life_topics || [];
    const suitableDirections = appState.gameState?.suitable_directions || analysis.suitable_directions || [];
    const highRiskFields = appState.gameState?.high_risk_fields || analysis.high_risk_fields || [];
    DOMElements.chartGrid.innerHTML = '';
    DOMElements.elementBoard.innerHTML = '';
    DOMElements.luckTimeline.innerHTML = '';
    if (!Object.keys(chart).length) return;
    const cards = [
        ['年柱', chart.year_pillar], ['月柱', chart.month_pillar], ['日柱', chart.day_pillar], ['时柱', chart.hour_pillar || '未知'],
        ['日主', chart.day_master], ['身势', chart.day_strength], ['模式', chart.mode], ['起运', chart.luck_start_label || '-'], ['出生', birth.datetime],
    ];
    const tenGods = Object.entries(chart.ten_gods || {})
        .map(([key, value]) => (tenGodLabels[key] || key) + '：' + value)
        .join(' / ');
    DOMElements.chartGrid.innerHTML = cards.map(([label, value]) => '<div class=\'chart-card\'><span>' + label + '</span><strong>' + escapeHtml(value) + '</strong></div>').join('') +
        '<div class=\'chart-card wide\'><span>喜用</span><strong>' + escapeHtml((chart.useful_elements || []).join('、')) + '</strong></div>' +
        '<div class=\'chart-card wide\'><span>忌神</span><strong>' + escapeHtml((chart.unfavorable_elements || []).join('、')) + '</strong></div>' +
        '<div class=\'chart-card wide\'><span>十神结构</span><strong>' + escapeHtml(tenGods || '待生成') + '</strong></div>' +
        '<div class=\'chart-card wide\'><span>命盘关键词</span><strong>' + escapeHtml((appState.gameState?.chart_tags || []).join(' / ')) + '</strong></div>' +
        '<div class=\'chart-card wide\'><span>人生课题</span><strong>' + escapeHtml(lifeTopics.join(' / ') || '待分析') + '</strong></div>' +
        '<div class=\'chart-card wide\'><span>适合方向</span><strong>' + escapeHtml(suitableDirections.join(' / ') || '待分析') + '</strong></div>' +
        '<div class=\'chart-card wide\'><span>高风险领域</span><strong>' + escapeHtml(highRiskFields.join(' / ') || '待分析') + '</strong></div>';

    const counts = chart.five_elements || {};
    const maxCount = Math.max(1, ...Object.values(counts).map(Number));
    DOMElements.elementBoard.innerHTML = '<h3>五行分布</h3>' + Object.entries(elementLabels).map(([key, label]) => {
        const value = Number(counts[key] || 0);
        const width = Math.max(8, Math.round((value / maxCount) * 100));
        return '<div class=\'element-row\'><span>' + label + '</span><div><i style=\'width:' + width + '%\'></i></div><b>' + value + '</b></div>';
    }).join('');

    DOMElements.luckTimeline.innerHTML = '<h3>大运时间轴</h3><div class=\'timeline-track\'>' + cycles.slice(0, 8).map(cycle => {
        const themes = (cycle.theme || []).join('、');
        const ageRange = (cycle.age_start_label && cycle.age_end_label)
            ? cycle.age_start_label + '-' + cycle.age_end_label
            : cycle.age_start + '-' + cycle.age_end + '岁';
        return '<article><strong>' + escapeHtml(ageRange) + ' ' + escapeHtml(cycle.pillar) + '</strong><span>' + escapeHtml(cycle.direction || '') + '</span><p>' + escapeHtml(themes) + '</p></article>';
    }).join('') + '</div>';
}
