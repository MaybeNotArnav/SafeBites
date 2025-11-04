import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import Home from '../pages/Home'
import RestaurantMenu from '../pages/RestaurantMenu'
import DishDetail from '../pages/DishDetail'

/**
 * STREAMLINED COMPONENT TESTS
 * 
 * 20 essential tests - maximum focus, zero redundancy
 * Tests critical functionality only
 */

// ===== REALISTIC MOCK DATA =====

const mockRestaurants = [
  {
    "name": "Coleman, Knapp and SerranoTrattoria",
    "location": "08525 Campbell Villages Suite 625, East Amy, MT 85100",
    "cuisine": ["American"],
    "rating": 4.5,
    "_id": "68fa5a5e687f33d798c56f6d"
  },
  {
    "name": "Parks-JohnsonCafe",
    "location": "8012 Stephanie Mount, Lake Adrianville, OH 44373",
    "cuisine": ["Japanese"],
    "rating": 5.0,
    "_id": "68fa5d0237fee74eef3b30b8"
  },
  {
    "name": "Rodriguez-ShawKitchen",
    "location": "9256 Thompson Pike Suite 751, Newmanshire, AS 52518",
    "cuisine": ["Italian"],
    "rating": 1.2,
    "_id": "68fa5cbf0ebdbe5dc4ed5523"
  }
]

const mockDishes = [
  {
    "_id": "dish001",
    "restaurant_id": "68fa5a5e687f33d798c56f6d",
    "name": "Grilled Salmon",
    "description": "Fresh Atlantic salmon grilled to perfection",
    "price": 24.99,
    "ingredients": ["salmon", "butter", "lemon", "garlic"],
    "explicit_allergens": [
      { "allergen": "Fish" },
      { "allergen": "Dairy" }
    ],
    "inferred_allergens": [
      {
        "allergen": "Garlic",
        "confidence": 0.95,
        "why": "Contains garlic in ingredient list"
      }
    ],
    "nutrition_facts": {
      "calories": { "value": 450 },
      "protein": { "value": 35 }
    },
    "availaibility": true,
    "serving_size": "8 oz"
  },
  {
    "_id": "dish002",
    "restaurant_id": "68fa5a5e687f33d798c56f6d",
    "name": "Caesar Salad",
    "description": "Classic Caesar salad",
    "price": 12.50,
    "ingredients": ["romaine lettuce", "parmesan cheese"],
    "explicit_allergens": [
      { "allergen": "Dairy" }
    ],
    "availaibility": false
  }
]

