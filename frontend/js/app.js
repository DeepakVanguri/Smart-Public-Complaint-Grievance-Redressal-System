/**
 * Smart Gov - API Client & App Utilities
 * Handles all API communication with the backend
 */

const API_BASE = 'http://localhost:8000/api';

// ─── Token Management ─────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('sg_token'),
  getUser: () => {
    const u = localStorage.getItem('sg_user');
    return u ? JSON.parse(u) : null;
  },
  save: (token, user) => {
    localStorage.setItem('sg_token', token);
    localStorage.setItem('sg_user', JSON.stringify(user));
  },
  clear: () => {
    localStorage.removeItem('sg_token');
    localStorage.removeItem('sg_user');
  },
  isLoggedIn: () => !!localStorage.getItem('sg_token'),
  hasRole: (role) => {
    const user = Auth.getUser();
    return user && user.role === role;
  },
  isAdmin: () => {
    const user = Auth.getUser();
    return user && ['admin', 'staff'].includes(user.role);
  }
};

// ─── API Client ───────────────────────────────────────────
const API = {
  _call: async (method, endpoint, data = null, isFormData = false) => {
    const headers = {};
    const token = Auth.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    if (!isFormData) headers['Content-Type'] = 'application/json';

    const options = { method, headers };
    if (data) options.body = isFormData ? data : JSON.stringify(data);

    const resp = await fetch(`${API_BASE}${endpoint}`, options);
    const json = await resp.json();

    if (!resp.ok) {
      const errMsg = json.detail || json.message || 'An error occurred';
      throw new Error(errMsg);
    }
    return json;
  },

  get: (endpoint) => API._call('GET', endpoint),
  post: (endpoint, data) => API._call('POST', endpoint, data),
  put: (endpoint, data) => API._call('PUT', endpoint, data),
  delete: (endpoint) => API._call('DELETE', endpoint),
  upload: (endpoint, formData) => API._call('POST', endpoint, formData, true),

  // Auth
  login: (data) => API.post('/auth/login', data),
  register: (data) => API.post('/auth/register', data),
  getMe: () => API.get('/auth/me'),

  // Complaints
  getComplaints: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return API.get(`/complaints${q ? '?' + q : ''}`);
  },
  getComplaint: (id) => API.get(`/complaints/${id}`),
  submitComplaint: (data) => API.post('/complaints', data),
  updateStatus: (id, data) => API.put(`/complaints/${id}/status`, data),
  deleteComplaint: (id) => API.delete(`/complaints/${id}`),
  submitFeedback: (complaintId, data) => API.post(`/complaints/${complaintId}/feedback`, data),

  // Analytics
  getDashboardAnalytics: () => API.get('/analytics/dashboard'),

  // Notifications
  getNotifications: () => API.get('/notifications'),
  markNotifRead: (id) => API.put(`/notifications/${id}/read`),

  // Admin
  getUsers: () => API.get('/admin/users'),
  getStaff: () => API.get('/admin/staff'),
};

// ─── Toast Notifications ──────────────────────────────────
const Toast = {
  container: null,
  init() {
    this.container = document.getElementById('toast-container');
    if (!this.container) {
      this.container = document.createElement('div');
      this.container.id = 'toast-container';
      this.container.className = 'toast-container';
      document.body.appendChild(this.container);
    }
  },
  show(message, type = 'info', duration = 4000) {
    if (!this.container) this.init();
    const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
    toast.onclick = () => toast.remove();
    this.container.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'toast-out 0.3s ease forwards';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },
  success: (msg) => Toast.show(msg, 'success'),
  error: (msg) => Toast.show(msg, 'error'),
  info: (msg) => Toast.show(msg, 'info'),
  warning: (msg) => Toast.show(msg, 'warning'),
};

