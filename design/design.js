/* ================= 原型交互演示 ================= */
const screens = document.querySelectorAll('.screen');
const navBtns = document.querySelectorAll('#proto-nav button[data-screen]');
function gotoScreen(id) {
    screens.forEach(s => s.classList.toggle('active', s.id === id));
    navBtns.forEach(b => b.classList.toggle('on', b.dataset.screen === id));
}
navBtns.forEach(b => b.addEventListener('click', () => gotoScreen(b.dataset.screen)));
document.querySelectorAll('[data-goto]').forEach(b => b.addEventListener('click', () => gotoScreen(b.dataset.goto)));

/* 快捷年龄 chips */
document.querySelectorAll('.quick-ages .chip').forEach(c => {
    c.addEventListener('click', () => {
        c.closest('.quick-ages').querySelectorAll('.chip').forEach(x => x.classList.remove('on'));
        c.classList.add('on');
    });
});

/* 愿望选择 */
document.querySelectorAll('[data-wish]').forEach(c => {
    c.addEventListener('click', () => {
        document.querySelectorAll('[data-wish]').forEach(x => x.classList.remove('on'));
        c.classList.add('on');
    });
});

/* 叙事筛选 chips（演示态） */
document.querySelectorAll('.fchip').forEach(c => {
    c.addEventListener('click', () => {
        c.closest('.filter-chips').querySelectorAll('.fchip').forEach(x => x.classList.remove('on'));
        c.classList.add('on');
    });
});

/* 行动 chips 多选（最多3） */
const picked = new Set(['深耕专业领域']);
document.querySelectorAll('#action-strip .action-chip').forEach(c => {
    c.addEventListener('click', () => {
        const name = c.dataset.pick;
        if (!name || name === '更多') return;
        if (picked.has(name)) { picked.delete(name); c.classList.remove('on'); }
        else if (picked.size < 3) { picked.add(name); c.classList.add('on'); }
        document.getElementById('picked-count').textContent = picked.size;
        document.getElementById('picked-names').textContent = picked.size ? [...picked].join('、') : '尚未选择';
    });
});

/* 推演预览开合 */
const dock = document.querySelector('.decision-dock');
const previewToggle = document.getElementById('preview-toggle');
if (previewToggle && dock) {
    previewToggle.addEventListener('click', () => {
        dock.classList.toggle('show-preview');
        previewToggle.textContent = dock.classList.contains('show-preview') ? '收起推演预览 ▴' : '展开推演预览 ▾';
    });
}

/* D100 天机骰演示 */
const rollOverlay = document.getElementById('roll-overlay');
const diceCore = document.getElementById('dice-core');
const diceNum = document.getElementById('dice-num');
const verdictWord = document.getElementById('verdict-word');
let rollTimer = null, settleTimer = null;
function startRoll() {
    rollOverlay.classList.add('open');
    diceCore.classList.add('rolling');
    verdictWord.classList.remove('show');
    clearInterval(rollTimer); clearTimeout(settleTimer);
    rollTimer = setInterval(() => { diceNum.textContent = String(1 + Math.floor(Math.random() * 100)); }, 70);
    settleTimer = setTimeout(() => {
        clearInterval(rollTimer);
        const final = 1 + Math.floor(Math.random() * 100);
        diceNum.textContent = String(final);
        diceCore.classList.remove('rolling');
        const ok = final <= 62;
        verdictWord.textContent = ok ? '大成' : '受挫';
        verdictWord.className = 'v-word show ' + (ok ? 'success' : 'fail');
    }, 1800);
}
document.getElementById('open-roll').addEventListener('click', startRoll);
document.getElementById('confirm-turn').addEventListener('click', startRoll);
rollOverlay.addEventListener('click', () => {
    rollOverlay.classList.remove('open');
    clearInterval(rollTimer); clearTimeout(settleTimer);
});

/* 图鉴弹窗 */
const codexModal = document.getElementById('codex-modal');
['open-codex', 'open-codex-2', 'open-codex-3'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('click', () => codexModal.classList.add('open'));
});
codexModal.addEventListener('click', e => { if (e.target === codexModal) codexModal.classList.remove('open'); });
document.querySelectorAll('[data-close]').forEach(b => b.addEventListener('click', () => {
    document.getElementById(b.dataset.close).classList.remove('open');
}));
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { codexModal.classList.remove('open'); rollOverlay.classList.remove('open'); }
});
