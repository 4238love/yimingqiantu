/* ===================================
   Status Panel - 状态面板增强脚本

   职责：
   - 状态数据分组展示
   - 人生愿望进度追踪
   - 历史记录折叠展开
   - 响应式状态管理
   =================================== */

const StatusPanel = {
    // 状态分组定义
    statusGroups: {
        core: {
            title: '核心状态',
            stats: ['health', 'wealth', 'intellect', 'charisma', 'energy', 'mood']
        },
        development: {
            title: '发展维度',
            stats: ['career', 'family', 'social', 'skills', 'wisdom', 'virtue']
        }
    },

    // 状态显示配置
    statConfig: {
        health: { label: '健康', icon: '💪', color: 'secondary' },
        wealth: { label: '财富', icon: '💰', color: 'primary' },
        intellect: { label: '智力', icon: '🧠', color: 'secondary' },
        charisma: { label: '魅力', icon: '✨', color: 'primary' },
        energy: { label: '精力', icon: '⚡', color: 'accent' },
        mood: { label: '心情', icon: '😊', color: 'secondary' },
        career: { label: '事业', icon: '💼', color: 'primary' },
        family: { label: '家庭', icon: '👨‍👩‍👧', color: 'secondary' },
        social: { label: '社交', icon: '👥', color: 'primary' },
        skills: { label: '技能', icon: '🎯', color: 'secondary' },
        wisdom: { label: '智慧', icon: '📚', color: 'primary' },
        virtue: { label: '德行', icon: '🙏', color: 'secondary' }
    },

    // 渲染核心状态
    renderCoreStats(stats) {
        const container = document.getElementById('core-stats');
        if (!container || !stats) return;

        const group = this.statusGroups.core;
        container.innerHTML = group.stats
            .filter(key => stats[key] !== undefined)
            .map(key => this.renderStatRow(key, stats[key]))
            .join('');
    },

    // 渲染发展维度
    renderDevelopmentStats(stats) {
        const container = document.getElementById('dev-stats');
        if (!container || !stats) return;

        const group = this.statusGroups.development;
        container.innerHTML = group.stats
            .filter(key => stats[key] !== undefined)
            .map(key => this.renderStatRow(key, stats[key]))
            .join('');
    },

    // 渲染单个状态行
    renderStatRow(key, value) {
        const config = this.statConfig[key];
        if (!config) return '';

        const percentage = Math.max(0, Math.min(100, value));
        const displayValue = Math.round(value);

        return `
            <div class="stat-row">
                <span class="stat-label" title="${config.label}">
                    ${config.icon} ${config.label}
                </span>
                <div class="stat-bar">
                    <div class="stat-fill" style="width: ${percentage}%"></div>
                </div>
                <span class="stat-value">${displayValue}</span>
            </div>
        `;
    },

    // 渲染人生愿望进度
    renderLifeGoal(goal) {
        const container = document.getElementById('life-goal-progress');
        if (!container || !goal) return;

        const progress = Math.max(0, Math.min(100, goal.progress || 0));
        const milestones = goal.milestones || [];
        const completed = milestones.filter(m => m.completed).length;

        container.innerHTML = `
            <div class="card mb-4">
                <div class="flex items-center justify-between mb-3">
                    <div>
                        <div class="text-lg font-bold">${goal.name}</div>
                        <div class="text-xs text-tertiary mt-1">${goal.description || ''}</div>
                    </div>
                    <div class="text-2xl">${goal.icon || '🎯'}</div>
                </div>

                <div class="progress mb-2">
                    <div class="progress-bar" style="width: ${progress}%"></div>
                </div>

                <div class="flex justify-between text-sm">
                    <span class="text-secondary">进度</span>
                    <span class="font-bold text-color-primary">${Math.round(progress)}%</span>
                </div>

                ${milestones.length > 0 ? `
                    <div class="mt-4 pt-4 border-t border-color-divider">
                        <div class="text-xs text-tertiary mb-2">里程碑 (${completed}/${milestones.length})</div>
                        <div class="flex flex-col gap-2">
                            ${milestones.map(m => `
                                <div class="flex items-center gap-2 text-sm">
                                    <span class="${m.completed ? 'text-color-success' : 'text-tertiary'}">
                                        ${m.completed ? '✓' : '○'}
                                    </span>
                                    <span class="${m.completed ? 'text-secondary' : 'text-tertiary'}">
                                        ${m.name}
                                    </span>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    },

    // 更新所有状态
    updateAll(data) {
        if (data.stats) {
            this.renderCoreStats(data.stats);
            this.renderDevelopmentStats(data.stats);
        }

        if (data.lifeGoal) {
            this.renderLifeGoal(data.lifeGoal);
        }
    }
};

// 历史记录管理
const HistoryManager = {
    filters: {
        all: { label: '全部', icon: '📜' },
        roll: { label: '判定', icon: '🎲' },
        stage: { label: '阶段', icon: '📍' },
        summary: { label: '总结', icon: '📝' },
        achievement: { label: '成就', icon: '🏆' }
    },

    currentFilter: 'all',
    collapsedGroups: new Set(),

    // 初始化历史记录面板
    init() {
        this.renderFilterButtons();
        this.bindFilterEvents();
    },

    // 渲染筛选按钮
    renderFilterButtons() {
        const container = document.getElementById('history-filters');
        if (!container) return;

        container.innerHTML = `
            <div class="flex gap-2 flex-wrap mb-4">
                ${Object.entries(this.filters).map(([key, filter]) => `
                    <button
                        class="chip ${key === this.currentFilter ? 'selected' : ''}"
                        data-filter="${key}"
                    >
                        ${filter.icon} ${filter.label}
                    </button>
                `).join('')}
            </div>
        `;
    },

    // 绑定筛选事件
    bindFilterEvents() {
        document.addEventListener('click', (e) => {
            const chip = e.target.closest('[data-filter]');
            if (!chip) return;

            const filter = chip.dataset.filter;
            this.setFilter(filter);
        });
    },

    // 设置筛选器
    setFilter(filter) {
        if (this.currentFilter === filter) return;

        this.currentFilter = filter;
        this.renderFilterButtons();
        this.filterEntries();
    },

    // 筛选历史记录
    filterEntries() {
        const entries = document.querySelectorAll('.history-entry');

        entries.forEach(entry => {
            const type = entry.dataset.type || 'all';
            const visible = this.currentFilter === 'all' || type === this.currentFilter;
            entry.style.display = visible ? '' : 'none';
        });
    },

    // 添加历史记录（支持分组）
    addEntry(entry) {
        const container = document.getElementById('narrative-window');
        if (!container) return;

        const type = entry.type || 'all';
        const timestamp = entry.timestamp || new Date().toLocaleString('zh-CN');

        // 检查是否需要创建新的年份分组
        const year = entry.year;
        let yearGroup = document.getElementById(`year-group-${year}`);

        if (!yearGroup && year) {
            yearGroup = this.createYearGroup(year);
            container.appendChild(yearGroup);
        }

        const entryHTML = `
            <div class="history-entry history-${type}" data-type="${type}">
                <div class="entry-timestamp">${timestamp}</div>
                <div class="entry-content">${entry.content}</div>
                ${entry.image ? `<img src="${entry.image}" alt="" class="mt-3 rounded-lg" loading="lazy">` : ''}
            </div>
        `;

        if (yearGroup) {
            const entriesContainer = yearGroup.querySelector('.year-entries');
            entriesContainer.insertAdjacentHTML('beforeend', entryHTML);
        } else {
            container.insertAdjacentHTML('beforeend', entryHTML);
        }

        this.filterEntries();
    },

    // 创建年份分组
    createYearGroup(year) {
        const group = document.createElement('div');
        group.id = `year-group-${year}`;
        group.className = 'year-group mb-6';
        group.innerHTML = `
            <div class="year-group-header">
                <button class="year-toggle" data-year="${year}">
                    <span class="year-toggle-icon">▼</span>
                    <span class="year-title">${year}年</span>
                </button>
            </div>
            <div class="year-entries"></div>
        `;

        // 绑定折叠事件
        const toggle = group.querySelector('.year-toggle');
        toggle.addEventListener('click', () => {
            this.toggleYearGroup(year);
        });

        return group;
    },

    // 切换年份分组展开/折叠
    toggleYearGroup(year) {
        const group = document.getElementById(`year-group-${year}`);
        if (!group) return;

        const entries = group.querySelector('.year-entries');
        const icon = group.querySelector('.year-toggle-icon');

        if (this.collapsedGroups.has(year)) {
            this.collapsedGroups.delete(year);
            entries.style.display = '';
            icon.textContent = '▼';
        } else {
            this.collapsedGroups.add(year);
            entries.style.display = 'none';
            icon.textContent = '▶';
        }
    },

    // 折叠所有旧年份
    collapseOldYears(currentYear) {
        const groups = document.querySelectorAll('.year-group');
        groups.forEach(group => {
            const year = parseInt(group.id.replace('year-group-', ''));
            if (year < currentYear) {
                this.collapsedGroups.add(year);
                const entries = group.querySelector('.year-entries');
                const icon = group.querySelector('.year-toggle-icon');
                if (entries) entries.style.display = 'none';
                if (icon) icon.textContent = '▶';
            }
        });
    }
};

// 移动端优化的侧边栏
const MobileSidebar = {
    init() {
        this.bindToggleEvents();
        this.bindSwipeGestures();
    },

    bindToggleEvents() {
        const toggle = document.getElementById('sidebar-toggle');
        const sidebar = document.getElementById('status-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');

        if (!toggle || !sidebar || !backdrop) return;

        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            backdrop.classList.toggle('visible');
        });

        backdrop.addEventListener('click', () => {
            sidebar.classList.remove('open');
            backdrop.classList.remove('visible');
        });
    },

    bindSwipeGestures() {
        const sidebar = document.getElementById('status-sidebar');
        if (!sidebar) return;

        let touchStartX = 0;
        let touchEndX = 0;

        sidebar.addEventListener('touchstart', (e) => {
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: true });

        sidebar.addEventListener('touchend', (e) => {
            touchEndX = e.changedTouches[0].screenX;
            this.handleSwipe();
        }, { passive: true });
    },

    handleSwipe() {
        const sidebar = document.getElementById('status-sidebar');
        const backdrop = document.getElementById('sidebar-backdrop');

        // 向左滑动超过 100px 则关闭
        if (touchStartX - touchEndX > 100) {
            sidebar.classList.remove('open');
            backdrop.classList.remove('visible');
        }
    }
};

// 导出到全局 API
if (window.YMQTApp) {
    window.YMQTApp.status = StatusPanel;
    window.YMQTApp.history = HistoryManager;
    window.YMQTApp.mobileSidebar = MobileSidebar;
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    HistoryManager.init();
    MobileSidebar.init();
    console.log('状态面板增强已加载');
});
