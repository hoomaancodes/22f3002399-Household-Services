<template>
  <div class="customer-requests">
    <PageHeader 
      title="My Service Requests" 
      subtitle="Track and manage your service requests">
      <template v-slot:actions>
        <router-link to="/customer/request-service" class="btn btn-accent">
          <i class="fas fa-plus"></i> New Request
        </router-link>
      </template>
    </PageHeader>
    
    <!-- Filter tabs -->
    <div class="card mb-4">
      <div class="card-body">
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <a class="nav-link" 
              :class="{ active: activeTab === 'all' }" 
              href="#" 
              @click.prevent="changeTab('all')"
            >
              All Requests
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" 
              :class="{ active: activeTab === 'active' }" 
              href="#" 
              @click.prevent="changeTab('active')"
            >
              <span class="d-flex align-items-center">
                Active
                <span v-if="getActiveCount() > 0" class="badge bg-accent ms-2">
                  {{ getActiveCount() }}
                </span>
              </span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" 
              :class="{ active: activeTab === 'completed' }" 
              href="#" 
              @click.prevent="changeTab('completed')"
            >
              Completed
            </a>
          </li>
        </ul>
        
        <div class="mt-3">
          <div class="input-group" style="max-width: 300px;">
            <input 
              type="text" 
              class="form-control" 
              placeholder="Search requests..." 
              v-model="searchQuery"
            >
            <button class="btn btn-outline-secondary" type="button">
              <i class="fas fa-search"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Requests List -->
    <div class="row">
      <div v-if="loading" class="col-12 text-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-else-if="filteredRequests.length === 0" class="col-12 text-center my-5">
        <p>No service requests found.</p>
        <p class="text-muted">Need a service? Request one now!</p>
        <router-link to="/customer/request-service" class="btn btn-accent mt-3">
          Request Service
        </router-link>
      </div>
      
      <template v-else>
        <div 
          v-for="request in filteredRequests" 
          :key="request.id"
          class="col-md-6 col-lg-4 mb-4"
        >
          <div class="card h-100" :class="{'border-accent': isNewRequest(request.id)}">
            <div class="card-header d-flex justify-content-between align-items-center" 
                :class="getStatusColorClass(request.status)">
              <span class="badge" :class="getStatusBadgeClass(request.status)">
                {{ request.status }}
              </span>
              <small class="text-muted">#{{ request.id }}</small>
            </div>
            <div class="card-body">
              <h5 class="card-title">{{ request.service_name }}</h5>
              
              <div class="request-details mt-3">
                <div class="request-detail">
                  <i class="far fa-calendar-alt text-primary me-2"></i>
                  <span>{{ formatDate(request.req_date) }}</span>
                </div>
                
                <div class="request-detail mt-2">
                  <i class="fas fa-user-tie text-primary me-2"></i>
                  <span v-if="request.professional_name">{{ request.professional_name }}</span>
                  <span v-else class="text-muted">Not assigned yet</span>
                </div>
                
                <div class="request-detail mt-2">
                  <i class="fas fa-tag text-primary me-2"></i>
                  <span>₹{{ request.price }}</span>
                </div>
                
                <div class="request-detail mt-2" v-if="request.remarks">
                  <i class="fas fa-comment-alt text-primary me-2"></i>
                  <span>{{ truncateText(request.remarks, 50) }}</span>
                </div>
              </div>
            </div>
            <div class="card-footer">
              <div class="d-flex flex-wrap justify-content-between">
                <button 
                  class="btn btn-sm btn-primary mb-2 me-2" 
                  @click="viewRequestDetails(request.id)"
                >
                  Details
                </button>
                
                <button 
                  v-if="canCancel(request)" 
                  class="btn btn-sm btn-danger mb-2 me-2" 
                  @click="cancelRequest(request.id)"
                >
                  Cancel
                </button>
                
                <button 
                  v-if="request.status === 'completed' && !request.has_review" 
                  class="btn btn-sm btn-accent mb-2" 
                  @click="openRatingModal(request)"
                >
                  Rate
                </button>
                
                <button 
                  v-if="request.status === 'completed' && request.has_review" 
                  class="btn btn-sm btn-secondary mb-2" 
                  @click="viewReview(request.id)"
                >
                  View Review
                </button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
    
    <!-- Request Details Modal -->
    <div v-if="showDetailsModal" class="modal-backdrop" @click="closeDetailsModal"></div>
    <div v-if="showDetailsModal" class="modal-container">
      <div class="modal-content" @click.stop>
        <div class="modal-header bg-primary text-white">
          <h5 class="modal-title">Service Request Details</h5>
          <button type="button" class="btn-close btn-close-white" @click="closeDetailsModal"></button>
        </div>
        
        <div class="modal-body">
          <div v-if="loadingDetails" class="text-center py-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else-if="selectedRequest">
            <div class="request-status-badge mb-4 text-center">
              <span class="badge" :class="getStatusBadgeClass(selectedRequest.status)">
                {{ selectedRequest.status }}
              </span>
            </div>
            
            <div class="section-header">
              <h3>Service Information</h3>
            </div>
            
            <div class="row mb-4">
              <div class="col-md-6">
                <p><strong>Service:</strong> {{ selectedRequest.service_name }}</p>
                <p><strong>Type:</strong> {{ selectedRequest.service_type }}</p>
                <p><strong>Price:</strong> ₹{{ selectedRequest.price }}</p>
              </div>
              
              <div class="col-md-6">
                <p><strong>Request ID:</strong> #{{ selectedRequest.id }}</p>
                <p>
                  <strong>Requested On:</strong> 
                  {{ formatDate(selectedRequest.req_date) }}
                </p>
                <p>
                  <strong>Scheduled For:</strong> 
                  {{ formatDateTime(selectedRequest.scheduled_date || selectedRequest.req_date) }}
                </p>
              </div>
            </div>

            <div class="section-header">
              <h3>Professional</h3>
            </div>
            
            <div class="mb-4">
              <p v-if="selectedRequest.professional_name">
                <strong>Name:</strong> {{ selectedRequest.professional_name }}
              </p>
              <p v-else class="text-muted">
                No professional assigned yet
              </p>
            </div>

            <div class="section-header">
              <h3>Address</h3>
            </div>
            
            <div class="mb-4">
              <p>{{ selectedRequest.customer_address }}</p>
            </div>

            <div v-if="selectedRequest.remarks" class="mb-4">
              <div class="section-header">
                <h3>Notes</h3>
              </div>
              <p>{{ selectedRequest.remarks }}</p>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeDetailsModal">Close</button>
          <button 
            v-if="selectedRequest && canCancel(selectedRequest)" 
            type="button" 
            class="btn btn-danger" 
            @click="cancelRequest(selectedRequest.id)"
          >
            Cancel Request
          </button>
        </div>
      </div>
    </div>
    
    <!-- Rating Modal -->
    <div v-if="showRatingModal" class="modal-backdrop" @click="closeRatingModal"></div>
    <div v-if="showRatingModal" class="modal-container">
      <div class="modal-content" @click.stop>
        <div class="modal-header bg-accent text-white">
          <h5 class="modal-title">Rate Your Service</h5>
          <button type="button" class="btn-close btn-close-white" @click="closeRatingModal"></button>
        </div>
        
        <div class="modal-body">
          <div v-if="selectedRequest">
            <p class="mb-3">How would you rate your service experience for {{ selectedRequest.service_name }}?</p>
            
            <div class="rating mb-4 text-center">
              <span v-for="i in 5" :key="i" class="star-container mx-1" @click="setRating(i)" style="cursor: pointer; font-size: 2rem;">
                <i class="fas fa-star" :class="{ 'text-accent': i <= rating, 'text-gray': i > rating }"></i>
              </span>
            </div>
            
            <div class="form-group">
              <label class="form-label">Leave a review (optional)</label>
              <textarea 
                class="form-control" 
                rows="4" 
                v-model="reviewComment" 
                placeholder="Share your experience with this service..."
              ></textarea>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeRatingModal">Cancel</button>
          <button 
            type="button" 
            class="btn btn-accent" 
            @click="submitRating"
            :disabled="rating === 0"
          >
            Submit Rating
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import PageHeader from '@/components/PageHeader.vue';

