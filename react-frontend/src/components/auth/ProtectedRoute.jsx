import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const ProtectedRoute = ({ children, fallback = null, showLoginPrompt = true }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="auth-loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
        </div>
        <p>Checking authentication...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    if (fallback) {
      return fallback;
    }

    if (showLoginPrompt) {
      return (
        <div className="auth-required">
          <div className="auth-required-content">
            <i className="fas fa-lock fa-3x"></i>
            <h3>Authentication Required</h3>
            <p>Please sign in to access this feature</p>
          </div>
        </div>
      );
    }

    return null;
  }

  return children;
};

export default ProtectedRoute;
