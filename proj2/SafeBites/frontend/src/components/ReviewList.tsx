import './ReviewList.css';

interface Review {
  _id: string;
  user_id: string;
  rating: number;
  comment?: string;
  created_at: string;
  updated_at?: string;
  userName?: string;
}

interface ReviewListProps {
  reviews: Review[];
  currentUserId?: string;
  onEdit?: (reviewId: string) => void;
  onDelete?: (reviewId: string) => Promise<void>;
  isLoading?: boolean;
}

function ReviewList({
  reviews,
  currentUserId,
  onEdit,
  onDelete,
  isLoading = false,
}: ReviewListProps) {
  const renderStars = (rating: number) => {
    return '★'.repeat(rating) + '☆'.repeat(5 - rating);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (!reviews || reviews.length === 0) {
    return (
      <div className="review-list-container">
        <p className="no-reviews">No reviews yet. Be the first to review!</p>
      </div>
    );
  }

  return (
    <div className="review-list-container">
      <h4 className="review-count">Reviews ({reviews.length})</h4>
      <div className="reviews-list">
        {reviews.map((review) => (
          <div key={review._id} className="review-card">
            <div className="review-header">
              <div className="review-rating">
                <span className="stars">{renderStars(review.rating)}</span>
                <span className="rating-text">{review.rating}/5</span>
              </div>
              {currentUserId === review.user_id && (
                <div className="review-actions">
                  <button
                    className="action-btn edit-btn"
                    onClick={() => onEdit?.(review._id)}
                    title="Edit review"
                  >
                    ✏️
                  </button>
                  <button
                    className="action-btn delete-btn"
                    onClick={() => onDelete?.(review._id)}
                    disabled={isLoading}
                    title="Delete review"
                  >
                    🗑️
                  </button>
                </div>
              )}
            </div>
            {review.comment && (
              <p className="review-comment">{review.comment}</p>
            )}
            <div className="review-footer">
              <span className="review-author">{review.userName || 'User'}</span>
              <span className="review-date">{formatDate(review.created_at)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ReviewList;
