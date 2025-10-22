import { useState, useEffect } from 'react';
import './Home.css';
import RestaurantMenu from './RestaurantMenu';

// Placeholder restaurants - based on restaurant_model.py structure
const placeholderRestaurants = [
  {
    _id: "rest_1",
    name: "Bella Italia Trattoria",
    location: "123 Main Street, Apex, NC 27502",
    cuisine: ["Italian"],
    rating: 4.5
  },
  {
    _id: "rest_2",
    name: "Tokyo Sushi House",
    location: "456 Oak Avenue, Apex, NC 27523",
    cuisine: ["Japanese", "Sushi"],
    rating: 4.8
  },
  {
    _id: "rest_3",
    name: "Spice Garden",
    location: "789 Elm Road, Apex, NC 27539",
    cuisine: ["Indian"],
    rating: 4.3
  },
  {
    _id: "rest_4",
    name: "El Mariachi Cantina",
    location: "321 Pine Street, Apex, NC 27502",
    cuisine: ["Mexican"],
    rating: 4.6
  },
  {
    _id: "rest_5",
    name: "Bangkok Street Kitchen",
    location: "654 Maple Drive, Apex, NC 27523",
    cuisine: ["Thai"],
    rating: 4.7
  },
  {
    _id: "rest_6",
    name: "The American Diner",
    location: "987 Cedar Lane, Apex, NC 27539",
    cuisine: ["American"],
    rating: 4.2
  }
];

function Home() {
  const [restaurants] = useState(placeholderRestaurants);
  const [filteredRestaurants, setFilteredRestaurants] = useState(placeholderRestaurants);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [sortBy, setSortBy] = useState<string>("none");
  const [selectedRestaurant, setSelectedRestaurant] = useState<any>(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);

  // Apply sorting
  useEffect(() => {
    let sorted = [...restaurants];

    if (sortBy === "name-asc") {
      sorted.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === "name-desc") {
      sorted.sort((a, b) => b.name.localeCompare(a.name));
    } else if (sortBy === "rating-desc") {
      sorted.sort((a, b) => b.rating - a.rating);
    } else if (sortBy === "rating-asc") {
      sorted.sort((a, b) => a.rating - b.rating);
    }

    setFilteredRestaurants(sorted);
  }, [sortBy, restaurants]);

  const handleRestaurantClick = (restaurant: any) => {
    setSelectedRestaurant(restaurant);
    setIsPopupOpen(true);
  };

  const closePopup = () => {
    setIsPopupOpen(false);
    setSelectedRestaurant(null);
  };

  return (
    <div className="home-container">
      {/* Header Section */}
      <div className="home-header">
        <h1 className="page-title">Restaurants</h1>
        
        <button 
          className="filter-btn"
          onClick={() => setIsFilterOpen(!isFilterOpen)}
        >
          <img src="/icons/hugeicons_filter.png" alt="Filter" className="filter-icon" />
        </button>
      </div>

      {/* Filter Dropdown */}
      {isFilterOpen && (
        <div className="filter-dropdown">
          <h3>Filter By:</h3>
          
          <div className="filter-section">
            <label>Sort by Name:</label>
            <div className="filter-options">
              <button 
                className={`filter-option-btn ${sortBy === "name-asc" ? 'active' : ''}`}
                onClick={() => setSortBy("name-asc")}
              >
                A-Z
              </button>
              <button 
                className={`filter-option-btn ${sortBy === "name-desc" ? 'active' : ''}`}
                onClick={() => setSortBy("name-desc")}
              >
                Z-A
              </button>
            </div>
          </div>

          <div className="filter-section">
            <label>Sort by Rating:</label>
            <div className="filter-options">
              <button 
                className={`filter-option-btn ${sortBy === "rating-desc" ? 'active' : ''}`}
                onClick={() => setSortBy("rating-desc")}
              >
                Highest First
              </button>
              <button 
                className={`filter-option-btn ${sortBy === "rating-asc" ? 'active' : ''}`}
                onClick={() => setSortBy("rating-asc")}
              >
                Lowest First
              </button>
            </div>
          </div>

          <button 
            className="clear-filter-btn"
            onClick={() => setSortBy("none")}
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Restaurant Cards Grid */}
      <div className="restaurant-grid">
        {filteredRestaurants.map((restaurant) => (
          <div 
            key={restaurant._id} 
            className="restaurant-card"
            onClick={() => handleRestaurantClick(restaurant)}
          >
            <div className="restaurant-card-content">
              <h2 className="restaurant-name">{restaurant.name}</h2>
              
              <div className="restaurant-rating">
                <img src="/icons/pixel_perfect_flaticon_star.png" alt="Rating" className="star-icon" />
                <span className="rating-value">{restaurant.rating.toFixed(1)}</span>
              </div>
              
              <div className="restaurant-cuisine">
                {restaurant.cuisine.join(', ')}
              </div>
              
              <div className="restaurant-location">
                <img src="/icons/md_tanvirul_haque_flaticon_location.png" alt="Location" className="location-icon" />
                {restaurant.location}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Popup Modal */}
      {selectedRestaurant && (
        <RestaurantMenu 
          restaurant={selectedRestaurant}
          isOpen={isPopupOpen}
          onClose={closePopup}
        />
      )}
    </div>
  );
}

export default Home;