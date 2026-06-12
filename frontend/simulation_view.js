import { escapeHtml, joinCleanList, renderText } from './view_helpers.js?v=arch-modules-20260608';

let appState;
let DOMElements;
let scrollState;
let smoothScrollToBottom = () => {};
let scheduleSceneBackgroundUpdate = () => {};
let toggleFocus = () => {};
let submitFocuses = () => {};

export function createSimulationView(context) {
    appState = context.appState;
    DOMElements = context.DOMElements;
    scrollState = context.scrollState;
    smoothScrollToBottom = context.smoothScrollToBottom || smoothScrollToBottom;
    scheduleSceneBackgroundUpdate = context.scheduleSceneBackgroundUpdate || scheduleSceneBackgroundUpdate;
    toggleFocus = context.toggleFocus || toggleFocus;
    submitFocuses = context.submitFocuses || submitFocuses;
    return {
        renderNarrative,
        renderStatus,
        renderYearBanner,
        renderTurnGuide,
        renderMonthFlowBoard,
        renderTurnResolutionCard,
        focusPendingResolution,
        renderFocusActions,
        renderEndingArchive,
        getStreakView,
        cleanActionOptions,
        actionGuideMap,
        recommendedActionGuides,
    };
}

const HISTORY_FILTERS = [
    { id: 'all', label: '全部' },
    { id: 'roll', label: '判定' },
    { id: 'stage', label: '阶段' },
    { id: 'summary', label: '总结' },
    { id: 'achievement', label: '成就' },
    { id: 'ending', label: '结局' },
    { id: 'system', label: '系统' },
];
const HISTORY_COMPACT_LIMIT = 12;
const TERM_DEFINITIONS = {
    '起运': '从出生到进入第一步大运的年龄，代表人生节奏开始换挡的时间点。',
    '大运': '十年左右的长期基调，像这段人生的天气背景。',
    '流年': '当年的事件倾向，会影响这一年更容易遇到的机会和阻力。',
    '流月': '本半年每个月的机会和风险提示，用来辅助选择行动重点。',
    'D100': '后台百分骰，只作为命盘、时运、状态和选择合参后的暗骰结果；界面会优先解释因果。',
    '四柱': '出生年、月、日、时组成的命盘信息；不知道时辰时会使用三柱模式。',
    '十神': '命理里描述资源、行动、压力、关系等倾向的术语，本游戏会尽量转译成白话。'
};
const PREVIEW_ACTION_KEYWORDS = {
    '专注学业': ['学', '考试', '考研', '读书', '课程', '技能', '证书', '研究', '论文', '培训'],
    '发展事业': ['工作', '事业', '职场', '升职', '职位', '项目', '跳槽', '老板', '绩效', '专业'],
    '经营感情': ['感情', '恋爱', '伴侣', '对象', '婚', '约会', '亲密', '表白', '分手', '关系'],
    '陪伴家人': ['家庭', '父母', '孩子', '亲人', '家人', '陪伴', '照顾', '亲子', '回家'],
    '投资理财': ['投资', '理财', '股票', '基金', '买房', '资产', '存钱', '赚钱', '副业', '财务'],
    '调养身体': ['健康', '身体', '运动', '休息', '睡眠', '体检', '治疗', '养生', '减压', '康复'],
    '社交拓展': ['社交', '朋友', '人脉', '合作', '贵人', '聚会', '圈子', '沟通', '团队'],
    '创业冒险': ['创业', '冒险', '公司', '合伙', '融资', '辞职', '开店', '产品', '市场'],
    '搬迁远行': ['搬家', '迁移', '远行', '旅行', '出国', '城市', '异地', '留学', '调动'],
};
const PREVIEW_MIGRATION_HINTS = ['北京', '上海', '广州', '深圳', '杭州', '成都', '南京', '武汉', '西安', '苏州', '重庆', '天津', '外地', '异地', '大城市', '一线城市', '换城市', '去外面', '离开家', '搬去', '搬到', '出省'];

function classifyHistoryItem(item) {
    const text = String(item || '');
    if (text.startsWith('【系统提示：') && text.includes('D100 判定')) return 'roll';
    if (text.startsWith('【阶段叙事】')) return 'stage';
    if (text.startsWith('【半年度总结】')) return 'summary';
    if (text.startsWith('【新成就】')) return 'achievement';
    if (text.startsWith('【结局')) return 'ending';
    if (text.startsWith('【系统提示】') || text.startsWith('【命书紊乱】')) return 'system';
    return 'story';
}

function historyFilterLabel(filterId) {
    return HISTORY_FILTERS.find(filter => filter.id === filterId)?.label || '全部';
}

function renderNarrativeToolbar(totalCount, filteredCount, hiddenCount) {
    const activeFilter = appState.historyFilter || 'all';
    const filterButtons = HISTORY_FILTERS.map(filter => {
        const active = filter.id === activeFilter;
        return '<button class=\'history-filter-chip' + (active ? ' active' : '') + '\' type=\'button\' data-history-filter=\'' + filter.id + '\' aria-pressed=\'' + String(active) + '\'>' + filter.label + '</button>';
    }).join('');
    const compactText = appState.historyExpanded ? '仅看最近' : '展开全部';
    const hint = activeFilter === 'all'
        ? '共 ' + totalCount + ' 条叙事'
        : historyFilterLabel(activeFilter) + '：' + filteredCount + ' / ' + totalCount + ' 条';
    return '<div class=\'history-toolbar\'>' +
        '<div><span>叙事记录</span><small>' + escapeHtml(hint) + (hiddenCount > 0 ? ' · 已折叠 ' + hiddenCount + ' 条' : '') + '</small></div>' +
        '<div class=\'history-filter-row\'>' + filterButtons + '</div>' +
        '<button class=\'history-expand-button\' type=\'button\' data-history-expand=\'toggle\'>' + compactText + '</button>' +
    '</div>';
}

