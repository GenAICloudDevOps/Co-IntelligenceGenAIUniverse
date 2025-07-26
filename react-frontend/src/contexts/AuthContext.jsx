import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = localStorage.getItem('auth_token');
        const storedUser = localStorage.getItem('auth_user');

        if (storedToken && storedUser) {
          setToken(storedToken);
          setUser(JSON.parse(storedUser));
          
          // Verify token is still valid
          try {
            const currentUser = await authService.getCurrentUser(storedToken);
            setUser(currentUser);
          } catch (error) {
            // Token is invalid, clear auth state
            console.log('Token validation failed, clearing auth state');
            clearAuth();
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const clearAuth = () => {
    setUser(null);
    setToken(null);
    setError(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('auth_user');
  };

  const login = async (username, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authService.login(username, password);
      
      setUser(response.user);
      setToken(response.token.access_token);
      
      // Store in localStorage
      localStorage.setItem('auth_token', response.token.access_token);
      localStorage.setItem('auth_user', JSON.stringify(response.user));
      
      return response;
    } catch (error) {
      setError(error.message || 'Login failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, username, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await authService.register(name, email, username, password);
      
      setUser(response.user);
      setToken(response.token.access_token);
      
      // Store in localStorage
      localStorage.setItem('auth_token', response.token.access_token);
      localStorage.setItem('auth_user', JSON.stringify(response.user));
      
      return response;
    } catch (error) {
      setError(error.message || 'Registration failed');
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      if (token) {
        await authService.logout(token);
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      clearAuth();
    }
  };

  const refreshToken = async () => {
    try {
      if (!token) return null;
      
      const response = await authService.refreshToken(token);
      setToken(response.access_token);
      localStorage.setItem('auth_token', response.access_token);
      
      return response.access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearAuth();
      throw error;
    }
  };

  const value = {
    user,
    token,
    loading,
    error,
    isAuthenticated: !!user && !!token,
    login,
    register,
    logout,
    refreshToken,
    clearError: () => setError(null)
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
