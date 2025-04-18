<template>
  <div class="admin-customers">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Customers Management</h2>
    </div>
    
    <div class="card">
      <div class="card-body">
        <!-- Filter controls -->
        <div class="mb-4 d-flex">
          <div class="me-3" style="width: 200px;">
            <label for="statusFilter" class="form-label">Filter by Status</label>
            <select v-model="statusFilter" class="form-select" id="statusFilter">
              <option value="">All Status</option>
              <option value="active">Active</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
          <div style="width: 250px;">
            <label for="searchInput" class="form-label">Search</label>
            <input 
              v-model="searchQuery" 
              type="text" 
              class="form-control" 
              id="searchInput" 
              placeholder="Search by name or email..."
            >
          </div>
        </div>
        
        <!-- Customers table -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="filteredCustomers.length === 0" class="text-center my-5">
          <p>No customers found matching the criteria.</p>
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
                  <th @click="sortBy('name')" class="sortable">
                    Name
                    <i class="fas" :class="getSortIconClass('name')"></i>
                  </th>
                  <th @click="sortBy('email')" class="sortable">
                    Email
                    <i class="fas" :class="getSortIconClass('email')"></i>
                  </th>
                  <th @click="sortBy('phone')" class="sortable">
                    PIN
                    <i class="fas" :class="getSortIconClass('phone')"></i>
                  </th>
                  <th @click="sortBy('address')" class="sortable">
                    Address
                    <i class="fas" :class="getSortIconClass('total_requests')"></i>
                  </th>
                  <th @click="sortBy('total_requests')" class="sortable">
                    Total Requests
                    <i class="fas" :class="getSortIconClass('total_requests')"></i>
                  </th>
                  <th @click="sortBy('status')" class="sortable">
                    Status
                    <i class="fas" :class="getSortIconClass('status')"></i>
                  </th>
                  <th>Joined Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="customer in filteredCustomers" :key="customer.id">
                  <td>{{ customer.id }}</td>
                  <td>{{ customer.name }}</td>
                  <td>{{ customer.email }}</td>
                  <td>{{ customer.pin }}</td>
                  <td>{{ customer.address }}</td>
                  <td>{{ customer.stats.total_requests || 0 }}</td>
                  <td>
                    <span :class="getStatusClass(customer.blocked?'blocked':'active')">
                      {{ customer.blocked?'blocked':'active' }}
                    </span>
                  </td>
                  <td>{{ formatDate(customer.created_date) }}</td>
                  <td>
                    <div class="btn-group">
                      <button @click="viewProfile(customer.id)" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button 
                        v-if="!customer.blocked" 
                        @click="blockCustomer(customer.id)" 
                        class="btn btn-sm btn-outline-danger"
                        title="Block"
                      >
                        <i class="fas fa-ban"></i>
                      </button>
                      <button 
                        v-else
                        @click="unblockCustomer(customer.id)" 
                        class="btn btn-sm btn-outline-warning"
                        title="Unblock"
                      >
                        <i class="fas fa-unlock"></i>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Customer Profile Modal -->
    <div v-if="showProfileModal" class="modal-backdrop" @click="closeProfileModal"></div>
    <div v-if="showProfileModal" class="modal-container">
      <div class="modal-content profile-modal" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">Customer Profile</h5>
          <button type="button" class="btn-close" @click="closeProfileModal"></button>
        </div>
        <div class="modal-body" v-if="selectedCustomer">
          <div v-if="profileLoading" class="text-center my-5">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          
          <div v-else>
            <div class="row">
              <div class="col-md-4 text-center mb-3">
                <div class="avatar-container">
                  <img 
                    src="../../assets/customer.jpg" 
                    alt="Profile Picture"
                    class="img-fluid rounded-circle profile-pic"
                  >
                </div>
                <h5 class="mt-2">{{ selectedCustomer.name }}</h5>
                <p class="text-muted">{{ selectedCustomer.email }}</p>
                <span :class="getStatusClass(selectedCustomer.blocked?'blocked':'active')">
                  {{ selectedCustomer.blocked?'blocked':'active'}}
                </span>
              </div>
              
              <div class="col-md-8">
                <h6>Personal Information</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <p><strong>Pin:</strong> {{ selectedCustomer.pin }}</p>
                    <p><strong>Address:</strong> {{ selectedCustomer.address }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Joined:</strong> {{ formatDate(selectedCustomer.created_date) }}</p>
                  </div>
                </div>
                
                
              </div>
            </div>
            
            <div class="mt-4">
              <h6>Recent Service Requests</h6>
              <div class="table-responsive">
                <table class="table table-sm table-striped">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Service</th>
                      <th>Professional</th>
                      <th>Status</th>
                      <th>Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="request in selectedCustomer.recent_requests" :key="request.id">
                      <td>{{ request.id }}</td>
                      <td>{{ request.service }}</td>
                      <td>{{ request.professional || 'Unassigned' }}</td>
                      <td>
                        <span :class="getRequestStatusClass(request.status)">
                          {{ request.status }}
                        </span>
                      </td>
                      <td>{{ formatDate(request.date) }}</td>
                    </tr>
                    <tr v-if="!selectedCustomer.recent_requests || selectedCustomer.recent_requests.length === 0">
                      <td colspan="5" class="text-center">No recent service requests</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="row mt-4">
              <div class="col-md-6">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-title">Customer Metrics</h6>
                    <div class="d-flex justify-content-between mb-2">
                      <span>Total Requests:</span>
                      <span>{{ selectedCustomer.stats.total_requests || 0 }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                      <span>Completed Requests:</span>
                      <span>{{ selectedCustomer.stats.completed_requests || 0 }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                      <span>Cancelled Requests:</span>
                      <span>{{ selectedCustomer.stats.cancelled_requests || 0 }}</span>
                    </div>
                    
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="card">
                  <div class="card-body">
                    <h6 class="card-title">Account Activity</h6>
                    <div class="d-flex justify-content-between mb-2">
                      <span>Last Login:</span>
                      <span>{{ formatDate(selectedCustomer.last_login) || 'N/A' }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                      <span>Last Request:</span>
                      <span>{{ formatDate(selectedCustomer.last_request_date) || 'N/A' }}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                      <span>Account Status:</span>
                      <span :class="getStatusClass(selectedCustomer.blocked?'blocked':'active')">
                        {{selectedCustomer.blocked?'blocked':'active'}}
                      </span>
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
                v-if="selectedCustomer && selectedCustomer.blocked"
                @click="unblockCustomer(selectedCustomer.id, true)" 
                class="btn btn-warning"
              >
                <i class="fas fa-unlock me-1"></i> Unblock Customer
              </button>
              <button 
                v-else-if="selectedCustomer && !selectedCustomer.blocked"
                @click="blockCustomer(selectedCustomer.id, true)" 
                class="btn btn-danger"
              >
                <i class="fas fa-ban me-1"></i> Block Customer
              </button>
            </div>
            <button type="button" class="btn btn-secondary" @click="closeProfileModal">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
  name: 'AdminCustomers',
  data() {
    return {
      customers: [],
      loading: false,
      profileLoading: false,
      showProfileModal: false,
      selectedCustomer: null,
      statusFilter: '',
      searchQuery: '',
      sortKey: 'id',
      sortOrder: 'asc'
    };
  },
  computed: {
    filteredCustomers() {
      let result = [...this.customers];
      
      // Apply status filter
      if (this.statusFilter) {
        console.log(this.statusFilter)
        result = result.filter(customer => customer.blocked?'blocked':'active' === this.statusFilter.toLowerCase());
      }
      
      // Apply search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(customer => 
          customer.name.toLowerCase().includes(query) || 
          customer.email.toLowerCase().includes(query) ||
          (customer.phone && customer.phone.includes(query))
        );
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let aValue = a[this.sortKey];
        let bValue = b[this.sortKey];
        
        // Handle numeric fields
        if (this.sortKey === 'id' || this.sortKey === 'total_requests') {
          aValue = parseInt(aValue || 0);
          bValue = parseInt(bValue || 0);
        } else {
          // Handle string fields
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
    }
  },
  created() {
    this.fetchCustomers();
    
    // Check URL for view parameter to open profile directly
    const urlParams = new URLSearchParams(window.location.search);
    const viewId = urlParams.get('view');
    if (viewId) {
      this.viewProfile(Number(viewId));
    }
  },
  methods: {
    fetchCustomers() {
      this.loading = true;
      ApiService.getCustomers()
        .then(response => {
          console.log(response.data.customers)
          this.customers = response.data.customers || [];
        })
        .catch(error => {
          console.error('Error fetching customers:', error);
          alert('Failed to load customers. Please try again.');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    viewProfile(customerId) {
      this.profileLoading = true;
      this.showProfileModal = true;
      
      ApiService.getCustomerById(customerId)
        .then(response => {
          this.selectedCustomer = response.data;
        })
        .catch(error => {
          console.error('Error fetching customer profile:', error);
          alert('Failed to load customer profile. Please try again.');
          this.closeProfileModal();
        })
        .finally(() => {
          this.profileLoading = false;
        });
    },
    
    blockCustomer(customerId, closeModalAfter = false) {
      if (confirm('Are you sure you want to block this customer?')) {
        ApiService.blockCustomer(customerId)
          .then(() => {
            alert('Customer blocked successfully!');
            
            // Update the customer's status in our data
            const index = this.customers.findIndex(c => c.id === customerId);
            if (index !== -1) {
              this.customers[index].status = 'blocked';
            }
            
            // Update selected customer if in modal
            if (this.selectedCustomer && this.selectedCustomer.id === customerId) {
              this.selectedCustomer.status = 'blocked';
            }
            
            if (closeModalAfter) {
              this.closeProfileModal();
            }
            this.fetchCustomers()
          })
          .catch(error => {
            console.error('Error blocking customer:', error);
            alert('Failed to block customer. Please try again.');
          });
      }
    },
    
    unblockCustomer(customerId, closeModalAfter = false) {
      if (confirm('Are you sure you want to unblock this customer?')) {
        ApiService.unblockCustomer(customerId)
          .then(() => {
            alert('Customer unblocked successfully!');
            
            // Update the customer's status in our data
            const index = this.customers.findIndex(c => c.id === customerId);
            if (index !== -1) {
              this.customers[index].status = 'active';
            }
            
            // Update selected customer if in modal
            if (this.selectedCustomer && this.selectedCustomer.id === customerId) {
              this.selectedCustomer.status = 'active';
            }
            
            if (closeModalAfter) {
              this.closeProfileModal();
            }
            this.fetchCustomers()
          })
          .catch(error => {
            console.error('Error unblocking customer:', error);
            alert('Failed to unblock customer. Please try again.');
          });
      }
    },
    
    closeProfileModal() {
      this.showProfileModal = false;
      this.selectedCustomer = null;
    },
    
    getStatusClass(status) {
      switch(status) {
        case 'active':
          return 'badge bg-success';
        case 'blocked':
          return 'badge bg-danger';
        default:
          return 'badge bg-secondary';
      }
    },
    
    getRequestStatusClass(status) {
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

.avatar-container {
  width: 120px;
  height: 120px;
  margin: 0 auto;
  overflow: hidden;
}

.profile-pic {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-modal {
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
}

.modal-footer {
  padding: 1rem;
  border-top: 1px solid #dee2e6;
}

.me-1 {
  margin-right: 0.25rem;
}

.badge {
  padding: 0.5em 0.75em;
}
</style> 