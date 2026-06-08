const API_BASE_URL = '/api';

const appState = {
    gameState: null,
    lastRollEventId: null,
    selectedFocuses: [],
    aiSettings: null,
    apiSettingsVisible: false,
    codexVisible: false,
    selectedApiProfileId: '',
    historyFilter: 'all',
    historyExpanded: false,
};

const scrollState = {
    animationId: null,
    isUserScrolling: false,
    scrollTimeout: null,
    isFirstRender: true,
};

const DOMElements = {
    loginView: document.getElementById('login-view'),
    gameView: document.getElementById('game-view'),
    loginError: document.getElementById('login-error'),
    guestLoginButton: document.getElementById('guest-login-button'),
    logoutButton: document.getElementById('logout-button'),
    resetButton: document.getElementById('reset-button'),
    codexButton: document.getElementById('codex-button'),
    codexBackdrop: document.getElementById('codex-backdrop'),
    codexPanel: document.getElementById('codex-panel'),
    codexCloseButton: document.getElementById('codex-close-button'),
    codexContent: document.getElementById('codex-content'),
    apiSettingsButton: document.getElementById('api-settings-button'),
    exportArchiveButton: document.getElementById('export-archive-button'),
    apiSettingsBackdrop: document.getElementById('api-settings-backdrop'),
    apiSettingsPanel: document.getElementById('api-settings-panel'),
    apiSettingsCloseButton: document.getElementById('api-settings-close-button'),
    apiSettingsForm: document.getElementById('api-settings-form'),
    apiProfileList: document.getElementById('api-profile-list'),
    addApiProfileButton: document.getElementById('add-api-profile-button'),
    customApiProfileId: document.getElementById('custom-api-profile-id'),
    customApiName: document.getElementById('custom-api-name'),
    customApiKey: document.getElementById('custom-api-key'),
    customApiBaseUrl: document.getElementById('custom-api-base-url'),
    customApiModel: document.getElementById('custom-api-model'),
    customApiEnabled: document.getElementById('custom-api-enabled'),
    testApiSettingsButton: document.getElementById('test-api-settings-button'),
    activateApiProfileButton: document.getElementById('activate-api-profile-button'),
    clearProfileKeyButton: document.getElementById('clear-profile-key-button'),
    clearApiSettingsButton: document.getElementById('clear-api-settings-button'),
    apiSettingsStatus: document.getElementById('api-settings-status'),
    sceneBackgroundImage: document.getElementById('scene-background-image'),
    statusToggleButton: document.getElementById('status-toggle-button'),
    statusCloseButton: document.getElementById('status-close-button'),
    statusRailButton: document.getElementById('status-rail-button'),
    characterStatus: document.getElementById('character-status'),
    phasePill: document.getElementById('phase-pill'),
    birthForm: document.getElementById('birth-form'),
    calendarType: document.getElementById('calendar-type'),
    birthTime: document.getElementById('birth-time'),
    unknownTime: document.getElementById('unknown-time'),
    startAge: document.getElementById('start-age'),
    birthPanel: document.getElementById('birth-panel'),
    chartPanel: document.getElementById('chart-panel'),
    preludePanel: document.getElementById('prelude-panel'),
    simulationPanel: document.getElementById('simulation-panel'),
    chartGrid: document.getElementById('chart-grid'),
    elementBoard: document.getElementById('element-board'),
    luckTimeline: document.getElementById('luck-timeline'),
    preludeContent: document.getElementById('prelude-content'),
    turnGuide: document.getElementById('turn-guide'),
    yearBanner: document.getElementById('year-banner'),
    monthFlowBoard: document.getElementById('month-flow-board'),
    narrativeWindow: document.getElementById('narrative-window'),
    focusActions: document.getElementById('focus-actions'),
    actionInput: document.getElementById('action-input'),
    actionButton: document.getElementById('action-button'),
    retrospectButton: document.getElementById('retrospect-button'),
    generatePreludeButton: document.getElementById('generate-prelude-button'),
    editBirthButton: document.getElementById('edit-birth-button'),
    acceptPreludeButton: document.getElementById('accept-prelude-button'),
    regenPreludeButton: document.getElementById('regen-prelude-button'),
    loadingSpinner: document.getElementById('loading-spinner'),
    rollOverlay: document.getElementById('roll-overlay'),
    rollStageLabel: document.getElementById('roll-stage-label'),
    rollType: document.getElementById('roll-type'),
    rollTarget: document.getElementById('roll-target'),
    rollResultDisplay: document.getElementById('roll-result-display'),
    rollOutcome: document.getElementById('roll-outcome'),
    rollValue: document.getElementById('roll-value'),
};

const api = {
    async initGame() {
        const response = await fetch(API_BASE_URL + '/game/init', { method: 'POST' });
        if (response.status === 401) throw new Error('Unauthorized');
        if (!response.ok) throw new Error('Failed to initialize game session');
        return response.json();
    },
    async guestLogin() {
        const response = await fetch(API_BASE_URL + '/guest', { method: 'POST' });
        if (!response.ok) throw new Error('Guest login failed');
        return response.json();
    },
    async logout() {
        await fetch(API_BASE_URL + '/logout', { method: 'POST' });
        window.location.href = '/';
    },
    async getAiSettings() {
        const response = await fetch(API_BASE_URL + '/settings/ai');
        if (!response.ok) throw new Error('Failed to load AI API settings');
        return response.json();
    },
    async saveAiSettings(data) {
        const response = await fetch(API_BASE_URL + '/settings/ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        if (!response.ok) {
            const payload = await response.json().catch(() => ({}));
            throw new Error(payload.detail || 'Failed to save AI API settings');
        }
        return response.json();
    },
    async testAiSettings(data) {
        const response = await fetch(API_BASE_URL + '/settings/ai/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.detail || 'Failed to test AI API settings');
        return payload;
    },
    async saveAiProfile(data) {
        const response = await fetch(API_BASE_URL + '/settings/ai/profiles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.detail || 'Failed to save AI API profile');
        return payload;
    },
    async activateAiProfile(profileId) {
        const response = await fetch(API_BASE_URL + '/settings/ai/profiles/' + encodeURIComponent(profileId) + '/activate', { method: 'POST' });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.detail || 'Failed to activate AI API profile');
        return payload;
    },
    async deleteAiProfile(profileId) {
        const response = await fetch(API_BASE_URL + '/settings/ai/profiles/' + encodeURIComponent(profileId), { method: 'DELETE' });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.detail || 'Failed to delete AI API profile');
        return payload;
    },
    async clearAiSettings() {
        const response = await fetch(API_BASE_URL + '/settings/ai', { method: 'DELETE' });
        if (!response.ok) throw new Error('Failed to clear AI API settings');
        return response.json();
    },
};

