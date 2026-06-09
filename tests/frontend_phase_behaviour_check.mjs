import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';

const baseUrl = process.env.YMQT_BASE_URL || '';
const allowSkip = process.env.YMQT_ALLOW_BEHAVIOUR_SKIP === '1';
if (!baseUrl) {
    if (allowSkip) {
        console.log('SKIP frontend_phase_behaviour_check: set YMQT_BASE_URL to run against a live app.');
        process.exit(0);
    }
    throw new Error('frontend_phase_behaviour_check requires YMQT_BASE_URL. Start the app and run with the live base URL.');
}

let chromium;
try {
    ({ chromium } = await import('playwright'));
} catch {
    if (allowSkip) {
        console.log('SKIP frontend_phase_behaviour_check: playwright package is not installed.');
        process.exit(0);
    }
    throw new Error('frontend_phase_behaviour_check requires the playwright package. Run npm install before behaviour checks.');
}

function localChromiumExecutable() {
    const candidates = [
        process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE,
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
        'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    ].filter(Boolean);
    return candidates.find(candidate => existsSync(candidate)) || '';
}

const executablePath = localChromiumExecutable();
const browser = await chromium.launch(executablePath ? { executablePath } : {});
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const consoleErrors = [];
page.on('console', message => {
    if (message.type() !== 'error') return;
    const text = message.text();
    if (text.includes('Failed to load resource') && text.includes('401')) return;
    consoleErrors.push(text);
});
page.on('pageerror', error => consoleErrors.push(error.message));

try {
    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    await page.locator('#guest-login-button').click();
    await page.locator('#phase-pill', { hasText: '出生信息' }).waitFor({ timeout: 10000 });
    await page.waitForTimeout(300);
    await page.locator('#birth-date').fill('2000-03-15');
    await page.locator('#birth-time').fill('08:30');
    await page.locator('#start-age').fill('22');
    await page.locator('#birth-form').evaluate(form => form.requestSubmit());
    await page.locator('#phase-pill', { hasText: '命盘已成' }).waitFor({ timeout: 10000 });
    await page.locator('#generate-prelude-button').click();
    await page.locator('#phase-pill', { hasText: '前传已成' }).waitFor({ timeout: 10000 });
    await page.locator('#accept-prelude-button').click();
    await page.locator('#phase-pill', { hasText: '人生模拟' }).waitFor({ timeout: 10000 });

    const metrics = await page.evaluate(() => {
        const rect = selector => document.querySelector(selector)?.getBoundingClientRect();
        const action = rect('#action-area');
        const main = rect('#main-content');
        const actionArea = document.querySelector('#action-area');
        if (actionArea) actionArea.scrollTop = actionArea.scrollHeight;
        const overlapArea = (firstSelector, secondSelector) => {
            const first = rect(firstSelector);
            const second = rect(secondSelector);
            if (!first || !second) return 0;
            const width = Math.max(0, Math.min(first.right, second.right) - Math.max(first.left, second.left));
            const height = Math.max(0, Math.min(first.bottom, second.bottom) - Math.max(first.top, second.top));
            return Math.round(width * height);
        };
        const commandStyle = window.getComputedStyle(document.querySelector('.action-input-row'));
        const isHidden = selector => document.querySelector(selector)?.classList.contains('hidden');
        return {
            phase: document.querySelector('#game-view')?.dataset.phase,
            statusCollapsed: document.querySelector('#game-view')?.classList.contains('status-collapsed'),
            chartHidden: isHidden('#chart-panel'),
            preludeHidden: isHidden('#prelude-panel'),
            simulationHidden: isHidden('#simulation-panel'),
            firstTurnCoachVisible: Boolean(document.querySelector('.first-turn-coach')),
            recommendedChipCount: document.querySelectorAll('.focus-chip.recommended-chip').length,
            moreActionsVisible: Boolean(document.querySelector('.more-actions-chip')),
            submitText: document.querySelector('.submit-focus-button')?.textContent?.trim(),
            freeTextButtonText: document.querySelector('#action-button')?.textContent?.trim(),
            retrospectInSettingsMenu: document.querySelector('#retrospect-button')?.closest('#settings-menu-panel')?.id === 'settings-menu-panel',
            termChipCount: document.querySelectorAll('.term-chip').length,
            monthFlowCollapsed: !document.querySelector('.month-flow-grid') && Boolean(document.querySelector('.month-flow-summary')),
            actionAreaRatio: action ? action.height / window.innerHeight : 1,
            mainContentHeight: main ? main.height : 0,
            actionTrayVerticalOverflow: actionArea ? actionArea.scrollHeight > actionArea.clientHeight + 1 : true,
            commandIsSticky: commandStyle.position === 'sticky',
            commandRailOverlap: overlapArea('.action-input-row', '.decision-action-rail'),
            commandPreviewOverlap: overlapArea('.action-input-row', '.action-preview-panel'),
            horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
        };
    });

    assert.equal(metrics.phase, 'life_simulation');
    assert.equal(metrics.statusCollapsed, true);
    assert.equal(metrics.chartHidden, true);
    assert.equal(metrics.preludeHidden, true);
    assert.equal(metrics.simulationHidden, false);
    assert.equal(metrics.firstTurnCoachVisible, true, 'first turn should show guided decision coach');
    assert.equal(metrics.recommendedChipCount, 3, 'decision dock should expose only top 3 recommendations by default');
    assert.equal(metrics.moreActionsVisible, true, 'less relevant actions should sit behind a more-actions control');
    assert.equal(metrics.submitText, '确认本半年选择');
    assert.equal(metrics.freeTextButtonText, '加入重点');
    assert.equal(metrics.retrospectInSettingsMenu, true, 'retrospection should move out of the regular action dock');
    assert.ok(metrics.termChipCount >= 4, 'term quick explanations should be clickable');
    assert.equal(metrics.monthFlowCollapsed, true, 'flowing months should start collapsed to a summary');
    assert.ok(metrics.actionAreaRatio < 0.25, 'action tray should stay compact enough for the main narrative');
    assert.ok(metrics.mainContentHeight > 320, 'main content should keep meaningful vertical space');
    assert.equal(metrics.actionTrayVerticalOverflow, false, 'action tray should not require vertical scrolling');
    assert.equal(metrics.commandIsSticky, false, 'command row should not use sticky positioning inside the dock');
    assert.equal(metrics.commandRailOverlap, 0, 'command row must not overlap the action chips when scrolled');
    assert.equal(metrics.commandPreviewOverlap, 0, 'command row must not overlap the preview panel when scrolled');
    assert.equal(metrics.horizontalOverflow, false);

    await page.locator('#settings-menu-button').click();
    await page.locator('#retrospect-button').click();
    await page.locator('#retrospect-panel:not(.hidden)').waitFor({ timeout: 3000 });
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.querySelector('#retrospect-panel')?.classList.contains('hidden'), null, { timeout: 3000 });

    await page.locator('#action-input').fill('准备作品集并找导师复盘');
    await page.locator('#action-button').click();
    await assert.doesNotReject(async () => {
        await page.locator('.action-preview-selected', { hasText: '准备作品集并找导师复盘' }).waitFor({ timeout: 3000 });
    }, 'custom free-text action should be added to the current focus set instead of submitting immediately');

    await page.locator('.submit-focus-button').click();
    await page.locator('#turn-resolution-card').waitFor({ timeout: 15000 });
    await page.waitForTimeout(3900);
    const settlement = await page.evaluate(() => ({
        visible: Boolean(document.querySelector('#turn-resolution-card')),
        hasD100: /D100/.test(document.querySelector('#turn-resolution-card')?.textContent || ''),
        hasDeltas: document.querySelectorAll('.delta-pill').length > 0,
        activeElementInsideSettlement: Boolean(document.querySelector('#turn-resolution-card')?.contains(document.activeElement)),
    }));
    assert.equal(settlement.visible, true);
    assert.equal(settlement.hasD100, true);
    assert.equal(settlement.hasDeltas, true);
    assert.equal(settlement.activeElementInsideSettlement, true, 'focus should move to the newest settlement card after resolution');
    assert.deepEqual(consoleErrors, []);
} finally {
    await browser.close();
}
