/* ===================================
   Theme Toggle & Initialization
   主题切换和初始化脚本
   =================================== */

// 主题管理
const ThemeManager = {
    THEME_KEY: 'yimingqiantu-theme',

    init() {
        // 读取保存的主题或使用系统偏好
        const savedTheme = localStorage.getItem(this.THEME_KEY);
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = savedTheme || (prefersDark ? 'dark' : 'light');

        this.setTheme(theme);
        this.bindToggle();
        this.watchSystemTheme();
    },

    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(this.THEME_KEY, theme);
    },

    toggleTheme() {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        this.setTheme(next);
    },

    bindToggle() {
        const button = document.getElementById('theme-toggle');
        if (button) {
            button.addEventListener('click', () => this.toggleTheme());
        }
    },

    watchSystemTheme() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            // 只在用户没有手动设置时跟随系统
            if (!localStorage.getItem(this.THEME_KEY)) {
                this.setTheme(e.matches ? 'dark' : 'light');
            }
        });
    }
};

// Toast 通知系统
const Toast = {
    container: null,

    init() {
        this.container = document.getElementById('toast-container');
    },

    show(message, type = 'info', duration = 3000) {
        if (!this.container) this.init();

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const title = this.getTitle(type);
        toast.innerHTML = `
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        `;

        this.container.appendChild(toast);

        // 自动消失
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, duration);
    },

    getTitle(type) {
        const titles = {
            success: '✓ 成功',
            warning: '⚠ 提醒',
            error: '✗ 错误',
            info: 'ℹ 提示'
        };
        return titles[type] || titles.info;
    },

    success(message) { this.show(message, 'success'); },
    warning(message) { this.show(message, 'warning'); },
    error(message) { this.show(message, 'error'); },
    info(message) { this.show(message, 'info'); }
};

// 模态框管理
const Modal = {
    show(modalId) {
        const modal = document.getElementById(modalId);
        const backdrop = document.getElementById(modalId.replace('-modal', '-backdrop'));

        if (modal) {
            modal.classList.add('visible');
            if (backdrop) backdrop.classList.add('visible');
            document.body.style.overflow = 'hidden';

            // 聚焦到第一个可交互元素
            const firstInput = modal.querySelector('input, button, select, textarea');
            if (firstInput) firstInput.focus();
        }
    },

    hide(modalId) {
        const modal = document.getElementById(modalId);
        const backdrop = document.getElementById(modalId.replace('-modal', '-backdrop'));

        if (modal) {
            modal.classList.remove('visible');
            if (backdrop) backdrop.classList.remove('visible');
            document.body.style.overflow = '';
        }
    },

    bindCloseButtons() {
        // 关闭按钮
        document.querySelectorAll('.modal-close').forEach(button => {
            button.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (modal) this.hide(modal.id);
            });
        });

        // 背景点击关闭
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            backdrop.addEventListener('click', () => {
                const modalId = backdrop.id.replace('-backdrop', '-modal');
                this.hide(modalId);
            });
        });

        // ESC 键关闭
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const visibleModal = document.querySelector('.modal.visible');
                if (visibleModal) this.hide(visibleModal.id);
            }
        });
    }
};

// 侧边栏管理（移动端）
const Sidebar = {
    init() {
        const sidebar = document.getElementById('status-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');
        const toggle = document.getElementById('sidebar-toggle');

        if (!sidebar || !backdrop || !toggle) return;

        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            backdrop.classList.toggle('visible');
        });

        backdrop.addEventListener('click', () => {
            sidebar.classList.remove('open');
            backdrop.classList.remove('visible');
        });
    }
};

// 加载覆盖层
const Loading = {
    show(text = '正在推演...', hint = '命运之轮缓缓转动') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.querySelector('.loading-text').textContent = text;
            overlay.querySelector('.loading-hint').textContent = hint;
            overlay.classList.remove('hidden');
        }
    },

    hide() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.classList.add('hidden');
    }
};

// 判定动画
const RollAnimation = {
    show(target, onComplete) {
        const overlay = document.getElementById('roll-overlay');
        const dice = document.getElementById('roll-dice');
        const result = document.getElementById('roll-result');

        if (!overlay || !dice || !result) return;

        overlay.classList.remove('hidden');
        dice.textContent = '?';
        dice.classList.add('rolling');
        result.textContent = '';
        result.className = 'roll-result';

        // 模拟掷骰动画
        let count = 0;
        const interval = setInterval(() => {
            dice.textContent = Math.floor(Math.random() * 100) + 1;
            count++;

            if (count >= 10) {
                clearInterval(interval);
                dice.classList.remove('rolling');

                // 显示最终结果
                setTimeout(() => {
                    dice.textContent = target.roll;

                    if (target.success) {
                        result.textContent = `✓ 成功！（目标 ${target.target}）`;
                        result.classList.add('success');
                    } else {
                        result.textContent = `✗ 失败（目标 ${target.target}）`;
                        result.classList.add('failure');
                    }

                    // 2秒后关闭
                    setTimeout(() => {
                        overlay.classList.add('hidden');
                        if (onComplete) onComplete();
                    }, 2000);
                }, 300);
            }
        }, 100);
    }
};

// 工具函数
const Utils = {
    // 格式化日期
    formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`;
    },

    // 防抖
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // 节流
    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },

    // 复制到剪贴板
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            Toast.success('已复制到剪贴板');
        } catch (err) {
            Toast.error('复制失败');
        }
    },

    // 平滑滚动到元素
    scrollToElement(element, offset = 0) {
        if (!element) return;
        const top = element.getBoundingClientRect().top + window.pageYOffset - offset;
        window.scrollTo({ top, behavior: 'smooth' });
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    ThemeManager.init();
    Toast.init();
    Modal.bindCloseButtons();
    Sidebar.init();

    console.log('一命千途 v2.0 - 前端重构版');
    console.log('设计系统已加载');
});

// 导出全局 API
window.YMQTApp = {
    theme: ThemeManager,
    toast: Toast,
    modal: Modal,
    loading: Loading,
    roll: RollAnimation,
    utils: Utils
};
