// ==================== TaskFlow Application ====================

class TaskFlowApp {
    constructor() {
        this.tasks = this.loadTasks();
        this.currentFilter = 'all';
        this.currentView = 'dashboard';
        this.editingTaskId = null;
        this.init();
    }

    // ==================== Initialization ====================
    init() {
        this.setupEventListeners();
        this.setupViews();
        this.loadTheme();
        this.render();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
                item.classList.add('active');
                this.switchView(item.dataset.view);
            });
        });

        // Task Modal
        document.getElementById('addNewTaskBtn').addEventListener('click', () => this.openTaskModal());
        document.getElementById('closeTaskModal').addEventListener('click', () => this.closeTaskModal());
        document.getElementById('cancelTaskBtn').addEventListener('click', () => this.closeTaskModal());
        document.getElementById('taskForm').addEventListener('submit', (e) => this.handleTaskSubmit(e));

        // Quick Add
        document.getElementById('quickAddBtn').addEventListener('click', () => this.quickAddTask());
        document.getElementById('quickAddInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.quickAddTask();
        });

        // Filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentFilter = e.target.dataset.filter;
                this.renderTasks();
            });
        });

        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => this.openSettingsModal());
        document.getElementById('closeSettingsModal').addEventListener('click', () => this.closeSettingsModal());
        document.getElementById('darkModeToggle').addEventListener('change', (e) => this.toggleDarkMode(e.target.checked));
        document.getElementById('exportDataBtn').addEventListener('click', () => this.exportData());
        document.getElementById('importDataBtn').addEventListener('click', () => this.importData());
        document.getElementById('clearAllDataBtn').addEventListener('click', () => this.clearAllData());

        // Calendar
        document.getElementById('prevMonth').addEventListener('click', () => this.previousMonth());
        document.getElementById('nextMonth').addEventListener('click', () => this.nextMonth());

        // Search
        document.getElementById('searchInput').addEventListener('input', (e) => this.searchTasks(e.target.value));

        // Close modals on outside click
        window.addEventListener('click', (e) => {
            const taskModal = document.getElementById('taskModal');
            const settingsModal = document.getElementById('settingsModal');
            if (e.target === taskModal) this.closeTaskModal();
            if (e.target === settingsModal) this.closeSettingsModal();
        });
    }

    // ==================== Views ====================
    setupViews() {
        // Set initial calendar
        this.currentDate = new Date();
        this.renderCalendar();
    }

    switchView(view) {
        document.querySelectorAll('.view-content').forEach(v => v.style.display = 'none');
        document.getElementById(view + 'View').style.display = 'block';
        this.currentView = view;

        if (view === 'calendar') {
            this.renderCalendar();
        } else if (view === 'analytics') {
            this.renderAnalytics();
        }
    }

    // ==================== Task Management ====================
    openTaskModal(taskId = null) {
        const modal = document.getElementById('taskModal');
        const title = document.getElementById('taskModalTitle');
        const form = document.getElementById('taskForm');

        if (taskId) {
            title.textContent = '编辑任务';
            const task = this.tasks.find(t => t.id === taskId);
            document.getElementById('taskTitle').value = task.text;
            document.getElementById('taskDescription').value = task.description || '';
            document.getElementById('taskCategory').value = task.category || 'personal';
            document.getElementById('taskPriority').value = task.priority || 'medium';
            document.getElementById('taskDueDate').value = task.dueDate || '';
            document.getElementById('taskTags').value = (task.tags || []).join(', ');
            this.editingTaskId = taskId;
        } else {
            title.textContent = '新建任务';
            form.reset();
            this.editingTaskId = null;
        }

        modal.classList.add('show');
    }

    closeTaskModal() {
        document.getElementById('taskModal').classList.remove('show');
        document.getElementById('taskForm').reset();
        this.editingTaskId = null;
    }

    handleTaskSubmit(e) {
        e.preventDefault();

        const taskData = {
            text: document.getElementById('taskTitle').value,
            description: document.getElementById('taskDescription').value,
            category: document.getElementById('taskCategory').value,
            priority: document.getElementById('taskPriority').value,
            dueDate: document.getElementById('taskDueDate').value,
            tags: document.getElementById('taskTags').value.split(',').map(t => t.trim()).filter(t => t)
        };

        if (this.editingTaskId) {
            const task = this.tasks.find(t => t.id === this.editingTaskId);
            Object.assign(task, taskData);
            this.showToast('任务已更新', 'success');
        } else {
            const task = {
                id: Date.now(),
                ...taskData,
                completed: false,
                createdAt: new Date().toISOString()
            };
            this.tasks.push(task);
            this.showToast('任务已添加', 'success');
        }

        this.saveTasks();
        this.render();
        this.closeTaskModal();
    }

    quickAddTask() {
        const input = document.getElementById('quickAddInput');
        const text = input.value.trim();

        if (!text) {
            this.showToast('请输入任务内容', 'warning');
            return;
        }

        const task = {
            id: Date.now(),
            text,
            description: '',
            category: 'personal',
            priority: 'medium',
            dueDate: '',
            tags: [],
            completed: false,
            createdAt: new Date().toISOString()
        };

        this.tasks.push(task);
        this.saveTasks();
        this.render();
        input.value = '';
        this.showToast('任务已添加', 'success');
    }

    toggleTask(taskId) {
        const task = this.tasks.find(t => t.id === taskId);
        if (task) {
            task.completed = !task.completed;
            this.saveTasks();
            this.render();
        }
    }

    deleteTask(taskId) {
        this.tasks = this.tasks.filter(t => t.id !== taskId);
        this.saveTasks();
        this.render();
        this.showToast('任务已删除', 'success');
    }

    // ==================== Filtering & Searching ====================
    getFilteredTasks() {
        let filtered = this.tasks;
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        switch (this.currentFilter) {
            case 'today':
                filtered = filtered.filter(t => {
                    if (!t.dueDate) return false;
                    const taskDate = new Date(t.dueDate);
                    taskDate.setHours(0, 0, 0, 0);
                    return taskDate.getTime() === today.getTime();
                });
                break;
            case 'week':
                const weekEnd = new Date(today);
                weekEnd.setDate(weekEnd.getDate() + 7);
                filtered = filtered.filter(t => {
                    if (!t.dueDate) return false;
                    const taskDate = new Date(t.dueDate);
                    return taskDate >= today && taskDate <= weekEnd;
                });
                break;
            case 'overdue':
                filtered = filtered.filter(t => {
                    if (!t.dueDate || t.completed) return false;
                    const taskDate = new Date(t.dueDate);
                    return taskDate < today;
                });
                break;
            case 'completed':
                filtered = filtered.filter(t => t.completed);
                break;
        }

        return filtered.sort((a, b) => {
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
        });
    }

    getTodayTasks() {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return this.tasks.filter(t => {
            if (!t.dueDate || t.completed) return false;
            const taskDate = new Date(t.dueDate);
            taskDate.setHours(0, 0, 0, 0);
            return taskDate.getTime() === today.getTime();
        }).slice(0, 5);
    }

    searchTasks(query) {
        if (!query.trim()) {
            this.renderTasks();
            return;
        }

        const filtered = this.tasks.filter(t =>
            t.text.toLowerCase().includes(query.toLowerCase()) ||
            (t.description || '').toLowerCase().includes(query.toLowerCase())
        );

        this.renderTasksCustom(filtered);
    }

    // ==================== Rendering ====================
    render() {
        this.updateStats();
        this.renderTodayTasks();
        this.updateProgress();
        this.renderTasks();
    }

    updateStats() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(t => t.completed).length;
        const active = total - completed;
        const overdue = this.tasks.filter(t => {
            if (t.completed) return false;
            if (!t.dueDate) return false;
            return new Date(t.dueDate) < new Date();
        }).length;

        document.getElementById('totalTasksStat').textContent = total;
        document.getElementById('completedTasksStat').textContent = completed;
        document.getElementById('activeTasksStat').textContent = active;
        document.getElementById('overdueTasksStat').textContent = overdue;
    }

    updateProgress() {
        const total = this.tasks.length;
        const completed = this.tasks.filter(t => t.completed).length;
        const percent = total === 0 ? 0 : Math.round((completed / total) * 100);

        document.getElementById('progressPercent').textContent = percent + '%';

        const circle = document.getElementById('progressCircle');
        const circumference = 2 * Math.PI * 50;
        const offset = circumference - (percent / 100) * circumference;
        circle.style.strokeDashoffset = offset;
    }

    renderTodayTasks() {
        const today = this.getTodayTasks();
        const container = document.getElementById('todayTasksList');

        if (today.length === 0) {
            container.innerHTML = '<p class="empty-message">没有今日任务</p>';
            return;
        }

        container.innerHTML = today.map(task => `
            <div class="today-task-item ${task.completed ? 'completed' : ''}">
                <input type="checkbox" ${task.completed ? 'checked' : ''} onchange="app.toggleTask(${task.id})">
                <span>${this.escapeHtml(task.text)}</span>
            </div>
        `).join('');
    }

    renderTasks() {
        const filtered = this.getFilteredTasks();
        this.renderTasksCustom(filtered);
    }

    renderTasksCustom(tasks) {
        const container = document.getElementById('tasksList');

        if (tasks.length === 0) {
            container.innerHTML = '<p class="empty-message">暂无任务</p>';
            return;
        }

        container.innerHTML = tasks.map(task => this.createTaskCard(task)).join('');

        // Add event listeners
        container.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleTask(parseInt(e.target.dataset.taskId));
            });
        });

        container.querySelectorAll('.task-edit-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.openTaskModal(parseInt(btn.dataset.taskId));
            });
        });

        container.querySelectorAll('.task-delete-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (confirm('确定删除此任务？')) {
                    this.deleteTask(parseInt(btn.dataset.taskId));
                }
            });
        });
    }

    createTaskCard(task) {
        const categoryIcons = {
            work: 'fa-briefcase',
            personal: 'fa-heart',
            shopping: 'fa-shopping-cart',
            health: 'fa-heartbeat'
        };

        const categoryLabels = {
            work: '工作',
            personal: '个人',
            shopping: '购物',
            health: '健康'
        };

        const dueDate = task.dueDate ? new Date(task.dueDate).toLocaleDateString('zh-CN') : '';
        const isOverdue = task.dueDate && !task.completed && new Date(task.dueDate) < new Date();

        return `
            <div class="task-card ${task.completed ? 'completed' : ''} ${isOverdue ? 'overdue' : ''}">
                <div class="task-card-header">
                    <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} data-task-id="${task.id}">
                    <div class="task-title">${this.escapeHtml(task.text)}</div>
                    <span class="task-priority ${task.priority}">${this.getPriorityLabel(task.priority)}</span>
                </div>
                <div class="task-meta">
                    <span class="task-category">
                        <i class="fas ${categoryIcons[task.category]}"></i>
                        ${categoryLabels[task.category]}
                    </span>
                    ${dueDate ? `<span class="task-date"><i class="fas fa-calendar"></i>${dueDate}</span>` : ''}
                </div>
                ${task.tags && task.tags.length > 0 ? `
                    <div class="task-tags">
                        ${task.tags.map(tag => `<span class="task-tag">${this.escapeHtml(tag)}</span>`).join('')}
                    </div>
                ` : ''}
                <div class="task-actions">
                    <button class="task-edit-btn" data-task-id="${task.id}">
                        <i class="fas fa-edit"></i> 编辑
                    </button>
                    <button class="task-delete-btn" data-task-id="${task.id}">
                        <i class="fas fa-trash"></i> 删除
                    </button>
                </div>
            </div>
        `;
    }

    getPriorityLabel(priority) {
        const labels = { low: '低', medium: '中', high: '高' };
        return labels[priority] || '中';
    }

    // ==================== Calendar ====================
    renderCalendar() {
        const year = this.currentDate.getFullYear();
        const month = this.currentDate.getMonth();
        const monthName = new Date(year, month).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long' });

        document.getElementById('currentMonth').textContent = monthName;

        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        let html = '<div class="calendar-grid">';

        // Day headers
        const dayNames = ['日', '一', '二', '三', '四', '五', '六'];
        dayNames.forEach(day => {
            html += `<div class="calendar-day-header">${day}</div>`;
        });

        // Empty cells
        for (let i = 0; i < startingDayOfWeek; i++) {
            html += '<div class="calendar-day other-month"></div>';
        }

        // Days
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            date.setHours(0, 0, 0, 0);

            const tasksCount = this.tasks.filter(t => {
                if (!t.dueDate) return false;
                const taskDate = new Date(t.dueDate);
                taskDate.setHours(0, 0, 0, 0);
                return taskDate.getTime() === date.getTime();
            }).length;

            const isToday = date.getTime() === today.getTime();

            html += `
                <div class="calendar-day ${isToday ? 'today' : ''}" title="${tasksCount} 个任务">
                    ${day}
                </div>
            `;
        }

        html += '</div>';

        const container = document.getElementById('calendar');
        container.innerHTML = html;
    }

    previousMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() - 1);
        this.renderCalendar();
    }

    nextMonth() {
        this.currentDate.setMonth(this.currentDate.getMonth() + 1);
        this.renderCalendar();
    }

    // ==================== Analytics ====================
    renderAnalytics() {
        const dailyContainer = document.getElementById('dailyChart');
        const categoryContainer = document.getElementById('categoryChart');

        // Daily completion chart
        const last7Days = [];
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            date.setHours(0, 0, 0, 0);
            const label = date.toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
            const count = this.tasks.filter(t => {
                if (!t.completedAt) return false;
                const completedDate = new Date(t.completedAt);
                completedDate.setHours(0, 0, 0, 0);
                return completedDate.getTime() === date.getTime();
            }).length;
            last7Days.push({ label, count });
        }

        const maxCount = Math.max(...last7Days.map(d => d.count), 1);
        dailyContainer.innerHTML = `
            <div style="display: flex; align-items: flex-end; gap: 0.5rem; height: 150px;">
                ${last7Days.map(d => `
                    <div style="flex: 1; display: flex; flex-direction: column; align-items: center;">
                        <div style="width: 30px; height: ${(d.count / maxCount) * 100}px; background: var(--primary); border-radius: 4px;"></div>
                        <span style="font-size: 0.75rem; margin-top: 0.5rem; color: var(--text-secondary);">${d.label}</span>
                    </div>
                `).join('')}
            </div>
        `;

        // Category chart
        const categories = {};
        this.tasks.forEach(t => {
            const cat = t.category || 'personal';
            categories[cat] = (categories[cat] || 0) + 1;
        });

        const categoryLabels = {
            work: '工作',
            personal: '个人',
            shopping: '购物',
            health: '健康'
        };

        categoryContainer.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 1rem;">
                ${Object.entries(categories).map(([cat, count]) => `
                    <div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                            <span>${categoryLabels[cat] || cat}</span>
                            <span style="font-weight: bold;">${count}</span>
                        </div>
                        <div style="width: 100%; height: 20px; background: var(--bg-secondary); border-radius: 10px; overflow: hidden;">
                            <div style="width: ${(count / Math.max(...Object.values(categories))) * 100}%; height: 100%; background: var(--primary);"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // ==================== Settings ====================
    openSettingsModal() {
        const modal = document.getElementById('settingsModal');
        document.getElementById('darkModeToggle').checked = document.body.classList.contains('dark-mode');
        modal.classList.add('show');
    }

    closeSettingsModal() {
        document.getElementById('settingsModal').classList.remove('show');
    }

    toggleDarkMode(enabled) {
        if (enabled) {
            document.body.classList.add('dark-mode');
            localStorage.setItem('theme', 'dark');
        } else {
            document.body.classList.remove('dark-mode');
            localStorage.setItem('theme', 'light');
        }
    }

    loadTheme() {
        const theme = localStorage.getItem('theme');
        if (theme === 'dark') {
            document.body.classList.add('dark-mode');
        }
    }

    exportData() {
        const dataStr = JSON.stringify(this.tasks, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `taskflow-${new Date().getTime()}.json`;
        link.click();
        URL.revokeObjectURL(url);
        this.showToast('数据已导出', 'success');
    }

    importData() {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.json';
        input.onchange = (e) => {
            const file = e.target.files[0];
            const reader = new FileReader();
            reader.onload = (event) => {
                try {
                    const imported = JSON.parse(event.target.result);
                    if (Array.isArray(imported)) {
                        this.tasks = imported;
                        this.saveTasks();
                        this.render();
                        this.showToast('数据已导入', 'success');
                    } else {
                        this.showToast('无效的数据格式', 'error');
                    }
                } catch (error) {
                    this.showToast('导入失败', 'error');
                }
            };
            reader.readAsText(file);
        };
        input.click();
    }

    clearAllData() {
        if (confirm('这会删除所有任务，是否继续？')) {
            this.tasks = [];
            this.saveTasks();
            this.render();
            this.showToast('所有数据已清除', 'success');
        }
    }

    // ==================== Storage ====================
    saveTasks() {
        try {
            localStorage.setItem('tasks', JSON.stringify(this.tasks));
        } catch (error) {
            this.showToast('保存失败', 'error');
        }
    }

    loadTasks() {
        try {
            return JSON.parse(localStorage.getItem('tasks')) || [];
        } catch (error) {
            return [];
        }
    }

    // ==================== Utilities ====================
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast show ${type}`;

        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ==================== Initialize ====================
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new TaskFlowApp();
});
