/* ===================================
   Interactions & Animations - 交互反馈增强

   职责：
   - D100 判定动画增强
   - 状态变化过渡动画
   - 微交互反馈
   - 进度指示器
   =================================== */

const InteractionFeedback = {
    // 初始化
    init() {
        this.initStatAnimations();
        this.initButtonFeedback();
        this.initProgressIndicators();
    },

    // 状态变化动画
    initStatAnimations() {
        // 监听状态更新
        this.observeStatChanges();
    },

    // 观察状态变化
    observeStatChanges() {
        const statBars = document.querySelectorAll('.stat-fill');

        statBars.forEach(bar => {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'style') {
                        this.animateStatChange(bar);
                    }
                });
            });

            observer.observe(bar, { attributes: true });
        });
    },

    // 动画化状态变化
    animateStatChange(bar) {
        const parent = bar.closest('.stat-row');
        if (!parent) return;

        // 闪烁效果
        parent.classList.add('stat-changing');
        setTimeout(() => {
            parent.classList.remove('stat-changing');
        }, 600);

        // 数值跳动
        const valueElement = parent.querySelector('.stat-value');
        if (valueElement) {
            this.animateNumber(valueElement);
        }
    },

    // 数字跳动动画
    animateNumber(element, duration = 600) {
        const target = parseInt(element.textContent);
        const start = target - Math.floor(Math.random() * 10 + 5); // 模拟变化
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(start + (target - start) * easeOutCubic);

            element.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    },

    // 增强的 D100 判定动画
    showEnhancedRoll(data, onComplete) {
        const overlay = document.getElementById('roll-overlay');
        const dice = document.getElementById('roll-dice');
        const result = document.getElementById('roll-result');
        const stage = overlay.querySelector('.roll-stage');

        if (!overlay || !dice || !result) return;

        overlay.classList.remove('hidden');

        // 第一阶段：展示行动
        stage.textContent = data.action || '天机判定';
        dice.textContent = '?';
        dice.classList.add('rolling');
        result.textContent = '';
        result.className = 'roll-result';

        // 创建进度环
        this.createProgressRing(dice, 2000);

        // 第二阶段：滚动骰子
        let count = 0;
        const rollDuration = 2000;
        const interval = 100;

        const rollInterval = setInterval(() => {
            const randomNum = Math.floor(Math.random() * 100) + 1;
            dice.textContent = randomNum;
            count++;

            if (count * interval >= rollDuration) {
                clearInterval(rollInterval);
                this.showRollResult(dice, result, data, onComplete);
            }
        }, interval);
    },

    // 创建进度环
    createProgressRing(container, duration) {
        const existing = container.querySelector('.progress-ring');
        if (existing) existing.remove();

        const ring = document.createElement('div');
        ring.className = 'progress-ring';
        ring.style.animationDuration = `${duration}ms`;
        container.appendChild(ring);

        setTimeout(() => ring.remove(), duration);
    },

    // 显示判定结果
    showRollResult(dice, result, data, onComplete) {
        dice.classList.remove('rolling');

        // 第三阶段：显示结果
        setTimeout(() => {
            dice.textContent = data.roll;

            // 成功/失败动画
            if (data.success) {
                dice.classList.add('roll-success');
                result.textContent = `✓ 成功！（目标 ${data.target}）`;
                result.classList.add('success');
                this.createSuccessParticles(dice);
            } else {
                dice.classList.add('roll-failure');
                result.textContent = `✗ 失败（目标 ${data.target}）`;
                result.classList.add('failure');
                this.createFailureEffect(dice);
            }

            // 显示属性影响
            if (data.modifiers) {
                this.showModifiers(result, data.modifiers);
            }

            // 2.5秒后关闭
            setTimeout(() => {
                const overlay = document.getElementById('roll-overlay');
                overlay.classList.add('hidden');
                dice.classList.remove('roll-success', 'roll-failure');
                if (onComplete) onComplete();
            }, 2500);
        }, 300);
    },

    // 成功粒子效果
    createSuccessParticles(container) {
        for (let i = 0; i < 12; i++) {
            const particle = document.createElement('div');
            particle.className = 'success-particle';
            particle.style.setProperty('--angle', `${(360 / 12) * i}deg`);
            container.appendChild(particle);

            setTimeout(() => particle.remove(), 1000);
        }
    },

    // 失败震动效果
    createFailureEffect(element) {
        element.classList.add('shake');
        setTimeout(() => element.classList.remove('shake'), 500);

        // 震动反馈
        if (navigator.vibrate) {
            navigator.vibrate([100, 50, 100]);
        }
    },

    // 显示修正值
    showModifiers(container, modifiers) {
        const modElement = document.createElement('div');
        modElement.className = 'roll-modifiers';

        const modText = Object.entries(modifiers)
            .map(([key, value]) => {
                const sign = value >= 0 ? '+' : '';
                return `${key} ${sign}${value}`;
            })
            .join(' | ');

        modElement.textContent = modText;
        container.appendChild(modElement);
    },

    // 按钮反馈
    initButtonFeedback() {
        document.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;

            this.createRipple(button, e);
        });
    },

    // 涟漪效果
    createRipple(element, event) {
        const ripple = document.createElement('span');
        ripple.className = 'ripple';

        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = `${size}px`;
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;

        element.appendChild(ripple);

        setTimeout(() => ripple.remove(), 600);
    },

    // 进度指示器
    initProgressIndicators() {
        // 为长时间操作添加进度指示
        this.trackLongOperations();
    },

    // 跟踪长时间操作
    trackLongOperations() {
        const originalFetch = window.fetch;

        window.fetch = async (...args) => {
            const startTime = Date.now();
            let progressBar = null;

            // 如果请求超过 500ms，显示进度条
            const timeout = setTimeout(() => {
                progressBar = this.showProgressBar();
            }, 500);

            try {
                const response = await originalFetch(...args);
                clearTimeout(timeout);

                if (progressBar) {
                    this.completeProgressBar(progressBar);
                }

                return response;
            } catch (error) {
                clearTimeout(timeout);

                if (progressBar) {
                    this.failProgressBar(progressBar);
                }

                throw error;
            }
        };
    },

    // 显示进度条
    showProgressBar() {
        const bar = document.createElement('div');
        bar.className = 'top-progress-bar';
        bar.innerHTML = '<div class="top-progress-fill"></div>';
        document.body.appendChild(bar);

        // 动画到 80%
        setTimeout(() => {
            bar.querySelector('.top-progress-fill').style.width = '80%';
        }, 10);

        return bar;
    },

    // 完成进度条
    completeProgressBar(bar) {
        const fill = bar.querySelector('.top-progress-fill');
        fill.style.width = '100%';

        setTimeout(() => {
            bar.remove();
        }, 300);
    },

    // 失败进度条
    failProgressBar(bar) {
        bar.classList.add('error');
        setTimeout(() => bar.remove(), 300);
    },

    // 加载骨架屏
    showSkeleton(container, type = 'text', count = 3) {
        const skeleton = document.createElement('div');
        skeleton.className = 'skeleton-container';

        for (let i = 0; i < count; i++) {
            const item = document.createElement('div');
            item.className = `skeleton skeleton-${type}`;
            skeleton.appendChild(item);
        }

        container.innerHTML = '';
        container.appendChild(skeleton);
    },

    // 移除骨架屏
    hideSkeleton(container) {
        const skeleton = container.querySelector('.skeleton-container');
        if (skeleton) {
            skeleton.style.opacity = '0';
            setTimeout(() => skeleton.remove(), 300);
        }
    },

    // 平滑内容切换
    transitionContent(container, newContent, duration = 300) {
        // 淡出
        container.style.opacity = '0';
        container.style.transform = 'translateY(10px)';

        setTimeout(() => {
            container.innerHTML = newContent;

            // 淡入
            container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, duration);
    },

    // 计数器动画
    animateCounter(element, start, end, duration = 1000) {
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeOutQuad = 1 - Math.pow(1 - progress, 2);
            const current = Math.round(start + (end - start) * easeOutQuad);

            element.textContent = current;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    },

    // 确认对话框（带动画）
    async confirm(message, options = {}) {
        return new Promise((resolve) => {
            const modal = document.createElement('div');
            modal.className = 'confirm-modal';
            modal.innerHTML = `
                <div class="confirm-backdrop"></div>
                <div class="confirm-dialog">
                    <div class="confirm-message">${message}</div>
                    <div class="confirm-actions">
                        <button class="btn-secondary confirm-cancel">
                            ${options.cancelText || '取消'}
                        </button>
                        <button class="btn-primary confirm-ok">
                            ${options.okText || '确定'}
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

            // 动画进入
            requestAnimationFrame(() => {
                modal.classList.add('visible');
            });

            const cleanup = (result) => {
                modal.classList.remove('visible');
                setTimeout(() => {
                    modal.remove();
                    resolve(result);
                }, 300);
            };

            modal.querySelector('.confirm-cancel').addEventListener('click', () => cleanup(false));
            modal.querySelector('.confirm-ok').addEventListener('click', () => cleanup(true));
            modal.querySelector('.confirm-backdrop').addEventListener('click', () => cleanup(false));
        });
    }
};

// 导出到全局 API
if (window.YMQTApp) {
    window.YMQTApp.feedback = InteractionFeedback;

    // 覆盖原有的 roll 方法
    window.YMQTApp.roll.show = (data, onComplete) => {
        InteractionFeedback.showEnhancedRoll(data, onComplete);
    };
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    InteractionFeedback.init();
    console.log('交互反馈增强已加载');
});
