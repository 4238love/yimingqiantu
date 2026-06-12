export const appState = {
    gameState: null,
    lastRollEventId: null,
    selectedFocuses: [],
    aiSettings: null,
    apiSettingsVisible: false,
    retrospectVisible: false,
    settingsMenuOpen: false,
    selectedApiProfileId: '',
    historyFilter: 'all',
    historyExpanded: false,
    actionOptionsExpanded: false,
    monthFlowExpanded: false,
    activeTerm: 'D100',
    turnCoachDismissed: false,
    pendingResolutionFocusId: '',
    readingLayoutActivated: false,
};

export const scrollState = {
    animationId: null,
    isUserScrolling: false,
    scrollTimeout: null,
    isFirstRender: true,
};
