/* ===================================
   Mobile Enhancements - 移动端交互增强

   职责：
   - 流月卡片横向滑动
   - 手势操作支持
   - 触摸反馈优化
   - 移动端特定交互
   =================================== */

const MobileEnhancements = {
    // 初始化所有移动端增强
    init() {
        this.initMonthFlowScroll();
        this.initActionDrawer();
        this.initSwipeGestures();
        this.initTouchFeedback();
        this.detectMobile();
    },

    // 检测移动设备
    detectMobile() {
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;

        if (isMobile || isTouch) {
            document.body.classList.add('touch-device');
        }
    },

    // 流月卡片横向滑动
    initMonthFlowScroll() {
        const monthFlow = document.querySelector('.month-flow-grid');
        if (!monthFlow) return;

        // 移动端改为横向滑动
        if (window.innerWidth <= 768) {
            monthFlow.classList.add('mobile-scroll');
            this.addScrollIndicators(monthFlow);
        }

        // 响应窗口大小变化
        window.addEventListener('resize', () => {
            if (window.innerWidth <= 768) {
                monthFlow.classList.add('mobile-scroll');
                this.addScrollIndicators(monthFlow);
            } else {
                monthFlow.classList.remove('mobile-scroll');
                this.removeScrollIndicators(monthFlow);
            }
        });
    },

    // 添加滑动指示器
    addScrollIndicators(container) {
        if (container.querySelector('.scroll-indicator')) return;

        const leftIndicator = document.createElement('div');
        leftIndicator.className = 'scroll-indicator scroll-left hidden';
        leftIndicator.innerHTML = '◀';
        leftIndicator.addEventListener('click', () => {
            container.scrollBy({ left: -200, behavior: 'smooth' });
        });

        const rightIndicator = document.createElement('div');
        rightIndicator.className = 'scroll-indicator scroll-right';
        rightIndicator.innerHTML = '▶';
        rightIndicator.addEventListener('click', () => {
            container.scrollBy({ left: 200, behavior: 'smooth' });
        });

        const wrapper = container.parentElement;
        wrapper.style.position = 'relative';
        wrapper.appendChild(leftIndicator);
        wrapper.appendChild(rightIndicator);

        // 滚动时更新指示器
        container.addEventListener('scroll', () => {
            this.updateScrollIndicators(container, leftIndicator, rightIndicator);
        });

        // 初始更新
        this.updateScrollIndicators(container, leftIndicator, rightIndicator);
    },

    // 更新滑动指示器状态
    updateScrollIndicators(container, leftIndicator, rightIndicator) {
        const atStart = container.scrollLeft <= 0;
        const atEnd = container.scrollLeft + container.clientWidth >= container.scrollWidth - 1;

        leftIndicator.classList.toggle('hidden', atStart);
        rightIndicator.classList.toggle('hidden', atEnd);
    },

    // 移除滑动指示器
    removeScrollIndicators(container) {
        const wrapper = container.parentElement;
        const indicators = wrapper.querySelectorAll('.scroll-indicator');
        indicators.forEach(ind => ind.remove());
    },

    // 行动选择抽屉（移动端）
    initActionDrawer() {
        const actionFooter = document.getElementById('action-footer');
        if (!actionFooter) return;

        // 仅在移动端启用
        if (window.innerWidth > 768) return;

        // 创建抽屉触发器
        const trigger = document.createElement('button');
        trigger.className = 'action-drawer-trigger';
        trigger.innerHTML = '选择行动 <span class="trigger-icon">▲</span>';
        trigger.addEventListener('click', () => {
            actionFooter.classList.toggle('drawer-open');
            trigger.classList.toggle('active');
        });

        actionFooter.parentElement.insertBefore(trigger, actionFooter);
        actionFooter.classList.add('action-drawer');
    },

    // 手势操作
    initSwipeGestures() {
        const panels = document.querySelectorAll('.panel');

        panels.forEach(panel => {
            let touchStartX = 0;
            let touchStartY = 0;
            let touchEndX = 0;
            let touchEndY = 0;

            panel.addEventListener('touchstart', (e) => {
                touchStartX = e.changedTouches[0].screenX;
                touchStartY = e.changedTouches[0].screenY;
            }, { passive: true });

            panel.addEventListener('touchend', (e) => {
                touchEndX = e.changedTouches[0].screenX;
                touchEndY = e.changedTouches[0].screenY;
                this.handlePanelSwipe(panel, touchStartX, touchEndX, touchStartY, touchEndY);
            }, { passive: true });
        });
    },

    // 处理面板滑动
    handlePanelSwipe(panel, startX, endX, startY, endY) {
        const deltaX = startX - endX;
        const deltaY = startY - endY;

        // 只处理水平滑动
        if (Math.abs(deltaX) < Math.abs(deltaY)) return;
        if (Math.abs(deltaX) < 80) return;

        // 向左滑动 - 展开
        if (deltaX < 0) {
            const details = panel.querySelector('details');
            if (details) details.open = true;
        }

        // 向右滑动 - 折叠
        if (deltaX > 0) {
            const details = panel.querySelector('details');
            if (details) details.open = false;
        }
    },

    // 触摸反馈优化
    initTouchFeedback() {
        // 为所有可点击元素添加触摸反馈
        const interactiveElements = document.querySelectorAll('button, .chip, .card-interactive, a');

        interactiveElements.forEach(element => {
            element.addEventListener('touchstart', () => {
                element.classList.add('touch-active');
            }, { passive: true });

            element.addEventListener('touchend', () => {
                element.classList.remove('touch-active');
            }, { passive: true });

            element.addEventListener('touchcancel', () => {
                element.classList.remove('touch-active');
            }, { passive: true });
        });
    },

    // 长按操作支持
    addLongPressSupport(element, callback, duration = 600) {
        let pressTimer;

        element.addEventListener('touchstart', (e) => {
            pressTimer = setTimeout(() => {
                callback(e);
                navigator.vibrate && navigator.vibrate(50); // 震动反馈
            }, duration);
        }, { passive: true });

        element.addEventListener('touchend', () => {
            clearTimeout(pressTimer);
        }, { passive: true });

        element.addEventListener('touchmove', () => {
            clearTimeout(pressTimer);
        }, { passive: true });
    },

    // 下拉刷新
    initPullToRefresh(container, onRefresh) {
        let startY = 0;
        let currentY = 0;
        let pulling = false;
        const threshold = 80;

        const refreshIndicator = document.createElement('div');
        refreshIndicator.className = 'pull-refresh-indicator';
        refreshIndicator.innerHTML = '↓ 下拉刷新';
        container.prepend(refreshIndicator);

        container.addEventListener('touchstart', (e) => {
            if (container.scrollTop === 0) {
                startY = e.touches[0].pageY;
                pulling = true;
            }
        }, { passive: true });

        container.addEventListener('touchmove', (e) => {
            if (!pulling) return;

            currentY = e.touches[0].pageY;
            const distance = currentY - startY;

            if (distance > 0 && distance < threshold * 2) {
                refreshIndicator.style.height = `${distance}px`;
                refreshIndicator.style.opacity = Math.min(distance / threshold, 1);

                if (distance >= threshold) {
                    refreshIndicator.innerHTML = '↑ 松开刷新';
                    refreshIndicator.classList.add('ready');
                } else {
                    refreshIndicator.innerHTML = '↓ 下拉刷新';
                    refreshIndicator.classList.remove('ready');
                }
            }
        }, { passive: true });

        container.addEventListener('touchend', () => {
            if (!pulling) return;

            const distance = currentY - startY;
            pulling = false;

            if (distance >= threshold) {
                refreshIndicator.innerHTML = '⟳ 刷新中...';
                refreshIndicator.classList.add('refreshing');

                onRefresh().finally(() => {
                    refreshIndicator.style.height = '0';
                    refreshIndicator.style.opacity = '0';
                    refreshIndicator.classList.remove('refreshing', 'ready');
                });
            } else {
                refreshIndicator.style.height = '0';
                refreshIndicator.style.opacity = '0';
                refreshIndicator.classList.remove('ready');
            }
        }, { passive: true });
    },

    // 虚拟滚动优化（长列表性能）
    initVirtualScroll(container, itemHeight, renderItem) {
        const items = [];
        let visibleStart = 0;
        let visibleEnd = 0;

        const viewport = document.createElement('div');
        viewport.className = 'virtual-scroll-viewport';
        viewport.style.position = 'relative';

        container.appendChild(viewport);

        function updateVisibleItems() {
            const scrollTop = container.scrollTop;
            const viewportHeight = container.clientHeight;

            visibleStart = Math.floor(scrollTop / itemHeight);
            visibleEnd = Math.ceil((scrollTop + viewportHeight) / itemHeight);

            viewport.innerHTML = '';
            viewport.style.height = `${items.length * itemHeight}px`;

            for (let i = visibleStart; i < Math.min(visibleEnd, items.length); i++) {
                const itemElement = renderItem(items[i], i);
                itemElement.style.position = 'absolute';
                itemElement.style.top = `${i * itemHeight}px`;
                itemElement.style.width = '100%';
                viewport.appendChild(itemElement);
            }
        }

        container.addEventListener('scroll', () => {
            requestAnimationFrame(updateVisibleItems);
        }, { passive: true });

        return {
            setItems(newItems) {
                items.splice(0, items.length, ...newItems);
                updateVisibleItems();
            },
            refresh() {
                updateVisibleItems();
            }
        };
    }
};

