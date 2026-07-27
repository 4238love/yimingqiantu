/* ===================================
   Accessibility Enhancements - 无障碍访问性增强

   职责：
   - 键盘导航管理
   - 焦点陷阱（模态框）
   - 屏幕阅读器支持
   - 跳过导航链接
   - ARIA 实时区域
   =================================== */

const AccessibilityManager = {
    // 当前焦点元素
    lastFocusedElement: null,

    // 焦点陷阱栈
    trapStack: [],

    // 初始化
    init() {
        this.setupSkipLinks();
        this.setupKeyboardNavigation();
        this.setupFocusTrap();
        this.setupAriaLive();
        this.setupReducedMotion();
        this.announcePageChanges();
    },

    // 跳过导航链接
    setupSkipLinks() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = '跳转到主内容';

        skipLink.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.getElementById('main-content');
            if (target) {
                target.setAttribute('tabindex', '-1');
                target.focus();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });

        document.body.insertBefore(skipLink, document.body.firstChild);
    },

    // 键盘导航
    setupKeyboardNavigation() {
        // Tab 键焦点可见性
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-nav');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-nav');
        });

        // Escape 键关闭模态框
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.handleEscape();
            }
        });

        // 方向键导航（用于列表和网格）
        this.setupArrowKeyNavigation();
    },

    // 方向键导航
    setupArrowKeyNavigation() {
        // 为可导航元素添加方向键支持
        const navigableContainers = document.querySelectorAll('[role="listbox"], [role="menu"], [role="tablist"]');

        navigableContainers.forEach(container => {
            const items = Array.from(container.querySelectorAll('[role="option"], [role="menuitem"], [role="tab"]'));

            container.addEventListener('keydown', (e) => {
                if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(e.key)) {
                    return;
                }

                e.preventDefault();
                const currentIndex = items.indexOf(document.activeElement);
                let nextIndex;

                switch (e.key) {
                    case 'ArrowUp':
                    case 'ArrowLeft':
                        nextIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
                        break;
                    case 'ArrowDown':
                    case 'ArrowRight':
                        nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
                        break;
                    case 'Home':
                        nextIndex = 0;
                        break;
                    case 'End':
                        nextIndex = items.length - 1;
                        break;
                }

                if (nextIndex !== undefined) {
                    items[nextIndex].focus();
                }
            });
        });
    },

    // 焦点陷阱（用于模态框）
    setupFocusTrap() {
        // 监听模态框打开
        document.addEventListener('modal-open', (e) => {
            this.trapFocus(e.detail.element);
        });

        // 监听模态框关闭
        document.addEventListener('modal-close', () => {
            this.releaseFocus();
        });
    },

    // 陷阱焦点在元素内
    trapFocus(element) {
        // 保存当前焦点
        this.lastFocusedElement = document.activeElement;

        // 获取所有可聚焦元素
        const focusableElements = this.getFocusableElements(element);

        if (focusableElements.length === 0) return;

        // 聚焦第一个元素
        focusableElements[0].focus();

        // 添加到栈
        const trap = { element, focusableElements };
        this.trapStack.push(trap);

        // 监听 Tab 键
        const handleTab = (e) => {
            if (e.key !== 'Tab') return;

            const currentTrap = this.trapStack[this.trapStack.length - 1];
            if (!currentTrap) return;

            const { focusableElements } = currentTrap;
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else {
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        };

        trap.handleTab = handleTab;
        document.addEventListener('keydown', handleTab);
    },

    // 释放焦点陷阱
    releaseFocus() {
        const trap = this.trapStack.pop();

        if (trap) {
            document.removeEventListener('keydown', trap.handleTab);
        }

        // 恢复之前的焦点
        if (this.lastFocusedElement && this.trapStack.length === 0) {
            this.lastFocusedElement.focus();
            this.lastFocusedElement = null;
        }
    },

    // 获取可聚焦元素
    getFocusableElements(element) {
        const selector = 'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])';
        return Array.from(element.querySelectorAll(selector)).filter(el => {
            return !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
        });
    },

    // 处理 Escape 键
    handleEscape() {
        // 关闭最顶层的模态框
        const visibleModal = document.querySelector('.modal.visible');
        if (visibleModal && window.YMQTApp?.modal) {
            window.YMQTApp.modal.hide(visibleModal.id);
            return;
        }

        // 关闭侧边栏
        const openSidebar = document.querySelector('#status-sidebar.open');
        if (openSidebar) {
            openSidebar.classList.remove('open');
            document.getElementById('sidebar-backdrop')?.classList.remove('visible');
            return;
        }

        // 关闭行动抽屉
        const openDrawer = document.querySelector('.action-drawer.drawer-open');
        if (openDrawer) {
            openDrawer.classList.remove('drawer-open');
            return;
        }
    },

    // ARIA 实时区域
    setupAriaLive() {
        // 创建屏幕阅读器通知区域
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('role', 'status');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.id = 'aria-live-region';
        document.body.appendChild(liveRegion);

        // 监听重要事件并播报
        this.watchAriaEvents();
    },

    // 监听需要播报的事件
    watchAriaEvents() {
        // 状态变化播报
        document.addEventListener('stat-change', (e) => {
            this.announce(`${e.detail.name}变化：${e.detail.oldValue} 到 ${e.detail.newValue}`);
        });

        // 判定结果播报
        document.addEventListener('roll-complete', (e) => {
            const result = e.detail.success ? '成功' : '失败';
            this.announce(`判定${result}，骰子点数 ${e.detail.roll}，目标 ${e.detail.target}`);
        });

        // 阶段变化播报
        document.addEventListener('phase-change', (e) => {
            this.announce(`进入${e.detail.phase}阶段`);
        });
    },

    // 播报消息给屏幕阅读器
    announce(message, priority = 'polite') {
        const liveRegion = document.getElementById('aria-live-region');
        if (!liveRegion) return;

        liveRegion.setAttribute('aria-live', priority);

        // 清空后再设置，确保触发播报
        liveRegion.textContent = '';
        setTimeout(() => {
            liveRegion.textContent = message;
        }, 100);
    },

    // 减弱动画支持
    setupReducedMotion() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

        const updateMotionPreference = (matches) => {
            if (matches) {
                document.body.classList.add('reduce-motion');
                this.announce('已启用减弱动画模式');
            } else {
                document.body.classList.remove('reduce-motion');
            }
        };

        updateMotionPreference(prefersReducedMotion.matches);
        prefersReducedMotion.addEventListener('change', (e) => {
            updateMotionPreference(e.matches);
        });
    },

    // 播报页面变化
    announcePageChanges() {
        // 监听视图切换
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.target.classList.contains('view') &&
                    mutation.attributeName === 'class' &&
                    mutation.target.classList.contains('active')) {

                    const viewId = mutation.target.id;
                    const viewNames = {
                        'login-view': '登录页面',
                        'game-view': '游戏页面'
                    };

                    this.announce(`已切换到${viewNames[viewId] || viewId}`);
                }
            });
        });

        document.querySelectorAll('.view').forEach(view => {
            observer.observe(view, { attributes: true });
        });
    },

    // 增强表单可访问性
    enhanceFormAccessibility(form) {
        const inputs = form.querySelectorAll('input, select, textarea');

        inputs.forEach(input => {
            const label = form.querySelector(`label[for="${input.id}"]`);

            // 确保有关联的 label
            if (!label && !input.getAttribute('aria-label')) {
                console.warn('Input without label:', input);
            }

            // 添加 required 属性的 ARIA
            if (input.hasAttribute('required')) {
                input.setAttribute('aria-required', 'true');
            }

            // 添加错误提示支持
            input.addEventListener('invalid', (e) => {
                e.preventDefault();
                const errorId = `${input.id}-error`;
                let errorElement = document.getElementById(errorId);

                if (!errorElement) {
                    errorElement = document.createElement('div');
                    errorElement.id = errorId;
                    errorElement.className = 'error-message';
                    errorElement.setAttribute('role', 'alert');
                    input.parentNode.appendChild(errorElement);
                }

                errorElement.textContent = input.validationMessage;
                input.setAttribute('aria-describedby', errorId);
                input.setAttribute('aria-invalid', 'true');
            });

            input.addEventListener('input', () => {
                if (input.validity.valid) {
                    input.removeAttribute('aria-invalid');
                    const errorId = `${input.id}-error`;
                    const errorElement = document.getElementById(errorId);
                    if (errorElement) {
                        errorElement.textContent = '';
                    }
                }
            });
        });
    },

    // 为动态内容添加加载状态
    setLoadingState(element, isLoading, loadingText = '加载中...') {
        if (isLoading) {
            element.setAttribute('aria-busy', 'true');
            element.setAttribute('aria-label', loadingText);
        } else {
            element.removeAttribute('aria-busy');
            element.removeAttribute('aria-label');
        }
    },

    // 检查页面可访问性问题
    auditAccessibility() {
        const issues = [];

        // 检查图片 alt 文本
        document.querySelectorAll('img').forEach(img => {
            if (!img.hasAttribute('alt')) {
                issues.push({ type: 'missing-alt', element: img });
            }
        });

        // 检查按钮文本
        document.querySelectorAll('button').forEach(button => {
            const text = button.textContent.trim();
            const ariaLabel = button.getAttribute('aria-label');

            if (!text && !ariaLabel) {
                issues.push({ type: 'missing-button-text', element: button });
            }
        });

        // 检查表单 label
        document.querySelectorAll('input, select, textarea').forEach(input => {
            const id = input.id;
            const label = document.querySelector(`label[for="${id}"]`);
            const ariaLabel = input.getAttribute('aria-label');

            if (!label && !ariaLabel) {
                issues.push({ type: 'missing-label', element: input });
            }
        });

        // 检查标题层级
        const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
        let lastLevel = 0;

        headings.forEach(heading => {
            const level = parseInt(heading.tagName[1]);

            if (level - lastLevel > 1) {
                issues.push({
                    type: 'heading-skip',
                    element: heading,
                    message: `跳过了标题层级：从 h${lastLevel} 到 h${level}`
                });
            }

            lastLevel = level;
        });

        return issues;
    }
};

// 导出到全局 API
if (window.YMQTApp) {
    window.YMQTApp.a11y = AccessibilityManager;
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    AccessibilityManager.init();

    // 增强所有表单
    document.querySelectorAll('form').forEach(form => {
        AccessibilityManager.enhanceFormAccessibility(form);
    });

    console.log('无障碍访问性增强已加载');

    // 开发模式下审计可访问性
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        const issues = AccessibilityManager.auditAccessibility();
        if (issues.length > 0) {
            console.warn('发现可访问性问题：', issues);
        }
    }
});
