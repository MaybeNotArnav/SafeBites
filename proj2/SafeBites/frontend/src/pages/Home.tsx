import { useState, useEffect, useCallback } from 'react';
import './Home.css';
import RestaurantMenu from './RestaurantMenu';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

interface Restaurant {
  _id: string;
  name: string;
  location: string;
  cuisine: string[];
  rating: number;
}

interface ActiveOrderItem {
  dish_id: string;
  name: string;
  quantity: number;
  price: number;
}

interface ActiveOrderRestaurant {
  restaurant_id?: string;
  restaurant_name?: string;
  item_total?: number;
}

interface ActiveOrder {
  _id: string;
  status: string;
  total: number;
  placed_at: string;
  estimated_arrival_time?: string;
  restaurants?: ActiveOrderRestaurant[];
  items?: ActiveOrderItem[];
  delivery_address?: string;
  special_instructions?: string;
}

function Home() {
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [filteredRestaurants, setFilteredRestaurants] = useState<Restaurant[]>([]);
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [sortBy, setSortBy] = useState<string>("none");
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);
  const [isPopupOpen, setIsPopupOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeOrders, setActiveOrders] = useState<ActiveOrder[]>([]);
  const [isLoadingOrders, setIsLoadingOrders] = useState(true);
  const [ordersError, setOrdersError] = useState<string | null>(null);
  const [selectedOrder, setSelectedOrder] = useState<ActiveOrder | null>(null);
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);

  // Fetch restaurants from API
  useEffect(() => {
    const fetchRestaurants = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await fetch(`${API_BASE_URL}/restaurants`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch restaurants: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Fetched restaurants:', data);
        
        setRestaurants(data);
        setFilteredRestaurants(data);
      } catch (err) {
        console.error('Error fetching restaurants:', err);
        setError(err instanceof Error ? err.message : 'Failed to load restaurants');
      } finally {
        setIsLoading(false);
      }
    };

    fetchRestaurants();
  }, []);

  // Apply sorting
  useEffect(() => {
    let next = [...restaurants];

    if (searchTerm.trim()) {
      const query = searchTerm.trim().toLowerCase();
      next = next.filter((restaurant) => {
        const matchesName = restaurant.name.toLowerCase().includes(query);
        const matchesCuisine = restaurant.cuisine.some((cuisine) => cuisine.toLowerCase().includes(query));
        const matchesLocation = restaurant.location.toLowerCase().includes(query);
        return matchesName || matchesCuisine || matchesLocation;
      });
    }

    if (sortBy === "name-asc") {
      next.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === "name-desc") {
      next.sort((a, b) => b.name.localeCompare(a.name));
    } else if (sortBy === "rating-desc") {
      next.sort((a, b) => b.rating - a.rating);
    } else if (sortBy === "rating-asc") {
      next.sort((a, b) => a.rating - b.rating);
    }

    setFilteredRestaurants(next);
  }, [sortBy, restaurants, searchTerm]);

  const fetchActiveOrders = useCallback(async () => {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
      setActiveOrders([]);
      setOrdersError(null);
      setIsLoadingOrders(false);
      return;
    }

    try {
      setIsLoadingOrders(true);
      setOrdersError(null);
      const response = await fetch(`${API_BASE_URL}/orders`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Unable to load active orders.');
      }

      const data: ActiveOrder[] = await response.json();
      const activeOnly = data.filter((order) => {
        const status = (order.status || '').toLowerCase();
        return status !== 'completed' && status !== 'cancelled';
      });
      setActiveOrders(activeOnly);
      setSelectedOrder((prev) => {
        if (!prev) {
          return prev;
        }
        const updated = activeOnly.find((order) => order._id === prev._id);
        if (!updated) {
          setIsOrderModalOpen(false);
          return null;
        }
        return updated;
      });
    } catch (err) {
      setOrdersError(err instanceof Error ? err.message : 'Unable to load active orders.');
    } finally {
      setIsLoadingOrders(false);
    }
  }, [API_BASE_URL]);

  useEffect(() => {
    fetchActiveOrders();
  }, [fetchActiveOrders]);

  useEffect(() => {
    const handleOrderPlaced = () => fetchActiveOrders();
    window.addEventListener('safebites:order-placed', handleOrderPlaced);
    return () => window.removeEventListener('safebites:order-placed', handleOrderPlaced);
  }, [fetchActiveOrders]);

  const formatCurrency = (value: number) => `$${value.toFixed(2)}`;
  const formatTime = (iso: string) =>
    new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString();
  const formatStatus = (status: string) =>
    status
      .replace(/_/g, ' ')
      .replace(/\b\w/g, (char) => char.toUpperCase());
  const openOrderDetail = (order: ActiveOrder) => {
    setSelectedOrder(order);
    setIsOrderModalOpen(true);
  };

  const closeOrderDetail = () => {
    setIsOrderModalOpen(false);
    setTimeout(() => setSelectedOrder(null), 150);
  };

  const handleOrderKeyOpen = (event: React.KeyboardEvent<HTMLDivElement>, order: ActiveOrder) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      openOrderDetail(order);
    }
  };

  const handleRestaurantClick = (restaurant: Restaurant) => {
    setSelectedRestaurant(restaurant);
    setIsPopupOpen(true);
  };

  const closePopup = () => {
    setIsPopupOpen(false);
    setTimeout(() => setSelectedRestaurant(null), 300);
  };

  return (
    <div className="home-container">
      <h1 className="page-title">Explore Restaurants</h1>

      <section className="active-orders-section">
        <div className="section-header">
          <div>
            <h2>Your Orders</h2>
            <p>Follow in-progress deliveries right from the dashboard.</p>
          </div>
        </div>

        {isLoadingOrders && <p className="active-orders-message">Loading active orders...</p>}
        {ordersError && !isLoadingOrders && (
          <p className="active-orders-message error">{ordersError}</p>
        )}

        {!isLoadingOrders && !ordersError && (
          activeOrders.length === 0 ? (
            <div className="active-orders-empty">No Active orders.</div>
          ) : (
            <div className="active-orders-list">
              {activeOrders.map((order) => (
                <div
                  key={order._id}
                  className="active-order-card"
                  role="button"
                  tabIndex={0}
                  aria-haspopup="dialog"
                  onClick={() => openOrderDetail(order)}
                  onKeyDown={(event) => handleOrderKeyOpen(event, order)}
                >
                  <div className="active-order-header">
                    <div>
                      <h3>Order #{order._id.slice(-6)}</h3>
                      <p className="active-order-meta">
                        Placed {formatDate(order.placed_at)} · {formatTime(order.placed_at)}
                      </p>
                    </div>
                    <span className={`order-status-badge ${(order.status || '').toLowerCase()}`}>
                      {formatStatus(order.status || 'Placed')}
                    </span>
                  </div>

                  <p className="active-order-restaurants">
                    {(order.restaurants || [])
                      .map((restaurant) => restaurant.restaurant_name || 'Restaurant')
                      .join(' · ')}
                  </p>

                  <div className="active-order-footer">
                    <span className="order-total-label">{formatCurrency(order.total)}</span>
                    {order.estimated_arrival_time && (
                      <span className="order-eta">ETA {formatTime(order.estimated_arrival_time)}</span>
                    )}
                  </div>
                  <p className="active-order-hint">Tap to view order details</p>
                </div>
              ))}
            </div>
          )
        )}
      </section>

      {/* Filter Section */}
      <div className="filter-section">
        <div className="home-search-bar">
          <input
            type="text"
            value={searchTerm}
            onChange={(event) => setSearchTerm(event.target.value)}
            placeholder="Search restaurants, cuisines, or locations"
          />
          {searchTerm && (
            <button
              type="button"
              className="clear-search-btn"
              onClick={() => setSearchTerm('')}
            >
              Clear
            </button>
          )}
        </div>
        <button
          className="filter-toggle-btn"
          onClick={() => setIsFilterOpen(!isFilterOpen)}
        >
          {isFilterOpen ? '▼' : '▶'} Sort & Filter
        </button>
      </div>

      {isFilterOpen && (
        <div className="filter-container">
          <div className="filter-group">
            <label className="filter-label">Sort by Name:</label>
            <div className="filter-options">
              <button 
                className={`filter-option-btn ${sortBy === "name-asc" ? 'active' : ''}`}
                onClick={() => setSortBy("name-asc")}
              >
                A → Z
              </button>
              <button 
                className={`filter-option-btn ${sortBy === "name-desc" ? 'active' : ''}`}
                onClick={() => setSortBy("name-desc")}
              >
                Z → A
              </button>
            </div>
          </div>

          <div className="filter-group">
            <label className="filter-label">Sort by Rating:</label>
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
            onClick={() => {
              setSortBy("none");
              setSearchTerm('');
            }}
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="loading-container">
          <p>Loading restaurants...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error-container">
          <p>Error: {error}</p>
          <p>Please try again later.</p>
        </div>
      )}

      {/* Restaurant Cards Grid */}
      {!isLoading && !error && (
        <div className="restaurant-grid">
          {filteredRestaurants.length === 0 ? (
            <p>No restaurants found.</p>
          ) : (
            filteredRestaurants.map((restaurant) => (
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
            ))
          )}
        </div>
      )}

      {/* Popup Modal */}
      {selectedRestaurant && (
        <RestaurantMenu 
          restaurant={selectedRestaurant}
          isOpen={isPopupOpen}
          onClose={closePopup}
        />
      )}

      {isOrderModalOpen && selectedOrder && (
        <div className="order-modal-overlay" onClick={closeOrderDetail}>
          <div className="order-modal" onClick={(event) => event.stopPropagation()}>
            <button className="order-modal-close" onClick={closeOrderDetail}>
              ✕
            </button>
            <div className="order-modal-header">
              <div>
                <p className="order-modal-label">Active Order</p>
                <h3>Order #{selectedOrder._id.slice(-6)}</h3>
                <p className="order-modal-meta">
                  Placed {formatDate(selectedOrder.placed_at)} · {formatTime(selectedOrder.placed_at)}
                </p>
              </div>
              <span className={`order-status-badge ${(selectedOrder.status || '').toLowerCase()}`}>
                {formatStatus(selectedOrder.status || 'Placed')}
              </span>
            </div>

            <div className="order-modal-summary">
              <div>
                <p>Total</p>
                <strong>{formatCurrency(selectedOrder.total)}</strong>
              </div>
              {selectedOrder.estimated_arrival_time && (
                <div>
                  <p>ETA</p>
                  <strong>{formatTime(selectedOrder.estimated_arrival_time)}</strong>
                </div>
              )}
            </div>

            {selectedOrder.restaurants && selectedOrder.restaurants.length > 0 && (
              <div className="order-modal-restaurants">
                <p className="order-modal-subtitle">Restaurants</p>
                {selectedOrder.restaurants.map((restaurant) => (
                  <div key={(restaurant.restaurant_id || '') + restaurant.restaurant_name} className="order-modal-restaurant-row">
                    <span>{restaurant.restaurant_name || 'Restaurant'}</span>
                    {typeof restaurant.item_total === 'number' && (
                      <strong>{formatCurrency(restaurant.item_total)}</strong>
                    )}
                  </div>
                ))}
              </div>
            )}

            <div className="order-modal-items">
              <p className="order-modal-subtitle">Items</p>
              {(selectedOrder.items || []).length === 0 ? (
                <p className="active-order-items-empty">No items found for this order.</p>
              ) : (
                (selectedOrder.items || []).map((item) => (
                  <div key={item.dish_id} className="order-modal-item-row">
                    <div>
                      <p className="order-modal-item-name">{item.name}</p>
                      <p className="order-modal-item-meta">Qty {item.quantity}</p>
                    </div>
                    <span className="order-modal-item-price">
                      {formatCurrency(item.price * item.quantity)}
                    </span>
                  </div>
                ))
              )}
            </div>

            {selectedOrder.delivery_address && (
              <div className="order-modal-note">
                <p className="order-modal-subtitle">Delivery</p>
                <p>{selectedOrder.delivery_address}</p>
              </div>
            )}

            {selectedOrder.special_instructions && (
              <div className="order-modal-note">
                <p className="order-modal-subtitle">Instructions</p>
                <p>{selectedOrder.special_instructions}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Home;