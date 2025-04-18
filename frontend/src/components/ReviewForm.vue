<template>
  <div class="review-form">
    <h5>Service Review</h5>
    <form @submit.prevent="submitReview">
      <div class="mb-3">
        <label for="rating" class="form-label">Rating</label>
        <div class="rating-stars mb-2">
          <span v-for="star in 5" :key="star" @click="rating = star" class="star">
            <i class="fas" :class="star <= rating ? 'fa-star text-warning' : 'fa-star text-muted'"></i>
          </span>
        </div>
        <div class="form-text">{{ ratingLabels[rating - 1] || 'Select a rating' }}</div>
      </div>
      <div class="mb-3">
        <label for="review-text" class="form-label">Your Review</label>
        <textarea 
          v-model="reviewText" 
          class="form-control" 
          id="review-text" 
          rows="3" 
          placeholder="Share your experience with this service"
          required
        ></textarea>
      </div>
      <div class="d-flex justify-content-end">
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting || !rating">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-1"></span>
          Submit Review
        </button>
      </div>
    </form>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
  name: 'ReviewForm',
  props: {
    serviceRequestId: {
      type: Number,
      required: true
    },
    professionalId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      rating: 0,
      reviewText: '',
      isSubmitting: false,
      ratingLabels: [
        'Poor', 
        'Fair', 
        'Good', 
        'Very Good', 
        'Excellent'
      ]
    };
  },
  methods: {
    async submitReview() {
      if (!this.rating) {
        return;
      }
      
      this.isSubmitting = true;
      try {
        await ApiService.post('/reviews', {
          service_request_id: this.serviceRequestId,
          professional_id: this.professionalId,
          rating: this.rating,
          review_text: this.reviewText
        });
        
        this.$emit('review-submitted', {
          rating: this.rating,
          review_text: this.reviewText
        });
        
        // Reset form
        this.rating = 0;
        this.reviewText = '';
      } catch (error) {
        console.error('Error submitting review:', error);
        this.$emit('review-error', error);
      } finally {
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<style scoped>
.rating-stars {
  display: flex;
  flex-direction: row;
}
.star {
  font-size: 1.5rem;
  cursor: pointer;
  margin-right: 0.5rem;
}
</style> 