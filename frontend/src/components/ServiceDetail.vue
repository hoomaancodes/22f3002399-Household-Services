<template>
  <div class="service-detail card">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">{{ service.name }}</h5>
      <span class="badge bg-primary">{{ service.service_type }}</span>
    </div>
    <div class="card-body">
      <div class="row">
        <div class="col-md-8">
          <p class="service-description">{{ service.description }}</p>
          
          <div class="service-info">
            <div class="info-item">
              <strong>Price:</strong> ${{ service.price }}
            </div>
            <div class="info-item">
              <strong>Time Required:</strong> {{ service.time_req }} hours
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="action-buttons">
            <button 
              v-if="isCustomer"
              @click="requestService" 
              class="btn btn-primary btn-block mb-2"
              :disabled="loading"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
              Book Service
            </button>
            <router-link 
              v-if="isCustomer"
              to="/customer/services" 
              class="btn btn-outline-secondary btn-block"
            >
              Back to Services
            </router-link>
          </div>
        </div>
      </div>
      
      <div v-if="showReviews" class="service-reviews mt-4">
        <h6>Customer Reviews</h6>
        <div v-if="reviews.length === 0" class="text-muted">
          No reviews yet for this service.
        </div>
        <div v-else>
          <div v-for="(review, index) in reviews" :key="index" class="review-item mb-3">
            <div class="d-flex justify-content-between">
              <div>
                <div class="rating">
                  <span v-for="star in 5" :key="star" class="star">
                    <i class="fas" :class="star <= review.rating ? 'fa-star text-warning' : 'fa-star text-muted'"></i>
                  </span>
                </div>
                <div class="review-text mt-1">
                  {{ review.review_text }}
                </div>
              </div>
              <div class="text-muted small">
                {{ formatDate(review.created_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import AuthService from '@/services/AuthService';

export default {
  name: 'ServiceDetail',
  props: {
    serviceId: {
      type: Number,
      required: true
    },
    showReviews: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      service: {},
      reviews: [],
      loading: false
    };
  },
  computed: {
    isCustomer() {
      const currentUser = AuthService.getCurrentUser();
      return currentUser && currentUser.role === 'customer';
    }
  },
  methods: {
    async fetchServiceDetails() {
      try {
        const response = await ApiService.get(`/services/${this.serviceId}`);
        this.service = response.data;
      } catch (error) {
        console.error('Error fetching service details:', error);
      }
    },
    async fetchServiceReviews() {
      if (!this.showReviews) return;
      
      try {
        const response = await ApiService.get(`/services/${this.serviceId}/reviews`);
        this.reviews = response.data;
      } catch (error) {
        console.error('Error fetching service reviews:', error);
      }
    },
    async requestService() {
      this.loading = true;
      try {
        await ApiService.post('/service-requests', {
          service_id: this.serviceId
        });
        this.$router.push('/customer/requests');
      } catch (error) {
        console.error('Error requesting service:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString();
    }
  },
  created() {
    this.fetchServiceDetails();
    this.fetchServiceReviews();
  },
  watch: {
    serviceId() {
      this.fetchServiceDetails();
      this.fetchServiceReviews();
    }
  }
}
</script>

<style scoped>
.service-detail {
  margin-bottom: 2rem;
}
.service-description {
  margin-bottom: 1.5rem;
}
.service-info {
  margin-bottom: 1.5rem;
}
.info-item {
  margin-bottom: 0.5rem;
}
.rating {
  font-size: 1rem;
}
.star {
  margin-right: 0.25rem;
}
.review-item {
  padding-bottom: 1rem;
  border-bottom: 1px solid #f0f0f0;
}
.review-item:last-child {
  border-bottom: none;
}
.review-text {
  color: #555;
}
</style> 