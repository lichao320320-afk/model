// ==================== Task Manager Class ====================
class TaskManager {
    constructor() {
        this.tasks = this.loadTasks();
        this.currentFilter = 'all';
        this.currentCategory = null;
        this.init();
    }

    // ==================== Initialization ====================
    init() {
        this.setupEventListeners();
        this.render();
        this.updateLastModified();
    }

    // ==================== Event Listeners ====================
    setupEventListeners() {
        // Add task
        document.getElementById('addBtn').addEventListener('click', () => this.addTask());
        document.getElementById('taskInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.addTask();
        });

        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.closest('.filter-btn').classList.add('active');
                this.currentFilter = e.target.closest('.filter-btn').dataset.filter;
                this.render();
            });
        });

        // Category buttons
        document.querySelectorAll('.category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.currentTarget.dataset.category;
                e.currentTarget.classList.toggle('active');
                this.currentCategory = e.currentTarget.classList.contains('active') ? category : null;
                this.render();
            });
        });

        // Action buttons
        document.getElementById('clearCompleted').addEventListener('click', () => this.clearCompleted());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportTasks());
        document.getElementById('clearAllBtn').addEventListener('click', () => this.showClearAllConfirm());
    }

    // ==================== Task Operations ====================
    addTask() {
        const input = document.getElementById('taskInput');
        const text = input.value.trim();

        if (!text) {
            this.showToast('Please enter a task', 'warning');
            return;
        }

        const task = {
            id: Date.now(),
            text,
            completed: false,
            category: this.currentCategory || 'personal',
            createdAt: new Date().toISOString(),
            completedAt: null
        };

        this.tasks.push(task);
        this.saveTasks();
        this.render();
        this.showToast('Task added successfully', 'success');
        input.value = '';
        input.focus();
    }

    toggleTask(id) {
        const task = this.tasks.find(t => t.id === id);
        if (task) {
            task.completed = !task.completed;
            task.completedAt = task.completed ? new Date().toISOString() : null;
            this.saveTasks();
            this.render();
        }
    }

    deleteTask(id) {
        this.tasks = this.tasks.filter(t => t.id !== id);
        this.saveTasks();
        this.render();
        this.showToast('Task deleted', 'success');
    }

    clearCompleted() {
        const completedCount = this.tasks.filter(t => t.completed).length;
        if (completedCount === 0) {
            this.showToast('No completed tasks to clear', 'warning');
            return;
        }
        this.showConfirm(
            `Delete ${completedCount} completed task(s)?`,
            () => {
                this.tasks = this.tasks.filter(t => !t.completed);
                this.saveTasks();
                this.render();
                this.showToast('Completed tasks cleared', 'success');
            }
        );
    }

    clearAll() {
        this.tasks = [];
        this.saveTasks();
        this.render();
        this.showToast('All tasks cleared', 'success');
    }

    // ==================== Filtering & Display ====================
    getFilteredTasks() {
        let filtered = this.tasks;

        // Apply status filter
        if (this.currentFilter === 'active') {
            filtered = filtered.filter(t => !t.completed);
        } else if (this.currentFilter === 'completed') {
            filtered = filtered.filter(t => t.completed);
        }

        // Apply category filter
        if (this.currentCategory) {
            filtered = filtered.filter(t => t.category === this.currentCategory);
        }

        return filtered;
    }

    getStats() {
        return {
            total: this.tasks.length,
            active: this.tasks.filter(t => !t.completed).length,
            completed: this.tasks.filter(t => t.completed).length
        };
    }

    // ==================== Rendering ====================
    render() {
        this.renderTasks();
        this.updateStats();
        this.updateActionButtons();
    }

    renderTasks() {
        const tasksList = document.getElementById('tasksList');
        const filtered = this.getFilteredTasks();

        if (filtered.length === 0) {
            tasksList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>${this.tasks.length === 0 ? 'No tasks yet. Add one to get started!' : 'No tasks match your filters'}</p>
                </div>
            `;
            return;
        }

        tasksList.innerHTML = filtered.map(task => this.createTaskElement(task)).join('');

        // Add event listeners to task elements
        tasksList.querySelectorAll('.task-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleTask(parseInt(e.target.dataset.id));
            });
        });

        tasksList.querySelectorAll('.task-btn.delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteTask(parseInt(btn.dataset.id));
            });
        });
    }

    createTaskElement(task) {
        const createdDate = new Date(task.createdAt).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });

        const categoryIcons = {
            work: 'fa-briefcase',
            personal: 'fa-heart',
            shopping: 'fa-shopping-cart',
            health: 'fa-heartbeat'
        };

        const categoryIcon = categoryIcons[task.category] || 'fa-tag';
        const categoryLabel = task.category.charAt(0).toUpperCase() + task.category.slice(1);

        return `
            <div class="task-item ${task.completed ? 'completed' : ''}">
                <input 
                    type="checkbox" 
                    class="task-checkbox" 
                    ${task.completed ? 'checked' : ''}
                    data-id="${task.id}"
                >
                <div class="task-content">
                    <div class="task-text">${this.escapeHtml(task.text)}</div>
                    <div class="task-meta">
                        <span class="task-category">
                            <i class="fas ${categoryIcon}"></i>
                            ${categoryLabel}
                        </span>
                        <span class="task-date">
                            <i class="fas fa-calendar"></i>
                            ${createdDate}
                        </span>
                    </div>
                </div>
                <div class="task-actions">
                    <button class="task-btn delete" data-id="${task.id}" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }

    updateStats() {
        const stats = this.getStats();
        document.getElementById('totalTasks').textContent = stats.total;
        document.getElementById('activeTasks').textContent = stats.active;
        document.getElementById('completedTasks').textContent = stats.completed;
    }

    updateActionButtons() {
        const clearCompletedBtn = document.getElementById('clearCompleted');
        const hasCompleted = this.tasks.some(t => t.completed);
        clearCompletedBtn.style.display = hasCompleted ? 'inline-flex' : 'none';
    }

    // ==================== Storage ====================
    saveTasks() {
        try {
            localStorage.setItem('tasks', JSON.stringify(this.tasks));
            this.updateLastModified();
        } catch (error) {
            console.error('Error saving tasks:', error);
            this.showToast('Error saving tasks', 'error');
        }
    }

    loadTasks() {
        try {
            const stored = localStorage.getItem('tasks');
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading tasks:', error);
            return [];
        }
    }

    updateLastModified() {
        const now = new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('lastUpdated').textContent = now;
    }

    // ==================== Export ====================
    exportTasks() {
        if (this.tasks.length === 0) {
            this.showToast('No tasks to export', 'warning');
            return;
        }

        const dataStr = JSON.stringify(this.tasks, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `tasks-${new Date().getTime()}.json`;
        link.click();
        URL.revokeObjectURL(url);
        this.showToast('Tasks exported successfully', 'success');
    }

    // ==================== UI Utilities ====================
    showToast(message, type = 'success') {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.className = `toast show ${type}`;
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    showConfirm(message, onConfirm) {
        const modal = document.getElementById('confirmModal');
        const confirmBtn = document.getElementById('confirmBtn');
        const cancelBtn = document.getElementById('cancelBtn');
        const confirmMessage = document.getElementById('confirmMessage');

        confirmMessage.textContent = message;
        modal.classList.add('show');

        const handleConfirm = () => {
            modal.classList.remove('show');
            onConfirm();
            cleanup();
        };

        const handleCancel = () => {
            modal.classList.remove('show');
            cleanup();
        };

        const cleanup = () => {
            confirmBtn.removeEventListener('click', handleConfirm);
            cancelBtn.removeEventListener('click', handleCancel);
        };

        confirmBtn.addEventListener('click', handleConfirm);
        cancelBtn.addEventListener('click', handleCancel);
    }

    showClearAllConfirm() {
        if (this.tasks.length === 0) {
            this.showToast('No tasks to clear', 'warning');
            return;
        }
        this.showConfirm(
            `Delete all ${this.tasks.length} task(s)? This cannot be undone.`,
            () => this.clearAll()
        );
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// ==================== Initialization ====================
let taskManager;

document.addEventListener('DOMContentLoaded', () => {
    taskManager = new TaskManager();
});