function renderNarrative() {
    const history = appState.gameState?.display_history || [];
    const activeFilter = HISTORY_FILTERS.some(filter => filter.id === appState.historyFilter) ? appState.historyFilter : 'all';
    appState.historyFilter = activeFilter;
    const filteredHistory = activeFilter === 'all'
        ? history
        : history.filter(item => classifyHistoryItem(item) === activeFilter);
    const visibleHistory = appState.historyExpanded
        ? filteredHistory
        : filteredHistory.slice(Math.max(0, filteredHistory.length - HISTORY_COMPACT_LIMIT));
    const hiddenCount = Math.max(0, filteredHistory.length - visibleHistory.length);
    const articles = visibleHistory.map(item => {
        const type = classifyHistoryItem(item);
        return '<article class=\'history-entry history-' + escapeHtml(type) + '\'>' + renderText(item) + '</article>';
    }).join('');
    const emptyState = filteredHistory.length ? '' : '<article class=\'history-entry history-empty\'><p>这个分类暂时还没有记录。</p></article>';
    DOMElements.narrativeWindow.innerHTML = renderNarrativeToolbar(history.length, filteredHistory.length, hiddenCount) + articles + emptyState;
    DOMElements.narrativeWindow.querySelectorAll('[data-history-filter]').forEach(button => {
        button.addEventListener('click', () => {
            appState.historyFilter = button.dataset.historyFilter || 'all';
            appState.historyExpanded = false;
            scrollState.isFirstRender = true;
            renderNarrative();
        });
    });
    const expandButton = DOMElements.narrativeWindow.querySelector('[data-history-expand]');
    if (expandButton) {
        expandButton.addEventListener('click', () => {
            appState.historyExpanded = !appState.historyExpanded;
            scrollState.isFirstRender = true;
            renderNarrative();
        });
    }
    if (scrollState.isFirstRender) {
        DOMElements.narrativeWindow.scrollTop = DOMElements.narrativeWindow.scrollHeight;
        scrollState.isFirstRender = false;
    } else {
        smoothScrollToBottom(DOMElements.narrativeWindow, 180);
    }
    scheduleSceneBackgroundUpdate();
}

function getStreakView(state) {
    const streak = state.focus_streak || {};
    const memory = state.focus_memory || {};
    const action = streak.action || memory.last_focus || '';
    const count = Number(streak.count || memory.streak || 0);
    const bonus = Number(streak.streak_bonus || 0);
    const warning = state.streak_warning || streak.streak_warning || '';
    return {
        action,
        count,
        bonus,
        warning,
        label: action ? ('连续 ' + Math.max(1, count) + ' 次 · ' + action) : '尚未形成行动惯性',
        hint: action
            ? (warning || '继续相同主重点会形成路径惯性，也会记录机会成本。')
            : '完成第一次半年度行动后，这里会显示连续选择反馈。',
    };
}

function renderStreakStatusCard(state) {
    const view = getStreakView(state || {});
    if (!view.action) return '';
    const bonusText = view.bonus > 0 ? '惯性 +' + view.bonus : '观察中';
    return '<article class=\'streak-card\'><div><b>' + escapeHtml(view.label) + '</b><span>' + escapeHtml(bonusText) + '</span></div>' +
        '<small>' + escapeHtml(view.hint) + '</small></article>';
}

function renderStatus() {
    const state = appState.gameState || {};
    const lifeState = state.life_state || {};
    const chart = state.bazi_chart || {};
    const rows = Object.entries(lifeState).map(([key, value]) => '<div class=\'stat-row\'><span>' + key + '</span><meter min=\'0\' max=\'100\' value=\'' + value + '\'></meter><b>' + value + '</b></div>').join('');
    const chartInfo = chart.day_master ? '<div class=\'side-card\'><b>' + chart.day_master + '</b><span>' + (chart.mode || '') + '</span><small>' + (state.chart_tags || []).join(' / ') + '</small></div>' : '<p>静待命盘生成...</p>';
    const goal = state.goal_progress || {};
    const goalCard = goal.title ? '<article class=\'goal-progress-card\'><div><b>' + escapeHtml(goal.title) + '</b><span>' + escapeHtml(goal.status || '') + '</span></div>' +
        '<meter min=\'0\' max=\'100\' value=\'' + Number(goal.percent || 0) + '\'></meter>' +
        '<small>' + escapeHtml(goal.summary || '') + ' · ' + Number(goal.score || 0) + '/' + Number(goal.threshold || 0) + '</small></article>' : '';
    const systems = state.life_systems || {};
    const systemCards = Object.values(systems).map(item => {
        const score = Number(item.score || 0);
        return '<article class=\'system-card\'><div><b>' + escapeHtml(item.label || '长期系统') + '</b><span>' + escapeHtml(item.trend || '平稳') + '</span></div>' +
            '<meter min=\'0\' max=\'100\' value=\'' + score + '\'></meter>' +
            '<small>' + escapeHtml(item.stage || '') + ' · ' + score + '分</small></article>';
    }).join('');
    const relationships = state.relationships || [];
    const relationCards = relationships.map(item => {
        const closeness = Number(item.closeness || 0);
        return '<article class=\'relationship-card\'><div><b>' + escapeHtml(item.name || '关系') + '</b><span>' + escapeHtml(item.status || '') + '</span></div>' +
            '<meter min=\'0\' max=\'100\' value=\'' + closeness + '\'></meter>' +
            '<small>' + escapeHtml(item.type || '') + ' · ' + closeness + '分</small></article>';
    }).join('');
    const achievements = state.achievements || [];
    const achievementCards = achievements.slice(-5).reverse().map(item => '<article class=\'achievement-card\'><span>' + escapeHtml(item.category || '成就') + '</span><b>' + escapeHtml(item.title || '') + '</b><small>' + escapeHtml(item.unlocked_at || '') + ' · ' + escapeHtml(item.description || '') + '</small></article>').join('');
    const milestones = state.milestones || [];
    const milestoneCards = milestones.slice(-4).reverse().map(item => '<article class=\'milestone-card\'><b>' + escapeHtml(item.title || '') + '</b><small>' + escapeHtml(item.text || '') + '</small></article>').join('');
    const streakCard = renderStreakStatusCard(state);
    DOMElements.characterStatus.innerHTML = chartInfo +
        (goalCard ? '<div class=\'status-section\'><h3>人生愿望</h3>' + goalCard + '</div>' : '') +
        (streakCard ? '<div class=\'status-section\'><h3>连续选择反馈</h3>' + streakCard + '</div>' : '') +
        (achievementCards ? '<div class=\'status-section\'><h3>已解锁成就</h3>' + achievementCards + '</div>' : '') +
        (milestoneCards ? '<div class=\'status-section\'><h3>人生里程碑</h3>' + milestoneCards + '</div>' : '') +
        (systemCards ? '<div class=\'status-section\'><h3>长期系统</h3>' + systemCards + '</div>' : '') +
        (relationCards ? '<div class=\'status-section\'><h3>关系网络</h3>' + relationCards + '</div>' : '') +
        '<div class=\'status-section\'><h3>基础属性</h3>' + rows + '</div>';
}

