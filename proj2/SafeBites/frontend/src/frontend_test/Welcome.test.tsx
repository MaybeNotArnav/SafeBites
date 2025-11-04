import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Welcome from '../pages/Welcome'

/**
 * STREAMLINED WELCOME TESTS
 * 
 * 8 essential tests - focused on critical functionality
 */

// Mock the useNavigate hook
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe('Welcome Component', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
  })

  // ================================================================
  // HEADER - 2 Essential Tests
  // ================================================================

  it('renders header with logo and sign up button', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('SafeBites')).toBeInTheDocument()
    expect(screen.getByAltText('SafeBites Logo')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument()
  })

  it('navigates to signup page when button clicked', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const signUpButton = screen.getByRole('button', { name: /sign up/i })
    fireEvent.click(signUpButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/signup')
  })

  // ================================================================
  // HERO SECTION - 2 Essential Tests
  // ================================================================

  it('renders hero section with search bar', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Find Restaurants Near You')).toBeInTheDocument()
    expect(screen.getByPlaceholderText(/enter street address or zip code/i)).toBeInTheDocument()
    expect(screen.getByAltText('Search')).toBeInTheDocument()
  })

  it('search input accepts user input', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const searchInput = screen.getByPlaceholderText(/enter street address or zip code/i) as HTMLInputElement
    fireEvent.change(searchInput, { target: { value: '27606' } })
    
    expect(searchInput.value).toBe('27606')
  })

  // ================================================================
  // FEATURES SECTION - 1 Essential Test
  // ================================================================

  it('renders all three feature cards with titles', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Eat Safely, Every Time')).toBeInTheDocument()
    expect(screen.getByText('Search Like You Talk')).toBeInTheDocument()
    expect(screen.getByText('Set It Once, Use It Forever')).toBeInTheDocument()
  })

  // ================================================================
  // ABOUT SECTION - 1 Essential Test
  // ================================================================

  it('renders about section with content', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('About SafeBites')).toBeInTheDocument()
    expect(screen.getByText(/dining out shouldn't be a guessing game/i)).toBeInTheDocument()
    expect(screen.getByText('Safe dining made simple.')).toBeInTheDocument()
  })

  // ================================================================
  // FOOTER - 2 Essential Tests
  // ================================================================

  it('renders footer with all sections and links', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    expect(screen.getByText('Get to know us')).toBeInTheDocument()
    expect(screen.getByText('Useful links')).toBeInTheDocument()
    expect(screen.getByText('Doing Business')).toBeInTheDocument()
    expect(screen.getByText('About Us')).toBeInTheDocument()
    expect(screen.getByText('Help')).toBeInTheDocument()
    expect(screen.getByText('© 2025 SafeBites - Group 6')).toBeInTheDocument()
  })

  it('navigates to add restaurant page when link clicked', () => {
    render(
      <BrowserRouter>
        <Welcome />
      </BrowserRouter>
    )
    
    const addRestaurantLink = screen.getByText('Add your restaurant')
    fireEvent.click(addRestaurantLink)
    
    expect(mockNavigate).toHaveBeenCalledWith('/add-restaurant')
  })
})