import './DishDetail.css';

interface InferredAllergen {
  allergen: string;
  confidence: number;
  why: string;
}

interface ExplicitAllergen {
  allergen: string;
}

interface NutritionFacts {
  calories?: { value: number };
  protein?: { value: number };
  fat?: { value: number };
  carbohydrates?: { value: number };
  sugar?: { value: number };
  fiber?: { value: number };
}

interface Dish {
  _id: string;
  restaurant_id: string;
  name: string;
  description: string;
  price: number;
  ingredients: string[];
  inferred_allergens?: InferredAllergen[];
  explicit_allergens?: ExplicitAllergen[];
  nutrition_facts?: NutritionFacts;
  availaibility?: boolean;
  serving_size?: string;
}

interface DishDetailProps {
  dish: Dish;
  isOpen: boolean;
  onClose: () => void;
}

function DishDetail({ dish, isOpen, onClose }: DishDetailProps) {
  if (!isOpen) return null;

  // Group inferred allergens by confidence level for visual distinction
  const highConfidenceAllergens = dish.inferred_allergens?.filter(a => a.confidence >= 0.9) || [];
  const mediumConfidenceAllergens = dish.inferred_allergens?.filter(a => a.confidence >= 0.7 && a.confidence < 0.9) || [];
  const lowConfidenceAllergens = dish.inferred_allergens?.filter(a => a.confidence < 0.7) || [];

  return (
    <div 
      className="dish-detail-popup"
      onClick={(e) => e.stopPropagation()}
    >
      <button className="popup-close-btn" onClick={onClose}>
        ✕
      </button>
      
      <h2 className="dish-detail-title">{dish.name}</h2>
      
      {/* Ingredients Section */}
      <div className="detail-section">
        <h3 className="section-title">
          <span className="section-icon">🥗</span>
          Ingredients
        </h3>
        <div className="ingredients-grid">
          {dish.ingredients && dish.ingredients.length > 0 ? (
            dish.ingredients.map((ingredient, index) => (
              <span key={index} className="ingredient-chip">
                {ingredient}
              </span>
            ))
          ) : (
            <p className="no-data">No ingredient information available.</p>
          )}
        </div>
      </div>

      {/* Explicit Allergens Section */}
      {dish.explicit_allergens && dish.explicit_allergens.length > 0 && (
        <div className="detail-section">
          <h3 className="section-title">
            <span className="section-icon">⚠️</span>
            Confirmed Allergens
          </h3>
          <div className="explicit-allergens-container">
            {dish.explicit_allergens.map((allergen, index) => (
              <div key={index} className="explicit-allergen-card">
                <span className="explicit-allergen-name">{allergen.allergen}</span>
              </div>
            ))}
          </div>
          <p className="allergen-note">
            These allergens have been explicitly confirmed for this dish.
          </p>
        </div>
      )}

      {/* Inferred Allergen Information Section */}
      {dish.inferred_allergens && dish.inferred_allergens.length > 0 && (
        <div className="detail-section">
          <h3 className="section-title">
            <span className="section-icon">🔍</span>
            AI-Detected Allergens
          </h3>
          
          <div className="allergens-container">
            {/* High Confidence Allergens */}
            {highConfidenceAllergens.length > 0 && (
              <div className="allergen-group">
                <h4 className="allergen-confidence-label high">
                  High Confidence (90%+)
                </h4>
                {highConfidenceAllergens.map((allergen, index) => (
                  <div key={index} className="allergen-card high-confidence">
                    <div className="allergen-header">
                      <span className="allergen-name">{allergen.allergen}</span>
                      <span className="allergen-confidence">
                        {(allergen.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="allergen-reason">{allergen.why}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Medium Confidence Allergens */}
            {mediumConfidenceAllergens.length > 0 && (
              <div className="allergen-group">
                <h4 className="allergen-confidence-label medium">
                  Medium Confidence (70-89%)
                </h4>
                {mediumConfidenceAllergens.map((allergen, index) => (
                  <div key={index} className="allergen-card medium-confidence">
                    <div className="allergen-header">
                      <span className="allergen-name">{allergen.allergen}</span>
                      <span className="allergen-confidence">
                        {(allergen.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="allergen-reason">{allergen.why}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Low Confidence Allergens */}
            {lowConfidenceAllergens.length > 0 && (
              <div className="allergen-group">
                <h4 className="allergen-confidence-label low">
                  Low Confidence (&lt;70%)
                </h4>
                {lowConfidenceAllergens.map((allergen, index) => (
                  <div key={index} className="allergen-card low-confidence">
                    <div className="allergen-header">
                      <span className="allergen-name">{allergen.allergen}</span>
                      <span className="allergen-confidence">
                        {(allergen.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="allergen-reason">{allergen.why}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <p className="allergen-note">
            These allergens were detected using AI analysis of ingredients.
          </p>
        </div>
      )}

      {/* Show message if no allergen information at all */}
      {(!dish.explicit_allergens || dish.explicit_allergens.length === 0) && 
       (!dish.inferred_allergens || dish.inferred_allergens.length === 0) && (
        <div className="detail-section">
          <h3 className="section-title">
            <span className="section-icon">⚠️</span>
            Allergen Information
          </h3>
          <p className="no-data">No allergen information available for this dish.</p>
        </div>
      )}

      {/* Nutrition Facts Section */}
      {dish.nutrition_facts && (
        <div className="detail-section">
          <h3 className="section-title">
            <span className="section-icon">📊</span>
            Nutrition Facts
          </h3>
          <div className="nutrition-grid">
            {dish.nutrition_facts.calories && (
              <div className="nutrition-item">
                <span className="nutrition-label">Calories</span>
                <span className="nutrition-value">{dish.nutrition_facts.calories.value} kcal</span>
              </div>
            )}
            {dish.nutrition_facts.protein && (
              <div className="nutrition-item">
                <span className="nutrition-label">Protein</span>
                <span className="nutrition-value">{dish.nutrition_facts.protein.value}g</span>
              </div>
            )}
            {dish.nutrition_facts.fat && (
              <div className="nutrition-item">
                <span className="nutrition-label">Fat</span>
                <span className="nutrition-value">{dish.nutrition_facts.fat.value}g</span>
              </div>
            )}
            {dish.nutrition_facts.carbohydrates && (
              <div className="nutrition-item">
                <span className="nutrition-label">Carbohydrates</span>
                <span className="nutrition-value">{dish.nutrition_facts.carbohydrates.value}g</span>
              </div>
            )}
            {dish.nutrition_facts.sugar && (
              <div className="nutrition-item">
                <span className="nutrition-label">Sugar</span>
                <span className="nutrition-value">{dish.nutrition_facts.sugar.value}g</span>
              </div>
            )}
            {dish.nutrition_facts.fiber && (
              <div className="nutrition-item">
                <span className="nutrition-label">Fiber</span>
                <span className="nutrition-value">{dish.nutrition_facts.fiber.value}g</span>
              </div>
            )}
          </div>
          {!dish.nutrition_facts.calories && 
           !dish.nutrition_facts.protein && 
           !dish.nutrition_facts.fat && 
           !dish.nutrition_facts.carbohydrates && 
           !dish.nutrition_facts.sugar && 
           !dish.nutrition_facts.fiber && (
            <p className="no-data">No nutrition information available.</p>
          )}
        </div>
      )}

      {/* Disclaimer */}
      <div className="allergen-disclaimer">
        <p>
          <strong>Note:</strong> Allergen and nutrition information should be 
          used as a guide only. Please consult with restaurant staff if you have severe 
          allergies or specific dietary restrictions.
        </p>
      </div>
    </div>
  );
}

export default DishDetail;