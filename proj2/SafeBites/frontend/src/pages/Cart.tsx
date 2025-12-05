import { useEffect, useMemo, useState } from 'react';
import './Cart.css';

const API_BASE_URL = 'http://127.0.0.1:8000';

interface CartItem {
  dish_id: string;
  restaurant_id?: string;
  restaurant_name?: string;
  name: string;
  price: number;
  quantity: number;
  description?: string;
  ingredients: string[];
}

interface CartResponse {
  _id: string;
  user_id: string;
  items: CartItem[];
  subtotal: number;
  updated_at: string;
}

interface CheckoutForm {
  deliveryAddress: string;
  paymentMethod: string;
  specialInstructions: string;
}

interface GroupedCartItems {
  restaurantId?: string;
  restaurantName: string;
  items: CartItem[];
  subtotal: number;
}

function Cart() {
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<CheckoutForm>({
    deliveryAddress: '',
    paymentMethod: 'card',
    specialInstructions: '',
  });
  const [checkoutMessage, setCheckoutMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const authToken = localStorage.getItem('authToken');

  useEffect(() => {
    if (!authToken) {
      setError('Please log in to view your cart.');
      setIsLoading(false);
      return;
    }
    fetchCart();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authToken]);

  const fetchCart = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/cart`, {
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load cart.');
      }

      const data: CartResponse = await response.json();
      setCart(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to load cart.');
    } finally {
      setIsLoading(false);
    }
  };

  const updateQuantity = async (dishId: string, quantity: number) => {
    if (!authToken) return;
    try {
      const response = await fetch(`${API_BASE_URL}/cart/items/${dishId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({ quantity }),
      });
      if (!response.ok) {
        throw new Error('Unable to update quantity.');
      }
      const data = await response.json();
      setError(null);
      setCart(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to update quantity.');
    }
  };

  const removeItem = async (dishId: string) => {
    if (!authToken) return;
    try {
      const response = await fetch(`${API_BASE_URL}/cart/items/${dishId}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${authToken}`,
        },
      });
      if (!response.ok) {
        throw new Error('Unable to remove item.');
      }
      const data = await response.json();
      setError(null);
      setCart(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to remove item.');
    }
  };

  const handleCheckout = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!authToken || !cart || cart.items.length === 0) return;

    try {
      setIsSubmitting(true);
      setCheckoutMessage(null);
      const response = await fetch(`${API_BASE_URL}/orders/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          payment_method: form.paymentMethod,
          delivery_address: form.deliveryAddress,
          special_instructions: form.specialInstructions,
        }),
      });

      if (!response.ok) {
        const message = await response.text();
        throw new Error(message || 'Checkout failed.');
      }

      const order = await response.json();
      window.dispatchEvent(new CustomEvent('safebites:order-placed', { detail: order }));
      setCheckoutMessage(`Order #${order._id} placed successfully!`);
      setForm({ deliveryAddress: '', paymentMethod: 'card', specialInstructions: '' });
      await fetchCart();
    } catch (err) {
      setCheckoutMessage(err instanceof Error ? err.message : 'Checkout failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const estimatedTax = cart ? Math.round(cart.subtotal * 0.08 * 100) / 100 : 0;
  const serviceFee = cart && cart.subtotal > 0 ? 2.5 : 0;
  const total = cart ? Math.round((cart.subtotal + estimatedTax + serviceFee) * 100) / 100 : 0;

  const groupedCart = useMemo<GroupedCartItems[]>(() => {
    if (!cart) return [];
    const groups = new Map<string, GroupedCartItems>();

    (cart.items || []).forEach((item) => {
      const key = item.restaurant_id || item.restaurant_name || 'restaurant';
      const group = groups.get(key) || {
        restaurantId: item.restaurant_id,
        restaurantName: item.restaurant_name || 'Restaurant',
        items: [],
        subtotal: 0,
      };
      group.items.push(item);
      group.subtotal += item.price * item.quantity;
      groups.set(key, group);
    });

    return Array.from(groups.values());
  }, [cart]);

  if (!authToken) {
    return (
      <div className="cart-page">
        <div className="cart-card empty">
          <p>Please log in to manage your cart.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="cart-page">
      <div className="cart-header">
        <div>
          <h2>Your Cart</h2>
          <p>Review dishes and proceed to checkout.</p>
        </div>
        <img src="/icons/icons8-shopping-cart-24.png" alt="Cart" />
      </div>

      {checkoutMessage && (
        <div className="checkout-message">
          {checkoutMessage}
        </div>
      )}

      {isLoading && <p>Loading cart...</p>}
      {error && <p className="cart-error">{error}</p>}

      {!isLoading && cart && (
        <div className="cart-content">
          <div className="cart-items">
            {groupedCart.length === 0 ? (
              <div className="cart-card empty">
                <p>Your cart is empty. Explore the menu to add dishes.</p>
              </div>
            ) : (
              groupedCart.map((group) => (
                <div key={group.restaurantId || group.restaurantName} className="cart-card restaurant-card">
                  <div className="restaurant-card-header">
                    <div>
                      <p className="restaurant-label">Your order from</p>
                      <h3>{group.restaurantName}</h3>
                    </div>
                    <span className="restaurant-subtotal">${group.subtotal.toFixed(2)}</span>
                  </div>
                  <div className="restaurant-items">
                    {group.items.map((item) => (
                      <div key={item.dish_id} className="cart-item">
                        <div className="cart-item-header">
                          <div>
                            <h4>{item.name}</h4>
                            <p className="cart-item-description">{item.description || 'No description available.'}</p>
                          </div>
                          <span className="cart-item-price">${item.price.toFixed(2)}</span>
                        </div>
                        <div className="cart-item-footer">
                          <div className="quantity-controls">
                            <button onClick={() => updateQuantity(item.dish_id, item.quantity - 1)}>-</button>
                            <span>{item.quantity}</span>
                            <button onClick={() => updateQuantity(item.dish_id, item.quantity + 1)}>+</button>
                          </div>
                          <span className="cart-item-total">${(item.price * item.quantity).toFixed(2)}</span>
                          <button className="remove-btn" onClick={() => removeItem(item.dish_id)}>
                            Remove
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>

          <div className="checkout-panel">
            <div className="summary-card">
              <h3>Order Summary</h3>
              <div className="summary-row">
                <span>Subtotal</span>
                <span>${cart.subtotal.toFixed(2)}</span>
              </div>
              <div className="summary-row">
                <span>Estimated Tax</span>
                <span>${estimatedTax.toFixed(2)}</span>
              </div>
              <div className="summary-row">
                <span>Service Fee</span>
                <span>${serviceFee.toFixed(2)}</span>
              </div>
              <div className="summary-row total">
                <span>Total</span>
                <span>${total.toFixed(2)}</span>
              </div>
            </div>

            <form className="checkout-form" onSubmit={handleCheckout}>
              <label>
                Delivery Address
                <textarea
                  value={form.deliveryAddress}
                  onChange={(e) => setForm((prev) => ({ ...prev, deliveryAddress: e.target.value }))}
                  placeholder="Enter delivery address"
                />
              </label>

              <label>
                Payment Method
                <select
                  value={form.paymentMethod}
                  onChange={(e) => setForm((prev) => ({ ...prev, paymentMethod: e.target.value }))}
                >
                  <option value="card">Card</option>
                  <option value="cash">Cash on Delivery</option>
                </select>
              </label>

              <label>
                Special Instructions
                <textarea
                  value={form.specialInstructions}
                  onChange={(e) => setForm((prev) => ({ ...prev, specialInstructions: e.target.value }))}
                  placeholder="Add notes for the kitchen or courier"
                />
              </label>

              <button type="submit" className="checkout-btn" disabled={isSubmitting || !cart.items.length}>
                {isSubmitting ? 'Placing Order...' : 'Place Order'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Cart;
