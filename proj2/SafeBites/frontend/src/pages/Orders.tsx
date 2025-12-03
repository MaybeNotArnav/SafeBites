import { useEffect, useState } from 'react';
import './Orders.css';

const API_BASE_URL = 'http://127.0.0.1:8000';

interface OrderItem {
  dish_id: string;
  restaurant_id?: string;
  restaurant_name?: string;
  name: string;
  price: number;
  quantity: number;
}

interface RestaurantSummary {
  restaurant_id?: string;
  restaurant_name?: string;
  item_count: number;
  item_total: number;
}

interface Order {
  _id: string;
  items: OrderItem[];
  restaurants?: RestaurantSummary[];
  subtotal: number;
  tax: number;
  fees: number;
  total: number;
  status: string;
  placed_at: string;
  payment_method?: string;
  delivery_address?: string;
}

function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const authToken = localStorage.getItem('authToken');

  useEffect(() => {
    const fetchOrders = async () => {
      if (!authToken) {
        setError('Please log in to view orders.');
        setIsLoading(false);
        return;
      }
      try {
        setError(null);
        const response = await fetch(`${API_BASE_URL}/orders`, {
          headers: {
            Authorization: `Bearer ${authToken}`,
          },
        });
        if (!response.ok) {
          throw new Error('Unable to fetch past orders.');
        }
        const data = await response.json();
        setOrders(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to fetch orders.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchOrders();
  }, [authToken]);

  const formatDate = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString();
  };

  return (
    <div className="orders-page">
      <div className="orders-header">
        <div>
          <h2>Past Orders</h2>
          <p>Track your previous purchases and reorder favorites.</p>
        </div>
        <img src="/icons/icons8-purchase-order-24.png" alt="Orders" />
      </div>

      {isLoading && <p>Loading orders...</p>}
      {error && <p className="orders-error">{error}</p>}

      {!isLoading && !error && (
        <div className="orders-list">
          {orders.length === 0 ? (
            <div className="orders-card empty">
              <p>No orders yet. Place your first order to see it here.</p>
            </div>
          ) : (
            orders.map((order) => (
              <div key={order._id} className="orders-card">
                <div className="orders-card-header">
                  <div>
                    <h3>Order #{order._id.slice(-6)}</h3>
                    <p className="order-date">Placed on {formatDate(order.placed_at)}</p>
                  </div>
                  <span className={`order-status ${order.status}`}>
                    {order.status.toUpperCase()}
                  </span>
                </div>

                {order.restaurants && order.restaurants.length > 0 && (
                  <div className="order-restaurant-groups">
                    {order.restaurants.map((restaurant) => (
                      <div key={(restaurant.restaurant_id || '') + restaurant.restaurant_name} className="order-restaurant-chip">
                        <p className="chip-label">Your order from</p>
                        <p className="chip-name">{restaurant.restaurant_name || 'Restaurant'}</p>
                        <span className="chip-amount">${restaurant.item_total.toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="order-items">
                  {order.items.map((item) => (
                    <div key={item.dish_id} className="order-item">
                      <div>
                        <p className="order-item-name">{item.name}</p>
                        <p className="order-item-qty">Qty: {item.quantity}</p>
                      </div>
                      <span>${(item.price * item.quantity).toFixed(2)}</span>
                    </div>
                  ))}
                </div>

                <div className="order-total">
                  <div>
                    <p>Subtotal: ${order.subtotal.toFixed(2)}</p>
                    <p>Tax & Fees: ${(order.tax + order.fees).toFixed(2)}</p>
                  </div>
                  <div className="order-total-amount">
                    Total: ${order.total.toFixed(2)}
                  </div>
                </div>

                {order.delivery_address && (
                  <p className="order-address">Delivery: {order.delivery_address}</p>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}

export default Orders;
