import { useState } from 'react';
import './ReviewForm.css';

interface ReviewFormProps {
  authToken: string | null;
  onSubmit: (rating: number, comment: string) => Promise<void>;
  isLoading: boolean;
  initialRating?: number;
  initialComment?: string;
  isEditing?: boolean;
}

function ReviewForm({
  authToken,
  onSubmit,
  isLoading,
  initialRating = 5,
  initialComment = '',
  isEditing = false,
}: ReviewFormProps) {
  const [rating, setRating] = useState(initialRating);
  const [comment, setComment] = useState(initialComment);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!authToken) {
      setError('Please log in to submit a review');
      return;
    }

    if (rating < 1 || rating > 5) {
      setError('Rating must be between 1 and 5');
      return;
    }

    try {
      await onSubmit(rating, comment);
      setComment('');
      setRating(5);
    } catch (err: any) {
      setError(err.message || 'Failed to submit review');
    }
  };

  if (!authToken) {
    return (
      <div className="review-form-container">
        <p className="login-prompt">Log in to write a review</p>
      </div>
    );
  }

  return (
    <form className="review-form" onSubmit={handleSubmit}>
      <h4 className="form-title">{isEditing ? 'Edit Review' : 'Write a Review'}</h4>

      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label className="form-label">Rating</label>
        <div className="rating-input">
          {[1, 2, 3, 4, 5].map((star) => (
            <button
              key={star}
              type="button"
              className={`star-btn ${star <= rating ? 'active' : ''}`}
              onClick={() => setRating(star)}
              title={`${star} star${star > 1 ? 's' : ''}`}
            >
              ★
            </button>
          ))}
        </div>
        <span className="rating-display">{rating} / 5</span>
      </div>

      <div className="form-group">
        <label htmlFor="comment" className="form-label">
          Comment (Optional)
        </label>
        <textarea
          id="comment"
          className="form-textarea"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Share your thoughts about this dish..."
          rows={4}
          maxLength={500}
        />
        <span className="char-count">{comment.length} / 500</span>
      </div>

      <button
        type="submit"
        className="submit-btn"
        disabled={isLoading}
      >
        {isLoading ? 'Submitting...' : isEditing ? 'Update Review' : 'Submit Review'}
      </button>
    </form>
  );
}

export default ReviewForm;