export default {
  name: 'CustomerRequests',
  components: {
    PageHeader
  },
  data() {
    return {
      requests: [],
      activeTab: 'all',
      searchQuery: '',
      loading: true,
      
      // Request details modal
      showDetailsModal: false,
      selectedRequest: null,
      loadingDetails: false,
      
      // Rating modal
      showRatingModal: false,
      rating: 0,
      reviewComment: '',
      
      // Tracking new requests
      newRequestIds: []
    };
  },
  computed: {
    filteredRequests() {
      if (!this.requests.length) return [];
      
      let result = [...this.requests];
      
      // Apply tab filter
      if (this.activeTab === 'active') {
        result = result.filter(request => 
          ['requested', 'assigned', 'accepted', 'in_progress'].includes(request.status)
        );
      } else if (this.activeTab === 'completed') {
        result = result.filter(request => 
          ['completed', 'cancelled', 'rejected'].includes(request.status)
        );
      }
      
      // Apply search filter if needed
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(request => 
          (request.service_name && request.service_name.toLowerCase().includes(query)) ||
          (request.professional_name && request.professional_name.toLowerCase().includes(query)) ||
          (request.status && request.status.toLowerCase().includes(query)) ||
          (request.id && request.id.toString().includes(query))
        );
      }
      
      // Sort by date, newest first
      return result.sort((a, b) => new Date(b.req_date) - new Date(a.req_date));
    }
  },
  methods: {
    fetchRequests() {
      this.loading = true;
      ApiService.getCustomerServiceRequests()
        .then(response => {
          this.requests = response.data;
          // Check if a new request was just created
          this.checkForNewRequest();
        })
        .catch(error => {
          console.error('Error fetching service requests:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    changeTab(tab) {
      this.activeTab = tab;
    },
    
    getActiveCount() {
      return this.requests.filter(request => 
        ['requested', 'assigned', 'accepted', 'in_progress'].includes(request.status)
      ).length;
    },
    
    getStatusColorClass(status) {
      const colorMap = {
        'requested': 'bg-light-primary',
        'assigned': 'bg-light-info',
        'accepted': 'bg-light-info',
        'in_progress': 'bg-light-accent',
        'completed': 'bg-light-success',
        'cancelled': 'bg-light-secondary',
        'rejected': 'bg-light-danger'
      };
      
      return colorMap[status] || 'bg-light-primary';
    },
    
    getStatusBadgeClass(status) {
      const badgeMap = {
        'requested': 'bg-primary',
        'assigned': 'bg-info',
        'accepted': 'bg-info',
        'in_progress': 'bg-accent',
        'completed': 'bg-success',
        'cancelled': 'bg-secondary',
        'rejected': 'bg-danger'
      };
      
      return badgeMap[status] || 'bg-primary';
    },
    
    canCancel(request) {
      return ['requested', 'assigned', 'accepted'].includes(request.status);
    },
    
    cancelRequest(requestId) {
      if (confirm('Are you sure you want to cancel this service request?')) {
        ApiService.updateServiceRequest(requestId, { status: 'cancelled' })
          .then(() => {
            this.fetchRequests();
            if (this.showDetailsModal) {
              this.closeDetailsModal();
            }
          })
          .catch(error => {
            console.error('Error cancelling request:', error);
            alert('Failed to cancel request. Please try again.');
          });
      }
    },
    
    viewRequestDetails(requestId) {
      this.loadingDetails = true;
      this.showDetailsModal = true;
      this.selectedRequest = null;
      
      ApiService.getServiceRequest(requestId)
        .then(response => {
          this.selectedRequest = response.data;
        })
        .catch(error => {
          console.error('Error fetching request details:', error);
          alert('Failed to load request details.');
        })
        .finally(() => {
          this.loadingDetails = false;
        });
    },
    
    closeDetailsModal() {
      this.showDetailsModal = false;
      this.selectedRequest = null;
    },
    
    openRatingModal(request) {
      this.selectedRequest = request;
      this.showRatingModal = true;
      this.rating = 0;
      this.reviewComment = '';
    },
    
    closeRatingModal() {
      this.showRatingModal = false;
      this.rating = 0;
      this.reviewComment = '';
    },
    
    setRating(value) {
      this.rating = value;
    },
    
    submitRating() {
      if (this.rating === 0) {
        alert('Please select a rating before submitting.');
        return;
      }
      
      ApiService.rateServiceRequest(
        this.selectedRequest.id, 
        this.rating, 
        this.reviewComment
      )
        .then(() => {
          this.closeRatingModal();
          this.fetchRequests();
          alert('Thank you for your feedback!');
        })
        .catch(error => {
          console.error('Error submitting rating:', error);
          alert('Failed to submit rating. Please try again.');
        });
    },
    
    viewReview(requestId) {
      // Implement showing the existing review
      console.log(`Viewing review for request ID: ${requestId}`);
      alert('This feature is coming soon!');
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
    },
    
    truncateText(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
    },
    
    checkForNewRequest() {
      // Check if we came from request creation page
      const newRequestId = this.$route.query.new_request;
      if (newRequestId && !this.newRequestIds.includes(Number(newRequestId))) {
        this.newRequestIds.push(Number(newRequestId));
        
        // Remove from list after 10 seconds
        setTimeout(() => {
          this.newRequestIds = this.newRequestIds.filter(id => id !== Number(newRequestId));
        }, 10000);
      }
    },
    
    isNewRequest(requestId) {
      return this.newRequestIds.includes(requestId);
    }
  },
  created() {
    this.fetchRequests();
    
    // If a specific tab is specified in the URL, activate it
    const tab = this.$route.query.tab;
    if (tab && ['all', 'active', 'completed'].includes(tab)) {
      this.activeTab = tab;
    }
  }
};
</script>

<style scoped>
.request-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
  gap: 20px;
}

.request-card {
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  overflow: hidden;
  background-color: #fff;
  transition: transform 0.3s, box-shadow 0.3s;
}

.request-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.request-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(0,0,0,0.1);
}

