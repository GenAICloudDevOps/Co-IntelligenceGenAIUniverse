import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const UserProfile = ({ onClose }) => {
  const { user, logout } = useAuth();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleLogout = async () => {
    try {
      await logout();
      onClose && onClose();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (!user) return null;

  return (
    <div className="user-profile">
      <div className="user-profile-header">
        <div className="user-avatar">
          <i className="fas fa-user-circle"></i>
        </div>
        <div className="user-info">
          <h3>{user.name}</h3>
          <p className="user-username">@{user.username}</p>
          <p className="user-email">{user.email}</p>
        </div>
      </div>

      <div className="user-profile-details">
        <div className="detail-item">
          <i className="fas fa-calendar-alt"></i>
          <div>
            <span className="detail-label">Member since</span>
            <span className="detail-value">{formatDate(user.created_at)}</span>
          </div>
        </div>

        <div className="detail-item">
          <i className="fas fa-check-circle"></i>
          <div>
            <span className="detail-label">Account status</span>
            <span className={`detail-value status ${user.is_active ? 'active' : 'inactive'}`}>
              {user.is_active ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>

        <div className="detail-item">
          <i className="fas fa-envelope"></i>
          <div>
            <span className="detail-label">Email verification</span>
            <span className={`detail-value status ${user.email_verified ? 'verified' : 'unverified'}`}>
              {user.email_verified ? 'Verified' : 'Unverified'}
            </span>
          </div>
        </div>
      </div>

      <div className="user-profile-actions">
        {!showLogoutConfirm ? (
          <button 
            className="logout-button"
            onClick={() => setShowLogoutConfirm(true)}
          >
            <i className="fas fa-sign-out-alt"></i>
            Sign Out
          </button>
        ) : (
          <div className="logout-confirm">
            <p>Are you sure you want to sign out?</p>
            <div className="logout-confirm-actions">
              <button 
                className="confirm-button danger"
                onClick={handleLogout}
              >
                Yes, Sign Out
              </button>
              <button 
                className="confirm-button secondary"
                onClick={() => setShowLogoutConfirm(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