function applyPatch(doc, patch) {
    for (const op of patch || []) {
        const parts = op.path.split('/').slice(1).map(part => part.replace(/~1/g, '/').replace(/~0/g, '~'));
        let target = doc;
        for (const part of parts.slice(0, -1)) target = target[part];
        const key = parts[parts.length - 1];
        if (op.op === 'remove') {
            if (Array.isArray(target)) target.splice(Number(key), 1);
            else delete target[key];
        } else if (op.op === 'add' && Array.isArray(target)) {
            if (key === '-') target.push(op.value);
            else target.splice(Number(key), 0, op.value);
        } else {
            target[key] = op.value;
        }
    }
    return doc;
}

const socketManager = {
    socket: null,
    connect() {
        return new Promise((resolve, reject) => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                resolve();
                return;
            }
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = protocol + '//' + window.location.host + API_BASE_URL + '/ws';
            this.socket = new WebSocket(wsUrl);
            this.socket.onopen = () => resolve();
            this.socket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                if (message.type === 'full_state') {
                    appState.gameState = message.data;
                } else if (message.type === 'patch' && appState.gameState) {
                    appState.gameState = applyPatch(appState.gameState, message.patch);
                }
                checkAndShowRollEvent();
                render();
            };
            this.socket.onclose = () => setTimeout(() => this.connect(), 3000);
            this.socket.onerror = (error) => reject(error);
        });
    },
    sendAction(action) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ action }));
        }
    },
};

function showView(viewId) {
    document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
}

function escapeHtml(text) {
    return String(text || '').replace(/[&<>]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[char]));
}

function joinCleanList(value, fallback = '') {
    const items = Array.isArray(value) ? value : [value];
    const text = items
        .map(item => String(item || '').trim())
        .filter(Boolean)
        .join('、');
    return text || fallback;
}

