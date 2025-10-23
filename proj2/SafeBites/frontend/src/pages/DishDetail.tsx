import './DishDetail.css';

interface Allergen {
  allergen: string;
  confidence: number;
  why: string;
}

interface DishDetailProps {
  dish: {
    _id: string;
    name: string;
    description: string;
    price: number;
    ingredients: string[];
    inferred_allergens?: Allergen[];
  };
  isOpen: boolean;
  onClose: () => void;
}

function DishDetail({ dish, isOpen, onClose }: DishDetailProps) {
  if (!isOpen) return null;

  return (
    <div className="dish-detail-container">
      <button className="detail-close-btn" onClick={onClose}>
        ✕
      </button>

      <h2 className="detail-dish-name">{dish.name}</h2>
      <p className="detail-dish-price">${dish.price.toFixed(2)}</p>

      {/* Ingredients Section */}
      <div className="detail-section">
        <h3 className="section-title">Ingredients</h3>
        <div className="ingredients-grid">
          {dish.ingredients.map((ingredient, index) => (
            <span key={index} className="ingredient-chip">
              {ingredient}
            </span>
          ))}
        </div>
      </div>

      {/* Allergen Information Section */}
      {dish.inferred_allergens && dish.inferred_allergens.length > 0 && (
        <div className="detail-section">
          <h3 className="section-title allergen-title">
            ⚠️ Allergen Information
          </h3>
          <div className="allergens-list">
            {dish.inferred_allergens.map((allergen, index) => (
              <div key={index} className="allergen-item">
                <div className="allergen-header">
                  <span className="allergen-name">{allergen.allergen}</span>
                  <span className="allergen-confidence">
                    {(allergen.confidence * 100).toFixed(0)}% confidence
                  </span>
                </div>
                <p className="allergen-reason">{allergen.why}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* No Allergens Message */}
      {(!dish.inferred_allergens || dish.inferred_allergens.length === 0) && (
        <div className="detail-section">
          <div className="no-allergens-message">
            <span className="check-icon">✓</span>
            <p>No major allergens detected in this dish</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default DishDetail;