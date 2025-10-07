import { useNavigate } from 'react-router-dom';
import './Welcome.css';

function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="welcome-container">
      {/* Header */}
      <header className="welcome-header">
        <div className="logo">
          <img src="/wolfLogo.png" alt="SafeBites Logo" className="logo-img" />
          <h1>SafeBites</h1>
        </div>
        <button 
          className="header-signup-btn"
          onClick={() => navigate('/signup')}
        >
          Sign Up
        </button>
      </header>

      {/* Hero Section with Search */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Find Restaurants Near You</h1>
          <div className="search-bar">
            <input 
              type="text" 
              placeholder="Enter street address or zip code"
              className="search-input"
            />
            <button className="search-button">
              <img src="/icons/icons8-search-24.png" alt="Search" className="search-icon" />
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="feature-card-large">
          <img src="/icons/victoruler-flaticon-food-package.png" alt="Allergen Protection" className="feature-icon-img" />
          <h2>Eat Safely, Every Time</h2>
          <p>
            Never worry about hidden allergens again. Our intelligent filtering instantly 
            removes unsafe dishes, showing you only meals you can enjoy with confidence.
          </p>
        </div>

        <div className="feature-card-large">
          <img src="/icons/parzival-flaticon-chatbot.png" alt="AI Search" className="feature-icon-img" />
          <h2>Search Like You Talk</h2>
          <p>
            Forget complex filters—just ask! Chat naturally with our AI to find exactly 
            what you're craving, whether it's "low-sodium options" or "vegan desserts nearby."
          </p>
        </div>

        <div className="feature-card-large">
          <img src="/icons/freepik-flaticon-selection.png" alt="Smart Filtering" className="feature-icon-img" />
          <h2>Set It Once, Use It Forever</h2>
          <p>
            Tell us your allergies and preferences once. Every time you search, SafeBites 
            automatically protects you—making safe dining effortless and stress-free.
          </p>
        </div>
      </section>

      {/* About Section */}
      <section className="about-section">
        <div className="about-image">
          <img src="/foodImages/foodAllergy.jpg" alt="Food Allergy Items" />
        </div>
        <div className="about-content">
          <h2>About SafeBites</h2>
          <p>
            Dining out shouldn't be a guessing game. SafeBites uses AI to help people with 
            food allergies and dietary restrictions find safe, delicious meals at their 
            favorite restaurants—instantly.
          </p>
          <p>
            Our intelligent platform analyzes restaurant menus, detects allergens, and filters 
            dishes based on your personal dietary profile. No more scrolling through unsafe 
            options or worrying about hidden ingredients. Just ask what you want, and SafeBites 
            delivers personalized recommendations you can trust.
          </p>
          <p className="tagline">Safe dining made simple.</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="welcome-footer">
        <div className="footer-content">
          <div className="footer-column">
            <h3>Get to know us</h3>
            <ul>
              <li><a href="#">About Us</a></li>
              <li><a href="#">Our Apps</a></li>
              <li><a href="#">Careers</a></li>
              <li><a href="#">Investors</a></li>
              <li><a href="#">Blogs</a></li>
            </ul>
          </div>

          <div className="footer-column">
            <h3>Useful links</h3>
            <ul>
              <li><a href="#">Help</a></li>
              <li><a href="#">Gift Cards</a></li>
              <li><a href="#">Account Details</a></li>
              <li><a href="#">Catering</a></li>
            </ul>
          </div>

          <div className="footer-column">
            <h3>Doing Business</h3>
            <ul>
              <li><a href="#">Add your restaurant</a></li>
              <li><a href="#">Sign up to deliver</a></li>
              <li><a href="#">Create a business account</a></li>
            </ul>
          </div>
        </div>

        <div className="footer-bottom">
          <div className="footer-links">
            <a href="#">Terms of Use</a>
            <a href="#">Privacy Policy</a>
            <a href="#">Do not sell or share my personal information</a>
          </div>
          <div className="footer-right">
            <div className="social-icons">
              <img src="/icons/icons8-twitter-bird-24.png" alt="Twitter" className="Twitter-icon" />
              <img src="/icons/icons8-facebook-circled-24.png" alt="Facebook" className="Facebook-icon" />
              <img src="/icons/icons8-instagram-24.png" alt="Instagram" className="Instagram-icon" />
            </div>
            <p className="footer-copyright">&copy; 2025 SafeBites - Group 6</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default Welcome;