<template>
  <div class="service-request-detail">
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="!request" class="alert alert-warning">
      Request not found or no longer available.
    </div>

    <div v-else class="card">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          Service Request #{{ request.id }}
        </h5>
        <span class="badge" :class="getStatusClass(request.status)">
          {{ formatStatus(request.status) }}
        </span>
      </div>

      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <h6>Request Information</h6>
            <table class="table table-borderless table-sm">
              <tbody>
                <tr>
                  <th width="150">Service:</th>
                  <td>{{ request.service_name }}</td>
                </tr>
                <tr>
                  <th>Date Created:</th>
                  <td>{{ formatDate(request.create_date) }}</td>
                </tr>
                <tr>
                  <th>Scheduled For:</th>
                  <td>{{ formatDate(request.scheduled_date) }} {{ request.scheduled_time }}</td>
                </tr>
                <tr>
                  <th>Price:</th>
                  <td>${{ request.price }}</td>
                </tr>
                <tr v-if="isCustomer && request.professional_id">
                  <th>Professional:</th>
                  <td>{{ request.professional_name }}</td>
                </tr>
                <tr v-if="isProfessional && request.customer_id">
                  <th>Customer:</th>
                  <td>{{ request.customer_name }}</td>
                </tr>
                <tr v-if="request.address">
                  <th>Address:</th>
                  <td>{{ request.address }}</td>
                </tr>
                <tr v-if="request.pincode">
                  <th>Pin Code:</th>
                  <td>{{ request.pincode }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="col-md-6">
            <h6>Details & Notes</h6>
            <div class="mb-3">
              <p v-if="request.description">{{ request.description }}</p>
              <p v-else class="text-muted">No additional details provided.</p>
            </div>

            <div v-if="request.status === 'completed' && request.remarks" class="mb-3">
              <h6>Completion Remarks</h6>
              <p>{{ request.remarks }}</p>
            </div>
          </div>
        </div>

        <div v-if="canShowReview" class="mt-4">
          <div v-if="request.review">
            <h6>Your Review</h6>
            <div class="review-container">
              <div class="rating mb-2">
                <span v-for="star in 5" :key="star" class="star">
                  <i class="fas" :class="star <= request.review.rating ? 'fa-star text-warning' : 'fa-star text-muted'"></i>
                </span>
              </div>
              <p>{{ request.review.review_text }}</p>
              <div class="text-muted small">
                Submitted on {{ formatDate(request.review.created_at) }}
              </div>
            </div>
          </div>
          <div v-else>
            <h6>Leave a Review</h6>
            <review-form 
              :service-request-id="request.id" 
              :professional-id="request.professional_id" 
              @review-submitted="onReviewSubmitted"
              @review-error="onReviewError"
            />
          </div>
        </div>

        <div class="action-buttons mt-4">
          <!-- Customer Actions -->
          <div v-if="isCustomer" class="d-flex justify-content-end">
            <button 
              v-if="request.status === 'pending'" 
              @click="cancelRequest" 
              class="btn btn-danger me-2"
            >
              Cancel Request
            </button>
            <button 
              v-if="request.status === 'in_progress'" 
              @click="completeRequest" 
              class="btn btn-success me-2"
            >
              Mark as Completed
            </button>
            <button 
              @click="$emit('close')" 
              class="btn btn-secondary"
            >
              Close
            </button>
          </div>

          <!-- Professional Actions -->
          <div v-if="isProfessional" class="d-flex justify-content-end">
            <button 
              v-if="request.status === 'requested'" 
              @click="acceptRequest" 
              class="btn btn-success me-2"
            >
              Accept Request
            </button>
            <button 
              v-if="request.status === 'requested'" 
              @click="rejectRequest" 
              class="btn btn-danger me-2"
            >
              Reject Request
            </button>
            <button 
              v-if="request.status === 'accepted'" 
              @click="startService" 
              class="btn btn-primary me-2"
            >
              Start Service
            </button>
            <button 
              v-if="request.status === 'in_progress'" 
              @click="finishService" 
              class="btn btn-success me-2"
            >
              Finish Service
            </button>
            <button 
              @click="$emit('close')" 
              class="btn btn-secondary"
            >
              Close
            </button>
          </div>

          <!-- Admin Actions -->
          <div v-if="isAdmin" class="d-flex justify-content-end">
            <button 
              v-if="['requested', 'accepted', 'in_progress'].includes(request.status)" 
              @click="cancelRequest" 
              class="btn btn-danger me-2"
            >
              Cancel Request
            </button>
            <button 
              @click="$emit('close')" 
              class="btn btn-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import AuthService from '@/services/AuthService';
import ReviewForm from '@/components/ReviewForm.vue';

export default {
  name: 'ServiceRequestDetail',
  components: {
    ReviewForm
  },
  props: {
    requestId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      request: null,
      loading: true,
      error: null,
      currentUser: null
    };
  },
  computed: {
    isCustomer() {
      return this.currentUser && this.currentUser.role === 'customer';
    },
    isProfessional() {
      return this.currentUser && this.currentUser.role === 'professional';
    },
    isAdmin() {
      return this.currentUser && this.currentUser.role === 'admin';
    },
    canShowReview() {
      return this.isCustomer && this.request.status === 'completed';
    }
  },
  methods: {
    async fetchRequestDetails() {
      this.loading = true;
      try {
        const response = await ApiService.get(`/service-requests/${this.requestId}`);
        this.request = response.data;
      } catch (error) {
        console.error('Error fetching request details:', error);
        this.error = 'Failed to load request details';
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    formatStatus(status) {
      if (!status) return '';
      return status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ');
    },
    getStatusClass(status) {
      const statusClasses = {
        'pending': 'bg-warning',
        'requested': 'bg-secondary',
        'accepted': 'bg-info',
        'assigned': 'bg-info',
        'in_progress': 'bg-primary',
        'completed': 'bg-success',
        'rejected': 'bg-danger',
        'cancelled': 'bg-danger'
      };
      return statusClasses[status] || 'bg-secondary';
    },
    async updateRequestStatus(status, additionalData = {}) {
      try {
        await ApiService.put(`/service-requests/${this.requestId}/status`, {
          status,
          ...additionalData
        });
        
        // Refresh the request details
        await this.fetchRequestDetails();
        this.$emit('status-updated', { id: this.requestId, status });
      } catch (error) {
        console.error(`Error updating request to ${status}:`, error);
      }
    },
    async cancelRequest() {
      if (confirm('Are you sure you want to cancel this request?')) {
        await this.updateRequestStatus('cancelled');
      }
    },
    async acceptRequest() {
      await this.updateRequestStatus('accepted');
    },
    async rejectRequest() {
      await this.updateRequestStatus('rejected');
    },
    async startService() {
      await this.updateRequestStatus('in_progress');
    },
    async finishService() {
      await this.updateRequestStatus('completed');
    },
    async completeRequest() {
      await this.updateRequestStatus('completed');
    },
    onReviewSubmitted(review) {
      // Add the review to the request object
      this.request.review = {
        ...review,
        created_at: new Date().toISOString()
      };
      this.$emit('review-submitted', { id: this.requestId, review });
    },
    onReviewError(error) {
      console.error('Review submission error:', error);
    }
  },
  created() {
    this.currentUser = AuthService.getCurrentUser();
    this.fetchRequestDetails();
  },
  watch: {
    requestId() {
      this.fetchRequestDetails();
    }
  }
}
</script>

<style scoped>
.review-container {
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 0.25rem;
}
.rating {
  font-size: 1.25rem;
}
.star {
  margin-right: 0.25rem;
}
</style> 