function renderYearBanner() {
    const state = appState.gameState || {};
    const luck = state.current_luck_cycle || {};
    const annual = state.current_annual_cycle || {};
    const stage = state.current_stage || {};
    DOMElements.yearBanner.innerHTML = '<div><span>年龄</span><strong>' + (state.current_age || '-') + '</strong></div>' +
        '<div><span>年份</span><strong>' + (state.current_year || '-') + '</strong></div>' +
        '<div><span>人生阶段</span><strong>' + escapeHtml(stage.label || '-') + '</strong></div>' +
        '<div><span>当前半年</span><strong>' + escapeHtml(state.current_half_label || '-') + '</strong></div>' +
        '<div><span>大运</span><strong>' + (luck.pillar || '-') + '</strong></div>' +
        '<div><span>流年</span><strong>' + (annual.pillar || '-') + '</strong></div>';
}

function renderTermChip(term) {
    const definition = TERM_DEFINITIONS[term] || '';
    const active = appState.activeTerm === term;
    return '<button class=\'term-chip' + (active ? ' active' : '') + '\' type=\'button\' data-term=\'' + escapeHtml(term) + '\' title=\'' + escapeHtml(definition) + '\' aria-label=\'' + escapeHtml(term + '：' + definition) + '\'>' + escapeHtml(term) + '</button>';
}

function wireTermChips(container) {
    const box = container.querySelector('.term-explain-box');
    container.querySelectorAll('[data-term]').forEach(button => {
        const activate = () => {
            appState.activeTerm = button.dataset.term || 'D100';
            container.querySelectorAll('[data-term]').forEach(item => item.classList.toggle('active', item === button));
            if (box) {
                const term = appState.activeTerm;
                box.innerHTML = '<b>' + escapeHtml(term) + '</b>：' + escapeHtml(TERM_DEFINITIONS[term] || '暂无解释');
            }
        };
        button.addEventListener('click', activate);
        button.addEventListener('focus', activate);
        button.addEventListener('mouseenter', activate);
    });
}

function renderFirstTurnCoach(state) {
    const summaries = Array.isArray(state.annual_summaries) ? state.annual_summaries : [];
    if (summaries.length || appState.turnCoachDismissed) return '';
    const recommended = recommendedActionGuides(state).slice(0, 3);
    const goal = state.goal_progress || {};
    const actions = recommended.map((guide, index) => {
        const action = guide.action || '随缘而行';
        const choice = lifeChoiceOf(guide, action);
        return '<button class=\'coach-action-button life-choice-coach-button\' type=\'button\' data-coach-action=\'' + escapeHtml(action) + '\'>' +
            '<span>抉择 ' + (index + 1) + '</span><b>' + escapeHtml(choice.short_label || action) + '</b><small>' + escapeHtml(choice.decision || recommendationReason(guide)) + '</small>' +
        '</button>';
    }).join('');
    return '<section class=\'first-turn-coach\' aria-label=\'第一回合引导\'>' +
        '<div class=\'first-turn-copy\'><span>第一次人生抉择</span><strong>先读命盘和时运，再决定这一半年怎么活</strong>' +
        '<p>人生愿望“' + escapeHtml(goal.title || '未选择') + '”只是方向；真正改变路径的是你在具体处境里的选择。</p></div>' +
        '<div class=\'coach-step-list\'><span>1 读命盘</span><span>2 看时运</span><span>3 做抉择</span></div>' +
        '<div class=\'coach-actions\'>' + actions + '</div>' +
        '<button class=\'coach-dismiss-button\' type=\'button\' data-turn-coach-dismiss>我知道了</button>' +
    '</section>';
}

