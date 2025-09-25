import React, { useState, useEffect, useRef } from 'react';
import { User, LogOut, Trash2, X } from 'lucide-react';
import './UserProfile.css';

const UserProfile = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    // Get user info from localStorage (set during login)
    const token = localStorage.getItem('token');
    const userInfo = localStorage.getItem('user');
    
    if (token && userInfo) {
      try {
        setUser(JSON.parse(userInfo));
      } catch (err) {
        console.error('Error parsing user info:', err);
      }
    }
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
        setShowDeleteConfirm(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignOut = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/auth'; // Redirect to auth page
  };

  const handleDeleteAccount = async () => {
    const token = localStorage.getItem('token');
    
    if (!token) {
      alert('No authentication token found');
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/auth/delete-account', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        alert('Account deleted successfully');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/auth';
      } else {
        const error = await response.json();
        alert(`Failed to delete account: ${error.message}`);
      }
    } catch (err) {
      console.error('Error deleting account:', err);
      alert('Error deleting account. Please try again.');
    }
  };

  if (!user) {
    return null; // Don't render if no user info
  }

  return (
    <div className="user-profile" ref={dropdownRef}>
      <button 
        className="user-profile-button"
        onClick={() => setIsOpen(!isOpen)}
      >
        <User size={20} />
        <span className="user-name">{user.name}</span>
      </button>

      {isOpen && (
        <div className="user-dropdown">
          <div className="user-info">
            <div className="user-avatar">
              <User size={32} />
            </div>
            <div className="user-details">
              <h3>{user.name}</h3>
              <p>{user.email}</p>
            </div>
          </div>

          <div className="dropdown-divider"></div>

          <div className="dropdown-actions">
            <button 
              className="dropdown-item signout-btn"
              onClick={handleSignOut}
            >
              <LogOut size={16} />
              Sign Out
            </button>

            <button 
              className="dropdown-item delete-btn"
              onClick={() => setShowDeleteConfirm(true)}
            >
              <Trash2 size={16} />
              Delete Account
            </button>
          </div>

          {showDeleteConfirm && (
            <div className="delete-confirm-overlay">
              <div className="delete-confirm-modal">
                <div className="modal-header">
                  <h3>Delete Account</h3>
                  <button 
                    className="close-btn"
                    onClick={() => setShowDeleteConfirm(false)}
                  >
                    <X size={20} />
                  </button>
                </div>
                <div className="modal-body">
                  <p>Are you sure you want to delete your account?</p>
                  <p className="warning-text">
                    This action cannot be undone. All your documents and data will be permanently deleted.
                  </p>
                </div>
                <div className="modal-actions">
                  <button 
                    className="cancel-btn"
                    onClick={() => setShowDeleteConfirm(false)}
                  >
                    Cancel
                  </button>
                  <button 
                    className="confirm-delete-btn"
                    onClick={handleDeleteAccount}
                  >
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UserProfile;
