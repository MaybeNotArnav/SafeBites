import { useState } from 'react';
import './Settings.css';

function Settings() {
  const [isEditingUsername, setIsEditingUsername] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Mock user data
  const [username, setUsername] = useState('johndoe');
  const [fullName] = useState('John Doe');
  const [joinDate] = useState('January 2025');

  // Temporary states for editing
  const [tempUsername, setTempUsername] = useState(username);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSaveUsername = () => {
    setUsername(tempUsername);
    setIsEditingUsername(false);
  };

  const handleCancelUsername = () => {
    setTempUsername(username);
    setIsEditingUsername(false);
  };

  const handleChangePassword = () => {
    if (newPassword !== confirmPassword) {
      alert("New passwords don't match!");
      return;
    }
    if (newPassword.length < 6) {
      alert("Password must be at least 6 characters!");
      return;
    }
    // Add password change logic here
    alert("Password changed successfully!");
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setIsChangingPassword(false);
  };

  return (
    <div className="settings-container">
      <h1 className="settings-page-title">Settings</h1>

      {/* User Profile Section */}
      <div className="settings-section">
        <div className="section-header">
          <h2>User Profile</h2>
          <p className="section-description">Manage your account information</p>
        </div>

        <div className="settings-card">
          {/* Profile Avatar */}
          <div className="settings-avatar-section">
            <div className="settings-avatar">
              <img src="/icons/hugeicons_male.png" alt="Profile" />
            </div>
            <div className="settings-basic-info">
              <h3>{fullName}</h3>
              <p className="settings-join-date">Member since {joinDate}</p>
            </div>
          </div>

          {/* Username */}
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Username</strong>
              <span className="info-description">Your unique identifier</span>
            </div>
            <div className="settings-info-value">
              {!isEditingUsername ? (
                <>
                  <span>@{username}</span>
                  <button 
                    className="settings-edit-btn"
                    onClick={() => setIsEditingUsername(true)}
                  >
                    Edit
                  </button>
                </>
              ) : (
                <div className="settings-edit-field">
                  <input
                    type="text"
                    value={tempUsername}
                    onChange={(e) => setTempUsername(e.target.value)}
                    placeholder="Enter new username"
                  />
                  <div className="settings-edit-actions">
                    <button className="settings-save-btn" onClick={handleSaveUsername}>Save</button>
                    <button className="settings-cancel-btn" onClick={handleCancelUsername}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Password */}
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Password</strong>
              <span className="info-description">Change your account password</span>
            </div>
            <div className="settings-info-value">
              {!isChangingPassword ? (
                <>
                  <span>••••••••</span>
                  <button 
                    className="settings-edit-btn"
                    onClick={() => setIsChangingPassword(true)}
                  >
                    Change
                  </button>
                </>
              ) : (
                <div className="settings-edit-field settings-password-field">
                  <input
                    type="password"
                    value={currentPassword}
                    onChange={(e) => setCurrentPassword(e.target.value)}
                    placeholder="Current password"
                  />
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="New password"
                  />
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Confirm new password"
                  />
                  <div className="settings-edit-actions">
                    <button className="settings-save-btn" onClick={handleChangePassword}>Update Password</button>
                    <button className="settings-cancel-btn" onClick={() => {
                      setIsChangingPassword(false);
                      setCurrentPassword('');
                      setNewPassword('');
                      setConfirmPassword('');
                    }}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Additional Settings Sections */}
      <div className="settings-section">
        <div className="section-header">
          <h2>Preferences</h2>
          <p className="section-description">Customize your SafeBites experience</p>
        </div>

        <div className="settings-card">
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Notifications</strong>
              <span className="info-description">Manage notification preferences</span>
            </div>
            <div className="settings-info-value">
              <label className="toggle-switch">
                <input type="checkbox" defaultChecked />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Dark Mode</strong>
              <span className="info-description">Toggle dark mode appearance</span>
            </div>
            <div className="settings-info-value">
              <label className="toggle-switch">
                <input type="checkbox" />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="settings-section">
        <div className="section-header danger-header">
          <h2>Danger Zone</h2>
          <p className="section-description">Irreversible actions</p>
        </div>

        <div className="settings-card danger-card">
          <div className="settings-info-row">
            <div className="settings-info-label">
              <strong>Delete Account</strong>
              <span className="info-description">Permanently delete your account and all data</span>
            </div>
            <div className="settings-info-value">
              <button className="settings-danger-btn">Delete Account</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;