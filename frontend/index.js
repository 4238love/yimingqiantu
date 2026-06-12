import { appState, scrollState } from './app_state.js?v=runtime-20260608';
import { DOMElements } from './dom_elements.js?v=runtime-20260608';
import { createApiClient } from './api_client.js?v=runtime-20260608';
import { createSocketManager } from './socket_manager.js?v=runtime-20260608';
import { createLayoutController } from './layout_controller.js?v=runtime-20260608';
import { createModalManager } from './modal_manager.js?v=runtime-20260608';
import { applyPhaseView, phaseLabel } from './phase_views.js?v=phase-view-20260608';
import { createArchiveView } from './archive_view.js?v=arch-modules-20260608';
import { createApiSettingsView } from './api_settings_view.js?v=arch-modules-20260608';
import { createChartView } from './chart_view.js?v=arch-modules-20260608';
import { createPreludeView } from './prelude_view.js?v=arch-modules-20260608';
import { createSimulationView } from './simulation_view.js?v=arch-modules-20260608';
import { escapeHtml } from './view_helpers.js?v=arch-modules-20260608';

const API_BASE_URL = '/api';
const api = createApiClient(API_BASE_URL);
const layoutController = createLayoutController({ DOMElements, scrollState });
const {
    showView,
    showLoading,
    smoothScrollToBottom,
    setupScrollInterruptListener,
    scheduleSceneBackgroundUpdate,
    setStatusPanelCollapsed,
    toggleStatusPanel,
    initializeStatusPanelLayout,
} = layoutController;
const socketManager = createSocketManager({
    apiBaseUrl: API_BASE_URL,
    appState,
    onStateChanged: () => {
        checkAndShowRollEvent();
        render();
    },
});

const chartView = createChartView({ appState, DOMElements });
const preludeView = createPreludeView({ appState, DOMElements, sendAction: action => socketManager.sendAction(action) });
const simulationView = createSimulationView({
    appState,
    DOMElements,
    scrollState,
    smoothScrollToBottom,
    scheduleSceneBackgroundUpdate,
    toggleFocus,
    submitFocuses,
});
const apiSettingsView = createApiSettingsView({ appState, DOMElements });
const archiveView = createArchiveView({ appState });
const modalManager = createModalManager({ appState, DOMElements, apiSettingsView });

function render() {
    if (!appState.gameState) return;
    if (appState.gameState.phase !== 'life_simulation') {
        appState.readingLayoutActivated = false;
        appState.turnCoachDismissed = false;
        appState.actionOptionsExpanded = false;
        appState.monthFlowExpanded = false;
    }
    if (appState.gameState.phase === 'life_simulation' && !appState.readingLayoutActivated) {
        appState.readingLayoutActivated = true;
        setStatusPanelCollapsed(true);
    }
    applyPhaseView(DOMElements, appState.gameState);
    simulationView.renderStatus();
    chartView.renderChart();
    preludeView.renderPrelude();
    simulationView.renderTurnGuide();
    simulationView.renderYearBanner();
    simulationView.renderMonthFlowBoard();
    simulationView.renderTurnResolutionCard();
    simulationView.renderNarrative();
    simulationView.renderFocusActions();
    apiSettingsView.renderApiSettings();
    modalManager.renderRetrospectPanel();
    renderSettingsMenu();
    applyPhaseView(DOMElements, appState.gameState);
    showLoading(appState.gameState.is_processing);
    simulationView.focusPendingResolution();
}

function checkAndShowRollEvent() {
    const rollEvent = appState.gameState?.roll_event;
    if (rollEvent && rollEvent.id && rollEvent.id !== appState.lastRollEventId) {
        appState.lastRollEventId = rollEvent.id;
        appState.pendingResolutionFocusId = rollEvent.id;
        renderRollEvent(rollEvent);
    }
}

function renderRollEvent(rollEvent) {
    DOMElements.rollOverlay.classList.remove('pending');
    DOMElements.rollOverlay.classList.add('revealing');
    DOMElements.rollStageLabel.textContent = '命运推演已落定';
    DOMElements.rollType.textContent = '后台判定：' + rollEvent.type;
    DOMElements.rollTarget.textContent = 'D100 目标 <= ' + rollEvent.target;
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
    DOMElements.rollTarget.textContent = '人生抉择：' + ((focuses || []).join('、') || '随缘而行');
    DOMElements.rollOutcome.textContent = '';
    DOMElements.rollValue.textContent = '...';
    DOMElements.rollResultDisplay.classList.remove('hidden');
}

function toggleFocus(option) {
    const index = appState.selectedFocuses.indexOf(option);
    if (index >= 0) appState.selectedFocuses.splice(index, 1);
    else if (appState.selectedFocuses.length < 3) appState.selectedFocuses.push(option);
    simulationView.renderFocusActions();
}

