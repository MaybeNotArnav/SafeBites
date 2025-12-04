import { ChangeEvent, FormEvent, useEffect, useState } from 'react';
import './AdminAnalytics.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

interface AnalyticsTotals {
  orders: number;
  revenue: number;
  customers: number;
  restaurants: number;
}

interface RestaurantInsight {
  restaurant_id?: string;
  restaurant_name: string;
  order_count: number;
  items_sold: number;
  revenue: number;
}

interface OrdersPerDay {
  date: string;
  orders: number;
  revenue: number;
}

interface TopDish {
  dish_id?: string;
  name: string;
  restaurant_name?: string;
  quantity: number;
  revenue: number;
}

interface TopAllergen {
  name: string;
  count: number;
}

interface TopCustomer {
  user_id: string;
  name: string;
  orders: number;
  lifetime_value: number;
  last_order?: string | null;
  allergen_preferences: string[];
}

interface AllergenWatchlist {
  flagged_orders: number;
  impacted_customers: number;
  top_allergens: TopAllergen[];
}

interface CustomerHealth {
  repeat_customers: number;
  new_customers: number;
  avg_orders_per_customer: number;
  avg_order_value: number;
  top_customers: TopCustomer[];
  allergen_watchlist: AllergenWatchlist;
}

interface MenuStats {
  unique_dishes: number;
  total_items_sold: number;
  avg_items_per_order: number;
  allergen_free_rate: number;
}

interface MenuPerformance {
  best_sellers: TopDish[];
  slow_movers: TopDish[];
  stats: MenuStats;
}

interface FiltersState {
  startDate: string;
  endDate: string;
  restaurantId: string;
}

interface AnalyticsResponse {
  generated_at: string;
  totals: AnalyticsTotals;
  restaurants: RestaurantInsight[];
  orders_per_day: OrdersPerDay[];
  top_dishes: TopDish[];
  customer_health: CustomerHealth;
  menu_performance: MenuPerformance;
}

