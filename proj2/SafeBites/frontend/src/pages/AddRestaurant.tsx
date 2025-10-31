import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AddRestaurant.css';

function AddRestaurant() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    restaurantName: '',
    cuisine: [] as string[],
    street: '',
    city: '',
    state: '',
    zipCode: '',
    phone: '',
    description: ''
  });

  const cuisineOptions = [
    'Italian', 'Japanese', 'Chinese', 'Mexican', 'Thai',
    'Indian', 'American', 'French', 'Mediterranean', 'Korean',
    'Vietnamese', 'Greek', 'Spanish', 'Brazilian', 'Middle Eastern'
  ];

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleCuisineToggle = (cuisine: string) => {
    setFormData(prev => ({
      ...prev,
      cuisine: prev.cuisine.includes(cuisine)
        ? prev.cuisine.filter(c => c !== cuisine)
        : [...prev.cuisine, cuisine]
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!formData.restaurantName.trim()) {
      alert('Please enter restaurant name');
      return;
    }
    if (formData.cuisine.length === 0) {
      alert('Please select at least one cuisine type');
      return;
    }
    if (!formData.street.trim() || !formData.city.trim() || !formData.state.trim() || !formData.zipCode.trim()) {
      alert('Please fill in all address fields');
      return;
    }

    // Add restaurant submission logic here
    console.log('Restaurant Data:', formData);
    alert('Restaurant submitted successfully! We will review your application.');
    navigate('/');
  };

  return (
    <div className="add-restaurant-page">
      {/* Header */}
      <header className="add-restaurant-header">
        <div className="header-content">
          <div className="logo" onClick={() => navigate('/')}>
            <img src="/wolfLogo.png" alt="SafeBites Logo" className="logo-img" />
            <h1>SafeBites</h1>
          </div>
          <button className="back-btn" onClick={() => navigate('/')}>
            ← Back to Home
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="add-restaurant-container">
        <div className="add-restaurant-hero">
          <h1>Add Your Restaurant</h1>
          <p>Join SafeBites and help people with food allergies dine safely at your establishment</p>
        </div>

        <div className="form-card">
          <form onSubmit={handleSubmit}>
            {/* Restaurant Information Section */}
            <div className="form-section">
              <h2 className="section-title">Restaurant Information</h2>
              
              <div className="form-group">
                <label htmlFor="restaurantName">
                  Restaurant Name <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="restaurantName"
                  name="restaurantName"
                  value={formData.restaurantName}
                  onChange={handleInputChange}
                  placeholder="Enter your restaurant name"
                  required
                />
              </div>

              <div className="form-group">
                <label>
                  Cuisine Type <span className="required">*</span>
                </label>
                <p className="field-description">Select all that apply</p>
                <div className="cuisine-grid">
                  {cuisineOptions.map((cuisine) => (
                    <button
                      key={cuisine}
                      type="button"
                      className={`cuisine-btn ${formData.cuisine.includes(cuisine) ? 'selected' : ''}`}
                      onClick={() => handleCuisineToggle(cuisine)}
                    >
                      {cuisine}
                    </button>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="description">Restaurant Description</label>
                <p className="field-description">Tell us about your restaurant (optional)</p>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Describe your restaurant, specialties, ambiance, etc."
                  rows={4}
                />
              </div>
            </div>

            {/* Location Section */}
            <div className="form-section">
              <h2 className="section-title">Location</h2>
              
              <div className="form-group">
                <label htmlFor="street">
                  Street Address <span className="required">*</span>
                </label>
                <input
                  type="text"
                  id="street"
                  name="street"
                  value={formData.street}
                  onChange={handleInputChange}
                  placeholder="123 Main Street"
                  required
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="city">
                    City <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="city"
                    name="city"
                    value={formData.city}
                    onChange={handleInputChange}
                    placeholder="City"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="state">
                    State <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="state"
                    name="state"
                    value={formData.state}
                    onChange={handleInputChange}
                    placeholder="NC"
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="zipCode">
                    ZIP Code <span className="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="zipCode"
                    name="zipCode"
                    value={formData.zipCode}
                    onChange={handleInputChange}
                    placeholder="27502"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Contact Information Section */}
            <div className="form-section">
              <h2 className="section-title">Contact Information</h2>
              
              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <p className="field-description">Customer service or reservation line (optional)</p>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={formData.phone}
                  onChange={handleInputChange}
                  placeholder="(555) 123-4567"
                />
              </div>
            </div>

            {/* Submit Section */}
            <div className="form-actions">
              <button type="button" className="cancel-btn" onClick={() => navigate('/')}>
                Cancel
              </button>
              <button type="submit" className="submit-btn">
                Submit Restaurant
              </button>
            </div>
          </form>
        </div>

        {/* Info Section */}
        <div className="info-section">
          <div className="info-card">
            <div className="info-icon">✓</div>
            <h3>Why Join SafeBites?</h3>
            <ul>
              <li>Reach customers with dietary restrictions</li>
              <li>Build trust with transparent allergen information</li>
              <li>Increase your restaurant's visibility</li>
              <li>Help create a safer dining experience</li>
            </ul>
          </div>

          <div className="info-card">
            <div className="info-icon">📋</div>
            <h3>What Happens Next?</h3>
            <ul>
              <li>Our team will review your application</li>
              <li>We'll contact you within 2-3 business days</li>
              <li>We'll help you add your menu and allergen info</li>
              <li>Your restaurant goes live on SafeBites!</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AddRestaurant;