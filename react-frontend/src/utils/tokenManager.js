class TokenManager {
  constructor() {
    this.TOKEN_KEY = 'auth_token';
    this.USER_KEY = 'auth_user';
  }

  // Get token from localStorage
  getToken() {
    try {
      return localStorage.getItem(this.TOKEN_KEY);
    } catch (error) {
      console.error('Error getting token:', error);
      return null;
    }
  }

  // Set token in localStorage
  setToken(token) {
    try {
      localStorage.setItem(this.TOKEN_KEY, token);
      return true;
    } catch (error) {
      console.error('Error setting token:', error);
      return false;
    }
  }

  // Remove token from localStorage
  removeToken() {
    try {
      localStorage.removeItem(this.TOKEN_KEY);
      return true;
    } catch (error) {
      console.error('Error removing token:', error);
      return false;
    }
  }

  // Get user data from localStorage
  getUser() {
    try {
      const userData = localStorage.getItem(this.USER_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  }

  // Set user data in localStorage
  setUser(user) {
    try {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
      return true;
    } catch (error) {
      console.error('Error setting user data:', error);
      return false;
    }
  }

  // Remove user data from localStorage
  removeUser() {
    try {
      localStorage.removeItem(this.USER_KEY);
      return true;
    } catch (error) {
      console.error('Error removing user data:', error);
      return false;
    }
  }

  // Clear all auth data
  clearAuth() {
    this.removeToken();
    this.removeUser();
  }

  // Check if token exists
  hasToken() {
    return !!this.getToken();
  }

  // Check if user data exists
  hasUser() {
    return !!this.getUser();
  }

  // Check if user is authenticated (has both token and user data)
  isAuthenticated() {
    return this.hasToken() && this.hasUser();
  }

  // Decode JWT token (basic decode without verification)
  decodeToken(token = null) {
    try {
      const tokenToUse = token || this.getToken();
      if (!tokenToUse) return null;

      const parts = tokenToUse.split('.');
      if (parts.length !== 3) return null;

      const payload = parts[1];
      const decoded = JSON.parse(atob(payload));
      return decoded;
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }

  // Check if token is expired
  isTokenExpired(token = null) {
    try {
      const decoded = this.decodeToken(token);
      if (!decoded || !decoded.exp) return true;

      const currentTime = Math.floor(Date.now() / 1000);
      return decoded.exp < currentTime;
    } catch (error) {
      console.error('Error checking token expiration:', error);
      return true;
    }
  }

  // Get token expiration time
  getTokenExpiration(token = null) {
    try {
      const decoded = this.decodeToken(token);
      if (!decoded || !decoded.exp) return null;

      return new Date(decoded.exp * 1000);
    } catch (error) {
      console.error('Error getting token expiration:', error);
      return null;
    }
  }

  // Get time until token expires (in minutes)
  getTimeUntilExpiration(token = null) {
    try {
      const expiration = this.getTokenExpiration(token);
      if (!expiration) return null;

      const now = new Date();
      const diff = expiration.getTime() - now.getTime();
      return Math.floor(diff / (1000 * 60)); // Convert to minutes
    } catch (error) {
      console.error('Error calculating time until expiration:', error);
      return null;
    }
  }
}

export const tokenManager = new TokenManager();
