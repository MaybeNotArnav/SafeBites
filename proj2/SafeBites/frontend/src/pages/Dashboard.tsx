import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import Home from './Home';
import SearchChat from './SearchChat';
import Menu from './Menu';
import Dish from './Dish';
import Settings from './Settings';

function Dashboard() {
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [currentPage, setCurrentPage] = useState('home');

  // Mock user data - replace with actual user data from auth context
  const user = {
    fullName: 'John Doe',
    username: '@johndoe'
  };

  const handleLogout = () => {
    // Add any logout logic here (clear tokens, etc.)
    navigate('/login');
  };

  const renderContent = () => {
    switch(currentPage) {
      case 'home':
        return <Home />;
      case 'search-chat':
        return <SearchChat />;
      case 'menu':
        return <Menu />;
      case 'dish':
        return <Dish />;
      case 'settings':
        return <Settings />;
      default:
        return null;
    }
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        {/* Left: Logo and Name */}
        <div className="header-left">
          <div className="logo">
            <img src="/wolfLogo.png" alt="SafeBites Logo" className="logo-img" />
            <h1>SafeBites</h1>
          </div>
        </div>

        {/* Middle: Search Bar */}
        <div className="header-middle">
          <div className="search-container">
            <div className="search-icon-wrapper">
              <img src="/icons/hugeicons_search.png" alt="Search" className="search-icon" />
            </div>
            <input 
              type="text" 
              placeholder="Search for dishes, restaurants..." 
              className="search-input"
            />
          </div>
        </div>

        {/* Right: Profile Icon */}
        <div className="header-right">
          <div className="profile-container">
            <button 
              className="profile-btn"
              onClick={() => setIsProfileOpen(!isProfileOpen)}
            >
              <img src="/icons/hugeicons_male.png" alt="Profile" className="profile-icon" />
            </button>
            
            {/* Profile Dropdown */}
            {isProfileOpen && (
              <div className="profile-dropdown">
                <div className="profile-info">
                  <p className="profile-fullname">{user.fullName}</p>
                  <p className="profile-username">{user.username}</p>
                </div>
                <button 
                  className="btn-logout"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="dashboard-body">
        {/* Sidebar */}
        <aside className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
          <button 
            className="menu-toggle-btn-sidebar"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            {isSidebarOpen ? (
              <span className="close-icon">✕</span>
            ) : (
              <span className="hamburger-icon">☰</span>
            )}
          </button>
          
          <nav className="sidebar-nav">
            <button 
              className={`sidebar-item ${currentPage === 'home' ? 'active' : ''}`}
              onClick={() => setCurrentPage('home')}
            >
              <img src="/icons/hugeicons_home.png" alt="Home" className="sidebar-icon" />
              {isSidebarOpen && <span className="sidebar-text">Home</span>}
            </button>

            <button 
              className={`sidebar-item ${currentPage === 'search-chat' ? 'active' : ''}`}
              onClick={() => setCurrentPage('search-chat')}
            >
              <img src="/icons/hugeicon_ai_search.png" alt="Search Chat" className="sidebar-icon" />
              {isSidebarOpen && <span className="sidebar-text">Search Chat</span>}
            </button>
            
            <button 
              className={`sidebar-item ${currentPage === 'menu' ? 'active' : ''}`}
              onClick={() => setCurrentPage('menu')}
            >
              <img src="/icons/hugeicons_menu_restaurant.png" alt="Menu" className="sidebar-icon" />
              {isSidebarOpen && <span className="sidebar-text">Menu</span>}
            </button>
            
            <button 
              className={`sidebar-item ${currentPage === 'dish' ? 'active' : ''}`}
              onClick={() => setCurrentPage('dish')}
            >
              <img src="/icons/hugeicons_dish.png" alt="Dish" className="sidebar-icon" />
              {isSidebarOpen && <span className="sidebar-text">Dish</span>}
            </button>
            
            <button 
              className={`sidebar-item ${currentPage === 'settings' ? 'active' : ''}`}
              onClick={() => setCurrentPage('settings')}
            >
              <img src="/icons/hugeicons_setting.png" alt="Settings" className="sidebar-icon" />
              {isSidebarOpen && <span className="sidebar-text">Settings</span>}
            </button>
          </nav>
        </aside>

        {/* Main Content */}
        <main className={`dashboard-main ${isSidebarOpen ? 'sidebar-open' : 'sidebar-closed'}`}>
          {renderContent()}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;