// ─── Utility Functions ────────────────────────────────────
const Utils = {
  // SQLite stores datetime('now') as UTC strings without 'Z'
  // e.g. "2026-02-28 05:51:00" — we must append 'Z' so JS parses as UTC,
  // then toLocaleDateString converts to the user's local timezone (IST etc.)
  _toUTC: (dateStr) => {
    if (!dateStr) return null;
    // Already has timezone info (Z or +offset)? Use as-is
    if (dateStr.includes('Z') || dateStr.includes('+')) return new Date(dateStr);
    // Replace space separator with 'T' and add 'Z' to mark as UTC
    return new Date(dateStr.replace(' ', 'T') + 'Z');
  },
  formatDate: (dateStr) => {
    if (!dateStr) return 'N/A';
    return Utils._toUTC(dateStr).toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  },
  formatDateShort: (dateStr) => {
    if (!dateStr) return 'N/A';
    return Utils._toUTC(dateStr).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  },
  timeAgo: (dateStr) => {
    if (!dateStr) return '';
    const seconds = Math.floor((new Date() - Utils._toUTC(dateStr)) / 1000);
    if (seconds < 60) return 'just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days < 30) return `${days}d ago`;
    return Utils.formatDateShort(dateStr);
  },
  capitalize: (str) => str ? str.charAt(0).toUpperCase() + str.slice(1).replace('_', ' ') : '',
  statusBadge: (status) => `<span class="badge badge-${status}">${Utils.capitalize(status)}</span>`,
  priorityBadge: (priority) => `<span class="badge badge-${priority}">
    ${priority === 'urgent' ? '🔴' : priority === 'high' ? '🟠' : priority === 'medium' ? '🟡' : '🟢'} ${Utils.capitalize(priority)}
  </span>`,
  categoryBadge: (cat) => {
    const icons = { water: '💧', electricity: '⚡', sanitation: '🗑️', infrastructure: '🏗️', other: '📋' };
    return `<span class="badge badge-${cat}">${icons[cat] || '📋'} ${Utils.capitalize(cat)}</span>`;
  },
  categoryIcon: (cat) => {
    const icons = { water: '💧', electricity: '⚡', sanitation: '🗑️', infrastructure: '🏗️', other: '📋' };
    return icons[cat] || '📋';
  },
  statusIcon: (status) => {
    const icons = { submitted: '📨', acknowledged: '👁️', in_progress: '🔧', resolved: '✅', closed: '🔒', rejected: '❌' };
    return icons[status] || '❓';
  },
  timelineColor: (status) => {
    const map = { resolved: 'success', closed: 'success', rejected: 'danger', in_progress: '', acknowledged: 'warning' };
    return map[status] || '';
  },
  debounce: (fn, delay) => {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
  },
  showLoading: (text = 'Loading...') => {
    let el = document.getElementById('global-loader');
    if (!el) {
      el = document.createElement('div');
      el.id = 'global-loader';
      el.className = 'loading-overlay';
      el.innerHTML = `<div class="spinner"></div><p style="color:var(--text-muted)">${text}</p>`;
      document.body.appendChild(el);
    }
  },
  hideLoading: () => { document.getElementById('global-loader')?.remove(); },
  guard: (requiredRole = null) => {
    if (!Auth.isLoggedIn()) {
      window.location.href = '/static/login.html';
      return false;
    }
    if (requiredRole === 'admin' && !Auth.hasRole('admin')) {
      // Admins only
      const user = Auth.getUser();
      if (user && user.role === 'staff') window.location.href = '/static/staff/dashboard.html';
      else window.location.href = '/static/citizen/dashboard.html';
      return false;
    }
    if (requiredRole === 'staff' && !Auth.hasRole('staff') && !Auth.hasRole('admin')) {
      // Staff or admin only
      window.location.href = '/static/citizen/dashboard.html';
      return false;
    }
    return true;
  },
  redirectDashboard: () => {
    const user = Auth.getUser();
    if (!user) { window.location.href = '/static/login.html'; return; }
    if (user.role === 'citizen') window.location.href = '/static/citizen/dashboard.html';
    else if (user.role === 'staff') window.location.href = '/static/staff/dashboard.html';
    else window.location.href = '/static/admin/dashboard.html';
  },
  renderStars: (rating) => {
    return Array.from({ length: 5 }, (_, i) =>
      `<span class="star ${i < rating ? 'filled' : ''}">★</span>`
    ).join('');
  }
};

// ─── Navbar Init ──────────────────────────────────────────
function initNavbar() {
  const user = Auth.getUser();
  const userNameEl = document.getElementById('nav-user-name');
  const userRoleEl = document.getElementById('nav-user-role');
  const avatarEl = document.getElementById('nav-avatar');
  const logoutBtn = document.getElementById('logout-btn');

  if (user) {
    if (userNameEl) userNameEl.textContent = user.full_name;
    if (userRoleEl) userRoleEl.textContent = Utils.capitalize(user.role);
    if (avatarEl) avatarEl.textContent = user.full_name.charAt(0).toUpperCase();
  }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      Auth.clear();
      window.location.href = '/static/index.html';
    });
  }

  // Notification bell
  loadNotifications();

  const notifBtn = document.getElementById('notif-btn');
  const notifDropdown = document.getElementById('notif-dropdown');
  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle('hidden');
    });
    document.addEventListener('click', () => notifDropdown.classList.add('hidden'));
  }
}

async function loadNotifications() {
  if (!Auth.isLoggedIn()) return;
  try {
    const data = await API.getNotifications();
    const badge = document.getElementById('notif-count');
    if (badge) {
      if (data.unread_count > 0) {
        badge.textContent = data.unread_count;
        badge.classList.remove('hidden');
      } else {
        badge.classList.add('hidden');
      }
    }
    const list = document.getElementById('notif-list');
    if (list) {
      if (data.notifications.length === 0) {
        list.innerHTML = `<div class="empty-state" style="padding:24px"><div class="empty-state-icon">🔔</div><p class="empty-state-desc">No notifications yet</p></div>`;
      } else {
        list.innerHTML = data.notifications.slice(0, 8).map(n => `
          <div class="notif-item ${n.is_read ? '' : 'unread'}" onclick="markRead(${n.id})">
            <div class="notif-msg">${n.message}</div>
            <div class="notif-time">${Utils.timeAgo(n.created_at)}</div>
          </div>
        `).join('');
      }
    }
  } catch (e) { /* silent fail */ }
}

async function markRead(id) {
  try {
    await API.markNotifRead(id);
    loadNotifications();
  } catch (e) { /* silent fail */ }
}

// ─── Mobile Sidebar Toggle ────────────────────────────────
function initSidebar() {
  const toggleBtn = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
  }
}

// Auto-init on DOM load
document.addEventListener('DOMContentLoaded', () => {
  Toast.init();
  if (document.getElementById('nav-user-name')) initNavbar();
  initSidebar();
});
