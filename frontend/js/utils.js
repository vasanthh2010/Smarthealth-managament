// utils.js - General utility functions

const Utils = {
  // Format Date safely
  formatDate: (dateString) => {
    if (!dateString) return '';
    const d = new Date(dateString);
    return isNaN(d.getTime()) ? dateString : d.toLocaleDateString();
  },

  // Shorten text
  truncateText: (text, maxLength = 50) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  },

  // Show a basic toast notification (mock)
  showToast: (message, type = 'success') => {
    alert(`[${type.toUpperCase()}] ${message}`);
  }
};

window.Utils = Utils;