function renderTurnGuide() {
    const state = appState.gameState || {};
    if (!DOMElements.turnGuide) return;
    if (!['life_simulation', 'ending'].includes(state.phase)) {
        DOMElements.turnGuide.innerHTML = '';
        return;
    }
    if (state.phase === 'ending') {
        DOMElements.turnGuide.innerHTML = '<section class=\'turn-guide-card ending-guide\'><div><span>回望完成</span><strong>人生档案已生成</strong></div><p>你可以查看下方结局档案，也可以点击顶部“导出档案”保存本周目的命盘、选择、成就与叙事记录。</p></section>';
        return;
    }
    const stage = state.current_stage || {};
    const goal = state.goal_progress || {};
    const luck = state.current_luck_cycle || {};
    const annual = state.current_annual_cycle || {};
    const months = state.current_monthly_cycles || [];
    const collect = (key, fallback) => {
        const values = [];
        months.forEach(month => {
            const raw = month[key];
            const list = Array.isArray(raw) ? raw : [raw];
            list.forEach(item => {
                const text = String(item || '').trim();
                if (text && !values.includes(text)) values.push(text);
            });
        });
        return values.slice(0, 4).join('、') || fallback;
    };
    const opportunity = collect('opportunity', '稳步推进');
    const risk = collect('risk', '贪多冒进');
    const goalText = goal.title ? goal.title + ' · ' + Number(goal.percent || 0) + '%' : '未选择人生愿望';
    const streakView = getStreakView(state);
    const streakBonus = streakView.bonus > 0 ? '路径惯性 +' + streakView.bonus : '尚未形成路径惯性';
    const chart = state.bazi_chart || {};
    const chartTags = Array.isArray(state.chart_tags) ? state.chart_tags.slice(0, 4).join('、') : '';
    const baziText = (chart.day_master ? chart.day_master + '日主' : '命盘底色') + (chartTags ? ' · ' + chartTags : '');
    const termNames = ['四柱', '大运', '流年', '流月', '十神', 'D100'];
    const activeDefinition = TERM_DEFINITIONS[appState.activeTerm] || TERM_DEFINITIONS.D100;
    DOMElements.turnGuide.innerHTML = renderFirstTurnCoach(state) + '<section class=\'turn-guide-card\'>' +
        '<div class=\'turn-guide-heading\'><div><span>本半年人生情境</span><strong>' + escapeHtml(stage.label || '人生阶段') + '</strong></div><p>' + escapeHtml(stage.summary || '选择会影响长期状态、愿望进度与结局档案。') + '</p></div>' +
        '<div class=\'turn-guide-grid\'>' +
            '<article><span>命盘底色</span><b>' + escapeHtml(baziText) + '</b><small>它决定你更容易在哪些课题上形成惯性，但不替你选择。</small></article>' +
            '<article><span>人生愿望</span><b>' + escapeHtml(goalText) + '</b><small>' + escapeHtml(goal.summary || '可在前传页选择主愿望。') + '</small></article>' +
            '<article><span>时运背景</span><b>' + escapeHtml((luck.pillar || '-') + ' 大运 / ' + (annual.pillar || '-') + ' 流年') + '</b><small>大运看十年基调，流年看当年事件倾向。</small></article>' +
            '<article><span>机会与阻力</span><b>' + escapeHtml(opportunity) + '</b><small>风险：' + escapeHtml(risk) + '</small></article>' +
            '<article class=\'streak-preview-card\'><span>路径惯性</span><b>' + escapeHtml(streakView.label) + '</b><small>' + escapeHtml(streakBonus + ' · ' + streakView.hint) + '</small></article>' +
        '</div>' +
        '<div class=\'turn-glossary\'><div><span>术语简明模式</span><div class=\'term-chip-row\'>' + termNames.map(renderTermChip).join('') + '</div></div><p class=\'term-explain-box\'><b>' + escapeHtml(appState.activeTerm) + '</b>：' + escapeHtml(activeDefinition) + '</p></div>' +
    '</section>';
    DOMElements.turnGuide.querySelectorAll('[data-coach-action]').forEach(button => {
        button.addEventListener('click', () => toggleFocus(button.dataset.coachAction || ''));
    });
    const dismiss = DOMElements.turnGuide.querySelector('[data-turn-coach-dismiss]');
    if (dismiss) {
        dismiss.addEventListener('click', () => {
            appState.turnCoachDismissed = true;
            renderTurnGuide();
        });
    }
    wireTermChips(DOMElements.turnGuide);
}

function renderEndingArchive(ending) {
    if (!ending) return '';
    const dimensions = ending.dimensions || {};
    const goal = ending.life_goal || {};
    const reasonLabels = { retrospect: '主动回望', health_zero: '健康归零', age_60: '六十岁终章', natural: '自然收束' };
    const reasonBlock = ending.reason ? '<p class=\'ending-reason\'>收束方式：' + escapeHtml(reasonLabels[ending.reason] || ending.reason) + '</p>' : '';
    const hidden = ending.hidden_ending || {};
    const hiddenBlock = hidden.title ? '<article class=\'hidden-ending-card\'><span>' + escapeHtml(hidden.rarity || '隐藏') + '结局</span><strong>' + escapeHtml(hidden.title) + '</strong><p>' + escapeHtml(hidden.description || '') + '</p><small>解锁条件：' + escapeHtml(hidden.unlock_reason || '达成特殊人生组合') + '</small></article>' : '';
    const goalBlock = goal.title ? '<article class=\'ending-goal-card\'><span>人生愿望</span><strong>' + escapeHtml(goal.title) + '</strong><p>' + escapeHtml(goal.achieved ? '最终达成' : '尚未完全达成') + ' · ' + Number(goal.score || 0) + '/' + Number(goal.threshold || 0) + ' · ' + escapeHtml(goal.status || '') + '</p></article>' : '';
    const dimensionCards = Object.values(dimensions).map(item => '<article><span>' + escapeHtml(item.label || '') + '</span><strong>' + escapeHtml(item.grade || '') + '</strong><small>' + Number(item.score || 0) + '分</small></article>').join('');
    const achievements = (ending.achievements || []).map(item => '<li>' + escapeHtml(item) + '</li>').join('');
    const regrets = (ending.regrets || []).map(item => '<li>' + escapeHtml(item) + '</li>').join('');
    const points = (ending.key_turning_points || []).map(item => '<li>' + escapeHtml(item) + '</li>').join('');
    const unlocked = (ending.achievements_unlocked || []).map(item => '<li><b>' + escapeHtml(item.title || '') + '</b>：' + escapeHtml(item.description || '') + '</li>').join('');
    return '<section class=\'ending-archive\'><h3>人生档案</h3>' + reasonBlock +
        hiddenBlock + goalBlock +
        '<div class=\'ending-grid\'>' + dimensionCards + '</div>' +
        '<div class=\'ending-lists\'>' +
        '<article><h4>主要成就</h4><ul>' + achievements + '</ul></article>' +
        '<article><h4>主要遗憾</h4><ul>' + regrets + '</ul></article>' +
        '<article><h4>关键转折</h4><ul>' + points + '</ul></article>' +
        '<article><h4>解锁成就</h4><ul>' + unlocked + '</ul></article>' +
        '</div></section>';
}

