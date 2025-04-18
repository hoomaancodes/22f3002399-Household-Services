<template>
  <div class="professional-service-requests">
    <h2>Service Requests</h2>
    
    <!-- Filter and Search -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">

          <div class="col-md-3">
            <label for="searchQuery" class="form-label">Search</label>
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                id="searchQuery" 
                v-model="searchQuery" 
                placeholder="Search by name or ID..."
              >
              <button class="btn btn-outline-secondary" type="button">
                <i class="fas fa-search"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
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
        <div v-if="tabFilter === 'new'">
          <p class="text-muted">You don't have any new service requests at the moment.</p>
        </div>
      </div>
      
      <div v-else class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr>
              <th @click="setSorting('id')" class="sortable-column">
                ID <i class="fas" :class="getSortIconClass('id')"></i>
              </th>
              <th @click="setSorting('service')" class="sortable-column">
                Service <i class="fas" :class="getSortIconClass('service')"></i>
              </th>
              <th @click="setSorting('customer')" class="sortable-column">
                Customer <i class="fas" :class="getSortIconClass('customer')"></i>
              </th>
              <th @click="setSorting('date')" class="sortable-column">
                Date <i class="fas" :class="getSortIconClass('date')"></i>
              </th>
              <th @click="setSorting('status')" class="sortable-column">
                Status <i class="fas" :class="getSortIconClass('status')"></i>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in paginatedRequests" :key="request.id">
              <td>#{{ request.id }}</td>
              <td>{{ request.service_name }}</td>
              <td>{{ request.customer_name }}</td>
              <td>{{ formatDate(request.req_date) }}</td>
              <td>
                <span class="badge" :class="getStatusClass(request.status)">
                  {{ formatStatus(request.status) }}
                </span>
              </td>
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
                    v-if="request.status === 'requested'"
                    class="btn btn-outline-success"
                    @click="acceptRequest(request)"
                    title="Accept Request"
                  >
                    <i class="fas fa-check"></i>
                  </button>
                  
                  <button 
                    v-if="request.status === 'requested'"
                    class="btn btn-outline-danger"
                    @click="rejectRequest(request)"
                    title="Reject Request"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                  
                  <button 
                    v-if="request.status === 'assigned'"
                    class="btn btn-outline-info"
                    @click="completeService(request)"
                    title="Complete Service"
                  >
                    <i class="fas fa-check-double"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div v-if="!loading && filteredRequests.length > 0" class="d-flex justify-content-between align-items-center mt-4">
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
                      <th>Scheduled For:</th>
                      <td>{{ formatDate(selectedRequest.req_date) }}</td>
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
                <h6>Customer Information</h6>
                <table class="table table-borderless table-sm">
                  <tbody>
                    <tr>
                      <th>Name:</th>
                      <td>{{ selectedRequest.customer_name }}</td>
                    </tr>
                    <tr>
                      <th>Pin:</th>
                      <td>{{ selectedRequest.customer_pin }}</td>
                    </tr>
                    
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="row mt-4">
              <div class="col-12">
                <h6>Service Location</h6>
                <p>{{ selectedRequest.customer_address }}</p>
                
                <h6>Special Instructions</h6>
                <p v-if="selectedRequest.remarks">{{ selectedRequest.remarks }}</p>
                <p v-else class="text-muted">No special instructions provided.</p>
                
                
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            
            <button 
              v-if="selectedRequest.status === 'pending'"
              class="btn btn-success me-2"
              @click="acceptSelectedRequest"
            >
              Accept Request
            </button>
            
            <button 
              v-if="selectedRequest.status === 'pending'"
              class="btn btn-danger me-2"
              @click="rejectSelectedRequest"
            >
              Reject Request
            </button>
            
            <button 
              v-if="selectedRequest.status === 'accepted'"
              class="btn btn-primary me-2"
              @click="startSelectedService"
            >
              Start Service
            </button>
            
            <button 
              v-if="selectedRequest.status === 'in_progress'"
              class="btn btn-primary me-2"
              @click="completeSelectedService"
            >
              Complete Service
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
  name: 'ProfessionalServiceRequests',
  data() {
    return {
      requests: [],
      myServices: [],
      loading: true,
      statusFilter: '',
      serviceFilter: '',
      dateFilter: '',
      searchQuery: '',
      tabFilter: 'all',
      sortField: 'date',
      sortDirection: 'desc',
      currentPage: 1,
      perPage: 10,
      selectedRequest: null,
      requestDetailModal: null
    };
  },
  computed: {
    filteredRequests() {
      if (!this.requests.length) return [];
      
      let result = [...this.requests];
      
      // Apply tab filter
      if (this.tabFilter === 'new') {
        result = result.filter(request => request.status === 'pending');
      } else if (this.tabFilter === 'ongoing') {
        result = result.filter(request => 
          request.status === 'accepted' || request.status === 'in_progress'
        );
      } else if (this.tabFilter === 'completed') {
        result = result.filter(request => request.status === 'completed');
      }
      
      
      
      // Apply service filter if selected
      if (this.serviceFilter) {
        console.log(this.serviceFilter)
        result = result.filter(request => request.service_type === this.serviceFilter);
      }
      
      
      
      // Apply search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(request => 
          request.id.toString().includes(query) ||
          request.customer_name.toLowerCase().includes(query) ||
          request.service_name.toLowerCase().includes(query)
        );
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let comparison = 0;
        
        if (this.sortField === 'id') {
          comparison = a.id - b.id;
        } else if (this.sortField === 'service') {
          comparison = a.service_name.localeCompare(b.service_name);
        } else if (this.sortField === 'customer') {
          comparison = a.customer_name.localeCompare(b.customer_name);
        } else if (this.sortField === 'date') {
          comparison = new Date(a.request_date) - new Date(b.request_date);
        } else if (this.sortField === 'status') {
          comparison = a.status.localeCompare(b.status);
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
    
    newRequestsCount() {
      return this.requests.filter(request => request.status === 'pending').length;
    },
    
    ongoingRequestsCount() {
      return this.requests.filter(request => 
        request.status === 'accepted' || request.status === 'in_progress'
      ).length;
    }
  },
  created() {
    this.fetchRequests();
    
  },
  mounted() {
    // Initialize Bootstrap modal
    this.requestDetailModal = new Modal(document.getElementById('requestDetailModal'));
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
      
      ApiService.getServiceRequests({ role: 'professional' })
        .then(response => {
          
          this.requests = response.data.requests || [];
          
          // Initialize status_timeline for each request
          this.requests.forEach(request => {
            if (!request.status_timeline) {
              request.status_timeline = [];
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
    
    acceptRequest(request) {
      if (confirm(`Are you sure you want to accept service request #${request.id}?`)) {
        ApiService.acceptServiceRequest(request.id)
          .then(() => {
            request.status = 'accepted';
            
            // Initialize status_timeline if it doesn't exist
            if (!request.status_timeline) {
              request.status_timeline = [];
            }
            
            // Add to status timeline
            const now = new Date().toISOString();
            request.status_timeline.push({
              status: 'accepted',
              timestamp: now,
              notes: 'Service request accepted by professional.'
            });
            
            alert('Service request accepted successfully!');
          })
          .catch(error => {
            console.error('Error accepting service request:', error);
            alert('Failed to accept service request. Please try again.');
          });
      }
    },
    
    rejectRequest(request) {
      if (confirm(`Are you sure you want to reject service request #${request.id}?`)) {
        ApiService.rejectServiceRequest(request.id)
          .then(() => {
            request.status = 'rejected';
            
            // Initialize status_timeline if it doesn't exist
            if (!request.status_timeline) {
              request.status_timeline = [];
            }
            
            // Add to status timeline
            const now = new Date().toISOString();
            request.status_timeline.push({
              status: 'rejected',
              timestamp: now,
              notes: 'Service request rejected by professional.'
            });
            
            alert('Service request rejected.');
          })
          .catch(error => {
            console.error('Error rejecting service request:', error);
            alert('Failed to reject service request. Please try again.');
          });
      }
    },
    
    
    
    completeService(request) {
      if (confirm(`Are you sure you want to mark service request #${request.id} as completed?`)) {
        ApiService.completeServiceRequest(request.id)
          .then(() => {
            request.status = 'completed';
            
            // Initialize status_timeline if it doesn't exist
            if (!request.status_timeline) {
              request.status_timeline = [];
            }
            
            // Add to status timeline
            const now = new Date().toISOString();
            request.status_timeline.push({
              status: 'completed',
              timestamp: now,
              notes: 'Service completed successfully.'
            });
            
            alert('Service marked as completed!');
          })
          .catch(error => {
            console.error('Error completing service:', error);
            alert('Failed to complete service. Please try again.');
          });
      }
    },
    
    startService(request) {
      if (confirm(`Are you sure you want to start service for request #${request.id}?`)) {
        // Update the request status to in_progress
        // This would typically call an API endpoint, but it seems there's no direct endpoint for this
        // So we're using the updateServiceRequest endpoint to change the status
        ApiService.updateServiceRequest(request.id, { status: 'in_progress' })
          .then(() => {
            request.status = 'in_progress';
            
            // Initialize status_timeline if it doesn't exist
            if (!request.status_timeline) {
              request.status_timeline = [];
            }
            
            // Add to status timeline
            const now = new Date().toISOString();
            request.status_timeline.push({
              status: 'in_progress',
              timestamp: now,
              notes: 'Service started by professional.'
            });
            
            alert('Service started successfully!');
          })
          .catch(error => {
            console.error('Error starting service:', error);
            alert('Failed to start service. Please try again.');
          });
      }
    },
    
    acceptSelectedRequest() {
      this.acceptRequest(this.selectedRequest);
      this.requestDetailModal.hide();
    },
    
    rejectSelectedRequest() {
      this.rejectRequest(this.selectedRequest);
      this.requestDetailModal.hide();
    },
    
    startSelectedService() {
      this.startService(this.selectedRequest);
      this.requestDetailModal.hide();
    },
    
    completeSelectedService() {
      this.completeService(this.selectedRequest);
      this.requestDetailModal.hide();
    }
  }
};
</script>

<style scoped>
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

.request-tabs .nav-link {
  cursor: pointer;
}

.request-tabs .badge {
  margin-left: 5px;
}
</style> 