function submitFocuses() {
    const defaultGuide = Array.isArray(appState.gameState?.action_guides) ? appState.gameState.action_guides[0] : null;
    const fallbackOption = simulationView.cleanActionOptions(appState.gameState || {})[0] || '随缘而行';
    const focuses = appState.selectedFocuses.length ? appState.selectedFocuses : [defaultGuide?.action || fallbackOption];
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
    if (appState.selectedFocuses.length >= 3) {
        DOMElements.actionInput.value = '';
        DOMElements.actionInput.placeholder = '最多选择 3 个重点，先取消一个再加入';
        return;
    }
    if (!appState.selectedFocuses.includes(value)) appState.selectedFocuses.push(value);
    DOMElements.actionInput.value = '';
    DOMElements.actionInput.placeholder = '也可以写下本半年行动/人生抉择，系统会自动归类...';
    simulationView.renderFocusActions();
}

function handleRetrospectLife() {
    const state = appState.gameState;
    if (!state || state.phase !== 'life_simulation' || state.is_finished || state.is_processing) return;
    const ageText = [state.current_age ? state.current_age + '岁' : '', state.current_half_label || ''].filter(Boolean).join('');
    const goal = state.goal_progress || {};
    DOMElements.retrospectConfirmSummary.innerHTML =
        '<article><span>当前节点</span><b>' + escapeHtml(ageText || '此刻') + '</b></article>' +
        '<article><span>人生愿望</span><b>' + escapeHtml(goal.title || '未选择') + '</b><small>' + Number(goal.percent || 0) + '% · ' + escapeHtml(goal.status || '') + '</small></article>' +
        '<article><span>提示</span><b>这是结束操作</b><small>建议先导出档案或确认已经读完最新半年结算。</small></article>';
    modalManager.setRetrospectVisible(true);
}

function confirmRetrospectLife() {
    modalManager.closeRetrospectPanel();
    socketManager.sendAction({ type: 'retrospect_life' });
}

function renderSettingsMenu() {
    DOMElements.settingsMenuButton.setAttribute('aria-expanded', String(appState.settingsMenuOpen));
    DOMElements.settingsMenuPanel.classList.toggle('hidden', !appState.settingsMenuOpen);
}

function setSettingsMenuOpen(open) {
    appState.settingsMenuOpen = open;
    renderSettingsMenu();
}

function toggleSettingsMenu() {
    setSettingsMenuOpen(!appState.settingsMenuOpen);
}

function closeSettingsMenu() {
    setSettingsMenuOpen(false);
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
        const profiles = apiSettingsView.apiProfiles();
        const savedProfile = payload.id
            ? profiles.find(profile => profile.id === payload.id)
            : profiles[profiles.length - 1];
        appState.selectedApiProfileId = savedProfile?.id || appState.aiSettings.active_profile_id || '';
        DOMElements.customApiKey.value = '';
        apiSettingsView.populateApiSettingsForm();
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
        apiSettingsView.startNewApiProfile();
        return;
    }
    try {
        appState.aiSettings = await api.deleteAiProfile(profileId);
        appState.selectedApiProfileId = appState.aiSettings.active_profile_id || apiSettingsView.apiProfiles()[0]?.id || '';
        DOMElements.customApiKey.value = '';
        apiSettingsView.populateApiSettingsForm();
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
        apiSettingsView.populateApiSettingsForm();
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
        apiSettingsView.populateApiSettingsForm();
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
    DOMElements.exportArchiveButton.addEventListener('click', archiveView.exportLifeArchive);
    DOMElements.settingsMenuButton.addEventListener('click', toggleSettingsMenu);
    DOMElements.settingsMenuPanel.addEventListener('click', event => {
        if (event.target.closest('button')) closeSettingsMenu();
    });
    document.addEventListener('click', event => {
        if (!appState.settingsMenuOpen) return;
        if (!DOMElements.settingsMenuPanel.contains(event.target) && !DOMElements.settingsMenuButton.contains(event.target)) closeSettingsMenu();
    });
    DOMElements.apiSettingsButton.addEventListener('click', modalManager.toggleApiSettingsPanel);
    DOMElements.apiSettingsBackdrop.addEventListener('click', modalManager.closeApiSettingsPanel);
    DOMElements.apiSettingsCloseButton.addEventListener('click', modalManager.closeApiSettingsPanel);
    DOMElements.addApiProfileButton.addEventListener('click', apiSettingsView.startNewApiProfile);
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
    DOMElements.retrospectBackdrop.addEventListener('click', modalManager.closeRetrospectPanel);
    DOMElements.retrospectCloseButton.addEventListener('click', modalManager.closeRetrospectPanel);
    DOMElements.retrospectCancelButton.addEventListener('click', modalManager.closeRetrospectPanel);
    DOMElements.retrospectConfirmButton.addEventListener('click', confirmRetrospectLife);
    document.addEventListener('keydown', modalManager.handleGlobalKeydown);
    document.addEventListener('keydown', event => {
        if (event.key === 'Escape' && appState.settingsMenuOpen) closeSettingsMenu();
    });
    initializeGame();
}

init();