describe('SafeBites - Streamlined Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    global.fetch = vi.fn((url: string) => {
      if (url.includes('/restaurants/')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => mockRestaurants
        } as Response)
      } else if (url.includes('/dishes/')) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => mockDishes
        } as Response)
      }
      return Promise.resolve({
        ok: false,
        status: 404,
        json: async () => ({})
      } as Response)
    }) as any
  })

  // ================================================================
  // HOME COMPONENT - 6 Essential Tests
  // ================================================================
  
  describe('Home Component', () => {
    it('renders restaurants with names, ratings, and cuisines', async () => {
      render(<Home />)
      
      await waitFor(() => {
        // Verify restaurants display
        expect(screen.getByText('Coleman, Knapp and SerranoTrattoria')).toBeInTheDocument()
        expect(screen.getByText('Parks-JohnsonCafe')).toBeInTheDocument()
        
        // Verify ratings
        expect(screen.getByText('4.5')).toBeInTheDocument()
        expect(screen.getByText('5.0')).toBeInTheDocument()
        
        // Verify cuisines
        expect(screen.getByText('American')).toBeInTheDocument()
        expect(screen.getByText('Japanese')).toBeInTheDocument()
      })
    })

    it('shows loading state initially', () => {
      render(<Home />)
      expect(screen.getByText(/loading/i)).toBeInTheDocument()
    })

    it('handles API error', async () => {
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          json: async () => ({})
        } as Response)
      )
      
      render(<Home />)
      
      await waitFor(() => {
        expect(screen.getByText(/failed to fetch restaurants/i)).toBeInTheDocument()
      })
    })

    it('shows empty state when no restaurants', async () => {
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: async () => []
        } as Response)
      )
      
      render(<Home />)
      
      await waitFor(() => {
        expect(screen.getByText(/no restaurants found/i)).toBeInTheDocument()
      })
    })

    it('toggles filter panel', async () => {
      render(<Home />)
      
      await waitFor(() => {
        expect(screen.getByText('Coleman, Knapp and SerranoTrattoria')).toBeInTheDocument()
      })
      
      const filterButton = screen.getByRole('button', { name: /sort & filter/i })
      fireEvent.click(filterButton)
      
      await waitFor(() => {
        expect(screen.getByText(/sort by rating/i)).toBeInTheDocument()
      })
    })

    it('sorts restaurants by rating', async () => {
      render(<Home />)
      
      await waitFor(() => {
        expect(screen.getByText('Parks-JohnsonCafe')).toBeInTheDocument()
      })
      
      const filterButton = screen.getByRole('button', { name: /sort & filter/i })
      fireEvent.click(filterButton)
      
      const sortButton = screen.getByText('Highest First')
      fireEvent.click(sortButton)
      
      await waitFor(() => {
        const restaurantCards = screen.getAllByRole('heading', { level: 2 })
        expect(restaurantCards[0]).toHaveTextContent('Parks-JohnsonCafe') // 5.0
        expect(restaurantCards[2]).toHaveTextContent('Rodriguez-ShawKitchen') // 1.2
      })
    })
  })

  // ================================================================
  // RESTAURANT MENU COMPONENT - 7 Essential Tests
  // ================================================================
  
  describe('RestaurantMenu Component', () => {
    const testRestaurant = mockRestaurants[0]

    it('renders menu with dishes and prices', async () => {
      render(
        <RestaurantMenu 
          restaurant={testRestaurant}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      await waitFor(() => {
        expect(screen.getByText('Coleman, Knapp and SerranoTrattoria')).toBeInTheDocument()
        expect(screen.getByText('Menu')).toBeInTheDocument()
        expect(screen.getByText('Grilled Salmon')).toBeInTheDocument()
        expect(screen.getByText('Caesar Salad')).toBeInTheDocument()
        expect(screen.getByText('$24.99')).toBeInTheDocument()
        expect(screen.getByText('$12.50')).toBeInTheDocument()
      })
    })

    it('shows availability status', async () => {
      render(
        <RestaurantMenu 
          restaurant={testRestaurant}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      await waitFor(() => {
        expect(screen.getByText(/✓ Available/i)).toBeInTheDocument()
        expect(screen.getByText(/✗ Unavailable/i)).toBeInTheDocument()
      })
    })

    it('shows loading state', () => {
      render(
        <RestaurantMenu 
          restaurant={testRestaurant}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      expect(screen.getByText(/loading menu/i)).toBeInTheDocument()
    })

    it('handles fetch error', async () => {
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 500,
          json: async () => ({})
        } as Response)
      )
      
      render(
        <RestaurantMenu 
          restaurant={testRestaurant}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      await waitFor(() => {
        expect(screen.getByText(/failed to fetch dishes/i)).toBeInTheDocument()
      })
    })

    it('shows empty state when no dishes', async () => {
      global.fetch = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: async () => []
        } as Response)
      )
      
      render(
        <RestaurantMenu 
          restaurant={testRestaurant}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      await waitFor(() => {
        expect(screen.getByText(/no dishes available/i)).toBeInTheDocument()
      })
    })

    it('displays allergen badges', async () => {
      render(
        <RestaurantMenu 
          restaurant={testRestaurant}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      await waitFor(() => {
        const allergenBadges = screen.getAllByText(/Fish|Dairy/i)
        expect(allergenBadges.length).toBeGreaterThan(0)
      })
    })

    it('closes when close button clicked', async () => {
      const mockOnClose = vi.fn()
      
      render(
        <RestaurantMenu 
          restaurant={testRestaurant}
          isOpen={true}
          onClose={mockOnClose}
        />
      )
      
      await waitFor(() => {
        expect(screen.getByText('Grilled Salmon')).toBeInTheDocument()
      })
      
      const closeButton = screen.getByRole('button', { name: '✕' })
      fireEvent.click(closeButton)
      
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  // ================================================================
  // DISH DETAIL COMPONENT - 6 Essential Tests
  // ================================================================
  
  describe('DishDetail Component', () => {
    const testDish = mockDishes[0]

    it('renders dish with all ingredients', () => {
      render(
        <DishDetail 
          dish={testDish}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      expect(screen.getByText('Grilled Salmon')).toBeInTheDocument()
      expect(screen.getByText('Ingredients')).toBeInTheDocument()
      
      testDish.ingredients.forEach(ingredient => {
        expect(screen.getByText(ingredient)).toBeInTheDocument()
      })
    })

    it('displays confirmed allergens', () => {
      render(
        <DishDetail 
          dish={testDish}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      expect(screen.getByText('Confirmed Allergens')).toBeInTheDocument()
      expect(screen.getByText('Fish')).toBeInTheDocument()
      expect(screen.getByText('Dairy')).toBeInTheDocument()
    })

    it('displays AI-detected allergens with confidence', () => {
      render(
        <DishDetail 
          dish={testDish}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      expect(screen.getByText('AI-Detected Allergens')).toBeInTheDocument()
      expect(screen.getByText('Garlic')).toBeInTheDocument()
      expect(screen.getByText(/95/i)).toBeInTheDocument()
    })

    it('displays nutrition facts', () => {
      render(
        <DishDetail 
          dish={testDish}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      expect(screen.getByText('Nutrition Facts')).toBeInTheDocument()
      expect(screen.getByText(/450/i)).toBeInTheDocument()
      expect(screen.getByText(/35/i)).toBeInTheDocument()
    })

    it('handles missing ingredients', () => {
      const dishNoIngredients = { ...testDish, ingredients: [] }
      
      render(
        <DishDetail 
          dish={dishNoIngredients}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      expect(screen.getByText(/no ingredient information available/i)).toBeInTheDocument()
    })

    it('closes when close button clicked', () => {
      const mockOnClose = vi.fn()
      
      render(
        <DishDetail 
          dish={testDish}
          isOpen={true}
          onClose={mockOnClose}
        />
      )
      
      const closeButton = screen.getByRole('button', { name: '✕' })
      fireEvent.click(closeButton)
      
      expect(mockOnClose).toHaveBeenCalledTimes(1)
    })
  })

  // ================================================================
  // INTEGRATION TEST - 1 Essential Test
  // ================================================================
  
  describe('Full User Flow', () => {
    it('complete navigation: restaurants → menu → dish details', async () => {
      const { rerender } = render(<Home />)
      
      // Step 1: Browse restaurants
      await waitFor(() => {
        expect(screen.getByText('Coleman, Knapp and SerranoTrattoria')).toBeInTheDocument()
      })
      
      // Step 2: View restaurant menu
      const restaurant = mockRestaurants[0]
      rerender(
        <RestaurantMenu 
          restaurant={restaurant}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      await waitFor(() => {
        expect(screen.getByText('Grilled Salmon')).toBeInTheDocument()
      })
      
      // Step 3: View dish details
      const dish = mockDishes[0]
      rerender(
        <DishDetail 
          dish={dish}
          isOpen={true}
          onClose={() => {}}
        />
      )
      
      // Verify complete dish information
      expect(screen.getByText('Grilled Salmon')).toBeInTheDocument()
      expect(screen.getByText('salmon')).toBeInTheDocument()
      expect(screen.getByText('Fish')).toBeInTheDocument()
      expect(screen.getByText(/450/i)).toBeInTheDocument()
    })
  })
})