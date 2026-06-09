import { escapeHtml } from './view_helpers.js?v=arch-modules-20260608';

let appState;
let DOMElements;

export function createCodexView(context) {
    appState = context.appState;
    DOMElements = context.DOMElements;
    return { renderEndingCodex };
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
    document.body.classList.toggle('modal-open', appState.apiSettingsVisible || appState.codexVisible || appState.retrospectVisible);
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
