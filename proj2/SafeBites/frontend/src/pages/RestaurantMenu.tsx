import { useState, useEffect, useCallback } from 'react';
import './RestaurantMenu.css';
import DishDetail from './DishDetail';

const API_BASE_URL = 'http://127.0.0.1:8000';

const extractDishId = (value: unknown): string | null => {
  if (!value) {
    return null;
  }
  if (typeof value === 'string') {
    return value;
  }
  if (typeof value === 'object' && '$oid' in (value as Record<string, unknown>)) {
    const maybeOid = (value as { $oid?: unknown }).$oid;
    return typeof maybeOid === 'string' ? maybeOid : null;
  }
  try {
    return String(value);
  } catch (err) {
    console.error('Unable to normalize dish id', err);
    return null;
  }
};

interface Dish {
  _id: string;
  restaurant_id: string;
  name: string;
  description: string;
  price: number;
  ingredients: string[];
  inferred_allergens?: Array<{
    allergen: string;
    confidence: number;
    why: string;
  }>;
  explicit_allergens?: Array<{
    allergen: string;
  }>;
  nutrition_facts?: {
    calories?: { value: number };
    protein?: { value: number };
    fat?: { value: number };
    carbohydrates?: { value: number };
    sugar?: { value: number };
    fiber?: { value: number };
  };
  availaibility?: boolean; // Note: Using their spelling from the API
  serving_size?: string;
  safe_for_user?: boolean; // Safety indicator based on user's allergen preferences
}

interface RestaurantMenuProps {
  restaurant: {
    _id: string;
    name: string;
    location: string;
    cuisine: string[];
    rating: number;
  };
  isOpen: boolean;
  onClose: () => void;
}

