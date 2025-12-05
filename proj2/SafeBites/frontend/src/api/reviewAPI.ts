const API_BASE_URL = 'http://localhost:8000';

export interface ReviewCreateData {
  dish_id: string;
  rating: number;
  comment?: string;
}

export interface ReviewUpdateData {
  rating?: number;
  comment?: string;
}

export const reviewAPI = {
  async createReview(data: ReviewCreateData, authToken: string) {
    const response = await fetch(`${API_BASE_URL}/reviews/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create review');
    }
    return response.json();
  },

  async listReviewsForDish(dishId: string) {
    const response = await fetch(`${API_BASE_URL}/reviews/dish/${dishId}`);
    if (!response.ok) {
      throw new Error('Failed to fetch reviews');
    }
    return response.json();
  },

  async listMyReviews(authToken: string) {
    const response = await fetch(`${API_BASE_URL}/reviews/me`, {
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });
    if (!response.ok) {
      throw new Error('Failed to fetch your reviews');
    }
    return response.json();
  },

  async updateReview(reviewId: string, data: ReviewUpdateData, authToken: string) {
    const response = await fetch(`${API_BASE_URL}/reviews/${reviewId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update review');
    }
    return response.json();
  },

  async deleteReview(reviewId: string, authToken: string) {
    const response = await fetch(`${API_BASE_URL}/reviews/${reviewId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authToken}`,
      },
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to delete review');
    }
    return response.json();
  },
};
