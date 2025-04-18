<template>
  <div class="customer-service-requests">
    <h2>My Service Requests</h2>
    
    <!-- Filter and Search -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label for="statusFilter" class="form-label">Status</label>
            <select v-model="statusFilter" class="form-select" id="statusFilter">
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="accepted">Accepted</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          <div class="col-md-3">
            <label for="serviceFilter" class="form-label">Service</label>
            <select v-model="serviceFilter" class="form-select" id="serviceFilter">
              <option value="">All Services</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label for="dateRange" class="form-label">Date Range</label>
            <select v-model="dateFilter" class="form-select" id="dateRange">
              <option value="">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
            </select>
          </div>
          <div class="col-md-3">
            <label for="searchQuery" class="form-label">Search</label>
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                id="searchQuery" 
                v-model="searchQuery" 
                placeholder="Search requests..."
              >
              <button class="btn btn-outline-secondary" type="button">
                <i class="fas fa-search"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Request Tabs -->
    <div class="request-tabs mb-4">
      <ul class="nav nav-tabs">
        <li class="nav-item">
          <a 
            class="nav-link" 
            :class="{ active: tabFilter === 'active' }" 
            @click.prevent="tabFilter = 'active'"
            href="#"
          >
            Active Requests <span class="badge bg-primary">{{ activeRequestsCount }}</span>
          </a>
        </li>
        <li class="nav-item">
          <a 
            class="nav-link" 
            :class="{ active: tabFilter === 'completed' }" 
            @click.prevent="tabFilter = 'completed'"
            href="#"
          >
            Completed
          </a>
        </li>
        <li class="nav-item">
          <a 
            class="nav-link" 
            :class="{ active: tabFilter === 'cancelled' }" 
            @click.prevent="tabFilter = 'cancelled'"
            href="#"
          >
            Cancelled
          </a>
        </li>
        <li class="nav-item">
          <a 
            class="nav-link" 
            :class="{ active: tabFilter === 'all' }" 
            @click.prevent="tabFilter = 'all'"
            href="#"
          >
            All Requests
          </a>
        </li>
      </ul>
    </div>
    
    <!-- Service Requests -->
    <div class="service-requests">
      <div v-if="loading" class="text-center my-5">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-else-if="filteredRequests.length === 0" class="text-center my-5">
        <p>No service requests found matching your criteria.</p>
        <div v-if="tabFilter === 'all' && !statusFilter && !serviceFilter && !dateFilter && !searchQuery">
          <p class="text-muted">You haven't made any service requests yet.</p>
          <router-link to="/customer/services" class="btn btn-primary mt-3">Browse Services</router-link>
        </div>
      </div>
      
      <div v-else>
        <!-- List View for Mobile -->
        <div class="d-md-none">
          <div 
            v-for="request in paginatedRequests" 
            :key="request.id" 
            class="card mb-3 request-card"
          >
            <div class="card-header d-flex justify-content-between align-items-center">
              <div>
                <h6 class="mb-0">{{ request }}</h6>
                <small class="text-muted">Request #{{ request.id }}</small>
              </div>
              <span class="badge" :class="getStatusClass(request.status)">
                {{ formatStatus(request.status) }}
              </span>
            </div>
            <div class="card-body">
              <p><strong>Professional:</strong> {{ request.professional_name || 'Not assigned' }}</p>
              <p><strong>Date:</strong> {{ formatDate(request.request_date) }}</p>
              <p><strong>Scheduled For:</strong> {{ formatDate(request.scheduled_date) }} {{ request.scheduled_time }}</p>
              <div class="d-flex justify-content-end">
                <button 
                  class="btn btn-sm btn-outline-primary me-2"
                  @click="viewRequest(request)"
                >
                  View Details
                </button>
                <button 
                  v-if="['pending', 'accepted'].includes(request.status)"
                  class="btn btn-sm btn-outline-danger"
                  @click="cancelRequest(request)"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Table View for Desktop -->
        <div class="d-none d-md-block table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th @click="setSorting('id')" class="sortable-column">
                  ID <i class="fas" :class="getSortIconClass('id')"></i>
                </th>
                <th @click="setSorting('service')" class="sortable-column">
                  Service <i class="fas" :class="getSortIconClass('service')"></i>
                </th>
                <th @click="setSorting('professional')" class="sortable-column">
                  Professional <i class="fas" :class="getSortIconClass('professional')"></i>
                </th>
                <th @click="setSorting('date')" class="sortable-column">
                  Date <i class="fas" :class="getSortIconClass('date')"></i>
                </th>
                <th @click="setSorting('status')" class="sortable-column">
                  Status <i class="fas" :class="getSortIconClass('status')"></i>
                </th>
                <th @click="setSorting('price')" class="sortable-column text-end">
                  Price <i class="fas" :class="getSortIconClass('price')"></i>
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="request in paginatedRequests" :key="request.id">
                <td>#{{ request.id }}</td>
                <td>{{ request.service_name }}</td>
                <td>{{ request.professional_name || 'Not assigned' }}</td>
                <td>{{ formatDate(request.scheduled_date) }}</td>
                <td>
                  <span class="badge" :class="getStatusClass(request.status)">
                    {{ formatStatus(request.status) }}
                  </span>
                </td>
                <td class="text-end">${{ request.price }}</td>
                <td>
                  <div class="btn-group btn-group-sm">
                    <button 
                      class="btn btn-outline-primary"
                      @click="viewRequest(request)"
                      title="View Details"
                    >
                      <i class="fas fa-eye"></i>
                    </button>
                    
                    <button 
                      v-if="['pending', 'accepted'].includes(request.status)"
                      class="btn btn-outline-danger"
                      @click="cancelRequest(request)"
                      title="Cancel Request"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                    
                    <button 
                      v-if="request.status === 'completed' && !request.is_rated"
                      class="btn btn-outline-warning"
                      @click="rateService(request)"
                      title="Rate Service"
                    >
                      <i class="fas fa-star"></i>
                    </button>
                    
                    <button 
                      v-if="['in_progress'].includes(request.status)"
                      class="btn btn-outline-success"
                      @click="requestCompletion(request)"
                      title="Mark as Complete"
                    >
                      <i class="fas fa-check"></i>
                    </button>
                    
                    <button 
                      v-if="canRebook(request)"
                      class="btn btn-outline-info"
                      @click="rebookService(request)"
                      title="Book Again"
                    >
                      <i class="fas fa-redo"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination -->
        <div v-if="filteredRequests.length > 0" class="d-flex justify-content-between align-items-center mt-4">
          <div>
            Showing {{ paginationInfo.from }} to {{ paginationInfo.to }} of {{ filteredRequests.length }} requests
          </div>
          <div>
            <button 
              class="btn btn-sm btn-outline-secondary me-2"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              <i class="fas fa-chevron-left"></i> Previous
            </button>
            <button 
              class="btn btn-sm btn-outline-secondary"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              Next <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Request Detail Modal -->
    <div 
      class="modal fade" 
      id="requestDetailModal" 
      tabindex="-1" 
      aria-labelledby="requestDetailModalLabel" 
      aria-hidden="true"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title" id="requestDetailModalLabel">
              Service Request #{{ selectedRequest.id }}
              <span class="badge ms-2" :class="getStatusClass(selectedRequest.status)">
                {{ formatStatus(selectedRequest.status) }}
              </span>
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-md-6">
                <h6>Request Information</h6>
                <table class="table table-borderless table-sm">
                  <tbody>
                    <tr>
                      <th>Service:</th>
                      <td>{{ selectedRequest.service_name }}</td>
                    </tr>
                    <tr>
                      <th>Request Date:</th>
                      <td>{{ formatDate(selectedRequest.request_date) }}</td>
                    </tr>
                    <tr>
                      <th>Scheduled For:</th>
                      <td>{{ formatDate(selectedRequest.scheduled_date) }} {{ selectedRequest.scheduled_time }}</td>
                    </tr>
                    <tr>
                      <th>Price:</th>
                      <td>${{ selectedRequest.price }}</td>
                    </tr>
                    <tr>
                      <th>Duration:</th>
                      <td>{{ selectedRequest.duration }} hours</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              
              <div class="col-md-6">
                <h6>Professional Information</h6>
                <table class="table table-borderless table-sm">
                  <tbody>
                    <tr v-if="selectedRequest.professional_name">
                      <th>Name:</th>
                      <td>{{ selectedRequest.professional_name }}</td>
                    </tr>
                    <tr v-if="selectedRequest.professional_email">
                      <th>Email:</th>
                      <td>{{ selectedRequest.professional_email }}</td>
                    </tr>
                    <tr v-if="selectedRequest.professional_phone">
                      <th>Phone:</th>
                      <td>{{ selectedRequest.professional_phone }}</td>
                    </tr>
                    <tr v-if="!selectedRequest.professional_name">
                      <td colspan="2" class="text-muted">
                        No professional assigned yet.
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="row mt-4">
              <div class="col-12">
                <h6>Service Location</h6>
                <p>{{ selectedRequest.address }}</p>
                
                <h6>Special Instructions</h6>
                <p v-if="selectedRequest.instructions">{{ selectedRequest.instructions }}</p>
                <p v-else class="text-muted">No special instructions provided.</p>
                
                <h6>Status Timeline</h6>
                <ul class="timeline">
                  <li v-for="(status, index) in selectedRequest.status_timeline" :key="index">
                    <div class="timeline-badge" :class="getTimelineClass(status.status)"></div>
                    <div class="timeline-panel">
                      <div class="timeline-heading">
                        <h6 class="timeline-title">{{ formatStatus(status.status) }}</h6>
                        <p><small class="text-muted">{{ formatDate(status.timestamp) }}</small></p>
                      </div>
                      <div class="timeline-body" v-if="status.notes">
                        <p>{{ status.notes }}</p>
                      </div>
                    </div>
                  </li>
                </ul>
                
                <div v-if="selectedRequest.is_rated" class="mt-4">
                  <h6>Your Rating</h6>
                  <div class="d-flex align-items-center">
                    <div class="rating-stars">
                      <i 
                        v-for="star in 5" 
                        :key="star" 
                        class="fas fa-star" 
                        :class="{ 'text-warning': star <= selectedRequest.rating }"
                      ></i>
                    </div>
                    <span class="ms-2">{{ selectedRequest.rating }}/5</span>
                  </div>
                  <p v-if="selectedRequest.review" class="mt-2 review-text">
                    "{{ selectedRequest.review }}"
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            
            <button 
              v-if="['pending', 'accepted'].includes(selectedRequest.status)"
              class="btn btn-danger me-2"
              @click="cancelSelectedRequest"
            >
              Cancel Request
            </button>
            
            <button 
              v-if="selectedRequest.status === 'completed' && !selectedRequest.is_rated"
              class="btn btn-warning me-2"
              @click="rateSelectedService"
            >
              Rate Service
            </button>
            
            <button 
              v-if="canRebook(selectedRequest)"
              class="btn btn-primary me-2"
              @click="rebookSelectedService"
            >
              Book Again
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Rating Modal -->
    <div 
      class="modal fade" 
      id="ratingModal" 
      tabindex="-1" 
      aria-labelledby="ratingModalLabel" 
      aria-hidden="true"
      data-bs-backdrop="static"
    >
      <div class="modal-dialog">
        <div class="modal-content" v-if="requestToRate">
          <div class="modal-header">
            <h5 class="modal-title" id="ratingModalLabel">Rate Your Service</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3">How would you rate your experience with {{ requestToRate.service_name }}?</p>
            
            <div class="rating-container text-center mb-4">
              <div class="star-rating">
                <i 
                  v-for="star in 5" 
                  :key="star" 
                  class="fas fa-star rating-star" 
                  :class="{ 'active': star <= rating }"
                  @click="rating = star"
                ></i>
              </div>
              <div class="rating-text mt-2">{{ getRatingText() }}</div>
            </div>
            
            <div class="form-group mb-3">
              <label for="reviewText" class="form-label">Review (Optional)</label>
              <textarea 
                id="reviewText" 
                v-model="review" 
                class="form-control" 
                rows="3" 
                placeholder="Share your experience..."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="submitRating"
              :disabled="!rating || submittingRating"
            >
              <span v-if="submittingRating" class="spinner-border spinner-border-sm me-2" role="status"></span>
              Submit Rating
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import { Modal } from 'bootstrap';

