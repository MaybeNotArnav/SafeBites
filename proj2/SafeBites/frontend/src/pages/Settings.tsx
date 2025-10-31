import { useState } from 'react';
import './Settings.css';

function Settings() {
  const [isEditingUsername, setIsEditingUsername] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  // Mock user data
  const [username, setUsername] = useState('johndoe');
  const [fullName] = useState('John Doe');
  const [joinDate] = useState('January 2025');
  const [allergies, setAllergies] = useState<string[]>(['Peanuts', 'Shellfish']);
  const [newAllergy, setNewAllergy] = useState('');

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

  const handleAddAllergy = () => {
    if (newAllergy.trim() === '') {
      alert('Please enter an allergy');
      return;
    }
    if (allergies.includes(newAllergy.trim())) {
      alert('This allergy is already in your list');
      return;
    }
    setAllergies([...allergies, newAllergy.trim()]);
    setNewAllergy('');
  };

  const handleRemoveAllergy = (allergyToRemove: string) => {
    setAllergies(allergies.filter(allergy => allergy !== allergyToRemove));
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

      {/* Dietary Restrictions Section */}
      <div className="settings-section">
        <div className="section-header">
          <h2>Dietary Restrictions</h2>
          <p className="section-description">Manage your food allergies and restrictions</p>
        </div>

        <div className="settings-card">
          <div className="settings-info-row allergies-row">
            <div className="settings-info-label">
              <strong>Food Allergies</strong>
              <span className="info-description">Add allergies to filter unsafe dishes</span>
            </div>
            <div className="settings-info-value allergies-value">
              <div className="allergies-container">
                {/* Display current allergies */}
                <div className="allergies-list">
                  {allergies.length === 0 ? (
                    <p className="no-allergies">No allergies added yet</p>
                  ) : (
                    allergies.map((allergy, index) => (
                      <div key={index} className="allergy-badge">
                        <span>{allergy}</span>
                        <button 
                          className="remove-allergy-btn"
                          onClick={() => handleRemoveAllergy(allergy)}
                          aria-label={`Remove ${allergy}`}
                        >
                          ×
                        </button>
                      </div>
                    ))
                  )}
                </div>

                {/* Add new allergy */}
                <div className="add-allergy-section">
                  <input
                    type="text"
                    value={newAllergy}
                    onChange={(e) => setNewAllergy(e.target.value)}
                    placeholder="Enter allergy (e.g., Peanuts, Dairy)"
                    className="allergy-input"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleAddAllergy();
                      }
                    }}
                  />
                  <button 
                    className="add-allergy-btn"
                    onClick={handleAddAllergy}
                  >
                    Add
                  </button>
                </div>
              </div>
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