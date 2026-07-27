/* ===================================
   Dark Mode Enhancements - 暗色模式增强

   职责：
   - 主题切换过渡动画
   - 图片亮度调整
   - 阅读模式优化
   - 特殊组件暗色适配
   =================================== */

const DarkModeEnhancements = {
    // 初始化
    init() {
        this.addTransitionStyles();
        this.adjustImagesForDarkMode();
        this.enhanceToggleButton();
        this.watchThemeChanges();
    },

    // 添加过渡样式（仅在切换时生效）
    addTransitionStyles() {
        const style = document.createElement('style');
        style.id = 'theme-transition-style';
        style.textContent = `
            * {
                transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease !important;
            }
        `;

        // 主题切换时临时添加
        document.addEventListener('theme-change-start', () => {
            document.head.appendChild(style);

            // 300ms 后移除，避免影响其他动画
            setTimeout(() => {
                style.remove();
            }, 300);
        });
    },

    // 监听主题变化
    watchThemeChanges() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.attributeName === 'data-theme') {
                    const newTheme = document.documentElement.getAttribute('data-theme');
                    this.onThemeChange(newTheme);
                }
            });
        });

        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['data-theme']
        });
    },

    // 主题变化处理
    onThemeChange(theme) {
        // 触发过渡事件
        document.dispatchEvent(new CustomEvent('theme-change-start'));

        // 调整图片
        this.adjustImagesForDarkMode();

        // 更新切换按钮
        this.updateToggleButton(theme);

        // 通知用户
        const message = theme === 'dark' ? '已切换到暗色模式' : '已切换到亮色模式';
        if (window.YMQTApp?.toast) {
            window.YMQTApp.toast.info(message);
        }

        // 触发完成事件
        setTimeout(() => {
            document.dispatchEvent(new CustomEvent('theme-change-complete', { detail: { theme } }));
        }, 300);
    },

    // 调整暗色模式下的图片
    adjustImagesForDarkMode() {
        const theme = document.documentElement.getAttribute('data-theme');
        const images = document.querySelectorAll('img:not([data-no-dark-adjust])');

        images.forEach(img => {
            if (theme === 'dark') {
                img.style.filter = 'brightness(0.9) contrast(0.95)';
            } else {
                img.style.filter = '';
            }
        });
    },

    // 增强切换按钮
    enhanceToggleButton() {
        const button = document.getElementById('theme-toggle');
        if (!button) return;

        // 添加键盘快捷键 (Ctrl/Cmd + Shift + D)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'D') {
                e.preventDefault();
                button.click();
            }
        });

        // 鼠标悬停提示
        button.title = '切换主题 (Ctrl+Shift+D)';

        // 添加动画效果
        button.addEventListener('click', () => {
            button.classList.add('theme-toggle-clicked');
            setTimeout(() => {
                button.classList.remove('theme-toggle-clicked');
            }, 300);
        });
    },

    // 更新切换按钮图标
    updateToggleButton(theme) {
        const button = document.getElementById('theme-toggle');
        if (!button) return;

        const sunIcon = button.querySelector('.icon-sun');
        const moonIcon = button.querySelector('.icon-moon');

        if (theme === 'dark') {
            sunIcon?.classList.add('hidden');
            moonIcon?.classList.remove('hidden');
        } else {
            moonIcon?.classList.add('hidden');
            sunIcon?.classList.remove('hidden');
        }
    },

    // 自动切换（根据时间）
    enableAutoSwitch(startHour = 18, endHour = 6) {
        setInterval(() => {
            const hour = new Date().getHours();
            const shouldBeDark = hour >= startHour || hour < endHour;
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const targetTheme = shouldBeDark ? 'dark' : 'light';

            // 只在用户没有手动设置时自动切换
            if (!localStorage.getItem('yimingqiantu-theme') && currentTheme !== targetTheme) {
                window.YMQTApp.theme.setTheme(targetTheme);
            }
        }, 60000); // 每分钟检查一次
    },

    // 阅读模式（进一步降低对比度）
    enableReadingMode() {
        document.body.classList.add('reading-mode');

        if (window.YMQTApp?.toast) {
            window.YMQTApp.toast.info('已启用阅读模式');
        }
    },

    disableReadingMode() {
        document.body.classList.remove('reading-mode');

        if (window.YMQTApp?.toast) {
            window.YMQTApp.toast.info('已关闭阅读模式');
        }
    },

    // 获取当前主题偏好的统计
    getThemePreference() {
        return {
            current: document.documentElement.getAttribute('data-theme'),
            saved: localStorage.getItem('yimingqiantu-theme'),
            system: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
        };
    },

    // 重置主题偏好（跟随系统）
    resetThemePreference() {
        localStorage.removeItem('yimingqiantu-theme');
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        window.YMQTApp.theme.setTheme(systemTheme);

        if (window.YMQTApp?.toast) {
            window.YMQTApp.toast.info('已重置为跟随系统主题');
        }
    },

    // 特殊元素暗色适配
    adaptSpecialElements() {
        const theme = document.documentElement.getAttribute('data-theme');

        // SVG 图标适配
        const svgs = document.querySelectorAll('svg[stroke]');
        svgs.forEach(svg => {
            if (theme === 'dark' && !svg.hasAttribute('data-original-stroke')) {
                svg.setAttribute('data-original-stroke', svg.getAttribute('stroke'));
                svg.setAttribute('stroke', 'currentColor');
            } else if (theme === 'light' && svg.hasAttribute('data-original-stroke')) {
                svg.setAttribute('stroke', svg.getAttribute('data-original-stroke'));
                svg.removeAttribute('data-original-stroke');
            }
        });

        // 代码块适配
        const codeBlocks = document.querySelectorAll('pre, code');
        codeBlocks.forEach(block => {
            if (theme === 'dark') {
                block.style.background = 'rgba(0, 0, 0, 0.3)';
            } else {
                block.style.background = '';
            }
        });
    },

    // 检测用户是否更喜欢暗色模式（基于使用时长）
    detectPreferredTheme() {
        const usage = JSON.parse(localStorage.getItem('theme-usage') || '{"dark":0,"light":0}');
        return usage.dark > usage.light ? 'dark' : 'light';
    },

    // 跟踪主题使用时长
    trackThemeUsage() {
        let startTime = Date.now();
        let currentTheme = document.documentElement.getAttribute('data-theme');

        // 页面可见性变化时保存
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.saveThemeUsage(currentTheme, Date.now() - startTime);
            } else {
                startTime = Date.now();
            }
        });

        // 主题变化时保存
        document.addEventListener('theme-change-complete', (e) => {
            this.saveThemeUsage(currentTheme, Date.now() - startTime);
            currentTheme = e.detail.theme;
            startTime = Date.now();
        });

        // 页面卸载时保存
        window.addEventListener('beforeunload', () => {
            this.saveThemeUsage(currentTheme, Date.now() - startTime);
        });
    },

    saveThemeUsage(theme, duration) {
        const usage = JSON.parse(localStorage.getItem('theme-usage') || '{"dark":0,"light":0}');
        usage[theme] = (usage[theme] || 0) + duration;
        localStorage.setItem('theme-usage', JSON.stringify(usage));
    }
};

