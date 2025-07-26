import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const RegisterForm = ({ onSuccess, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const { register } = useAuth();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Clear error when user types
  };

  const validateForm = () => {
    if (!formData.name || !formData.email || !formData.username || !formData.password) {
      return 'Please fill in all fields';
    }

    if (formData.username.length < 3) {
      return 'Username must be at least 3 characters long';
    }

    if (!/^[a-zA-Z0-9]+$/.test(formData.username)) {
      return 'Username must contain only letters and numbers';
    }

    if (formData.password.length < 6) {
      return 'Password must be at least 6 characters long';
    }

    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match';
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      return 'Please enter a valid email address';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError('');

    try {
      await register(formData.name, formData.email, formData.username, formData.password);
      onSuccess && onSuccess();
    } catch (error) {
      setError(error.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2 className="auth-title">Create Account</h2>
      <p className="auth-subtitle">Join the Co-Intelligence platform</p>
      
      {error && (
        <div className="error-message">
          <i className="fas fa-exclamation-circle"></i>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="auth-form-content">
        <div className="form-group">
          <label htmlFor="name">Full Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Enter your full name"
            disabled={loading}
            autoComplete="name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="email">Email Address</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Enter your email address"
            disabled={loading}
            autoComplete="email"
          />
        </div>

        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Choose a username (letters and numbers only)"
            disabled={loading}
            autoComplete="username"
          />
          <small className="form-hint">At least 3 characters, letters and numbers only</small>
        </div>

        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Create a password"
            disabled={loading}
            autoComplete="new-password"
          />
          <small className="form-hint">At least 6 characters</small>
        </div>

        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <input
            type="password"
            id="confirmPassword"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            placeholder="Confirm your password"
            disabled={loading}
            autoComplete="new-password"
          />
        </div>

        <button 
          type="submit" 
          className="auth-button primary"
          disabled={loading}
        >
          {loading ? (
            <>
              <i className="fas fa-spinner fa-spin"></i>
              Creating Account...
            </>
          ) : (
            <>
              <i className="fas fa-user-plus"></i>
              Create Account
            </>
          )}
        </button>
      </form>

      <div className="auth-switch">
        <p>Already have an account?</p>
        <button 
          type="button" 
          className="auth-link"
          onClick={onSwitchToLogin}
          disabled={loading}
        >
          Sign In
        </button>
      </div>
    </div>
  );
};

export default RegisterForm;
