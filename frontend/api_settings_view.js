import { escapeHtml } from './view_helpers.js?v=arch-modules-20260608';

let appState;
let DOMElements;

export function createApiSettingsView(context) {
    appState = context.appState;
    DOMElements = context.DOMElements;
    return {
        renderApiSettings,
        apiProfiles,
        selectedApiProfile,
        renderApiProfileList,
        populateApiSettingsForm,
        selectApiProfile,
        startNewApiProfile,
    };
}

function renderApiSettings() {
    const settings = appState.aiSettings || {};
    DOMElements.apiSettingsPanel.classList.toggle('hidden', !appState.apiSettingsVisible);
    DOMElements.apiSettingsBackdrop.classList.toggle('hidden', !appState.apiSettingsVisible);
    DOMElements.apiSettingsPanel.setAttribute('aria-hidden', String(!appState.apiSettingsVisible));
    DOMElements.apiSettingsBackdrop.setAttribute('aria-hidden', String(!appState.apiSettingsVisible));
    DOMElements.apiSettingsButton.setAttribute('aria-expanded', String(appState.apiSettingsVisible));
    document.body.classList.toggle('modal-open', appState.apiSettingsVisible || appState.codexVisible || appState.retrospectVisible);
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