function renderMonthFlowBoard() {
    if (appState.gameState?.phase === 'ending' && appState.gameState?.ending) {
        DOMElements.monthFlowBoard.innerHTML = renderEndingArchive(appState.gameState.ending);
        return;
    }
    const months = appState.gameState?.current_monthly_cycles || [];
    if (!months.length) {
        DOMElements.monthFlowBoard.innerHTML = '';
        return;
    }
    const collect = (key, fallback) => {
        const values = [];
        months.forEach(month => {
            const raw = month[key];
            const list = Array.isArray(raw) ? raw : [raw];
            list.forEach(item => {
                const text = String(item || '').trim();
                if (text && !values.includes(text)) values.push(text);
            });
        });
        return values.slice(0, 3).join('、') || fallback;
    };
    const monthCards = months.map(month => {
        const theme = joinCleanList(month.theme, '平稳推进');
        const opportunity = joinCleanList(month.opportunity, '守成');
        const risk = joinCleanList(month.risk, '贪多');
        return '<article class=\'month-flow-card\'>' +
            '<span>' + escapeHtml(month.month_name || (month.month + '月')) + '</span>' +
            '<strong>' + escapeHtml(month.pillar || '-') + '</strong>' +
            '<p>' + escapeHtml(theme) + '</p>' +
            '<small>机：' + escapeHtml(opportunity) + '</small>' +
            '<small>忌：' + escapeHtml(risk) + '</small>' +
        '</article>';
    }).join('');
    const expanded = Boolean(appState.monthFlowExpanded);
    DOMElements.monthFlowBoard.innerHTML =
        '<div class=\'month-flow-summary\'>' +
            '<div><span>本半年流月</span><strong>' + escapeHtml(months.map(month => month.month_name || (month.month + '月')).filter(Boolean).join(' / ')) + '</strong></div>' +
            '<p><b>机会：</b>' + escapeHtml(collect('opportunity', '稳步推进')) + ' <b>风险：</b>' + escapeHtml(collect('risk', '贪多冒进')) + '</p>' +
            '<button type=\'button\' data-month-flow-toggle aria-expanded=\'' + String(expanded) + '\'>' + (expanded ? '收起流月' : '展开6个月') + '</button>' +
        '</div>' +
        (expanded ? '<div class=\'month-flow-grid\'>' + monthCards + '</div>' : '');
    const toggle = DOMElements.monthFlowBoard.querySelector('[data-month-flow-toggle]');
    if (toggle) {
        toggle.addEventListener('click', () => {
            appState.monthFlowExpanded = !appState.monthFlowExpanded;
            renderMonthFlowBoard();
        });
    }
}

function formatStateDeltaList(changes) {
    const entries = Object.entries(changes || {}).filter(([, value]) => Number(value || 0) !== 0);
    if (!entries.length) return '<span>无明显变化</span>';
    return entries.slice(0, 6).map(([key, value]) => {
        const number = Number(value || 0);
        const positive = number > 0;
        return '<span class=\'delta-pill ' + (positive ? 'positive' : 'negative') + '\'>' + escapeHtml(key) + ' ' + (positive ? '+' : '') + number + '</span>';
    }).join('');
}

function formatGoalDelta(before, after) {
    const start = Number(before?.percent ?? before?.score ?? 0);
    const end = Number(after?.percent ?? after?.score ?? 0);
    const delta = end - start;
    if (!after?.title) return '未选择人生愿望';
    return after.title + ' · ' + Number(after.percent || 0) + '%' + (delta ? '（' + (delta > 0 ? '+' : '') + delta + '）' : '（持平）');
}

function choiceDisplay(record) {
    const rawText = String(record?.raw_choice_text || '').trim();
    const intent = record?.choice_intent || {};
    const normalized = Array.isArray(record?.normalized_focuses) ? record.normalized_focuses : (record?.focuses || [record?.main_focus || '人生抉择']);
    const normalizedText = normalized.filter(Boolean).join('、') || '人生抉择';
    if (rawText && intent.is_custom) return rawText + ' → ' + normalizedText;
    return normalizedText;
}

function memoryEchoText(record) {
    const memory = record?.life_memory || {};
    const echoes = Array.isArray(record?.memory_echoes) ? record.memory_echoes : [];
    if (echoes.length) return echoes.map(item => item.text || '').filter(Boolean).join('；');
    return memory.text || '本次选择已进入人生记忆，后续阶段可能再次回响。';
}

