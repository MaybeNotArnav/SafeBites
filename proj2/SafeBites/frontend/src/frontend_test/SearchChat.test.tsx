import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import SearchChat from '../pages/SearchChat'

/**
 * STREAMLINED SEARCH CHAT TESTS
 * 
 * 9 essential tests - focused on critical functionality
 * API responses are mocked to avoid 4-5 minute wait times
 */

// Mock successful API response with dishes
const mockSuccessResponse = {
  menu_results: {
    "Show me pizza dishes": [
      {
        dish_id: "dish001",
        dish_name: "Margherita Pizza",
        description: "Classic pizza with tomato, mozzarella, and basil",
        price: 14.99,
        ingredients: ["tomato", "mozzarella", "basil"],
        allergens: ["Dairy", "Gluten"],
        nutrition_facts: {
          calories: { value: 800 },
          protein: { value: 30 }
        },
        serving_size: "12 inch",
        availaibility: true
      }
    ]
  },
  status: "success"
}

describe('SearchChat Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Reset fetch mock before each test
    global.fetch = vi.fn()
  })

  // ================================================================
  // RENDERING - 2 Essential Tests
  // ================================================================

  it('renders header with title and instructions', () => {
    render(<SearchChat />)
    
    expect(screen.getByText('Search Chat')).toBeInTheDocument()
    expect(screen.getByText('How to use:')).toBeInTheDocument()
    expect(screen.getByText(/Ask questions in natural language/i)).toBeInTheDocument()
  })

  it('shows empty state with example queries', () => {
    render(<SearchChat />)
    
    expect(screen.getByText('Start a Conversation')).toBeInTheDocument()
    expect(screen.getByText('Show me pizza dishes')).toBeInTheDocument()
    expect(screen.getByText('What dishes contain nuts?')).toBeInTheDocument()
  })

  // ================================================================
  // INPUT FUNCTIONALITY - 3 Essential Tests
  // ================================================================

  it('input accepts text', () => {
    render(<SearchChat />)
    
    const input = screen.getByPlaceholderText(/Ask about dishes/i) as HTMLTextAreaElement
    fireEvent.change(input, { target: { value: 'Show me pasta' } })
    
    expect(input.value).toBe('Show me pasta')
  })

  it('example query button fills input', () => {
    render(<SearchChat />)
    
    const exampleButton = screen.getByText('Show me pizza dishes')
    fireEvent.click(exampleButton)
    
    const input = screen.getByPlaceholderText(/Ask about dishes/i) as HTMLTextAreaElement
    expect(input.value).toBe('Show me pizza dishes')
  })

  it('send button is disabled when input is empty', () => {
    render(<SearchChat />)
    
    const sendButton = screen.getByRole('button', { name: /send/i })
    expect(sendButton).toBeDisabled()
  })

  // ================================================================
  // MESSAGING - 3 Essential Tests
  // ================================================================

  it('displays user message when sent', async () => {
    // Mock successful API response
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        text: async () => JSON.stringify(mockSuccessResponse),
      } as Response)
    )

    render(<SearchChat />)
    
    const input = screen.getByPlaceholderText(/Ask about dishes/i)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Show me pizza' } })
    fireEvent.click(sendButton)
    
    // User message should appear
    await waitFor(() => {
      expect(screen.getByText('Show me pizza')).toBeInTheDocument()
    })
  })

  it('displays assistant response with dish results', async () => {
    // Mock successful API response
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        text: async () => JSON.stringify(mockSuccessResponse),
      } as Response)
    )

    render(<SearchChat />)
    
    const input = screen.getByPlaceholderText(/Ask about dishes/i)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Show me pizza' } })
    fireEvent.click(sendButton)
    
    // Wait for assistant response
    await waitFor(() => {
      expect(screen.getByText(/I found 1 dish/i)).toBeInTheDocument()
    }, { timeout: 3000 })
    
    // Check dish details are displayed
    expect(screen.getByText('Margherita Pizza')).toBeInTheDocument()
    expect(screen.getByText('$14.99')).toBeInTheDocument()
  })

  it('displays dish card with allergens and nutrition', async () => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        status: 200,
        text: async () => JSON.stringify(mockSuccessResponse),
      } as Response)
    )

    render(<SearchChat />)
    
    const input = screen.getByPlaceholderText(/Ask about dishes/i)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Show me pizza' } })
    fireEvent.click(sendButton)
    
    await waitFor(() => {
      expect(screen.getByText('Margherita Pizza')).toBeInTheDocument()
    }, { timeout: 3000 })
    
    // Check allergens
    expect(screen.getByText('Dairy')).toBeInTheDocument()
    expect(screen.getByText('Gluten')).toBeInTheDocument()
    
    // Check nutrition
    expect(screen.getByText(/800 cal/i)).toBeInTheDocument()
    expect(screen.getByText(/30g protein/i)).toBeInTheDocument()
  })

  // ================================================================
  // STATES - 2 Essential Tests
  // ================================================================

  it('shows loading state while waiting for response', async () => {
    // Using a simple type assertion on vi.fn()
    global.fetch = vi.fn<typeof fetch>(() =>
    new Promise((resolve) =>
      setTimeout(() => {
        resolve({
          ok: true,
          status: 200,
          text: async () => JSON.stringify(mockSuccessResponse),
        } as Response);
      }, 100)
    )
  );

    render(<SearchChat />)
    
    const input = screen.getByPlaceholderText(/Ask about dishes/i)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Show me pizza' } })
    fireEvent.click(sendButton)
    
    // Loading indicator should appear
    expect(screen.getByText('Searching...')).toBeInTheDocument()
    
    // Wait for loading to finish
    await waitFor(() => {
      expect(screen.queryByText('Searching...')).not.toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('handles API error gracefully', async () => {
    // Mock error response
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: false,
        status: 500,
        text: async () => JSON.stringify({ error: 'Server error' }),
      } as Response)
    )

    render(<SearchChat />)
    
    const input = screen.getByPlaceholderText(/Ask about dishes/i)
    const sendButton = screen.getByRole('button', { name: /send/i })
    
    fireEvent.change(input, { target: { value: 'Show me pizza' } })
    fireEvent.click(sendButton)
    
    // Error message should appear
    await waitFor(() => {
      expect(screen.getByText(/encountered an error/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })
})