function formatLegacyStateEffectLine(line) {
    const rawLine = String(line || '');
    const prefix = '状态变化：';
    const index = rawLine.indexOf(prefix);
    if (index === -1) return rawLine;
    const rawEffect = rawLine.slice(index + prefix.length).trim();
    if (!rawEffect.startsWith('{')) return rawLine;
    const entries = Array.from(rawEffect.matchAll(/[\'"]([^\'"]+)[\'"]\s*:\s*(-?\d+)/g))
        .map(match => {
            const value = Number(match[2]);
            return match[1] + ' ' + (value > 0 ? '+' : '') + value;
        });
    return entries.length ? rawLine.slice(0, index + prefix.length) + entries.join('、') : rawLine;
}

function parseLegacyPreludeEvent(text) {
    const raw = String(text || '').trim();
    if (!raw.startsWith('{') || !raw.includes('event')) return null;
    const pickText = (key) => {
        const match = raw.match(new RegExp('[\\\'"]' + key + '[\\\'"]\\s*:\\s*[\\\'"]([^\\\'"]*)[\\\'"]'));
        return match ? match[1] : '';
    };
    const pickNumber = (key) => {
        const match = raw.match(new RegExp('[\\\'"]' + key + '[\\\'"]\\s*:\\s*(\\d+)'));
        return match ? match[1] : '';
    };
    const event = pickText('event') || pickText('text') || pickText('summary') || pickText('description');
    if (!event) return null;
    return {
        age: pickNumber('age') || pickText('age'),
        year: pickNumber('year') || pickText('year'),
        event,
        impact: pickText('impact') || pickText('effect') || pickText('influence'),
    };
}

function normalizePreludeEvent(item) {
    if (item && typeof item === 'object' && !Array.isArray(item)) {
        return {
            age: item.age || '',
            year: item.year || '',
            event: item.event || item.text || item.summary || item.description || JSON.stringify(item),
            impact: item.impact || item.effect || item.influence || '',
        };
    }
    const legacy = parseLegacyPreludeEvent(item);
    if (legacy) return legacy;
    return { age: '', year: '', event: String(item || ''), impact: '' };
}

function renderPreludeEvent(item, compact = false) {
    const event = normalizePreludeEvent(item);
    const meta = [
        event.age ? event.age + '岁' : '',
        event.year ? event.year + '年' : '',
    ].filter(Boolean).join(' · ');
    return '<article class=\'prelude-event-card' + (compact ? ' compact' : '') + '\'>' +
        (meta ? '<span class=\'prelude-event-meta\'>' + escapeHtml(meta) + '</span>' : '') +
        '<p>' + escapeHtml(event.event) + '</p>' +
        (event.impact ? '<small>影响：' + escapeHtml(event.impact) + '</small>' : '') +
        '</article>';
}

function renderText(text) {
    return String(text || '').split('\n').map(line => {
        line = formatLegacyStateEffectLine(line);
        if (line.startsWith('# ')) return '<h1>' + escapeHtml(line.slice(2)) + '</h1>';
        if (line.startsWith('## ')) return '<h2>' + escapeHtml(line.slice(3)) + '</h2>';
        if (line.startsWith('- ')) {
            const body = line.slice(2);
            if (parseLegacyPreludeEvent(body)) return renderPreludeEvent(body, true);
            return '<p class=\'bullet-line\'>• ' + escapeHtml(body) + '</p>';
        }
        return line ? '<p>' + escapeHtml(line) + '</p>' : '';
    }).join('');
}

function showLoading(isLoading) {
    DOMElements.loadingSpinner.style.display = isLoading ? 'flex' : 'none';
}

function phaseLabel(phase) {
    return ({ birth_input: '出生信息', chart_ready: '命盘已成', prelude_ready: '前传已成', life_simulation: '人生模拟', ending: '结局' })[phase] || '待排盘';
}

function showPanel(panel, visible) {
    panel.classList.toggle('hidden', !visible);
}

const elementLabels = { wood: '木', fire: '火', earth: '土', metal: '金', water: '水' };
const tenGodLabels = { year: '年干', month: '月干', day: '日干', hour: '时干' };
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

function renderPrelude() {
    const prelude = appState.gameState?.prelude;
    if (!prelude) return;
    const goals = appState.gameState?.life_goals || [];
    const activeGoalId = appState.gameState?.active_life_goal_id || appState.gameState?.goal_progress?.goal_id || '';
    const canSelectGoal = appState.gameState?.phase === 'prelude_ready';
    const goalHtml = goals.length ? '<h3>选择人生愿望</h3><div class=\'life-goal-grid\'>' + goals.map(goal => {
        const active = goal.id === activeGoalId;
        return '<article class=\'life-goal-card' + (active ? ' active' : '') + '\'>' +
            '<span>' + escapeHtml(active ? '当前愿望' : goal.status || '可选择') + '</span>' +
            '<strong>' + escapeHtml(goal.title || '') + '</strong>' +
            '<p>' + escapeHtml(goal.summary || '') + '</p>' +
            '<small>初始进度：' + Number(goal.current_score || 0) + '/' + Number(goal.ending_threshold || 0) + ' · 支持行动：' + escapeHtml((goal.support_actions || []).join('、')) + '</small>' +
            (canSelectGoal ? '<button type=\'button\' data-life-goal-id=\'' + escapeHtml(goal.id) + '\'>' + (active ? '已选择' : '选这个愿望') + '</button>' : '') +
        '</article>';
    }).join('') + '</div>' : '';
    DOMElements.preludeContent.innerHTML = '<p>' + escapeHtml(prelude.text) + '</p>' +
        '<h3>性格底色</h3><div class=\'tag-row\'>' + (prelude.personality || []).map(item => '<span>' + escapeHtml(item) + '</span>').join('') + '</div>' +
        goalHtml +
        '<h3>早年关键事件</h3><div class=\'prelude-event-list\'>' + (prelude.early_events || []).map(item => renderPreludeEvent(item)).join('') + '</div>';
    DOMElements.preludeContent.querySelectorAll('[data-life-goal-id]').forEach(button => {
        button.addEventListener('click', () => {
            socketManager.sendAction({ type: 'set_life_goal', goal_id: button.dataset.lifeGoalId || '' });
        });
    });
}

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
            ? (warning || '继续相同主重点会获得 D100 加成，也会记录机会成本。')
            : '完成第一次半年度行动后，这里会显示连续选择反馈。',
    };
}

function renderStreakStatusCard(state) {
    const view = getStreakView(state || {});
    if (!view.action) return '';
    const bonusText = view.bonus > 0 ? 'D100 +' + view.bonus : '观察中';
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
    const streakBonus = streakView.bonus > 0 ? 'D100 +' + streakView.bonus : '暂未加成';
    DOMElements.turnGuide.innerHTML = '<section class=\'turn-guide-card\'>' +
        '<div class=\'turn-guide-heading\'><div><span>本半年决策提示</span><strong>' + escapeHtml(stage.label || '人生阶段') + '</strong></div><p>' + escapeHtml(stage.summary || '选择会影响长期状态、愿望进度与结局档案。') + '</p></div>' +
        '<div class=\'turn-guide-grid\'>' +
            '<article><span>目标</span><b>' + escapeHtml(goalText) + '</b><small>' + escapeHtml(goal.summary || '可在前传页选择主愿望。') + '</small></article>' +
            '<article><span>时势</span><b>' + escapeHtml((luck.pillar || '-') + ' 大运 / ' + (annual.pillar || '-') + ' 流年') + '</b><small>大运看十年基调，流年看当年事件倾向。</small></article>' +
            '<article><span>流月机会</span><b>' + escapeHtml(opportunity) + '</b><small>可优先选择能承接机会的行动。</small></article>' +
            '<article><span>风险提醒</span><b>' + escapeHtml(risk) + '</b><small>压力过高会拖累 D100 目标值。</small></article>' +
            '<article class=\'streak-preview-card\'><span>连续投入</span><b>' + escapeHtml(streakView.label) + '</b><small>' + escapeHtml(streakBonus + ' · ' + streakView.hint) + '</small></article>' +
        '</div>' +
        '<details class=\'turn-glossary\'><summary>术语速查</summary><p><b>起运</b>：从出生到进入第一步大运的年龄；<b>大运</b>：十年基调；<b>流年</b>：当年主题；<b>流月</b>：本半年每月机会/风险；<b>D100</b>：系统用百分骰判定行动成败。</p></details>' +
    '</section>';
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
    DOMElements.monthFlowBoard.innerHTML = '<h3>本半年流月</h3><div class=\'month-flow-grid\'>' + months.map(month => {
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
    }).join('') + '</div>';
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

function formatGuideEffect(guide) {
    if (!guide) return '选择后会根据命盘、时势和 D100 判定产生状态变化。';
    const primary = guide.primary ? guide.primary + ' ' + Number(guide.primary_score || 0) + '分' : '主属性待定';
    const secondary = guide.secondary ? guide.secondary + ' ' + Number(guide.secondary_score || 0) + '分' : '副属性待定';
    const risk = guide.risk ? guide.risk + ' ' + Number(guide.risk_score || 0) + '分' : '风险待定';
    return '主推 ' + primary + ' · 辅助 ' + secondary + ' · 风险 ' + risk;
}

function renderActionPreviewPanel(state, options) {
    const guides = actionGuideMap(state);
    const selected = appState.selectedFocuses.length ? appState.selectedFocuses : [options[0]].filter(Boolean);
    const mainAction = selected[0] || options[0] || '随缘而行';
    const guide = guides.get(mainAction) || {};
    const alignment = guide.goal_alignment || {};
    const streak = guide.streak_preview || {};
    const target = Number(guide.roll_target_preview || guide.roll_target_base || 0);
    const base = Number(guide.roll_target_base || target || 0);
    const bonus = Number(streak.bonus || 0);
    const selectedPills = selected.map(action => {
        const item = guides.get(action) || {};
        const itemAlignment = item.goal_alignment || {};
        return '<span>' + escapeHtml(action) + ' · ' + escapeHtml(itemAlignment.level || '待判定') + '</span>';
    }).join('');
    return '<section class=\'action-preview-panel\' aria-live=\'polite\'>' +
        '<div class=\'action-preview-head\'><div><span>行动预览</span><strong>' + escapeHtml(mainAction) + '</strong></div>' +
        '<b>' + escapeHtml(alignment.level || '等待选择') + '</b></div>' +
        '<p>' + escapeHtml(guide.summary || '先选择一个本半年重点，系统会预览愿望同频、判定目标和连续投入。') + '</p>' +
        '<div class=\'action-preview-grid\'>' +
            '<article><span>预计判定</span><b>' + escapeHtml(target ? String(target) : '-') + '</b><small>' + escapeHtml(bonus ? ('基础 ' + base + ' / 连续投入 +' + bonus) : '合参大运、流年、流月与当前属性') + '</small></article>' +
            '<article><span>愿望同频</span><b>' + escapeHtml(alignment.level || '-') + '</b><small>' + escapeHtml(alignment.reason || '选择人生愿望后会显示更准确的同频提示。') + '</small></article>' +
            '<article><span>属性走向</span><b>' + escapeHtml(formatGuideEffect(guide)) + '</b><small>' + escapeHtml(guide.clue || '阶段事件会留下后续伏笔。') + '</small></article>' +
            '<article><span>连续预判</span><b>' + escapeHtml((Number(streak.count || 1)) + ' 次' + (bonus ? ' / D100 +' + bonus : ' / 暂无加成')) + '</b><small>同一主行动连续选择会形成加成，也会积累机会成本。</small></article>' +
        '</div>' +
        (selectedPills ? '<div class=\'action-preview-selected\'><small>本次组合</small>' + selectedPills + '</div>' : '') +
    '</section>';
}

function renderEndingCodex() {
    const codex = appState.gameState?.ending_codex || {};
    const entries = Array.isArray(codex.entries) ? codex.entries : [];
    const total = Number(codex.total_count || entries.length || 0);
    const unlocked = Number(codex.unlocked_count || 0);
    DOMElements.codexButton.textContent = '图鉴 ' + unlocked + '/' + total;
    DOMElements.codexButton.setAttribute('aria-expanded', String(appState.codexVisible));
    DOMElements.codexPanel.classList.toggle('hidden', !appState.codexVisible);
    DOMElements.codexBackdrop.classList.toggle('hidden', !appState.codexVisible);
    DOMElements.codexPanel.setAttribute('aria-hidden', String(!appState.codexVisible));
    DOMElements.codexBackdrop.setAttribute('aria-hidden', String(!appState.codexVisible));
    document.body.classList.toggle('modal-open', appState.apiSettingsVisible || appState.codexVisible);
    if (!appState.codexVisible) return;
    if (!entries.length) {
        DOMElements.codexContent.innerHTML = '<p class=\'codex-empty\'>图鉴正在等待第一段人生结局。</p>';
        return;
    }
    const latest = (codex.latest_unlocks || []).map(item => item.title).filter(Boolean).join('、');
    const progress = total ? Math.round((unlocked / total) * 100) : 0;
    const cards = entries.map(entry => {
        const unlockedClass = entry.unlocked ? ' unlocked' : ' locked';
        const rarityClass = ' rarity-' + String(entry.rarity || '普通').toLowerCase();
        const title = entry.unlocked ? entry.title : '未解锁';
        const body = entry.unlocked ? entry.description : entry.hint;
        const meta = entry.unlocked
            ? ('已解锁' + (entry.unlock_count > 1 ? ' ×' + entry.unlock_count : '') + (entry.unlocked_at ? ' · 首次 ' + entry.unlocked_at : ''))
            : '线索';
        return '<article class=\'codex-card' + unlockedClass + rarityClass + '\'>' +
            '<span>' + escapeHtml(entry.rarity || '普通') + ' · ' + escapeHtml(entry.category || '结局') + '</span>' +
            '<strong>' + escapeHtml(title) + '</strong>' +
            '<p>' + escapeHtml(body || '') + '</p>' +
            '<small>' + escapeHtml(meta) + '</small>' +
        '</article>';
    }).join('');
    DOMElements.codexContent.innerHTML =
        '<section class=\'codex-summary\'><div><span>收集进度</span><strong>' + unlocked + '/' + total + '</strong></div>' +
        '<meter min=\'0\' max=\'100\' value=\'' + progress + '\'></meter>' +
        '<p>' + escapeHtml(latest ? '本次新解锁：' + latest : '完成不同人生路线，点亮更多结局。未解锁卡片只显示线索。') + '</p></section>' +
        '<div class=\'codex-grid\'>' + cards + '</div>';
}

function renderFocusActions() {
    const state = appState.gameState || {};
    const canAct = state.phase === 'life_simulation' && !state.is_finished;
    DOMElements.focusActions.innerHTML = '';
    DOMElements.gameView.classList.toggle('action-tray-compact', canAct);
    if (!canAct) return;
    const options = cleanActionOptions(state);
    const guides = actionGuideMap(state);
    appState.selectedFocuses = appState.selectedFocuses.filter(option => options.includes(option));
    const stage = state.current_stage || {};
    const meta = document.createElement('div');
    meta.className = 'decision-dock-meta';
    const selectedText = appState.selectedFocuses.length ? appState.selectedFocuses.join('、') : '尚未选择，默认参考第一项';
    meta.innerHTML =
        '<p class=\'stage-action-hint\'><span>' + escapeHtml(stage.label || '本半年行动') + '</span><small>' + escapeHtml(stage.summary || '请选择符合当前人生阶段的行动重点。') + '</small></p>' +
        '<div class=\'selected-focus-summary\'><span>已选 ' + appState.selectedFocuses.length + '/3</span><strong>' + escapeHtml(selectedText) + '</strong></div>';
    DOMElements.focusActions.appendChild(meta);

    const rail = document.createElement('div');
    rail.className = 'decision-action-rail';
    const chipStrip = document.createElement('div');
    chipStrip.className = 'focus-chip-strip';
    options.forEach(option => {
        const guide = guides.get(option) || {};
        const alignment = guide.goal_alignment || {};
        const streak = guide.streak_preview || {};
        const button = document.createElement('button');
        button.textContent = option;
        button.className = 'focus-chip' + (appState.selectedFocuses.includes(option) ? ' selected' : '') + (Number(alignment.score || 0) >= 3 ? ' goal-fit' : '') + (Number(streak.bonus || 0) > 0 ? ' streak-ready' : '');
        button.setAttribute('aria-pressed', String(appState.selectedFocuses.includes(option)));
        button.title = [alignment.level, guide.summary, Number(streak.bonus || 0) > 0 ? '连续投入 +' + Number(streak.bonus || 0) : ''].filter(Boolean).join(' · ');
        button.addEventListener('click', () => toggleFocus(option));
        chipStrip.appendChild(button);
    });
    const submit = document.createElement('button');
    submit.className = 'primary-button compact submit-focus-button';
    submit.textContent = '提交本半年重点';
    submit.addEventListener('click', submitFocuses);
    rail.appendChild(chipStrip);
    rail.appendChild(submit);
    DOMElements.focusActions.appendChild(rail);
    DOMElements.focusActions.insertAdjacentHTML('beforeend', renderActionPreviewPanel(state, options));
}

function renderApiSettings() {
    const settings = appState.aiSettings || {};
    DOMElements.apiSettingsPanel.classList.toggle('hidden', !appState.apiSettingsVisible);
    DOMElements.apiSettingsBackdrop.classList.toggle('hidden', !appState.apiSettingsVisible);
    DOMElements.apiSettingsPanel.setAttribute('aria-hidden', String(!appState.apiSettingsVisible));
    DOMElements.apiSettingsBackdrop.setAttribute('aria-hidden', String(!appState.apiSettingsVisible));
    DOMElements.apiSettingsButton.setAttribute('aria-expanded', String(appState.apiSettingsVisible));
    document.body.classList.toggle('modal-open', appState.apiSettingsVisible || appState.codexVisible);
    if (!appState.apiSettingsVisible) return;
    renderApiProfileList();
    DOMElements.apiSettingsStatus.className = 'api-settings-status' + (settings.custom_enabled ? ' enabled' : '');
    DOMElements.apiSettingsStatus.textContent = settings.custom_enabled
        ? '已启用自定义 AI API：' + (settings.base_url || '') + ' / ' + (settings.model || '')
        : '未启用自定义 AI API；当前使用本地规则或服务器环境变量。';
}

function apiProfiles() {
    return appState.aiSettings?.profiles || [];
}

function selectedApiProfile() {
    const profiles = apiProfiles();
    return profiles.find(profile => profile.id === appState.selectedApiProfileId) ||
        profiles.find(profile => profile.id === appState.aiSettings?.active_profile_id) ||
        profiles[0] ||
        null;
}

function renderApiProfileList() {
    const profiles = apiProfiles();
    if (!profiles.length) {
        DOMElements.apiProfileList.innerHTML = '<p class=\'empty-profile-note\'>还没有保存的 API 配置。点击“新增配置”创建一个档案。</p>';
        return;
    }
    DOMElements.apiProfileList.innerHTML = profiles.map(profile => {
        const classes = ['api-profile-card'];
        if (profile.id === appState.selectedApiProfileId) classes.push('selected');
        if (profile.active) classes.push('active');
        return '<button class=\'' + classes.join(' ') + '\' type=\'button\' data-profile-id=\'' + escapeHtml(profile.id) + '\'>' +
            '<span>' + escapeHtml(profile.active ? '默认' : (profile.enabled ? '启用' : '停用')) + '</span>' +
            '<strong>' + escapeHtml(profile.name || '自定义 API') + '</strong>' +
            '<small>' + escapeHtml(profile.model || '-') + '</small>' +
            '<em>' + escapeHtml(profile.api_key_set ? profile.api_key_mask : '未设置 Key') + '</em>' +
        '</button>';
    }).join('');
    DOMElements.apiProfileList.querySelectorAll('[data-profile-id]').forEach(button => {
        button.addEventListener('click', () => selectApiProfile(button.dataset.profileId || ''));
    });
}

function populateApiSettingsForm() {
    const profile = selectedApiProfile();
    DOMElements.customApiProfileId.value = profile?.id || '';
    DOMElements.customApiName.value = profile?.name || '';
    DOMElements.customApiBaseUrl.value = profile?.base_url || 'https://api.openai.com/v1';
    DOMElements.customApiModel.value = profile?.model || 'gpt-4o-mini';
    DOMElements.customApiEnabled.checked = profile ? Boolean(profile.enabled) : true;
    DOMElements.customApiKey.placeholder = profile?.api_key_set ? '已保存：' + profile.api_key_mask + '，输入新 Key 可覆盖' : 'sk-...';
    renderApiSettings();
}

function selectApiProfile(profileId) {
    appState.selectedApiProfileId = profileId;
    DOMElements.customApiKey.value = '';
    populateApiSettingsForm();
}

function startNewApiProfile() {
    appState.selectedApiProfileId = '';
    DOMElements.customApiProfileId.value = '';
    DOMElements.customApiName.value = '';
    DOMElements.customApiKey.value = '';
    DOMElements.customApiBaseUrl.value = 'https://api.openai.com/v1';
    DOMElements.customApiModel.value = 'gpt-4o-mini';
    DOMElements.customApiEnabled.checked = true;
    renderApiSettings();
    DOMElements.customApiName.focus();
}

function setApiSettingsVisible(visible) {
    appState.apiSettingsVisible = visible;
    if (visible) {
        appState.codexVisible = false;
        renderEndingCodex();
        DOMElements.customApiKey.value = '';
        if (!appState.selectedApiProfileId) {
            appState.selectedApiProfileId = appState.aiSettings?.active_profile_id || apiProfiles()[0]?.id || '';
        }
        populateApiSettingsForm();
        setTimeout(() => DOMElements.customApiKey.focus(), 0);
    } else {
        renderApiSettings();
        DOMElements.apiSettingsButton.focus();
    }
}

function render() {
    if (!appState.gameState) return;
    const phase = appState.gameState.phase;
    DOMElements.phasePill.textContent = phaseLabel(phase);
    DOMElements.exportArchiveButton.disabled = phase === 'birth_input';
    renderStatus();
    renderChart();
    renderPrelude();
    renderTurnGuide();
    renderYearBanner();
    renderMonthFlowBoard();
    renderNarrative();
    renderFocusActions();
    renderEndingCodex();
    renderApiSettings();
    showPanel(DOMElements.birthPanel, phase === 'birth_input');
    showPanel(DOMElements.chartPanel, ['chart_ready', 'prelude_ready'].includes(phase));
    showPanel(DOMElements.preludePanel, phase === 'prelude_ready');
    showPanel(DOMElements.simulationPanel, ['life_simulation', 'ending'].includes(phase));
    DOMElements.actionInput.disabled = phase !== 'life_simulation' || appState.gameState.is_finished || appState.gameState.is_processing;
    DOMElements.actionButton.disabled = DOMElements.actionInput.disabled;
    DOMElements.retrospectButton.disabled = DOMElements.actionInput.disabled;
    showLoading(appState.gameState.is_processing);
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
        lines.push('- 判定加成：' + (streakView.bonus > 0 ? 'D100 +' + streakView.bonus : '暂无'));
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
    const codex = state.ending_codex || {};
    if (codex.entries?.length) {
        lines.push('');
        lines.push('## 结局图鉴');
        lines.push('- 收集进度：' + Number(codex.unlocked_count || 0) + '/' + Number(codex.total_count || codex.entries.length || 0));
        codex.entries.filter(item => item.unlocked).forEach(item => {
            lines.push('- ' + (item.title || '') + '（' + (item.rarity || '普通') + '）：' + (item.description || ''));
        });
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

function stopSmoothScroll() {
    if (scrollState.animationId) cancelAnimationFrame(scrollState.animationId);
    scrollState.animationId = null;
}

function smoothScrollToBottom(element, pixelsPerSecond = 150) {
    stopSmoothScroll();
    if (!element || scrollState.isUserScrolling) return;
    const start = element.scrollTop;
    const target = element.scrollHeight - element.clientHeight;
    const distance = target - start;
    if (distance <= 0) return;
    const duration = Math.max(250, (distance / pixelsPerSecond) * 1000);
    const startTime = performance.now();
    function tick(now) {
        const progress = Math.min(1, (now - startTime) / duration);
        element.scrollTop = start + distance * (1 - Math.pow(1 - progress, 2));
        if (progress < 1 && !scrollState.isUserScrolling) scrollState.animationId = requestAnimationFrame(tick);
    }
    scrollState.animationId = requestAnimationFrame(tick);
}

function setupScrollInterruptListener(element) {
    element.addEventListener('wheel', () => {
        scrollState.isUserScrolling = true;
        stopSmoothScroll();
        clearTimeout(scrollState.scrollTimeout);
        scrollState.scrollTimeout = setTimeout(() => { scrollState.isUserScrolling = false; }, 1800);
    }, { passive: true });
}

function scheduleSceneBackgroundUpdate() {
    requestAnimationFrame(updateSceneBackground);
}

function updateSceneBackground() {
    const images = DOMElements.narrativeWindow.querySelectorAll('img[src]');
    const latestImage = Array.from(images).reverse().find(img => img.complete && img.naturalWidth > 0);
    if (!latestImage) {
        images.forEach(img => {
            img.addEventListener('load', scheduleSceneBackgroundUpdate, { once: true });
            img.addEventListener('error', scheduleSceneBackgroundUpdate, { once: true });
        });
        document.body.classList.remove('has-scene-background');
        DOMElements.sceneBackgroundImage.removeAttribute('src');
        return;
    }
    const imageUrl = latestImage.currentSrc || latestImage.src;
    DOMElements.sceneBackgroundImage.src = imageUrl;
    document.body.classList.add('has-scene-background');
}

function checkAndShowRollEvent() {
    const rollEvent = appState.gameState?.roll_event;
    if (rollEvent && rollEvent.id && rollEvent.id !== appState.lastRollEventId) {
        appState.lastRollEventId = rollEvent.id;
        renderRollEvent(rollEvent);
    }
}

function renderRollEvent(rollEvent) {
    DOMElements.rollOverlay.classList.remove('pending');
    DOMElements.rollOverlay.classList.add('revealing');
    DOMElements.rollStageLabel.textContent = 'D100 已落定';
    DOMElements.rollType.textContent = '判定：' + rollEvent.type;
    DOMElements.rollTarget.textContent = '目标 <= ' + rollEvent.target;
    DOMElements.rollOutcome.textContent = rollEvent.outcome;
    DOMElements.rollOutcome.className = 'outcome-' + rollEvent.outcome;
    DOMElements.rollValue.textContent = rollEvent.result;
    DOMElements.rollResultDisplay.classList.add('hidden');
    DOMElements.rollOverlay.classList.remove('hidden');
    setTimeout(() => DOMElements.rollResultDisplay.classList.remove('hidden'), 700);
    setTimeout(() => {
        DOMElements.rollOverlay.classList.add('hidden');
        DOMElements.rollOverlay.classList.remove('revealing');
    }, 3200);
}

function showRollPending(focuses) {
    DOMElements.rollOverlay.classList.remove('hidden', 'revealing');
    DOMElements.rollOverlay.classList.add('pending');
    DOMElements.rollStageLabel.textContent = '命书推演中';
    DOMElements.rollType.textContent = '合参：大运 / 流年 / 流月';
    DOMElements.rollTarget.textContent = '行动：' + ((focuses || []).join('、') || '随缘而行');
    DOMElements.rollOutcome.textContent = '';
    DOMElements.rollValue.textContent = '...';
    DOMElements.rollResultDisplay.classList.remove('hidden');
}

function setStatusPanelCollapsed(isCollapsed) {
    DOMElements.gameView.classList.toggle('status-collapsed', isCollapsed);
    DOMElements.statusToggleButton.textContent = isCollapsed ? '展开状态' : '收起状态';
    DOMElements.statusToggleButton.setAttribute('aria-expanded', String(!isCollapsed));
}

function toggleStatusPanel() {
    setStatusPanelCollapsed(!DOMElements.gameView.classList.contains('status-collapsed'));
}

function initializeStatusPanelLayout() {
    setStatusPanelCollapsed(window.matchMedia('(max-width: 850px)').matches);
}

function toggleFocus(option) {
    const index = appState.selectedFocuses.indexOf(option);
    if (index >= 0) appState.selectedFocuses.splice(index, 1);
    else if (appState.selectedFocuses.length < 3) appState.selectedFocuses.push(option);
    renderFocusActions();
}

function submitFocuses() {
    const focuses = appState.selectedFocuses.length ? appState.selectedFocuses : ['随缘而行'];
    appState.selectedFocuses = [];
    showRollPending(focuses);
    socketManager.sendAction({ type: 'annual_action', focuses });
}

function submitBirthForm(event) {
    event.preventDefault();
    socketManager.sendAction({
        type: 'generate_chart',
        birth_info: {
            calendar: DOMElements.calendarType.value,
            birth_date: document.getElementById('birth-date').value,
            birth_time: DOMElements.unknownTime.checked ? '' : DOMElements.birthTime.value,
            unknown_time: DOMElements.unknownTime.checked,
            gender: document.getElementById('gender').value,
            start_age: Number(DOMElements.startAge.value || 22),
            birth_place: document.getElementById('birth-place').value,
            timezone: 'Asia/Shanghai',
        },
    });
}

function handleTypedAction() {
    const value = DOMElements.actionInput.value.trim();
    if (!value) return;
    DOMElements.actionInput.value = '';
    showRollPending([value]);
    socketManager.sendAction({ type: 'annual_action', focuses: [value] });
}

function handleRetrospectLife() {
    const state = appState.gameState;
    if (!state || state.phase !== 'life_simulation' || state.is_finished || state.is_processing) return;
    const ageText = [state.current_age ? state.current_age + '岁' : '', state.current_half_label || ''].filter(Boolean).join('');
    const ok = window.confirm('确定要在' + (ageText || '此刻') + '回望一生并生成结局档案吗？本周目会结束，但仍可导出档案或重开。');
    if (!ok) return;
    socketManager.sendAction({ type: 'retrospect_life' });
}

function handleUnknownTimeToggle() {
    DOMElements.birthTime.disabled = DOMElements.unknownTime.checked;
}

function handleEditBirth() {
    socketManager.sendAction({ type: 'reset_game' });
}

async function loadAiSettings() {
    try {
        appState.aiSettings = await api.getAiSettings();
        appState.selectedApiProfileId = appState.aiSettings.active_profile_id || (appState.aiSettings.profiles || [])[0]?.id || '';
    } catch (error) {
        appState.aiSettings = { custom_enabled: false, api_key_set: false, base_url: 'https://api.openai.com/v1', model: 'gpt-4o-mini', profiles: [], active_profile_id: '' };
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = error.message;
    }
}

function toggleApiSettingsPanel() {
    setApiSettingsVisible(!appState.apiSettingsVisible);
}

function setCodexVisible(visible) {
    appState.codexVisible = visible;
    if (visible) {
        appState.apiSettingsVisible = false;
        renderEndingCodex();
        renderApiSettings();
        setTimeout(() => DOMElements.codexCloseButton.focus(), 0);
    } else {
        renderEndingCodex();
        DOMElements.codexButton.focus();
    }
}

function toggleCodexPanel() {
    setCodexVisible(!appState.codexVisible);
}

function closeCodexPanel() {
    setCodexVisible(false);
}

function closeApiSettingsPanel() {
    setApiSettingsVisible(false);
}

function modalFocusableElements() {
    const activePanel = appState.apiSettingsVisible ? DOMElements.apiSettingsPanel : appState.codexVisible ? DOMElements.codexPanel : null;
    if (!activePanel) return [];
    return Array.from(activePanel.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )).filter(element => Boolean(element.offsetWidth || element.offsetHeight || element.getClientRects().length));
}

function handleGlobalKeydown(event) {
    if (!appState.apiSettingsVisible && !appState.codexVisible) return;
    if (event.key === 'Escape') {
        event.preventDefault();
        if (appState.apiSettingsVisible) closeApiSettingsPanel();
        else closeCodexPanel();
        return;
    }
    if (event.key === 'Tab') {
        const focusable = modalFocusableElements();
        if (!focusable.length) return;
        const first = focusable[0];
        const last = focusable[focusable.length - 1];
        const activePanel = appState.apiSettingsVisible ? DOMElements.apiSettingsPanel : DOMElements.codexPanel;
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        } else if (!activePanel.contains(document.activeElement)) {
            event.preventDefault();
            first.focus();
        }
    }
}

async function submitApiSettings(event) {
    event.preventDefault();
    const apiKey = DOMElements.customApiKey.value.trim();
    const payload = {
        id: DOMElements.customApiProfileId.value.trim() || undefined,
        name: DOMElements.customApiName.value.trim() || '自定义 API',
        base_url: DOMElements.customApiBaseUrl.value.trim(),
        model: DOMElements.customApiModel.value.trim(),
        enabled: DOMElements.customApiEnabled.checked,
    };
    if (apiKey) payload.api_key = apiKey;
    try {
        appState.aiSettings = await api.saveAiProfile(payload);
        const profiles = apiProfiles();
        const savedProfile = payload.id
            ? profiles.find(profile => profile.id === payload.id)
            : profiles[profiles.length - 1];
        appState.selectedApiProfileId = savedProfile?.id || appState.aiSettings.active_profile_id || '';
        DOMElements.customApiKey.value = '';
        populateApiSettingsForm();
    } catch (error) {
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = error.message;
    }
}

async function testApiSettings() {
    DOMElements.apiSettingsStatus.className = 'api-settings-status testing';
    DOMElements.apiSettingsStatus.textContent = '正在测试 AI API 连接...';
    const payload = {
        profile_id: DOMElements.customApiProfileId.value.trim(),
        base_url: DOMElements.customApiBaseUrl.value.trim(),
        model: DOMElements.customApiModel.value.trim(),
    };
    const apiKey = DOMElements.customApiKey.value.trim();
    if (!payload.profile_id && !apiKey) {
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = '新配置请先填写 API Key；已保存的配置可直接复用隐藏 Key 测试。';
        return;
    }
    if (apiKey) payload.api_key = apiKey;
    try {
        const result = await api.testAiSettings(payload);
        DOMElements.apiSettingsStatus.className = 'api-settings-status' + (result.ok ? ' enabled' : ' error');
        DOMElements.apiSettingsStatus.textContent = (result.message || (result.ok ? '连接成功' : '连接失败')) +
            '（' + (result.base_url || '') + ' / ' + (result.model || '') + '）';
    } catch (error) {
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = error.message;
    }
}

async function clearApiSettings() {
    const profileId = DOMElements.customApiProfileId.value.trim();
    if (!profileId) {
        startNewApiProfile();
        return;
    }
    try {
        appState.aiSettings = await api.deleteAiProfile(profileId);
        appState.selectedApiProfileId = appState.aiSettings.active_profile_id || apiProfiles()[0]?.id || '';
        DOMElements.customApiKey.value = '';
        populateApiSettingsForm();
    } catch (error) {
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = error.message;
    }
}

async function activateApiProfile() {
    const profileId = DOMElements.customApiProfileId.value.trim();
    if (!profileId) {
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = '请先保存配置，再设为默认。';
        return;
    }
    try {
        appState.aiSettings = await api.activateAiProfile(profileId);
        appState.selectedApiProfileId = profileId;
        populateApiSettingsForm();
    } catch (error) {
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = error.message;
    }
}

async function clearProfileKey() {
    const profileId = DOMElements.customApiProfileId.value.trim();
    DOMElements.customApiKey.value = '';
    if (!profileId) return;
    try {
        appState.aiSettings = await api.saveAiProfile({
            id: profileId,
            name: DOMElements.customApiName.value.trim() || '自定义 API',
            api_key: '',
            base_url: DOMElements.customApiBaseUrl.value.trim(),
            model: DOMElements.customApiModel.value.trim(),
            enabled: DOMElements.customApiEnabled.checked,
        });
        appState.selectedApiProfileId = profileId;
        populateApiSettingsForm();
    } catch (error) {
        DOMElements.apiSettingsStatus.className = 'api-settings-status error';
        DOMElements.apiSettingsStatus.textContent = error.message;
    }
}

async function initializeGame() {
    showLoading(true);
    try {
        appState.gameState = await api.initGame();
        await loadAiSettings();
        showView('game-view');
        render();
        await socketManager.connect();
    } catch (error) {
        showView('login-view');
        if (error.message !== 'Unauthorized') DOMElements.loginError.textContent = error.message;
    } finally {
        showLoading(false);
    }
}

async function startGuest() {
    try {
        await api.guestLogin();
        await initializeGame();
    } catch (error) {
        DOMElements.loginError.textContent = error.message;
    }
}

function init() {
    initializeStatusPanelLayout();
    setupScrollInterruptListener(DOMElements.narrativeWindow);
    DOMElements.guestLoginButton.addEventListener('click', startGuest);
    DOMElements.logoutButton.addEventListener('click', () => api.logout());
    DOMElements.resetButton.addEventListener('click', () => socketManager.sendAction({ type: 'reset_game' }));
    DOMElements.exportArchiveButton.addEventListener('click', exportLifeArchive);
    DOMElements.codexButton.addEventListener('click', toggleCodexPanel);
    DOMElements.codexBackdrop.addEventListener('click', closeCodexPanel);
    DOMElements.codexCloseButton.addEventListener('click', closeCodexPanel);
    DOMElements.apiSettingsButton.addEventListener('click', toggleApiSettingsPanel);
    DOMElements.apiSettingsBackdrop.addEventListener('click', closeApiSettingsPanel);
    DOMElements.apiSettingsCloseButton.addEventListener('click', closeApiSettingsPanel);
    DOMElements.addApiProfileButton.addEventListener('click', startNewApiProfile);
    DOMElements.apiSettingsForm.addEventListener('submit', submitApiSettings);
    DOMElements.testApiSettingsButton.addEventListener('click', testApiSettings);
    DOMElements.activateApiProfileButton.addEventListener('click', activateApiProfile);
    DOMElements.clearProfileKeyButton.addEventListener('click', clearProfileKey);
    DOMElements.clearApiSettingsButton.addEventListener('click', clearApiSettings);
    DOMElements.statusToggleButton.addEventListener('click', toggleStatusPanel);
    DOMElements.statusCloseButton.addEventListener('click', () => setStatusPanelCollapsed(true));
    DOMElements.statusRailButton.addEventListener('click', () => setStatusPanelCollapsed(false));
    DOMElements.birthForm.addEventListener('submit', submitBirthForm);
    DOMElements.unknownTime.addEventListener('change', handleUnknownTimeToggle);
    document.querySelectorAll('.quick-age-row button[data-age]').forEach(button => {
        button.addEventListener('click', () => { DOMElements.startAge.value = button.dataset.age; });
    });
    DOMElements.generatePreludeButton.addEventListener('click', () => socketManager.sendAction({ type: 'generate_prelude' }));
    DOMElements.editBirthButton.addEventListener('click', handleEditBirth);
    DOMElements.regenPreludeButton.addEventListener('click', () => socketManager.sendAction({ type: 'generate_prelude' }));
    DOMElements.acceptPreludeButton.addEventListener('click', () => socketManager.sendAction({ type: 'accept_prelude' }));
    DOMElements.actionButton.addEventListener('click', handleTypedAction);
    DOMElements.actionInput.addEventListener('keydown', event => { if (event.key === 'Enter') handleTypedAction(); });
    DOMElements.retrospectButton.addEventListener('click', handleRetrospectLife);
    document.addEventListener('keydown', handleGlobalKeydown);
    initializeGame();
}

init();