export default {
  name: 'CustomerServiceRequests',
  data() {
    return {
      requests: [],
      services: [],
      loading: true,
      statusFilter: '',
      serviceFilter: '',
      dateFilter: '',
      searchQuery: '',
      tabFilter: 'active',
      sortField: 'date',
      sortDirection: 'desc',
      currentPage: 1,
      perPage: 10,
      selectedRequest: null,
      requestToRate: null,
      rating: 0,
      review: '',
      submittingRating: false,
      requestDetailModal: null,
      ratingModal: null
    };
  },
  computed: {
    filteredRequests() {
      if (!this.requests.length) return [];
      
      let result = [...this.requests];
      
      // Apply tab filter
      if (this.tabFilter === 'active') {
        result = result.filter(request => 
          ['pending', 'accepted', 'in_progress'].includes(request.status)
        );
      } else if (this.tabFilter === 'completed') {
        result = result.filter(request => request.status === 'completed');
      } else if (this.tabFilter === 'cancelled') {
        result = result.filter(request => 
          ['cancelled', 'rejected'].includes(request.status)
        );
      }
      
      // Apply status filter if selected
      if (this.statusFilter) {
        result = result.filter(request => request.status === this.statusFilter);
      }
      
      // Apply service filter if selected
      if (this.serviceFilter) {
        result = result.filter(request => request.service_id === parseInt(this.serviceFilter));
      }
      
      // Apply date filter if selected
      if (this.dateFilter) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const requestDate = date => new Date(date);
        
        if (this.dateFilter === 'today') {
          result = result.filter(request => {
            const date = requestDate(request.request_date);
            return date >= today && date < new Date(today.getTime() + 86400000);
          });
        } else if (this.dateFilter === 'week') {
          const weekStart = new Date(today);
          weekStart.setDate(today.getDate() - today.getDay());
          
          result = result.filter(request => {
            return requestDate(request.request_date) >= weekStart;
          });
        } else if (this.dateFilter === 'month') {
          const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
          
          result = result.filter(request => {
            return requestDate(request.request_date) >= monthStart;
          });
        }
      }
      
      // Apply search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(request => 
          request.id.toString().includes(query) ||
          request.service_name.toLowerCase().includes(query) ||
          (request.professional_name && request.professional_name.toLowerCase().includes(query))
        );
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let comparison = 0;
        
        if (this.sortField === 'id') {
          comparison = a.id - b.id;
        } else if (this.sortField === 'service') {
          comparison = a.service_name.localeCompare(b.service_name);
        } else if (this.sortField === 'professional') {
          const aName = a.professional_name || '';
          const bName = b.professional_name || '';
          comparison = aName.localeCompare(bName);
        } else if (this.sortField === 'date') {
          comparison = new Date(a.scheduled_date) - new Date(b.scheduled_date);
        } else if (this.sortField === 'status') {
          comparison = a.status.localeCompare(b.status);
        } else if (this.sortField === 'price') {
          comparison = a.price - b.price;
        }
        
        return this.sortDirection === 'asc' ? comparison : -comparison;
      });
      
      return result;
    },
    
    paginatedRequests() {
      const start = (this.currentPage - 1) * this.perPage;
      const end = start + this.perPage;
      return this.filteredRequests.slice(start, end);
    },
    
    totalPages() {
      return Math.ceil(this.filteredRequests.length / this.perPage);
    },
    
    paginationInfo() {
      const from = this.filteredRequests.length === 0 ? 0 : 
        (this.currentPage - 1) * this.perPage + 1;
      const to = Math.min(from + this.perPage - 1, this.filteredRequests.length);
      return { from, to };
    },
    
    activeRequestsCount() {
      return this.requests.filter(request => 
        ['pending', 'accepted', 'in_progress'].includes(request.status)
      ).length;
    }
  },
  created() {
    this.fetchRequests();
    this.fetchServices();
    
    // Check for status filter in URL
    const status = this.$route.query.status;
    if (status) {
      this.statusFilter = status;
      
      if (status === 'completed') {
        this.tabFilter = 'completed';
      } else if (['cancelled', 'rejected'].includes(status)) {
        this.tabFilter = 'cancelled';
      } else {
        this.tabFilter = 'active';
      }
    }
  },
  mounted() {
    // Initialize Bootstrap modals
    this.requestDetailModal = new Modal(document.getElementById('requestDetailModal'));
    this.ratingModal = new Modal(document.getElementById('ratingModal'));
  },
  watch: {
    // Reset pagination when filters change
    statusFilter() { this.currentPage = 1; },
    serviceFilter() { this.currentPage = 1; },
    dateFilter() { this.currentPage = 1; },
    searchQuery() { this.currentPage = 1; },
    tabFilter() { this.currentPage = 1; }
  },
  methods: {
    fetchRequests() {
      this.loading = true;
      
      ApiService.getCustomerServiceRequests()
        .then(response => {
          console.log(response)
          this.requests = response.data || [];
          
          // Add status timeline to each request (mock data for now)
          this.requests.forEach(request => {
            if (!request.status_timeline) {
              request.status_timeline = [
                { 
                  status: 'pending', 
                  timestamp: request.request_date,
                  notes: 'Service request submitted.'
                }
              ];
              
              if (request.status !== 'pending') {
                const acceptedDate = new Date(request.request_date);
                acceptedDate.setHours(acceptedDate.getHours() + 2);
                request.status_timeline.push({
                  status: 'accepted',
                  timestamp: acceptedDate.toISOString(),
                  notes: 'Service request accepted by professional.'
                });
              }
              
              if (request.status === 'in_progress' || request.status === 'completed') {
                const startDate = new Date(request.request_date);
                startDate.setHours(startDate.getHours() + 24);
                request.status_timeline.push({
                  status: 'in_progress',
                  timestamp: startDate.toISOString(),
                  notes: 'Service started.'
                });
              }
              
              if (request.status === 'completed') {
                const completedDate = new Date(request.request_date);
                completedDate.setHours(completedDate.getHours() + 28);
                request.status_timeline.push({
                  status: 'completed',
                  timestamp: completedDate.toISOString(),
                  notes: 'Service completed successfully.'
                });
              }
              
              if (request.status === 'cancelled') {
                const cancelledDate = new Date(request.request_date);
                cancelledDate.setHours(cancelledDate.getHours() + 1);
                request.status_timeline.push({
                  status: 'cancelled',
                  timestamp: cancelledDate.toISOString(),
                  notes: 'Service request cancelled by customer.'
                });
              }
              
              if (request.status === 'rejected') {
                const rejectedDate = new Date(request.request_date);
                rejectedDate.setHours(rejectedDate.getHours() + 4);
                request.status_timeline.push({
                  status: 'rejected',
                  timestamp: rejectedDate.toISOString(),
                  notes: 'Service request rejected by professional.'
                });
              }
            }
          });
        })
        .catch(error => {
          console.error('Error fetching service requests:', error);
          alert('Failed to load service requests. Please try again.');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    fetchServices() {
      ApiService.getServices()
        .then(response => {
          this.services = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching services:', error);
        });
    },
    
    setSorting(field) {
      if (this.sortField === field) {
        this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortField = field;
        this.sortDirection = 'asc';
      }
    },
    
    getSortIconClass(field) {
      if (this.sortField !== field) return 'fa-sort';
      return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },
    
    formatStatus(status) {
      if (!status) return '';
      
      const statusMap = {
        'pending': 'Pending',
        'accepted': 'Accepted',
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'rejected': 'Rejected'
      };
      
      return statusMap[status] || status;
    },
    
    getStatusClass(status) {
      const statusClassMap = {
        'pending': 'bg-warning text-dark',
        'accepted': 'bg-info',
        'in_progress': 'bg-primary',
        'completed': 'bg-success',
        'cancelled': 'bg-secondary',
        'rejected': 'bg-danger'
      };
      
      return statusClassMap[status] || 'bg-secondary';
    },
    
    getTimelineClass(status) {
      const timelineClassMap = {
        'pending': 'bg-warning',
        'accepted': 'bg-info',
        'in_progress': 'bg-primary',
        'completed': 'bg-success',
        'cancelled': 'bg-secondary',
        'rejected': 'bg-danger'
      };
      
      return timelineClassMap[status] || 'bg-secondary';
    },
    
    viewRequest(request) {
      this.selectedRequest = request;
      this.requestDetailModal.show();
    },
    
    
    
    
    rateService(request) {
      this.requestToRate = request;
      this.rating = 0;
      this.review = '';
      this.ratingModal.show();
    },
    
    rateSelectedService() {
      this.requestToRate = this.selectedRequest;
      this.rating = 0;
      this.review = '';
      this.requestDetailModal.hide();
      this.ratingModal.show();
    },
    
    getRatingText() {
      if (!this.rating) return 'Select your rating';
      
      const ratingTexts = [
        '',
        'Poor',
        'Fair',
        'Good',
        'Very Good',
        'Excellent'
      ];
      
      return ratingTexts[this.rating];
    },
    
    submitRating() {
      if (!this.rating) {
        alert('Please select a rating before submitting.');
        return;
      }
      
      this.submittingRating = true;
      
      ApiService.rateServiceRequest(this.requestToRate.id, this.rating, this.review)
        .then(() => {
          // Update the request in the list
          const request = this.requests.find(r => r.id === this.requestToRate.id);
          if (request) {
            request.rating = this.rating;
            request.review = this.review;
            request.is_rated = true;
          }
          
          alert('Thank you for your rating!');
          this.ratingModal.hide();
        })
        .catch(error => {
          console.error('Error submitting rating:', error);
          alert('Failed to submit your rating. Please try again.');
        })
        .finally(() => {
          this.submittingRating = false;
        });
    },
    
    requestCompletion(request) {
      if (confirm(`Are you sure the service for request #${request.id} is complete?`)) {
        ApiService.updateServiceRequestStatus(request.id, 'completed')
          .then(() => {
            request.status = 'completed';
            
            // Add to status timeline
            const now = new Date().toISOString();
            request.status_timeline.push({
              status: 'completed',
              timestamp: now,
              notes: 'Service marked as completed by customer.'
            });
            
            alert('Service marked as completed!');
            
            // Prompt for rating
            this.rateService(request);
          })
          .catch(error => {
            console.error('Error completing service request:', error);
            alert('Failed to mark service as completed. Please try again.');
          });
      }
    },
    
    canRebook(request) {
      return request.status === 'completed' || request.status === 'cancelled' || request.status === 'rejected';
    },
    
    rebookService(request) {
      // Navigate to request service page with service ID
      this.$router.push({
        path: '/customer/request-service',
        query: { service: request.service_id, rebook: request.id }
      });
    },
    
    rebookSelectedService() {
      this.rebookService(this.selectedRequest);
      this.requestDetailModal.hide();
    }
  }
};
</script>

<style scoped>
.request-tabs .nav-link {
  cursor: pointer;
}

.request-tabs .badge {
  margin-left: 5px;
}

.service-requests .table th.sortable-column {
  cursor: pointer;
}

.service-requests .table th.sortable-column:hover {
  background-color: #f8f9fa;
}

.timeline {
  list-style: none;
  padding: 0;
  position: relative;
}

.timeline:before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 20px;
  width: 2px;
  background-color: #e9ecef;
}

.timeline > li {
  position: relative;
  margin-bottom: 20px;
}

.timeline > li:after {
  clear: both;
  content: "";
  display: table;
}

.timeline .timeline-badge {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: absolute;
  left: 15px;
  top: 5px;
  z-index: 1;
}

.timeline .timeline-panel {
  margin-left: 40px;
  position: relative;
  padding-bottom: 20px;
}

.timeline .timeline-title {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1rem;
}

.request-card {
  transition: transform 0.2s;
}

.request-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.1);
}

.rating-container {
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #f8f9fa;
}

.star-rating {
  display: flex;
  justify-content: center;
  gap: 0.5rem;
}

.rating-star {
  font-size: 2rem;
  cursor: pointer;
  color: #dee2e6;
  transition: color 0.2s;
}

.rating-star:hover,
.rating-star.active {
  color: #ffc107;
}

.rating-text {
  font-weight: 600;
  min-height: 1.5rem;
}

.review-text {
  font-style: italic;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 0.5rem;
  position: relative;
}

.review-text:before {
  content: '\201C';
  position: absolute;
  top: 0;
  left: 0.5rem;
  font-size: 2rem;
  color: #dee2e6;
}
</style> 