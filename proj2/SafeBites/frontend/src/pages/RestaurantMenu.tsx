import { useState } from 'react';
import './RestaurantMenu.css';

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

// Mock dish data - replace with API call later
const mockDishes: Dish[] = [
  {
    _id: "dish_1",
    restaurant_id: "rest_1",
    name: "Szechuan Beef",
    description: "Stir-fried Szechuan-style beef marinated with egg white and cornstarch, cooked with vegetables in soy and oyster sauces and finished with sesame oil.",
    price: 15.56,
    ingredients: ["Beef", "Salt", "Sesame Seed Oil", "Pepper", "Egg White", "Starch", "Oil", "Ginger", "Garlic", "Onion"],
    inferred_allergens: [
      { allergen: "egg", confidence: 0.99, why: "Egg white is used in the beef marinade." },
      { allergen: "soy", confidence: 0.99, why: "Soy sauce is listed among the ingredients." }
    ]
  },
  {
    _id: "dish_2",
    restaurant_id: "rest_1",
    name: "Prawn & Fennel Bisque",
    description: "A creamy seafood bisque of prawns and fennel simmered with aromatics, tomatoes, wine, and fish stock, finished with double cream.",
    price: 6.84,
    ingredients: ["Tiger Prawns", "Olive Oil", "Onion", "Fennel", "Carrots", "Dry White Wine"],
    inferred_allergens: [
      { allergen: "shellfish", confidence: 0.99, why: "Contains prawns (shellfish)." },
      { allergen: "dairy", confidence: 0.9, why: "Contains double cream." }
    ]
  },
  {
    _id: "dish_3",
    restaurant_id: "rest_1",
    name: "English Breakfast",
    description: "A hearty full English breakfast with sausages, bacon, eggs, black pudding, grilled mushrooms and tomatoes, and bread.",
    price: 17.79,
    ingredients: ["Sausages", "Bacon", "Mushrooms", "Tomatoes", "Black Pudding", "Eggs", "Bread"],
    inferred_allergens: [
      { allergen: "egg", confidence: 0.99, why: "Whole eggs are listed as an ingredient." }
    ]
  },
  {
    _id: "dish_4",
    restaurant_id: "rest_1",
    name: "Shawarma",
    description: "Yogurt-marinated, spice-rubbed chicken shawarma served in pita with lettuce and tomato.",
    price: 12.99,
    ingredients: ["Chicken Thighs", "Coriander", "Cumin", "Greek Yogurt", "Pita Bread"],
    inferred_allergens: [
      { allergen: "dairy", confidence: 0.99, why: "Contains Greek yogurt." }
    ]
  },
  {
    _id: "dish_5",
    restaurant_id: "rest_1",
    name: "Moussaka",
    description: "Greek-style baked casserole of beef, aubergine, tomato and potatoes topped with a yogurt-egg-parmesan layer.",
    price: 26.21,
    ingredients: ["Beef", "Aubergine", "Greek Yogurt", "Egg", "Parmesan", "Tomato"],
    inferred_allergens: [
      { allergen: "dairy", confidence: 0.98, why: "Contains yogurt and parmesan." }
    ]
  }
];

function RestaurantMenu({ restaurant, isOpen, onClose }: RestaurantMenuProps) {
  const [selectedDish, setSelectedDish] = useState<Dish | null>(null);
  const [isDishDetailOpen, setIsDishDetailOpen] = useState(false);

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

        {/* Dishes List */}
        <div className="dishes-list">
          {mockDishes.map((dish, index) => (
            <div 
              key={dish._id} 
              className={`dish-item ${index % 2 === 0 ? 'highlighted' : ''}`}
            >
              <div className="dish-header">
                <h4 className="dish-name">{dish.name}</h4>
                <span className="dish-price">${dish.price.toFixed(2)}</span>
              </div>
              
              <p className="dish-description">{dish.description}</p>
              
              <div className="dish-footer">
                <button 
                  className="ingredients-btn"
                  onClick={() => handleIngredientsClick(dish)}
                >
                  Ingredients
                </button>
                
                {dish.inferred_allergens && dish.inferred_allergens.length > 0 && (
                  <div className="allergen-badges">
                    {dish.inferred_allergens.slice(0, 3).map((allergen, idx) => (
                      <span key={idx} className="allergen-badge">
                        {allergen.allergen}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Dish Detail Popup */}
      {isDishDetailOpen && selectedDish && (
        <div 
          className="dish-detail-popup"
          onClick={(e) => e.stopPropagation()}
        >
          <button className="popup-close-btn" onClick={handleCloseDishDetail}>
            ✕
          </button>
          
          <h2 className="dish-detail-title">{selectedDish.name}</h2>
          <p className="wip-message">Work in progress</p>
        </div>
      )}
    </div>
  );
}

export default RestaurantMenu;