import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../pages/Dashboard'

// Mock the useNavigate hook
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Mock fetch for Home component (it fetches restaurants)
beforeEach(() => {
  mockNavigate.mockClear()
  
  // Mock the restaurants API that Home component calls
  global.fetch = vi.fn(() =>
    Promise.resolve({
      ok: true,
      json: async () => ([
        {
          _id: '1',
          name: 'Test Restaurant',
          location: 'Test Location',
          cuisine: ['Test'],
          rating: 4.5
        }
      ])
    } as Response)
  )
})

describe('Dashboard Component', () => {
  // ===== HEADER TESTS =====
  
  it('renders the SafeBites logo and title', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    expect(screen.getByText('SafeBites')).toBeInTheDocument()
    expect(screen.getByAltText('SafeBites Logo')).toBeInTheDocument()
  })

  it('renders the profile button', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    expect(profileButton).toBeInTheDocument()
  })

  // ===== PROFILE DROPDOWN TESTS =====
  
  it('toggles profile dropdown when profile button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    
    // Initially closed
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument()
    
    // Click to open
    fireEvent.click(profileButton)
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('@johndoe')).toBeInTheDocument()
    
    // Click to close
    fireEvent.click(profileButton)
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument()
  })

  it('displays user information in profile dropdown', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    fireEvent.click(profileButton)
    
    expect(screen.getByText('John Doe')).toBeInTheDocument()
    expect(screen.getByText('@johndoe')).toBeInTheDocument()
  })

  it('displays logout button in profile dropdown', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    fireEvent.click(profileButton)
    
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  it('navigates to login page when logout is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const profileButton = screen.getByRole('button', { name: /profile/i })
    fireEvent.click(profileButton)
    
    const logoutButton = screen.getByRole('button', { name: /logout/i })
    fireEvent.click(logoutButton)
    
    expect(mockNavigate).toHaveBeenCalledWith('/login')
  })

  // ===== SIDEBAR TESTS =====
  
  it('renders sidebar with all navigation items', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    expect(screen.getByAltText('Home')).toBeInTheDocument()
    expect(screen.getByText('Search Chat')).toBeInTheDocument()
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('sidebar starts in open state', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const sidebar = document.querySelector('.sidebar')
    expect(sidebar).toHaveClass('open')
    expect(screen.getByText('✕')).toBeInTheDocument()
  })

  it('toggles sidebar open and closed', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const toggleButton = screen.getByText('✕')
    
    // Click to close
    fireEvent.click(toggleButton)
    
    // Sidebar should now show hamburger icon
    expect(screen.getByText('☰')).toBeInTheDocument()
    
    // Click to open again
    const hamburgerButton = screen.getByText('☰')
    fireEvent.click(hamburgerButton)
    
    // Should show close icon again
    expect(screen.getByText('✕')).toBeInTheDocument()
  })

  // ===== NAVIGATION/PAGE SWITCHING TESTS =====
  
  it('displays Home content by default', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    // Home component shows "Explore Restaurants" heading
    await waitFor(() => {
      expect(screen.getByText('Explore Restaurants')).toBeInTheDocument()
    })
  })

  it('navigates to Search Chat page when Search Chat button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const searchChatButton = screen.getByText('Search Chat')
    fireEvent.click(searchChatButton)
    
    // Check for the heading (more flexible)
  expect(screen.getByRole('heading', { name: /search chat/i })).toBeInTheDocument()
  })

  it('navigates to Settings page when Settings button is clicked', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const settingsButton = screen.getByText('Settings')
    fireEvent.click(settingsButton)
    
    // Settings component shows "Settings" heading
    expect(screen.getByRole('heading', { name: /settings/i })).toBeInTheDocument()
  })

  it('applies active class to current page button', async () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    // Home button should be active by default
    const homeButton = screen.getByAltText('Home').closest('button')
    expect(homeButton).toHaveClass('active')
  
    // Click Search Chat
    const searchChatButton = screen.getByText('Search Chat').closest('button')
    fireEvent.click(searchChatButton!)
  
    // Search Chat should now be active
    expect(searchChatButton).toHaveClass('active')
    // Home should no longer be active
    expect(homeButton).not.toHaveClass('active')
  })

  it('renders main content area', () => {
    render(
      <BrowserRouter>
        <Dashboard />
      </BrowserRouter>
    )
    
    const mainContent = screen.getByRole('main')
    expect(mainContent).toBeInTheDocument()
  })
})