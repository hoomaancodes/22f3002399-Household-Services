<template>
  <div class="admin-service-requests">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Service Requests Management</h2>
    </div>
    
    <div class="card">
      <div class="card-body">
        <!-- Filter controls -->
        <div class="mb-4 d-flex flex-wrap gap-3">
          <div style="width: 200px;">
            <label for="statusFilter" class="form-label">Status</label>
            <select v-model="filters.status" class="form-select" id="statusFilter">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div style="width: 200px;">
            <label for="serviceFilter" class="form-label">Service</label>
            <select v-model="filters.service_id" class="form-select" id="serviceFilter">
              <option value="">All Services</option>
              <option v-for="service in services" :key="service.id" :value="service.id">
                {{ service.name }}
              </option>
            </select>
          </div>
          
          <div style="width: 200px;">
            <label for="dateRangeFilter" class="form-label">Date Range</label>
            <select v-model="filters.dateRange" class="form-select" id="dateRangeFilter">
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
          
          <div style="width: 250px;">
            <label for="searchInput" class="form-label">Search</label>
            <input 
              v-model="filters.search" 
              type="text" 
              class="form-control" 
              id="searchInput" 
              placeholder="Search requests..."
            >
          </div>
        </div>
        
        <!-- Service requests table -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="filteredRequests.length === 0" class="text-center my-5">
          <p>No service requests found matching the criteria.</p>
        </div>
        
        <div v-else>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th @click="sortBy('id')" class="sortable">
                    ID
                    <i class="fas" :class="getSortIconClass('id')"></i>
                  </th>
                  <th @click="sortBy('service_name')" class="sortable">
                    Service
                    <i class="fas" :class="getSortIconClass('service_name')"></i>
                  </th>
                  <th @click="sortBy('customer_name')" class="sortable">
                    Customer
                    <i class="fas" :class="getSortIconClass('customer_name')"></i>
                  </th>
                  <th @click="sortBy('professional_name')" class="sortable">
                    Professional
                    <i class="fas" :class="getSortIconClass('professional_name')"></i>
                  </th>
                  <th @click="sortBy('status')" class="sortable">
                    Status
                    <i class="fas" :class="getSortIconClass('status')"></i>
                  </th>
                  <th @click="sortBy('created_at')" class="sortable">
                    Request Date
                    <i class="fas" :class="getSortIconClass('created_at')"></i>
                  </th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="request in filteredRequests" :key="request.id">
                  <td>{{ request.id }}</td>
                  <td>{{ request.service_name }}</td>
                  <td>
                    <a href="#" @click.prevent="viewCustomer(request.customer_id)">
                      {{ request.customer_name }}
                    </a>
                  </td>
                  <td>
                    <a 
                      v-if="request.professional_id" 
                      href="#" 
                      @click.prevent="viewProfessional(request.professional_id)"
                    >
                      {{ request.professional_name }}
                    </a>
                    <span v-else class="text-muted">Unassigned</span>
                  </td>
                  <td>
                    <span :class="getStatusBadgeClass(request.status)">
                      {{ request.status }}
                    </span>
                  </td>
                  <td>{{ formatDate(request.created_at) }}</td>
                  <td>
                    <div class="btn-group">
                      <button 
                        @click="viewRequestDetails(request.id)" 
                        class="btn btn-sm btn-outline-primary"
                        title="View Details"
                      >
                        <i class="fas fa-eye"></i>
                      </button>
                      <button 
                        v-if="request.status === 'pending' && !request.professional_id"
                        @click="assignProfessional(request.id)" 
                        class="btn btn-sm btn-outline-success"
                        title="Assign Professional"
                      >
                        <i class="fas fa-user-plus"></i>
                      </button>
                      <button 
                        v-if="['pending', 'in_progress'].includes(request.status)"
                        @click="cancelRequest(request.id)" 
                        class="btn btn-sm btn-outline-danger"
                        title="Cancel Request"
                      >
                        <i class="fas fa-times"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Pagination -->
          <div class="d-flex justify-content-between align-items-center mt-3">
            <div>
              <span>Showing {{ paginatedRequests.length }} of {{ filteredRequests.length }} requests</span>
            </div>
            <nav aria-label="Page navigation">
              <ul class="pagination">
                <li class="page-item" :class="{ disabled: currentPage === 1 }">
                  <a class="page-link" href="#" @click.prevent="currentPage--">Previous</a>
                </li>
                <li 
                  v-for="page in totalPages" 
                  :key="page" 
                  class="page-item"
                  :class="{ active: currentPage === page }"
                >
                  <a class="page-link" href="#" @click.prevent="currentPage = page">{{ page }}</a>
                </li>
                <li class="page-item" :class="{ disabled: currentPage === totalPages }">
                  <a class="page-link" href="#" @click.prevent="currentPage++">Next</a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Request Details Modal -->
    <div v-if="showDetailsModal" class="modal-backdrop" @click="closeDetailsModal"></div>
    <div v-if="showDetailsModal" class="modal-container">
      <div class="modal-content details-modal" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">Service Request Details</h5>
          <button type="button" class="btn-close" @click="closeDetailsModal"></button>
        </div>
        <div class="modal-body" v-if="selectedRequest">
          <div v-if="detailsLoading" class="text-center my-5">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else>
            <div class="row">
              <div class="col-md-6">
                <h6>Request Information</h6>
                <div class="mb-3">
                  <p><strong>ID:</strong> #{{ selectedRequest.id }}</p>
                  <p><strong>Service:</strong> {{ selectedRequest.service_name }}</p>
                  <p><strong>Status:</strong> 
                    <span :class="getStatusBadgeClass(selectedRequest.status)">
                      {{ selectedRequest.status }}
                    </span>
                  </p>
                  <p><strong>Requested:</strong> {{ formatDateTime(selectedRequest.created_at) }}</p>
                  <p v-if="selectedRequest.scheduled_at">
                    <strong>Scheduled For:</strong> {{ formatDateTime(selectedRequest.scheduled_at) }}
                  </p>
                  <p v-if="selectedRequest.completed_at">
                    <strong>Completed:</strong> {{ formatDateTime(selectedRequest.completed_at) }}
                  </p>
                </div>
                
                <h6>Additional Details</h6>
                <div class="card mb-3">
                  <div class="card-body">
                    <p v-if="selectedRequest.description">{{ selectedRequest.description }}</p>
                    <p v-else class="text-muted">No additional details provided.</p>
                  </div>
                </div>
                
                <h6>Address</h6>
                <div class="card mb-3">
                  <div class="card-body">
                    <p>{{ selectedRequest.address }}</p>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <div class="card mb-3">
                  <div class="card-header">Customer Information</div>
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-2">
                      <div class="me-3">
                        <img 
                          :src="selectedRequest.customer && selectedRequest.customer.profile_pic || 'https://via.placeholder.com/50'" 
                          alt="Customer" 
                          class="rounded-circle"
                          width="50" 
                          height="50"
                        >
                      </div>
                      <div>
                        <h6 class="mb-0">{{ selectedRequest.customer_name }}</h6>
                        <p class="mb-0 text-muted">{{ selectedRequest.customer && selectedRequest.customer.email }}</p>
                      </div>
                    </div>
                    <button @click="viewCustomer(selectedRequest.customer_id)" class="btn btn-sm btn-outline-primary">
                      View Profile
                    </button>
                  </div>
                </div>
                
                <div class="card mb-3" v-if="selectedRequest.professional_id">
                  <div class="card-header">Professional Information</div>
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-2">
                      <div class="me-3">
                        <img 
                          :src="selectedRequest.professional && selectedRequest.professional.profile_pic || 'https://via.placeholder.com/50'" 
                          alt="Professional" 
                          class="rounded-circle"
                          width="50" 
                          height="50"
                        >
                      </div>
                      <div>
                        <h6 class="mb-0">{{ selectedRequest.professional_name }}</h6>
                        <p class="mb-0 text-muted">{{ selectedRequest.professional && selectedRequest.professional.email }}</p>
                      </div>
                    </div>
                    <button @click="viewProfessional(selectedRequest.professional_id)" class="btn btn-sm btn-outline-primary">
                      View Profile
                    </button>
                  </div>
                </div>
                
                <div v-if="selectedRequest.status === 'completed' && selectedRequest.rating">
                  <h6>Customer Rating</h6>
                  <div class="card">
                    <div class="card-body">
                      <div class="d-flex mb-2">
                        <div class="me-2" v-for="i in 5" :key="i">
                          <i class="fas fa-star" :class="i <= selectedRequest.rating ? 'text-warning' : 'text-muted'"></i>
                        </div>
                        <div class="ms-1">
                          <strong>{{ selectedRequest.rating }}/5</strong>
                        </div>
                      </div>
                      <p v-if="selectedRequest.review">{{ selectedRequest.review }}</p>
                      <p v-else class="text-muted">No written review provided.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <div class="d-flex w-100 justify-content-between">
            <div>
              <button 
                v-if="selectedRequest && selectedRequest.status === 'pending' && !selectedRequest.professional_id"
                @click="assignProfessional(selectedRequest.id, true)" 
                class="btn btn-success me-2"
              >
                <i class="fas fa-user-plus me-1"></i> Assign Professional
              </button>
              <button 
                v-if="selectedRequest && ['pending', 'in_progress'].includes(selectedRequest.status)"
                @click="cancelRequest(selectedRequest.id, true)" 
                class="btn btn-danger"
              >
                <i class="fas fa-times me-1"></i> Cancel Request
              </button>
            </div>
            <button type="button" class="btn btn-secondary" @click="closeDetailsModal">Close</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Assign Professional Modal -->
    <div v-if="showAssignModal" class="modal-backdrop" @click="closeAssignModal"></div>
    <div v-if="showAssignModal" class="modal-container">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">Assign Professional</h5>
          <button type="button" class="btn-close" @click="closeAssignModal"></button>
        </div>
        <div class="modal-body">
          <div v-if="assignLoading" class="text-center my-5">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else>
            <p>Select a professional to assign to service request #{{ selectedRequestId }}:</p>
            
            <div class="mb-3">
              <label for="professionalSearch" class="form-label">Search Professionals</label>
              <input
                v-model="professionalSearchQuery"
                type="text"
                class="form-control"
                id="professionalSearch"
                placeholder="Search by name..."
              >
            </div>
            
            <div v-if="availableProfessionals.length === 0" class="alert alert-info">
              No professionals available for this service.
            </div>
            
            <div v-else class="list-group">
              <a 
                v-for="professional in filteredProfessionals" 
                :key="professional.id"
                href="#"
                @click.prevent="selectProfessional(professional)"
                class="list-group-item list-group-item-action"
                :class="{ active: selectedProfessionalId === professional.id }"
              >
                <div class="d-flex align-items-center">
                  <div class="me-3">
                    <img
                      :src="professional.profile_pic || 'https://via.placeholder.com/50'"
                      alt="Professional"
                      class="rounded-circle"
                      width="50"
                      height="50"
                    >
                  </div>
                  <div>
                    <h6 class="mb-0">{{ professional.name }}</h6>
                    <p class="mb-0 text-muted">{{ professional.email }}</p>
                    <div>
                      <span class="badge bg-info me-1" v-for="(service, index) in professional.services" :key="index">
                        {{ getServiceName(service) }}
                      </span>
                    </div>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" @click="closeAssignModal">Cancel</button>
          <button 
            type="button" 
            class="btn btn-primary" 
            :disabled="!selectedProfessionalId || saving"
            @click="confirmAssignment"
          >
            <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
            Assign Professional
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
  name: 'AdminServiceRequests',
  data() {
    return {
      requests: [],
      services: [],
      loading: false,
      detailsLoading: false,
      assignLoading: false,
      saving: false,
      showDetailsModal: false,
      showAssignModal: false,
      selectedRequest: null,
      selectedRequestId: null,
      selectedProfessionalId: null,
      availableProfessionals: [],
      professionalSearchQuery: '',
      filters: {
        status: '',
        service_id: '',
        dateRange: 'all',
        search: ''
      },
      sortKey: 'created_at',
      sortOrder: 'desc',
      currentPage: 1,
      pageSize: 10
    };
  },
  computed: {
    filteredRequests() {
      let result = this.requests;
      
      // Check if requests is an array before proceeding
      if (!Array.isArray(result)) {
        console.warn('Expected requests to be an array but got:', result);
        result = []; // Default to empty array if not an array
      } else {
        result = [...result]; // Create a copy if it's an array
      }
      
      // Apply status filter
      if (this.filters.status) {
        result = result.filter(request => request.status === this.filters.status);
      }
      
      // Apply service filter
      if (this.filters.service_id) {
        const serviceId = parseInt(this.filters.service_id);
        result = result.filter(request => request.service_id === serviceId);
      }
      
      // Apply date range filter
      if (this.filters.dateRange !== 'all') {
        const now = new Date();
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
        
        switch(this.filters.dateRange) {
          case 'today':
            result = result.filter(request => {
              const requestDate = new Date(request.created_at);
              return requestDate >= today;
            });
            break;
          case 'week':
            {
              const weekStart = new Date(today);
              weekStart.setDate(today.getDate() - today.getDay());
              result = result.filter(request => {
                const requestDate = new Date(request.created_at);
                return requestDate >= weekStart;
              });
            }
            break;
          case 'month':
            {
              const monthStart = new Date(today.getFullYear(), today.getMonth(), 1);
              result = result.filter(request => {
                const requestDate = new Date(request.created_at);
                return requestDate >= monthStart;
              });
            }
            break;
        }
      }
      
      // Apply search query
      if (this.filters.search) {
        const query = this.filters.search.toLowerCase();
        result = result.filter(request => 
          (request.customer_name && request.customer_name.toLowerCase().includes(query)) ||
          (request.professional_name && request.professional_name.toLowerCase().includes(query)) ||
          (request.service_name && request.service_name.toLowerCase().includes(query)) ||
          (request.id.toString().includes(query))
        );
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let aValue = a[this.sortKey];
        let bValue = b[this.sortKey];
        
        // Handle date fields
        if (this.sortKey === 'created_at' || this.sortKey === 'completed_at' || this.sortKey === 'scheduled_at') {
          aValue = aValue ? new Date(aValue).getTime() : 0;
          bValue = bValue ? new Date(bValue).getTime() : 0;
        }
        // Handle numeric fields
        else if (this.sortKey === 'id') {
          aValue = parseInt(aValue);
          bValue = parseInt(bValue);
        }
        // Handle string fields
        else {
          aValue = String(aValue || '').toLowerCase();
          bValue = String(bValue || '').toLowerCase();
        }
        
        if (this.sortOrder === 'asc') {
          return aValue > bValue ? 1 : -1;
        } else {
          return aValue < bValue ? 1 : -1;
        }
      });
      
      return result;
    },
    
    paginatedRequests() {
      const startIndex = (this.currentPage - 1) * this.pageSize;
      return this.filteredRequests.slice(startIndex, startIndex + this.pageSize);
    },
    
    totalPages() {
      return Math.ceil(this.filteredRequests.length / this.pageSize);
    },
    
    filteredProfessionals() {
      if (!this.professionalSearchQuery) {
        return this.availableProfessionals;
      }
      
      const query = this.professionalSearchQuery.toLowerCase();
      return this.availableProfessionals.filter(professional => 
        professional.name.toLowerCase().includes(query) ||
        professional.email.toLowerCase().includes(query)
      );
    }
  },
  created() {
    this.fetchRequests();
    this.fetchServices();
    
    // Check URL for parameters
    const urlParams = new URLSearchParams(window.location.search);
    const viewId = urlParams.get('view');
    if (viewId) {
      this.viewRequestDetails(Number(viewId));
    }
  },
  watch: {
    'filters.status'() {
      this.currentPage = 1;
    },
    'filters.service_id'() {
      this.currentPage = 1;
    },
    'filters.dateRange'() {
      this.currentPage = 1;
    },
    'filters.search'() {
      this.currentPage = 1;
    }
  },
  methods: {
    fetchRequests() {
      this.loading = true;
      ApiService.getServiceRequests()
        .then(response => {
          // Ensure the response is an array
          if (Array.isArray(response.data)) {
            this.requests = response.data;
          } else if (response.data && typeof response.data === 'object') {
            // If it's an object with nested data array
            if (Array.isArray(response.data.requests)) {
              this.requests = response.data.requests;
            } else if (Array.isArray(response.data.data)) {
              this.requests = response.data.data;
            } else {
              console.error('Unexpected response format:', response.data);
              this.requests = [];
            }
          } else {
            console.error('Invalid response data format:', response.data);
            this.requests = [];
          }
        })
        .catch(error => {
          console.error('Error fetching service requests:', error);
          alert('Failed to load service requests. Please try again.');
          this.requests = [];
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
    
    viewRequestDetails(requestId) {
      this.detailsLoading = true;
      this.showDetailsModal = true;
      
      ApiService.getServiceRequestById(requestId)
        .then(response => {
          this.selectedRequest = response.data;
        })
        .catch(error => {
          console.error('Error fetching request details:', error);
          alert('Failed to load request details. Please try again.');
          this.closeDetailsModal();
        })
        .finally(() => {
          this.detailsLoading = false;
        });
    },
    
    assignProfessional(requestId, closeDetailsModal = false) {
      this.selectedRequestId = requestId;
      if (closeDetailsModal) {
        this.closeDetailsModal();
      }
      
      this.assignLoading = true;
      this.showAssignModal = true;
      
      ApiService.getAvailableProfessionals(requestId)
        .then(response => {
          this.availableProfessionals = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching available professionals:', error);
          alert('Failed to load available professionals. Please try again.');
          this.closeAssignModal();
        })
        .finally(() => {
          this.assignLoading = false;
        });
    },
    
    selectProfessional(professional) {
      this.selectedProfessionalId = professional.id;
    },
    
    confirmAssignment() {
      if (!this.selectedProfessionalId || !this.selectedRequestId) {
        return;
      }
      
      this.saving = true;
      
      ApiService.assignProfessional(this.selectedRequestId, this.selectedProfessionalId)
        .then(() => {
          alert('Professional assigned successfully!');
          
          // Update request in the list
          const index = this.requests.findIndex(r => r.id === this.selectedRequestId);
          if (index !== -1) {
            const professional = this.availableProfessionals.find(p => p.id === this.selectedProfessionalId);
            if (professional) {
              this.requests[index].professional_id = professional.id;
              this.requests[index].professional_name = professional.name;
            }
          }
          
          this.closeAssignModal();
          this.fetchRequests(); // Refresh the data
        })
        .catch(error => {
          console.error('Error assigning professional:', error);
          alert('Failed to assign professional. Please try again.');
        })
        .finally(() => {
          this.saving = false;
        });
    },
    
    cancelRequest(requestId, closeDetailsModal = false) {
      if (confirm('Are you sure you want to cancel this service request?')) {
        ApiService.cancelServiceRequest(requestId)
          .then(() => {
            alert('Service request cancelled successfully!');
            
            // Update request status in our data
            const index = this.requests.findIndex(r => r.id === requestId);
            if (index !== -1) {
              this.requests[index].status = 'cancelled';
            }
            
            // Update selected request if in modal
            if (this.selectedRequest && this.selectedRequest.id === requestId) {
              this.selectedRequest.status = 'cancelled';
            }
            
            if (closeDetailsModal) {
              this.closeDetailsModal();
            }
          })
          .catch(error => {
            console.error('Error cancelling request:', error);
            alert('Failed to cancel request. Please try again.');
          });
      }
    },
    
    viewCustomer(customerId) {
      this.$router.push({ path: '/admin/customers', query: { view: customerId } });
    },
    
    viewProfessional(professionalId) {
      this.$router.push({ path: '/admin/professionals', query: { view: professionalId } });
    },
    
    closeDetailsModal() {
      this.showDetailsModal = false;
      this.selectedRequest = null;
    },
    
    closeAssignModal() {
      this.showAssignModal = false;
      this.selectedRequestId = null;
      this.selectedProfessionalId = null;
      this.availableProfessionals = [];
      this.professionalSearchQuery = '';
    },
    
    getServiceName(service) {
      if (typeof service === 'object' && service.name) {
        return service.name;
      }
      
      const serviceId = typeof service === 'object' ? service.id : service;
      const foundService = this.services.find(s => s.id === serviceId);
      return foundService ? foundService.name : `Service #${serviceId}`;
    },
    
    getStatusBadgeClass(status) {
      switch(status) {
        case 'pending':
          return 'badge bg-warning';
        case 'in_progress':
          return 'badge bg-primary';
        case 'completed':
          return 'badge bg-success';
        case 'cancelled':
          return 'badge bg-danger';
        default:
          return 'badge bg-secondary';
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    
    formatDateTime(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return `${date.toLocaleDateString()} ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
    },
    
    sortBy(key) {
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        this.sortKey = key;
        this.sortOrder = 'asc';
      }
    },
    
    getSortIconClass(key) {
      if (this.sortKey !== key) {
        return 'fa-sort';
      }
      return this.sortOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    }
  }
};
</script>

<style scoped>
.sortable {
  cursor: pointer;
}

.details-modal {
  width: 800px;
  max-width: 90%;
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
  background-color: white;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  max-width: 90%;
  width: 600px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-body {
  padding: 1rem;
  max-height: 70vh;
  overflow-y: auto;
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.me-1 {
  margin-right: 0.25rem;
}

.me-2 {
  margin-right: 0.5rem;
}

.me-3 {
  margin-right: 1rem;
}

.badge {
  text-transform: capitalize;
}
</style>