function renderTurnResolutionCard() {
    const state = appState.gameState || {};
    if (!DOMElements.turnResolution) return;
    const records = Array.isArray(state.annual_summaries) ? state.annual_summaries : [];
    if (state.phase === 'ending' || !records.length) {
        DOMElements.turnResolution.innerHTML = '';
        return;
    }
    const record = records[records.length - 1] || {};
    const roll = record.roll_event || {};
    const achievements = Array.isArray(record.new_achievements) ? record.new_achievements : [];
    const milestone = record.milestone || {};
    const goalBefore = record.goal_progress_before || {};
    const goalAfter = record.goal_progress_after || {};
    const fate = record.fate_explanation || {};
    const nextGuide = recommendedActionGuides(state)[0] || {};
    const resolutionId = roll.id || String(records.length);
    const hiddenRoll = fate.hidden_roll || ('后台 D100：目标' + String(roll.target || '-') + '，投掷' + String(roll.result || '-') + '，结果' + String(roll.outcome || '未知') + '。');
    DOMElements.turnResolution.innerHTML =
        '<section id=\'turn-resolution-card\' class=\'turn-resolution-card\' tabindex=\'-1\' aria-live=\'polite\' data-resolution-id=\'' + escapeHtml(resolutionId) + '\'>' +
            '<div class=\'turn-resolution-head\'><div><span>命运推演</span><strong>' + escapeHtml((record.age || state.current_age || '-') + '岁' + (record.half_label || '') + ' · ' + (record.main_focus || '人生抉择')) + '</strong><small>' + escapeHtml(hiddenRoll) + '</small></div><b class=\'outcome-' + escapeHtml(roll.outcome || '未知') + '\'>' + escapeHtml(roll.outcome || '未知') + '</b></div>' +
            '<div class=\'turn-resolution-grid\'>' +
                '<article class=\'turn-resolution-story\'><span>生活片段</span><b>这一半年怎么过</b><small>' + escapeHtml(fate.life_scene || fate.choice_influence || '这次选择会先落在日常作息、关系反馈和身体感受里。') + '</small></article>' +
                '<article><span>命盘影响</span><b>' + escapeHtml(record.main_focus || '随缘而行') + '</b><small>' + escapeHtml(fate.bazi_influence || '命盘提供底色，但不替你做决定。') + '</small></article>' +
                '<article><span>时运影响</span><b>' + escapeHtml((record.annual_cycle || {}).pillar || '流年') + '</b><small>' + escapeHtml(fate.fortune_influence || '大运、流年与流月共同改变机会和阻力。') + '</small></article>' +
                '<article><span>玩家选择</span><b>' + escapeHtml(choiceDisplay(record)) + '</b><small>' + escapeHtml(fate.choice_influence || milestone.text || '本半年事件已写入叙事记录。') + '</small></article>' +
                '<article><span>人生愿望</span><b>' + escapeHtml(formatGoalDelta(goalBefore, goalAfter)) + '</b><small>' + escapeHtml(goalAfter.summary || '后续结局会追踪愿望达成度。') + '</small></article>' +
                '<article><span>伏笔与回声</span><b>' + escapeHtml((record.life_memory || {}).title || choiceShortLabel(nextGuide, nextGuide.action || '阅读最新叙事')) + '</b><small>' + escapeHtml(memoryEchoText(record)) + '</small></article>' +
            '</div>' +
            '<div class=\'turn-resolution-deltas\'><span>人生变化</span>' + formatStateDeltaList(record.state_effect || {}) + '</div>' +
            (achievements.length ? '<div class=\'turn-resolution-achievements\'><span>人生回声</span>' + achievements.map(item => '<b>' + escapeHtml(item.title || '') + '</b>').join('') + '</div>' : '') +
        '</section>';
}

function focusPendingResolution() {
    const pendingId = appState.pendingResolutionFocusId;
    if (!pendingId || !DOMElements.turnResolution) return;
    const card = DOMElements.turnResolution.querySelector('[data-resolution-id="' + CSS.escape(pendingId) + '"]');
    if (!card) return;
    appState.pendingResolutionFocusId = '';
    setTimeout(() => {
        card.focus({ preventScroll: true });
        card.scrollIntoView({ block: 'center', behavior: 'smooth' });
    }, 3500);
}

function cleanActionOptions(state) {
    const directOptions = Array.isArray(state.action_options) ? state.action_options : [];
    const stageOptions = Array.isArray(state.current_stage?.action_options) ? state.current_stage.action_options : [];
    const merged = directOptions.map((option, index) => {
        const text = String(option || '').trim();
        return text || String(stageOptions[index] || '').trim();
    }).filter(Boolean);
    const fallback = stageOptions.map(option => String(option || '').trim()).filter(Boolean);
    const options = merged.length ? merged : fallback;
    return Array.from(new Set(options));
}

function actionGuideMap(state) {
    const guides = Array.isArray(state.action_guides) ? state.action_guides : [];
    return new Map(guides.filter(item => item && item.action).map(item => [String(item.action), item]));
}

function recommendedActionGuides(state) {
    const guides = Array.isArray(state.action_guides) ? state.action_guides.filter(item => item && item.action) : [];
    if (guides.length) return guides;
    return cleanActionOptions(state).map(action => ({ action }));
}

function guideForAction(guides, action) {
    return guides.get(action) || {};
}

function lifeChoiceOf(guide, action) {
    return guide?.life_choice || {
        short_label: action,
        title: action,
        situation: '当前人生处在新的岔口。',
        decision: '你选择把本半年交给“' + action + '”。',
        bazi_hint: '命盘提供底色，但不会替你做决定。',
        fortune_hint: '时运会改变机会和阻力的出现方式。',
        choice_impact: '这会进入后续人生记忆，影响长期资源、关系和心理惯性。',
    };
}

function choiceShortLabel(guide, action) {
    return lifeChoiceOf(guide, action).short_label || action;
}

function formatGuideBenefit(guide) {
    if (!guide?.action) return '系统会根据输入自动归类，再计算本半年影响。';
    const parts = [];
    if (guide.primary) parts.push(guide.primary + '主收益');
    if (guide.secondary) parts.push(guide.secondary + '副收益');
    return parts.join(' / ') || '探索潜在机会';
}

