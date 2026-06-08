export const PHASE_VIEW_MODULES = {
    birth_input: {
        label: '出生信息',
        visiblePanels: ['birthPanel'],
        canExportArchive: false,
        canSubmitAction: false,
    },
    chart_ready: {
        label: '命盘已成',
        visiblePanels: ['chartPanel'],
        canExportArchive: true,
        canSubmitAction: false,
    },
    prelude_ready: {
        label: '前传已成',
        visiblePanels: ['chartPanel', 'preludePanel'],
        canExportArchive: true,
        canSubmitAction: false,
    },
    life_simulation: {
        label: '人生模拟',
        visiblePanels: ['simulationPanel'],
        canExportArchive: true,
        canSubmitAction: true,
    },
    ending: {
        label: '结局',
        visiblePanels: ['simulationPanel'],
        canExportArchive: true,
        canSubmitAction: false,
    },
};

const PANEL_KEYS = ['birthPanel', 'chartPanel', 'preludePanel', 'simulationPanel'];

export function resolvePhaseView(phase) {
    return PHASE_VIEW_MODULES[phase] || {
        label: '待排盘',
        visiblePanels: ['birthPanel'],
        canExportArchive: false,
        canSubmitAction: false,
    };
}

function showPanel(panel, visible) {
    if (!panel) return;
    panel.classList.toggle('hidden', !visible);
}

export function phaseLabel(phase) {
    return resolvePhaseView(phase).label;
}

export function applyPhaseView(elements, state) {
    const phase = state?.phase || 'birth_input';
    const view = resolvePhaseView(phase);
    const visible = new Set(view.visiblePanels);
    if (elements.gameView) {
        elements.gameView.dataset.phase = phase;
    }
    if (elements.phasePill) {
        elements.phasePill.textContent = view.label;
    }
    if (elements.exportArchiveButton) {
        elements.exportArchiveButton.disabled = !view.canExportArchive;
    }
    PANEL_KEYS.forEach(key => showPanel(elements[key], visible.has(key)));
    const actionDisabled = !view.canSubmitAction || Boolean(state?.is_finished) || Boolean(state?.is_processing);
    [elements.actionInput, elements.actionButton, elements.retrospectButton].forEach(control => {
        if (control) control.disabled = actionDisabled;
    });
    return view;
}
