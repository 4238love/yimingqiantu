import { escapeHtml, renderPreludeEvent } from './view_helpers.js?v=arch-modules-20260608';

let appState;
let DOMElements;
let sendAction = () => {};

export function createPreludeView(context) {
    appState = context.appState;
    DOMElements = context.DOMElements;
    sendAction = context.sendAction || sendAction;
    return { renderPrelude };
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
            sendAction({ type: 'set_life_goal', goal_id: button.dataset.lifeGoalId || '' });
        });
    });
}
