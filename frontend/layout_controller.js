export function createLayoutController({ DOMElements, scrollState }) {
    function showView(viewId) {
        document.querySelectorAll('.view').forEach(view => view.classList.remove('active'));
        document.getElementById(viewId).classList.add('active');
    }

    function showLoading(isLoading) {
        DOMElements.loadingSpinner.style.display = isLoading ? 'flex' : 'none';
    }

    function stopSmoothScroll() {
        if (scrollState.animationId) cancelAnimationFrame(scrollState.animationId);
        scrollState.animationId = null;
    }

    function smoothScrollToBottom(element, pixelsPerSecond = 150) {
        stopSmoothScroll();
        if (!element || scrollState.isUserScrolling) return;
        const start = element.scrollTop;
        const target = element.scrollHeight - element.clientHeight;
        const distance = target - start;
        if (distance <= 0) return;
        const duration = Math.max(250, (distance / pixelsPerSecond) * 1000);
        const startTime = performance.now();
        function tick(now) {
            const progress = Math.min(1, (now - startTime) / duration);
            element.scrollTop = start + distance * (1 - Math.pow(1 - progress, 2));
            if (progress < 1 && !scrollState.isUserScrolling) scrollState.animationId = requestAnimationFrame(tick);
        }
        scrollState.animationId = requestAnimationFrame(tick);
    }

    function setupScrollInterruptListener(element) {
        element.addEventListener('wheel', () => {
            scrollState.isUserScrolling = true;
            stopSmoothScroll();
            clearTimeout(scrollState.scrollTimeout);
            scrollState.scrollTimeout = setTimeout(() => { scrollState.isUserScrolling = false; }, 1800);
        }, { passive: true });
    }

    function scheduleSceneBackgroundUpdate() {
        requestAnimationFrame(updateSceneBackground);
    }

    function updateSceneBackground() {
        const images = DOMElements.narrativeWindow.querySelectorAll('img[src]');
        const latestImage = Array.from(images).reverse().find(img => img.complete && img.naturalWidth > 0);
        if (!latestImage) {
            images.forEach(img => {
                img.addEventListener('load', scheduleSceneBackgroundUpdate, { once: true });
                img.addEventListener('error', scheduleSceneBackgroundUpdate, { once: true });
            });
            document.body.classList.remove('has-scene-background');
            DOMElements.sceneBackgroundImage.removeAttribute('src');
            return;
        }
        const imageUrl = latestImage.currentSrc || latestImage.src;
        DOMElements.sceneBackgroundImage.src = imageUrl;
        document.body.classList.add('has-scene-background');
    }

    function setStatusPanelCollapsed(isCollapsed) {
        DOMElements.gameView.classList.toggle('status-collapsed', isCollapsed);
        DOMElements.statusToggleButton.textContent = isCollapsed ? '展开状态' : '收起状态';
        DOMElements.statusToggleButton.setAttribute('aria-expanded', String(!isCollapsed));
    }

    function toggleStatusPanel() {
        setStatusPanelCollapsed(!DOMElements.gameView.classList.contains('status-collapsed'));
    }

    function initializeStatusPanelLayout() {
        setStatusPanelCollapsed(window.matchMedia('(max-width: 850px)').matches);
    }

    return {
        showView,
        showLoading,
        smoothScrollToBottom,
        setupScrollInterruptListener,
        scheduleSceneBackgroundUpdate,
        setStatusPanelCollapsed,
        toggleStatusPanel,
        initializeStatusPanelLayout,
    };
}