function formatGuideRisk(guide) {
    if (!guide?.action) return '自定义行动暂无法预估风险，建议提交前保持重点清晰。';
    return guide.risk ? guide.risk + '可能被消耗' : '风险较低，但仍会受 D100 结果影响';
}

function recommendationReason(guide) {
    if (!guide?.action) return '自由输入会在提交后自动归入最接近的行动类型。';
    const alignment = guide.goal_alignment || {};
    const tags = Array.isArray(guide.tags) ? guide.tags.filter(Boolean).slice(0, 3).join('、') : '';
    return alignment.reason || guide.clue || tags || '综合当前阶段、愿望与时势排序靠前。';
}

function inferPreviewActions(text, guides) {
    const raw = String(text || '').trim();
    if (!raw) return [];
    if (guides.has(raw)) return [raw];
    const matches = [];
    Object.entries(PREVIEW_ACTION_KEYWORDS).forEach(([action, keywords]) => {
        const effectiveKeywords = action === '发展事业' && matches.includes('专注学业')
            ? keywords.filter(keyword => keyword !== '专业')
            : keywords;
        if (effectiveKeywords.some(keyword => raw.includes(keyword))) matches.push(action);
    });
    if (PREVIEW_MIGRATION_HINTS.some(keyword => raw.includes(keyword)) && !matches.includes('搬迁远行')) {
        matches.push('搬迁远行');
    }
    return Array.from(new Set(matches)).filter(action => guides.has(action)).slice(0, 3);
}

function resolvePreviewAction(guides, action) {
    const raw = String(action || '').trim();
    const normalized = inferPreviewActions(raw, guides);
    const primaryAction = normalized[0] || raw;
    return {
        raw,
        normalized,
        primaryAction,
        isCustom: Boolean(raw && !guides.has(raw)),
        guide: guideForAction(guides, primaryAction),
    };
}

function previewChoiceLabel(resolution) {
    if (!resolution.isCustom) return resolution.primaryAction || resolution.raw;
    const normalizedText = resolution.normalized.length ? resolution.normalized.join('、') : '待归类';
    return resolution.raw + ' → ' + normalizedText;
}

function renderActionPreviewPanel(state, options) {
    const guides = actionGuideMap(state);
    const recommended = recommendedActionGuides(state);
    const defaultAction = recommended[0]?.action || options[0] || '随缘而行';
    const selected = appState.selectedFocuses.length ? appState.selectedFocuses : [defaultAction].filter(Boolean);
    const mainAction = selected[0] || defaultAction;
    const preview = resolvePreviewAction(guides, mainAction);
    const guide = preview.guide;
    const choice = lifeChoiceOf(guide, preview.primaryAction || mainAction);
    const alignment = guide.goal_alignment || {};
    const streak = guide.streak_preview || {};
    const target = Number(guide.roll_target_preview || guide.roll_target_base || 0);
    const base = Number(guide.roll_target_base || target || 0);
    const bonus = Number(streak.bonus || 0);
    const eventPreview = guide.event_preview || {};
    const eventDomains = Array.isArray(eventPreview.life_domains) ? eventPreview.life_domains.filter(Boolean).slice(0, 3).join('、') : '';
    const selectedPills = selected.map(action => {
        const resolved = resolvePreviewAction(guides, action);
        const item = resolved.guide;
        const itemAlignment = item.goal_alignment || {};
        const label = resolved.isCustom ? previewChoiceLabel(resolved) : choiceShortLabel(item, action);
        return '<span>' + escapeHtml(label) + ' · ' + escapeHtml(itemAlignment.level || (resolved.normalized.length ? '已预归类' : '待判定')) + '</span>';
    }).join('');
    return '<section class=\'action-preview-panel\' aria-live=\'polite\'>' +
        '<div class=\'action-preview-head\'><div><span>' + (appState.selectedFocuses.length ? '人生抉择' : '默认抉择') + '</span><strong>' + escapeHtml(preview.isCustom ? preview.raw : (choice.short_label || mainAction)) + '</strong><small>' + escapeHtml(previewChoiceLabel(preview)) + '</small></div>' +
        '<b>' + escapeHtml(alignment.level || '等待选择') + '</b></div>' +
        '<p>' + escapeHtml(preview.isCustom ? ('你写下“' + preview.raw + '”，系统预判会归入“' + (preview.normalized.join('、') || '随缘而行') + '”；提交后以后端权威归类为准。') : (choice.decision || guide.summary || '先选择一个本半年抉择，系统会解释命盘、时运和选择如何共同影响人生。')) + '</p>' +
        '<div class=\'action-preview-grid\'>' +
            '<article><span>当前处境</span><b>' + escapeHtml(choice.title || mainAction) + '</b><small>' + escapeHtml(choice.situation || '人生处在新的岔口。') + '</small></article>' +
            '<article><span>命盘提示</span><b>' + escapeHtml(formatGuideBenefit(guide)) + '</b><small>' + escapeHtml(choice.bazi_hint || '命盘提供底色，但不替你做决定。') + '</small></article>' +
            '<article><span>时运提示</span><b>' + escapeHtml(alignment.level || '自由探索') + '</b><small>' + escapeHtml(choice.fortune_hint || recommendationReason(guide)) + '</small></article>' +
            '<article><span>命盘事件倾向</span><b>' + escapeHtml(eventPreview.title || '待触发') + '</b><small>' + escapeHtml(eventPreview.bazi_event_influence || (eventDomains ? '更容易落在“' + eventDomains + '”这些生活面向。' : '提交后会按命盘、时运和行动重新抽取阶段事件。')) + '</small></article>' +
            '<article><span>取舍代价</span><b>' + escapeHtml(formatGuideRisk(guide)) + '</b><small>' + escapeHtml(choice.choice_impact || '选择会留下长期回声。') + '</small></article>' +
            '<article><span>后台推演</span><b>' + escapeHtml(target ? 'D100 约 ' + String(target) : '待归类') + '</b><small>' + escapeHtml(bonus ? ('基础 ' + base + ' / 路径惯性 +' + bonus) : '暗中合参大运、流年、流月与当前状态') + '</small></article>' +
        '</div>' +
        (selectedPills ? '<div class=\'action-preview-selected\'><small>本次组合</small>' + selectedPills + '</div>' : '') +
    '</section>';
}