.request-body {
  padding: 15px;
}

.request-footer {
  padding: 15px;
  border-top: 1px solid rgba(0,0,0,0.1);
  display: flex;
  justify-content: flex-end;
}

.status-warning {
  background-color: #fff3cd;
}

.status-info {
  background-color: #cff4fc;
}

.status-primary {
  background-color: #cfe2ff;
}

.status-success {
  background-color: #d1e7dd;
}

.status-danger {
  background-color: #f8d7da;
}

.status-secondary {
  background-color: #e2e3e5;
}

.details-section-header {
  border-bottom: 1px solid #e9ecef;
  padding-bottom: 5px;
  margin-bottom: 10px;
  color: #495057;
}

.rating-stars {
  margin: 20px 0;
}

.star-label {
  font-weight: bold;
  margin-right: 10px;
}

.star-container {
  display: inline-block;
  margin: 0 5px;
}

.rating-star {
  color: #e0e0e0;
  cursor: pointer;
  transition: color 0.2s;
}

.rating-star:hover,
.rating-star.active {
  color: #ffc107;
}

.request-status-badge {
  display: flex;
  justify-content: center;
}

.badge {
  text-transform: capitalize;
  padding: 0.5em 0.75em;
}

.highlight-new {
  animation: highlight 2s ease-in-out;
  box-shadow: 0 0 0 3px #0d6efd;
}

@keyframes highlight {
  0% { box-shadow: 0 0 0 3px rgba(13, 110, 253, 0.9); }
  70% { box-shadow: 0 0 0 10px rgba(13, 110, 253, 0); }
  100% { box-shadow: none; }
}

/* Modal styles */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.modal-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.modal-content {
  width: 700px;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  background-color: white;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-header,
.modal-footer {
  display: flex;
  align-items: center;
  padding: 1rem;
}

.modal-header {
  justify-content: space-between;
  border-bottom: 1px solid #dee2e6;
}

.modal-footer {
  justify-content: flex-end;
  border-top: 1px solid #dee2e6;
}

.modal-body {
  padding: 1.5rem;
}

.me-1 {
  margin-right: 0.25rem;
}

.me-2 {
  margin-right: 0.5rem;
}

.ms-2 {
  margin-left: 0.5rem;
}

@media (max-width: 768px) {
  .request-cards {
    grid-template-columns: 1fr;
  }
}
</style> 