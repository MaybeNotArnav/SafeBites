import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { vi } from 'vitest';
import AddRestaurant from '../pages/AddRestaurant';

/**
 * STREAMLINED ADD RESTAURANT TESTS
 * 
 * 5 essential tests - focused on inputs, buttons, and CSV file
 * No time-based tests (API can be slow)
 */

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Mock fetch
global.fetch = vi.fn();

describe('AddRestaurant', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    window.alert = vi.fn();
    
    // Mock successful API response
    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ id: 1, message: 'Restaurant created' }),
    });
  });

  const renderComponent = () => {
    return render(
      <BrowserRouter>
        <AddRestaurant />
      </BrowserRouter>
    );
  };

  // ================================================================
  // FORM RENDERING - 1 Test
  // ================================================================

  test('renders form with all required fields', () => {
    renderComponent();
    
    expect(screen.getByLabelText(/Restaurant Name/i)).toBeInTheDocument();
    expect(screen.getByText(/Cuisine Type/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Street Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Restaurant Rating/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Menu CSV File/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Submit Restaurant/i })).toBeInTheDocument();
  });

  // ================================================================
  // INPUT FUNCTIONALITY - 2 Tests
  // ================================================================

  test('allows user to fill in all form fields', () => {
    renderComponent();
    
    const nameInput = screen.getByLabelText(/Restaurant Name/i);
    const streetInput = screen.getByLabelText(/Street Address/i);
    const cityInput = screen.getByLabelText(/City/i);
    const stateInput = screen.getByLabelText(/State/i);
    const zipInput = screen.getByLabelText(/ZIP Code/i);
    const ratingInput = screen.getByLabelText(/Restaurant Rating/i);
    
    fireEvent.change(nameInput, { target: { value: 'Test Restaurant' } });
    fireEvent.change(streetInput, { target: { value: '123 Main St' } });
    fireEvent.change(cityInput, { target: { value: 'Raleigh' } });
    fireEvent.change(stateInput, { target: { value: 'NC' } });
    fireEvent.change(zipInput, { target: { value: '27502' } });
    fireEvent.change(ratingInput, { target: { value: '4.5' } });
    
    expect(nameInput).toHaveValue('Test Restaurant');
    expect(streetInput).toHaveValue('123 Main St');
    expect(cityInput).toHaveValue('Raleigh');
    expect(stateInput).toHaveValue('NC');
    expect(zipInput).toHaveValue('27502');
    expect(ratingInput).toHaveValue(4.5);
  });

  test('allows user to select multiple cuisine types', () => {
    renderComponent();
    
    const italianBtn = screen.getByRole('button', { name: 'Italian' });
    const japaneseBtn = screen.getByRole('button', { name: 'Japanese' });
    const mexicanBtn = screen.getByRole('button', { name: 'Mexican' });
    
    // Select multiple cuisines
    fireEvent.click(italianBtn);
    fireEvent.click(japaneseBtn);
    fireEvent.click(mexicanBtn);
    
    expect(italianBtn).toHaveClass('selected');
    expect(japaneseBtn).toHaveClass('selected');
    expect(mexicanBtn).toHaveClass('selected');
    
    // Deselect one
    fireEvent.click(japaneseBtn);
    expect(japaneseBtn).not.toHaveClass('selected');
  });

  // ================================================================
  // FILE UPLOAD - 1 Test
  // ================================================================

  test('allows user to upload and remove CSV file', () => {
    renderComponent();
    
    // Upload file
    const file = new File(['menu,allergens\nPizza,dairy'], 'menu.csv', { type: 'text/csv' });
    const fileInput = screen.getByLabelText(/Menu CSV File/i) as HTMLInputElement;
    
    fireEvent.change(fileInput, { target: { files: [file] } });
    
    expect(screen.getByText('📄 menu.csv')).toBeInTheDocument();
    
    // Remove file
    const removeButton = screen.getByRole('button', { name: /Remove file/i });
    fireEvent.click(removeButton);
    
    expect(screen.queryByText('📄 menu.csv')).not.toBeInTheDocument();
  });

  // ================================================================
  // VALIDATION - 1 Test
  // ================================================================

  test('validates CSV file format', () => {
    renderComponent();
    
    // Try to upload non-CSV file
    const invalidFile = new File(['content'], 'menu.txt', { type: 'text/plain' });
    const fileInput = screen.getByLabelText(/Menu CSV File/i) as HTMLInputElement;
    
    fireEvent.change(fileInput, { target: { files: [invalidFile] } });
    
    expect(window.alert).toHaveBeenCalledWith('Please upload a CSV file');
  });
});