// 暗色模式辅助工具
const DarkModeUtils = {
    // 检查是否为暗色模式
    isDark() {
        return document.documentElement.getAttribute('data-theme') === 'dark';
    },

    // 获取适应当前主题的颜色
    getThemedColor(lightColor, darkColor) {
        return this.isDark() ? darkColor : lightColor;
    },

    // 反转颜色亮度
    invertBrightness(element) {
        if (this.isDark()) {
            element.style.filter = 'invert(1) hue-rotate(180deg)';
        } else {
            element.style.filter = '';
        }
    },

    // 为图片添加暗色遮罩
    addDarkOverlay(image) {
        if (!this.isDark()) return;

        const overlay = document.createElement('div');
        overlay.className = 'dark-image-overlay';
        image.parentElement.style.position = 'relative';
        image.parentElement.appendChild(overlay);
    }
};

// 导出到全局 API
if (window.YMQTApp) {
    window.YMQTApp.darkMode = DarkModeEnhancements;
    window.YMQTApp.darkModeUtils = DarkModeUtils;

    // 扩展主题管理器
    const originalSetTheme = window.YMQTApp.theme.setTheme;
    window.YMQTApp.theme.setTheme = function(theme) {
        originalSetTheme.call(this, theme);
        DarkModeEnhancements.adaptSpecialElements();
    };
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    DarkModeEnhancements.init();
    DarkModeEnhancements.trackThemeUsage();
    console.log('暗色模式增强已加载');

    // 初始化时也调整特殊元素
    DarkModeEnhancements.adaptSpecialElements();
});