function RestaurantMenu({ restaurant, isOpen, onClose }: RestaurantMenuProps) {
  const [dishes, setDishes] = useState<Dish[]>([]);
  const [selectedDish, setSelectedDish] = useState<Dish | null>(null);
  const [isDishDetailOpen, setIsDishDetailOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cartStatus, setCartStatus] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const [cartQuantities, setCartQuantities] = useState<Record<string, number>>({});

  const updateQuantitiesFromCart = useCallback((items: Array<{ dish_id?: unknown; quantity?: number }>) => {
    const mapping: Record<string, number> = {};
    items.forEach((item) => {
      const normalizedId = extractDishId(item?.dish_id);
      if (!normalizedId) {
        return;
      }
      const qty = typeof item?.quantity === 'number' ? item.quantity : 0;
      if (qty > 0) {
        mapping[normalizedId] = qty;
      }
    });
    setCartQuantities(mapping);
  }, []);

  // Fetch dishes for this restaurant
  useEffect(() => {
    if (isOpen && restaurant._id) {
      const fetchDishes = async () => {
        try {
          setIsLoading(true);
          setError(null);
          
          // Use the restaurant and user_id query parameters to filter dishes
          const userId = localStorage.getItem("authToken"); // Placeholder user ID
          const response = await fetch(`${API_BASE_URL}/dishes/?restaurant=${restaurant._id}&user_id=${userId}`);
          
          if (!response.ok) {
            throw new Error(`Failed to fetch dishes: ${response.status}`);
          }
          
          const data = await response.json();
          console.log('Fetched dishes:', data);
          
          setDishes(data);
        } catch (err) {
          console.error('Error fetching dishes:', err);
          setError(err instanceof Error ? err.message : 'Failed to load menu');
        } finally {
          setIsLoading(false);
        }
      };

      fetchDishes();
    }
  }, [isOpen, restaurant._id]);

  const fetchCartState = useCallback(async () => {
    const authToken = localStorage.getItem('authToken');
    if (!isOpen || !authToken) {
      setCartQuantities({});
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/cart`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Failed to load cart');
      }
      const data = await response.json();
      updateQuantitiesFromCart(data.items || []);
    } catch (err) {
      console.error('Failed to load cart state:', err);
      setCartQuantities({});
    }
  }, [isOpen, updateQuantitiesFromCart]);

  useEffect(() => {
    fetchCartState();
  }, [fetchCartState]);

  const handleAddToCart = async (dish: Dish) => {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
      setCartStatus({ type: 'error', message: 'Please log in to add dishes to your cart.' });
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/cart/items`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({ dish_id: dish._id, quantity: 1 }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Unable to add to cart.');
      }

      const data = await response.json();
      if (data?.items) {
        updateQuantitiesFromCart(data.items);
      } else {
        fetchCartState();
      }
      setCartStatus({ type: 'success', message: `${dish.name} added to cart.` });
    } catch (err) {
      setCartStatus({ type: 'error', message: err instanceof Error ? err.message : 'Unable to add to cart.' });
    } finally {
      setTimeout(() => setCartStatus(null), 4000);
    }
  };

  const handleUpdateQuantity = async (dishId: string, nextQuantity: number) => {
    const authToken = localStorage.getItem('authToken');
    if (!authToken) {
      setCartStatus({ type: 'error', message: 'Please log in to manage your cart.' });
      return;
    }
    try {
      let response: Response;
      if (nextQuantity <= 0) {
        response = await fetch(`${API_BASE_URL}/cart/items/${dishId}`, {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        });
      } else {
        response = await fetch(`${API_BASE_URL}/cart/items/${dishId}`, {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${authToken}`,
          },
          body: JSON.stringify({ quantity: nextQuantity }),
        });
      }

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Unable to update cart.');
      }

      const data = await response.json();
      if (data?.items) {
        updateQuantitiesFromCart(data.items);
      } else {
        fetchCartState();
      }
      setCartStatus({ type: 'success', message: 'Cart updated.' });
    } catch (err) {
      setCartStatus({ type: 'error', message: err instanceof Error ? err.message : 'Unable to update cart.' });
    } finally {
      setTimeout(() => setCartStatus(null), 4000);
    }
  };

  if (!isOpen) return null;

  const handleIngredientsClick = (dish: Dish) => {
    setSelectedDish(dish);
    setIsDishDetailOpen(true);
  };

  const handleCloseDishDetail = () => {
    setIsDishDetailOpen(false);
    setTimeout(() => setSelectedDish(null), 300); // Wait for animation
  };

  return (
    <div className="popup-overlay" onClick={onClose}>
      <div 
        className={`menu-popup-content ${isDishDetailOpen ? 'slide-left' : ''}`}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="popup-close-btn" onClick={onClose}>
          ✕
        </button>
        
        {/* Restaurant Header */}
        <h2 className="restaurant-title">{restaurant.name}</h2>
        <h3 className="menu-title">Menu</h3>
        <hr className="menu-divider" />

        {/* Loading State */}
        {isLoading && (
          <div className="menu-loading">
            <p>Loading menu...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="menu-error">
            <p>Error: {error}</p>
            <p>Unable to load menu items.</p>
          </div>
        )}

        {cartStatus && (
          <div className={`cart-status ${cartStatus.type}`}>
            {cartStatus.message}
          </div>
        )}

        {/* Dishes List */}
        {!isLoading && !error && (
          <div className="dishes-list">
            {dishes.length === 0 ? (
              <p className="no-dishes">No dishes available for this restaurant yet.</p>
            ) : (
              dishes.map((dish, index) => (
                <div 
                  key={dish._id} 
                  className={`dish-item ${index % 2 === 0 ? 'highlighted' : ''} ${
                    dish.safe_for_user !== undefined 
                      ? dish.safe_for_user 
                        ? 'dish-safe' 
                        : 'dish-unsafe' 
                      : ''
                  }`}
                >
                  <div className="dish-header">
                    <div className="dish-title-container">
                      <h4 className="dish-name">{dish.name}</h4>
                      {/* Safety Badge */}
                      {dish.safe_for_user !== undefined && (
                        <span className={`safety-badge ${dish.safe_for_user ? 'safe' : 'unsafe'}`}>
                          {dish.safe_for_user ? '✓ Safe for You' : '⚠ May Contain Allergens'}
                        </span>
                      )}
                    </div>
                    <div className="dish-header-right">
                      <span className="dish-price">${dish.price.toFixed(2)}</span>
                      {/* Availability Badge */}
                      {dish.availaibility !== undefined && (
                        <span className={`availability-badge ${dish.availaibility ? 'available' : 'unavailable'}`}>
                          {dish.availaibility ? '✓ Available' : '✗ Unavailable'}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <p className="dish-description">{dish.description}</p>
                  
                  {/* Serving Size */}
                  {dish.serving_size && (
                    <div className="serving-size">
                      <span className="serving-icon">🍽️</span>
                      <span className="serving-text">Serving: {dish.serving_size}</span>
                    </div>
                  )}
                  
                  <div className="dish-footer">
                    <div className="dish-actions">
                      <button 
                        className="ingredients-btn"
                        onClick={() => handleIngredientsClick(dish)}
                      >
                        Ingredients & Details
                      </button>
                      {cartQuantities[dish._id] && cartQuantities[dish._id] > 0 ? (
                        <div className="inline-quantity">
                          <button
                            className="qty-btn"
                            onClick={() => handleUpdateQuantity(dish._id, cartQuantities[dish._id] - 1)}
                          >
                            -
                          </button>
                          <span>{cartQuantities[dish._id]}</span>
                          <button
                            className="qty-btn"
                            onClick={() => handleUpdateQuantity(dish._id, cartQuantities[dish._id] + 1)}
                          >
                            +
                          </button>
                        </div>
                      ) : (
                        <button
                          className="add-cart-btn"
                          onClick={() => handleAddToCart(dish)}
                        >
                          Add to Cart
                        </button>
                      )}
                    </div>
                    
                    {/* Show explicit allergens or inferred allergens */}
                    {((dish.explicit_allergens && dish.explicit_allergens.length > 0) || 
                      (dish.inferred_allergens && dish.inferred_allergens.length > 0)) && (
                      <div className="allergen-badges">
                        {dish.explicit_allergens && dish.explicit_allergens.length > 0 ? (
                          // Show explicit allergens
                          dish.explicit_allergens.slice(0, 3).map((allergen, idx) => (
                            <span key={idx} className="allergen-badge explicit">
                              {allergen.allergen}
                            </span>
                          ))
                        ) : (
                          // Fall back to inferred allergens
                          dish.inferred_allergens?.slice(0, 3).map((allergen, idx) => (
                            <span key={idx} className="allergen-badge inferred">
                              {allergen.allergen}
                            </span>
                          ))
                        )}
                        {/* Show count if there are more allergens */}
                        {((dish.explicit_allergens?.length || 0) + (dish.inferred_allergens?.length || 0)) > 3 && (
                          <span className="allergen-badge more">
                            +{((dish.explicit_allergens?.length || 0) + (dish.inferred_allergens?.length || 0)) - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>

      {/* Dish Detail Component */}
      {isDishDetailOpen && selectedDish && (
        <DishDetail 
          dish={selectedDish}
          isOpen={isDishDetailOpen}
          onClose={handleCloseDishDetail}
        />
      )}
    </div>
  );
}

export default RestaurantMenu;