function AdminAnalytics() {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<FiltersState>({ startDate: '', endDate: '', restaurantId: '' });
  const [draftFilters, setDraftFilters] = useState<FiltersState>(filters);
  const [restaurantOptions, setRestaurantOptions] = useState<RestaurantInsight[]>([]);

  useEffect(() => {
    const fetchAnalytics = async () => {
      const token = localStorage.getItem('authToken');
      if (!token) {
        setError('Please log in as an admin to view analytics.');
        setIsLoading(false);
        return;
      }
      try {
        setError(null);
        setIsLoading(true);
        const params = new URLSearchParams();
        if (filters.startDate) params.append('start_date', filters.startDate);
        if (filters.endDate) params.append('end_date', filters.endDate);
        if (filters.restaurantId) params.append('restaurant_id', filters.restaurantId);
        const query = params.toString();
        const response = await fetch(`${API_BASE_URL}/admin/analytics${query ? `?${query}` : ''}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.status === 403 || response.status === 401) {
          throw new Error('Admin access required.');
        }
        if (!response.ok) {
          const message = await response.text();
          throw new Error(message || 'Unable to load analytics.');
        }
        const data: AnalyticsResponse = await response.json();
        setAnalytics(data);
        setRestaurantOptions((prev) => {
          const merged = new Map<string, RestaurantInsight>();
          [...prev, ...data.restaurants].forEach((rest) => {
            const key = rest.restaurant_id || rest.restaurant_name;
            if (!merged.has(key)) {
              merged.set(key, rest);
            }
          });
          return Array.from(merged.values());
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unable to load analytics.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAnalytics();
  }, [filters]);

  const formatCurrency = (value: number) => {
    return `$${value.toFixed(2)}`;
  };

  const handleDraftChange = (event: ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = event.target;
    setDraftFilters((prev) => ({ ...prev, [name]: value }));
  };

  const applyFilters = (event: FormEvent) => {
    event.preventDefault();
    setFilters({ ...draftFilters });
  };

  const resetFilters = () => {
    const cleared = { startDate: '', endDate: '', restaurantId: '' };
    setDraftFilters(cleared);
    setFilters(cleared);
  };

  return (
    <div className="admin-analytics-page">
      <div className="page-header">
        <div>
          <h2>Admin Analytics Dashboard</h2>
          <p>Track platform-wide restaurant and order performance.</p>
        </div>
        <img src="/icons/icons8-receipt-dollar-24.png" alt="Analytics" />
      </div>

      <form className="analytics-filters" onSubmit={applyFilters}>
        <div className="filter-group">
          <label htmlFor="start-date">Start date</label>
          <input
            id="start-date"
            type="date"
            name="startDate"
            value={draftFilters.startDate}
            onChange={handleDraftChange}
          />
        </div>
        <div className="filter-group">
          <label htmlFor="end-date">End date</label>
          <input
            id="end-date"
            type="date"
            name="endDate"
            value={draftFilters.endDate}
            onChange={handleDraftChange}
          />
        </div>
        <div className="filter-group">
          <label htmlFor="restaurant-filter">Restaurant</label>
          <select
            id="restaurant-filter"
            name="restaurantId"
            value={draftFilters.restaurantId}
            onChange={handleDraftChange}
          >
            <option value="">All restaurants</option>
            {restaurantOptions.map((rest) => (
              <option key={rest.restaurant_id || rest.restaurant_name} value={rest.restaurant_id || rest.restaurant_name}>
                {rest.restaurant_name}
              </option>
            ))}
          </select>
        </div>
        <div className="filter-actions">
          <button type="submit">Apply filters</button>
          <button type="button" onClick={resetFilters} className="ghost">
            Reset
          </button>
        </div>
      </form>

      {isLoading && <p>Loading analytics...</p>}
      {error && <p className="analytics-error">{error}</p>}

      {!isLoading && !error && analytics && (
        <div className="analytics-content">
          <div className="summary-cards">
            <div className="summary-card">
              <p>Total Orders</p>
              <h3>{analytics.totals.orders}</h3>
            </div>
            <div className="summary-card">
              <p>Total Revenue</p>
              <h3>{formatCurrency(analytics.totals.revenue)}</h3>
            </div>
            <div className="summary-card">
              <p>Unique Customers</p>
              <h3>{analytics.totals.customers}</h3>
            </div>
            <div className="summary-card">
              <p>Active Restaurants</p>
              <h3>{analytics.totals.restaurants}</h3>
            </div>
          </div>

          <div className="analytics-grid">
            <div className="analytics-panel">
              <div className="panel-header">
                <h4>Orders Trend</h4>
                <span>Last {analytics.orders_per_day.length} days</span>
              </div>
              <div className="orders-trend">
                {analytics.orders_per_day.length === 0 ? (
                  <p className="empty-state">No orders yet.</p>
                ) : (
                  analytics.orders_per_day.map((day) => (
                    <div key={day.date} className="trend-row">
                      <div>
                        <p className="trend-date">{day.date}</p>
                        <p className="trend-orders">{day.orders} orders</p>
                      </div>
                      <span className="trend-revenue">{formatCurrency(day.revenue)}</span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="analytics-panel">
              <div className="panel-header">
                <h4>Top Dishes</h4>
                <span>By quantity sold</span>
              </div>
              <div className="top-dishes">
                {analytics.top_dishes.length === 0 ? (
                  <p className="empty-state">No dish data yet.</p>
                ) : (
                  analytics.top_dishes.map((dish, index) => (
                    <div key={dish.dish_id || dish.name} className="dish-row">
                      <div className="dish-rank">{index + 1}</div>
                      <div>
                        <p className="dish-name">{dish.name}</p>
                        <p className="dish-meta">{dish.restaurant_name || 'Restaurant'}</p>
                      </div>
                      <div className="dish-stats">
                        <span>{dish.quantity} sold</span>
                        <strong>{formatCurrency(dish.revenue)}</strong>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="analytics-panel">
              <div className="panel-header">
                <h4>Customer Health Signals</h4>
                <span>Loyalty and spending overview</span>
              </div>
              <div className="customer-metrics">
                <div className="metric-pill">
                  <p>Repeat Customers</p>
                  <strong>{analytics.customer_health.repeat_customers}</strong>
                </div>
                <div className="metric-pill">
                  <p>New Customers</p>
                  <strong>{analytics.customer_health.new_customers}</strong>
                </div>
                <div className="metric-pill">
                  <p>Avg. Orders / Customer</p>
                  <strong>{analytics.customer_health.avg_orders_per_customer}</strong>
                </div>
                <div className="metric-pill">
                  <p>Avg. Order Value</p>
                  <strong>{formatCurrency(analytics.customer_health.avg_order_value)}</strong>
                </div>
              </div>
              <div className="top-customers">
                <h5>Top Lifetime Customers</h5>
                {analytics.customer_health.top_customers.length === 0 ? (
                  <p className="empty-state">No customer data yet.</p>
                ) : (
                  analytics.customer_health.top_customers.map((customer) => (
                    <div key={customer.user_id} className="customer-row">
                      <div>
                        <p className="customer-name">{customer.name}</p>
                        <p className="customer-meta">
                          {customer.orders} orders · {formatCurrency(customer.lifetime_value)} lifetime spend
                        </p>
                        {customer.allergen_preferences.length > 0 && (
                          <p className="customer-allergens">
                            Avoids: {customer.allergen_preferences.join(', ')}
                          </p>
                        )}
                      </div>
                      <span className="customer-last-order">
                        {customer.last_order ? new Date(customer.last_order).toLocaleDateString() : '—'}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="analytics-panel">
              <div className="panel-header">
                <h4>Allergen Watchlist</h4>
                <span>Orders flagged against preferences</span>
              </div>
              <div className="watchlist-metrics">
                <div>
                  <p>Flagged Orders</p>
                  <strong>{analytics.customer_health.allergen_watchlist.flagged_orders}</strong>
                </div>
                <div>
                  <p>Impacted Customers</p>
                  <strong>{analytics.customer_health.allergen_watchlist.impacted_customers}</strong>
                </div>
              </div>
              <div className="top-allergens">
                <h5>Top Allergens Detected</h5>
                {analytics.customer_health.allergen_watchlist.top_allergens.length === 0 ? (
                  <p className="empty-state">No allergen data yet.</p>
                ) : (
                  analytics.customer_health.allergen_watchlist.top_allergens.map((allergen) => (
                    <div key={allergen.name} className="allergen-row">
                      <span>{allergen.name}</span>
                      <strong>{allergen.count} mentions</strong>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="analytics-panel full-width">
            <div className="panel-header">
              <h4>Menu Performance</h4>
              <span>Selling velocity & allergen safety</span>
            </div>
            <div className="menu-stats-grid">
              <div>
                <p>Unique Dishes Sold</p>
                <strong>{analytics.menu_performance.stats.unique_dishes}</strong>
              </div>
              <div>
                <p>Total Items Sold</p>
                <strong>{analytics.menu_performance.stats.total_items_sold}</strong>
              </div>
              <div>
                <p>Avg. Items / Order</p>
                <strong>{analytics.menu_performance.stats.avg_items_per_order}</strong>
              </div>
              <div>
                <p>Allergen-Free Rate</p>
                <strong>{analytics.menu_performance.stats.allergen_free_rate}%</strong>
              </div>
            </div>
            <div className="menu-performance-grid">
              <div>
                <h5>Best Sellers</h5>
                {analytics.menu_performance.best_sellers.length === 0 ? (
                  <p className="empty-state">No dish data yet.</p>
                ) : (
                  analytics.menu_performance.best_sellers.map((dish, index) => (
                    <div key={`${dish.dish_id || dish.name}-best`} className="dish-row">
                      <div className="dish-rank">{index + 1}</div>
                      <div>
                        <p className="dish-name">{dish.name}</p>
                        <p className="dish-meta">{dish.restaurant_name || 'Restaurant'}</p>
                      </div>
                      <div className="dish-stats">
                        <span>{dish.quantity} sold</span>
                        <strong>{formatCurrency(dish.revenue)}</strong>
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div>
                <h5>Slow Movers</h5>
                {analytics.menu_performance.slow_movers.length === 0 ? (
                  <p className="empty-state">No slow mover data yet.</p>
                ) : (
                  analytics.menu_performance.slow_movers.map((dish, index) => (
                    <div key={`${dish.dish_id || dish.name}-slow`} className="dish-row">
                      <div className="dish-rank slow">{index + 1}</div>
                      <div>
                        <p className="dish-name">{dish.name}</p>
                        <p className="dish-meta">{dish.restaurant_name || 'Restaurant'}</p>
                      </div>
                      <div className="dish-stats">
                        <span>{dish.quantity} sold</span>
                        <strong>{formatCurrency(dish.revenue)}</strong>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          <div className="analytics-panel full-width">
            <div className="panel-header">
              <h4>Restaurant Performance</h4>
              <span>Orders and revenue per restaurant</span>
            </div>
            <div className="restaurant-table">
              <div className="restaurant-row header">
                <span>Restaurant</span>
                <span>Orders</span>
                <span>Items Sold</span>
                <span>Revenue</span>
              </div>
              {analytics.restaurants.length === 0 ? (
                <p className="empty-state">No restaurant orders yet.</p>
              ) : (
                analytics.restaurants.map((restaurant) => (
                  <div
                    key={restaurant.restaurant_id || restaurant.restaurant_name}
                    className="restaurant-row"
                  >
                    <span className="restaurant-name">{restaurant.restaurant_name}</span>
                    <span>{restaurant.order_count}</span>
                    <span>{restaurant.items_sold}</span>
                    <span>{formatCurrency(restaurant.revenue)}</span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default AdminAnalytics;