function wireHorizontalWheelScroll(strip) {
    if (!strip) return;
    strip.addEventListener('wheel', event => {
        if (strip.scrollWidth <= strip.clientWidth) return;
        const delta = Math.abs(event.deltaY) >= Math.abs(event.deltaX) ? event.deltaY : event.deltaX;
        if (!delta) return;
        const maxScrollLeft = strip.scrollWidth - strip.clientWidth;
        const nextScrollLeft = Math.max(0, Math.min(maxScrollLeft, strip.scrollLeft + delta));
        if (nextScrollLeft === strip.scrollLeft) return;
        event.preventDefault();
        strip.scrollLeft = nextScrollLeft;
    }, { passive: false });
}

function renderFocusActions() {
    const state = appState.gameState || {};
    const canAct = state.phase === 'life_simulation' && !state.is_finished;
    DOMElements.focusActions.innerHTML = '';
    DOMElements.gameView.classList.toggle('action-tray-compact', canAct);
    if (!canAct) return;
    const options = cleanActionOptions(state);
    const guides = actionGuideMap(state);
    const recommended = recommendedActionGuides(state).map(guide => guide.action).filter(Boolean);
    const topOptions = Array.from(new Set((recommended.length ? recommended : options).concat(options))).slice(0, 3);
    const visibleOptions = appState.actionOptionsExpanded ? options : topOptions;
    appState.selectedFocuses = appState.selectedFocuses.map(option => String(option || '').trim()).filter(Boolean).slice(0, 3);
    const stage = state.current_stage || {};
    const meta = document.createElement('div');
    meta.className = 'decision-dock-meta';
    const defaultText = topOptions[0] || options[0] || '随缘而行';
    const selectedText = appState.selectedFocuses.length
        ? appState.selectedFocuses.map(action => {
            const resolved = resolvePreviewAction(guides, action);
            return resolved.isCustom ? previewChoiceLabel(resolved) : choiceShortLabel(guideForAction(guides, action), action);
        }).join('、')
        : '尚未选择，默认采用推荐：' + choiceShortLabel(guideForAction(guides, defaultText), defaultText);
    meta.innerHTML =
        '<p class=\'stage-action-hint\'><span>' + escapeHtml(stage.label || '本半年人生抉择') + '</span><small>' + escapeHtml(stage.summary || '请选择符合当前人生阶段的抉择。') + '</small></p>' +
        '<div class=\'selected-focus-summary\'><span>已选 ' + appState.selectedFocuses.length + '/3</span><strong>' + escapeHtml(selectedText) + '</strong></div>';
    DOMElements.focusActions.appendChild(meta);

    const rail = document.createElement('div');
    rail.className = 'decision-action-rail';
    const chipStrip = document.createElement('div');
    chipStrip.className = 'focus-chip-strip';
    visibleOptions.forEach((option, index) => {
        const guide = guideForAction(guides, option);
        const alignment = guide.goal_alignment || {};
        const streak = guide.streak_preview || {};
        const choice = lifeChoiceOf(guide, option);
        const button = document.createElement('button');
        button.textContent = choice.short_label || option;
        button.className = 'focus-chip' +
            (appState.selectedFocuses.includes(option) ? ' selected' : '') +
            (Number(alignment.score || 0) >= 3 ? ' goal-fit' : '') +
            (Number(streak.bonus || 0) > 0 ? ' streak-ready' : '') +
            (!appState.actionOptionsExpanded && index < 3 ? ' recommended-chip' : '');
        button.setAttribute('aria-pressed', String(appState.selectedFocuses.includes(option)));
        if (!appState.actionOptionsExpanded && index < 3) button.dataset.rank = String(index + 1);
        button.title = [option, alignment.level, choice.decision || guide.summary, Number(streak.bonus || 0) > 0 ? '路径惯性 +' + Number(streak.bonus || 0) : ''].filter(Boolean).join(' · ');
        button.addEventListener('click', () => toggleFocus(option));
        chipStrip.appendChild(button);
    });
    if (options.length > topOptions.length) {
        const more = document.createElement('button');
        more.className = 'focus-chip more-actions-chip';
        more.type = 'button';
        more.textContent = appState.actionOptionsExpanded ? '收起抉择' : '更多抉择 +' + (options.length - topOptions.length);
        more.setAttribute('aria-label', appState.actionOptionsExpanded ? '收起更多行动' : '更多行动：展开更多人生抉择');
        more.setAttribute('aria-expanded', String(appState.actionOptionsExpanded));
        more.addEventListener('click', () => {
            appState.actionOptionsExpanded = !appState.actionOptionsExpanded;
            renderFocusActions();
        });
        chipStrip.appendChild(more);
    }
    wireHorizontalWheelScroll(chipStrip);
    const submit = document.createElement('button');
    submit.className = 'primary-button compact submit-focus-button';
    submit.textContent = '确认本半年选择';
    submit.addEventListener('click', submitFocuses);
    rail.appendChild(chipStrip);
    rail.appendChild(submit);
    DOMElements.focusActions.appendChild(rail);
    DOMElements.focusActions.insertAdjacentHTML('beforeend', renderActionPreviewPanel(state, options));
}
