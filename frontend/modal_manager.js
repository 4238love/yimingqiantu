export function createModalManager({ appState, DOMElements, apiSettingsView }) {
    function syncBodyModalState() {
        document.body.classList.toggle('modal-open', appState.apiSettingsVisible || appState.retrospectVisible);
    }

    function setApiSettingsVisible(visible) {
        appState.apiSettingsVisible = visible;
        if (visible) {
            appState.retrospectVisible = false;
            renderRetrospectPanel();
            DOMElements.customApiKey.value = '';
            if (!appState.selectedApiProfileId) {
                appState.selectedApiProfileId = appState.aiSettings?.active_profile_id || apiSettingsView.apiProfiles()[0]?.id || '';
            }
            apiSettingsView.populateApiSettingsForm();
            setTimeout(() => DOMElements.customApiKey.focus(), 0);
        } else {
            apiSettingsView.renderApiSettings();
            (DOMElements.settingsMenuButton || DOMElements.apiSettingsButton).focus();
        }
        syncBodyModalState();
    }

    function toggleApiSettingsPanel() {
        setApiSettingsVisible(!appState.apiSettingsVisible);
    }

    function closeApiSettingsPanel() {
        setApiSettingsVisible(false);
    }

    function renderRetrospectPanel() {
        DOMElements.retrospectPanel.classList.toggle('hidden', !appState.retrospectVisible);
        DOMElements.retrospectBackdrop.classList.toggle('hidden', !appState.retrospectVisible);
        DOMElements.retrospectPanel.setAttribute('aria-hidden', String(!appState.retrospectVisible));
        DOMElements.retrospectBackdrop.setAttribute('aria-hidden', String(!appState.retrospectVisible));
    }

    function setRetrospectVisible(visible) {
        appState.retrospectVisible = visible;
        if (visible) {
            appState.apiSettingsVisible = false;
            apiSettingsView.renderApiSettings();
            renderRetrospectPanel();
            setTimeout(() => DOMElements.retrospectCancelButton.focus(), 0);
        } else {
            renderRetrospectPanel();
            (DOMElements.settingsMenuButton || DOMElements.retrospectButton).focus();
        }
        syncBodyModalState();
    }

    function closeRetrospectPanel() {
        setRetrospectVisible(false);
    }

    function modalFocusableElements() {
        const activePanel = appState.apiSettingsVisible
            ? DOMElements.apiSettingsPanel
            : appState.retrospectVisible
                ? DOMElements.retrospectPanel
                : null;
        if (!activePanel) return [];
        return Array.from(activePanel.querySelectorAll(
            'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
        )).filter(element => Boolean(element.offsetWidth || element.offsetHeight || element.getClientRects().length));
    }

    function handleGlobalKeydown(event) {
        if (!appState.apiSettingsVisible && !appState.retrospectVisible) return;
        if (event.key === 'Escape') {
            event.preventDefault();
            if (appState.apiSettingsVisible) closeApiSettingsPanel();
            else closeRetrospectPanel();
            return;
        }
        if (event.key === 'Tab') {
            const focusable = modalFocusableElements();
            if (!focusable.length) return;
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            const activePanel = appState.apiSettingsVisible
                ? DOMElements.apiSettingsPanel
                : DOMElements.retrospectPanel;
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

    return {
        setApiSettingsVisible,
        toggleApiSettingsPanel,
        closeApiSettingsPanel,
        setRetrospectVisible,
        closeRetrospectPanel,
        renderRetrospectPanel,
        handleGlobalKeydown,
    };
}
