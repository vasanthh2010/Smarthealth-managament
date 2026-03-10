/* ──────────────────────────────────────────────────────────────
   Smart Hospital - API Client Utility
   Base URL auto-detects: localhost:5000
────────────────────────────────────────────────────────────── */

const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://localhost:5000'
  : window.location.origin;

/* ─── TOKEN MANAGEMENT ───────────────────────────────────────── */
const Auth = {
  getToken: () => localStorage.getItem('sh_token'),
  getUser:  () => { try { return JSON.parse(localStorage.getItem('sh_user') || 'null'); } catch { return null; } },
  setSession: (token, user) => {
    localStorage.setItem('sh_token', token);
    localStorage.setItem('sh_user', JSON.stringify(user));
  },
  clearSession: () => {
    localStorage.removeItem('sh_token');
    localStorage.removeItem('sh_user');
  },
  isLoggedIn: () => !!localStorage.getItem('sh_token'),
  requireRole: (role) => {
    const user = Auth.getUser();
    if (!user || user.role !== role) {
      Auth.clearSession();
      window.location.href = '/frontend/index.html';
      return false;
    }
    return true;
  }
};

/* ─── FETCH WRAPPER ──────────────────────────────────────────── */
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  try {
    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || data.message || `HTTP ${res.status}`);
    }
    return data;
  } catch (err) {
    if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
      throw new Error('Cannot connect to server. Make sure the backend is running on port 5000.');
    }
    throw err;
  }
}

/* ─── TOAST NOTIFICATIONS ────────────────────────────────────── */
function showToast(message, type = 'default', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.animation = 'fadeIn 0.3s ease reverse both';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

/* ─── LOADING HELPER ─────────────────────────────────────────── */
function setLoading(btn, loading, text = 'Processing...') {
  if (loading) {
    btn.disabled = true;
    btn._origText = btn.innerHTML;
    btn.innerHTML = `<span class="spinner-sm" style="display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,0.3);border-top-color:white;border-radius:50%;animation:spin 0.7s linear infinite;"></span> ${text}`;
  } else {
    btn.disabled = false;
    btn.innerHTML = btn._origText || text;
  }
}

/* ─── ERROR DISPLAY ──────────────────────────────────────────── */
function showError(containerId, message) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = `<div class="alert alert-error">⚠️ ${message}</div>`;
  el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
function clearError(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = '';
}

/* ─── FORMAT HELPERS ─────────────────────────────────────────── */
const fmt = {
  date: (d) => d ? new Date(d).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : '-',
  time: (d) => d ? new Date(d).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : '-',
  datetime: (d) => d ? `${fmt.date(d)}, ${fmt.time(d)}` : '-',
  currency: (n) => `₹${Number(n || 0).toLocaleString('en-IN')}`,
  wait: (mins) => mins < 60 ? `${mins} min` : `${Math.floor(mins/60)}h ${mins%60}m`,
  capitalize: (s) => s ? s.charAt(0).toUpperCase() + s.slice(1) : '',
  badge: (status) => {
    const map = {
      available: 'success', occupied: 'danger',
      pending: 'warning', completed: 'success',
      in_service: 'primary', cancelled: 'danger',
      approved: 'success', rejected: 'danger', requested: 'warning',
      dispatched: 'primary'
    };
    return `<span class="badge badge-${map[status]||'primary'}">${fmt.capitalize(status?.replace('_',' '))}</span>`;
  }
};

/* ─── WEBSOCKET HELPER ───────────────────────────────────────── */
let ws = null;
function connectWS(hospitalId, onMessage) {
  if (ws) ws.close();
  const wsUrl = API_BASE.replace('http', 'ws') + '/socket.io/?EIO=4&transport=websocket';
  // Using socket.io client from CDN instead
  if (typeof io !== 'undefined') {
    ws = io(API_BASE);
    ws.emit('join_hospital', { hospital_id: hospitalId });
    ws.on('bed_update', onMessage);
    ws.on('token_update', onMessage);
    return ws;
  }
}
function disconnectWS() { if (ws) { ws.close(); ws = null; } }

/* ─── MODAL HELPER ───────────────────────────────────────────── */
function openModal(id) { document.getElementById(id)?.classList.add('open'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('open'); }
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});
