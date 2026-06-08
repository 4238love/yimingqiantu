import assert from 'node:assert/strict';

const baseUrl = process.env.YMQT_BASE_URL || '';
if (!baseUrl) {
    console.log('SKIP frontend_phase_behaviour_check: set YMQT_BASE_URL to run against a live app.');
    process.exit(0);
}

let chromium;
try {
    ({ chromium } = await import('playwright'));
} catch {
    console.log('SKIP frontend_phase_behaviour_check: playwright package is not installed.');
    process.exit(0);
}

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
const consoleErrors = [];
page.on('console', message => {
    if (message.type() === 'error') consoleErrors.push(message.text());
});
page.on('pageerror', error => consoleErrors.push(error.message));

try {
    await page.goto(baseUrl, { waitUntil: 'networkidle' });
    await page.locator('#guest-login-button').click();
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
        const isHidden = selector => document.querySelector(selector)?.classList.contains('hidden');
        return {
            phase: document.querySelector('#game-view')?.dataset.phase,
            chartHidden: isHidden('#chart-panel'),
            preludeHidden: isHidden('#prelude-panel'),
            simulationHidden: isHidden('#simulation-panel'),
            actionAreaRatio: action ? action.height / window.innerHeight : 1,
            mainContentHeight: main ? main.height : 0,
            horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
        };
    });

    assert.equal(metrics.phase, 'life_simulation');
    assert.equal(metrics.chartHidden, true);
    assert.equal(metrics.preludeHidden, true);
    assert.equal(metrics.simulationHidden, false);
    assert.ok(metrics.actionAreaRatio < 0.35, 'action tray should not cover most of the viewport');
    assert.ok(metrics.mainContentHeight > 320, 'main content should keep meaningful vertical space');
    assert.equal(metrics.horizontalOverflow, false);
    assert.deepEqual(consoleErrors, []);
} finally {
    await browser.close();
}
