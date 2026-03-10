// auth.js - JWT handling and authentication utilities

const Auth = {
  // Store token in localStorage
  setToken: (token) => {
    localStorage.setItem('jwtToken', token);
  },

  // Get token from localStorage
  getToken: () => {
    return localStorage.getItem('jwtToken');
  },

  // Remove token on logout
  removeToken: () => {
    localStorage.removeItem('jwtToken');
    localStorage.removeItem('userRole');
  },

  // Store user role
  setRole: (role) => {
    localStorage.setItem('userRole', role);
  },

  // Get user role
  getRole: () => {
    return localStorage.getItem('userRole');
  },

  // Check if authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('jwtToken');
  },

  // Logout redirect
  logout: () => {
    Auth.removeToken();
    window.location.href = '/index.html';
  }
};

window.Auth = Auth;