// 响应式布局管理
const ResponsiveManager = {
    breakpoints: {
        sm: 640,
        md: 768,
        lg: 1024,
        xl: 1280
    },

    current: 'xl',

    init() {
        this.updateBreakpoint();
        window.addEventListener('resize', () => {
            this.updateBreakpoint();
        });
    },

    updateBreakpoint() {
        const width = window.innerWidth;
        let newBreakpoint = 'xl';

        if (width < this.breakpoints.sm) {
            newBreakpoint = 'xs';
        } else if (width < this.breakpoints.md) {
            newBreakpoint = 'sm';
        } else if (width < this.breakpoints.lg) {
            newBreakpoint = 'md';
        } else if (width < this.breakpoints.xl) {
            newBreakpoint = 'lg';
        }

        if (newBreakpoint !== this.current) {
            this.current = newBreakpoint;
            document.body.setAttribute('data-breakpoint', newBreakpoint);
            this.onBreakpointChange(newBreakpoint);
        }
    },

    onBreakpointChange(breakpoint) {
        // 触发断点变化事件
        window.dispatchEvent(new CustomEvent('breakpoint-change', {
            detail: { breakpoint }
        }));
    },

    is(breakpoint) {
        return this.current === breakpoint;
    },

    isSmaller(breakpoint) {
        const order = ['xs', 'sm', 'md', 'lg', 'xl'];
        return order.indexOf(this.current) < order.indexOf(breakpoint);
    }
};

// 导出到全局 API
if (window.YMQTApp) {
    window.YMQTApp.mobile = MobileEnhancements;
    window.YMQTApp.responsive = ResponsiveManager;
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    MobileEnhancements.init();
    ResponsiveManager.init();
    console.log('移动端增强已加载');
});
