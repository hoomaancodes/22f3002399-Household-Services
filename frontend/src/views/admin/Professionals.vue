<template>
  <div class="admin-professionals">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Professionals Management</h2>
    </div>
    
    <div class="card">
      <div class="card-body">
        <!-- Filter controls -->
        <div class="mb-4 d-flex">
          <div class="me-3" style="width: 200px;">
            <label for="statusFilter" class="form-label">Filter by Status</label>
            <select v-model="statusFilter" class="form-select" id="statusFilter">
              <option value="">All Status</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
          <div class="me-3" style="width: 200px;">
            <label for="serviceFilter" class="form-label">Filter by Service</label>
            <select v-model="serviceFilter" class="form-select" id="serviceFilter">
              <option value="">All Services</option>
              <option v-for="service in services" :key="service.id" :value="service.service_type">
                {{ service.service_type }}
              </option>
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
        
        <!-- Professionals table -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="filteredProfessionals.length === 0" class="text-center my-5">
          <p>No professionals found matching the criteria.</p>
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
                    Phone
                    <i class="fas" :class="getSortIconClass('phone')"></i>
                  </th>
                  <th>Services</th>
                  <th @click="sortBy('status')" class="sortable">
                    Status
                    <i class="fas" :class="getSortIconClass('status')"></i>
                  </th>
                  <th>Joined Date</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="professional in filteredProfessionals" :key="professional.id">
                  <td>{{ professional.id }}</td>
                  <td>{{ professional.name }}</td>
                  <td>{{ professional.email }}</td>
                  <td>{{ professional.mobile }}</td>
                  <td>
                    <span  class="badge bg-info me-1">
                      {{professional.service_type }}
                    </span>
                  </td>
                  <td>
                    <span :class="getStatusClass((!professional.approved)?'pending':(professional.blocked)?'blocked':'approved')">
                      {{ (!professional.approved)?'pending':(professional.blocked)?'blocked':'approved' }}
                    </span>
                  </td>
                  <td>{{ formatDate(professional.created_date) }}</td>
                  <td>
                    <div class="btn-group">
                      <button @click="viewProfile(professional.id)" class="btn btn-sm btn-outline-primary">
                        <i class="fas fa-eye"></i>
                      </button>
                      <button 
                        v-if="!professional.approved" 
                        @click="approveProfessional(professional.id)" 
                        class="btn btn-sm btn-outline-success"
                        title="Approve"
                      >
                        <i class="fas fa-check"></i>
                      </button>
                      <button 
                        v-if="! professional.blocked" 
                        @click="blockProfessional(professional.id)" 
                        class="btn btn-sm btn-outline-danger"
                        title="Block"
                      >
                        <i class="fas fa-ban"></i>
                      </button>
                      <button 
                        v-else
                        @click="unblockProfessional(professional.id)" 
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
    
    <!-- Professional Profile Modal -->
    <div v-if="showProfileModal" class="modal-backdrop" @click="closeProfileModal"></div>
    <div v-if="showProfileModal" class="modal-container">
      <div class="modal-content profile-modal" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">Professional Profile</h5>
          <button type="button" class="btn-close" @click="closeProfileModal"></button>
        </div>
        <div class="modal-body" v-if="selectedProfessional">
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
                <h5 class="mt-2">{{ selectedProfessional.name }}</h5>
                <p class="text-muted">{{ selectedProfessional.email }}</p>
                <span :class="getStatusClass((!selectedProfessional.approved)?'pending':(selectedProfessional.blocked)?'blocked':'approved')">
                  {{(!selectedProfessional.approved)?'pending':(selectedProfessional.blocked)?'blocked':'approved' }}
                </span>
              </div>
              
              <div class="col-md-8">
                <h6>Personal Information</h6>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <p><strong>Pin:</strong> {{ selectedProfessional.pin }}</p>
                    <p><strong>Phone:</strong> {{ selectedProfessional.mobile }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Joined:</strong> {{ formatDate(selectedProfessional.created_date) }}</p>
                    <p><strong>Experience:</strong> {{ selectedProfessional.experience }}</p>
                  </div>
                </div>
                
                <h6>Services Offered</h6>
                <div class="mb-3">
                  <span 
                    
                    class="badge bg-info me-1 mb-1"
                  >
                    {{ selectedProfessional.service_type }}
                  </span>
                </div>
                
                <h6>Professional Bio</h6>
                <p>{{ selectedProfessional.description  }}</p>
                
               
              </div>
            </div>
            
            <div class="mt-4">
              <h6>Performance</h6>
              <div class="row">
                <div class="col-md-3 mb-2">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3>{{ selectedProfessional.stats.average_rating|| 'N/A' }}</h3>
                      <p class="mb-0">Average Rating</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 mb-2">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3>{{ selectedProfessional.stats.completed_requests || 0 }}</h3>
                      <p class="mb-0">Completed</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 mb-2">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3>{{ selectedProfessional.stats.ongoing_requests || 0 }}</h3>
                      <p class="mb-0">Ongoing</p>
                    </div>
                  </div>
                </div>
                <div class="col-md-3 mb-2">
                  <div class="card bg-light">
                    <div class="card-body text-center">
                      <h3>{{ selectedProfessional.stats.cancelled_requests || 0 }}</h3>
                      <p class="mb-0">Cancelled</p>
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
                v-if="selectedProfessional && selectedProfessional.blocked"
                @click="unblockProfessional(selectedProfessional.id, true)" 
                class="btn btn-warning"
              >
                <i class="fas fa-unlock me-1"></i> Unblock Professional
              </button>
              <button 
                v-else-if="selectedProfessional && !selectedProfessional.blocked"
                @click="blockProfessional(selectedProfessional.id, true)" 
                class="btn btn-danger"
              >
                <i class="fas fa-ban me-1"></i> Block Professional
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
  name: 'AdminProfessionals',
  data() {
    return {
      professionals: [],
      services: [],
      loading: false,
      profileLoading: false,
      showProfileModal: false,
      selectedProfessional: null,
      statusFilter: '',
      serviceFilter: '',
      searchQuery: '',
      sortKey: 'id',
      sortOrder: 'asc',
      notificationMessage: '',
      notificationType: 'info'
    };
  },
  computed: {
    filteredProfessionals() {
      let result = [...this.professionals];
      
      // Apply status filter
      if (this.statusFilter) {
        result = result.filter(professional =>(!professional.approved)?'pending':(professional.blocked)?'blocked':'approved' == this.statusFilter.toLowerCase());
      }
      
      // Apply service filter
      if (this.serviceFilter) {
        result = result.filter((professional)=>professional.service_type==this.serviceFilter)
      }
      
      // Apply search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(professional => 
          professional.name.toLowerCase().includes(query) || 
          professional.email.toLowerCase().includes(query) ||
          (professional.phone && professional.phone.includes(query))
        );
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let aValue = a[this.sortKey];
        let bValue = b[this.sortKey];
        
        // Handle numeric fields
        if (this.sortKey === 'id') {
          aValue = parseInt(aValue);
          bValue = parseInt(bValue);
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
    this.fetchProfessionals();
    this.fetchServices();
    
    // Check URL for view parameter to open profile directly
    const urlParams = new URLSearchParams(window.location.search);
    const viewId = urlParams.get('view');
    if (viewId) {
      this.viewProfile(Number(viewId));
    }
  },
  methods: {
    fetchProfessionals() {
      this.loading = true;
      ApiService.getProfessionals()
        .then(response => {
          console.log(response.data)
          this.professionals = response.data.professionals || [];
        })
        .catch(error => {
          console.error('Error fetching professionals:', error);
          alert('Failed to load professionals. Please try again.');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    fetchServices() {
      ApiService.getServices()
        .then(response => {
          response.data.forEach((ele)=>{
            if(this.services.filter((data)=>data.service_type==ele.service_type).length==0){
              this.services.push(ele)
            }
        
          })
        })
        .catch(error => {
          console.error('Error fetching services:', error);
        });
    },
    
    viewProfile(professionalId) {
      this.profileLoading = true;
      this.showProfileModal = true;
      
      ApiService.getProfessionalById(professionalId)
        .then(response => {
          this.selectedProfessional = response.data;
        })
        .catch(error => {
          console.error('Error fetching professional profile:', error);
          alert('Failed to load professional profile. Please try again.');
          this.closeProfileModal();
        })
        .finally(() => {
          this.profileLoading = false;
        });
    },
    
    approveProfessional(professionalId, closeModalAfter = false) {
      if (confirm('Are you sure you want to approve this professional?')) {
        ApiService.approveProfessional(professionalId)
          .then(() => {
            alert('Professional approved successfully!');
            
            // Update the professional's status in our data
            const index = this.professionals.findIndex(p => p.id === professionalId);
            if (index !== -1) {
              this.professionals[index].status = 'approved';
            }
            
            // Update selected professional if in modal
            if (this.selectedProfessional && this.selectedProfessional.id === professionalId) {
              this.selectedProfessional.status = 'approved';
            }
            
            if (closeModalAfter) {
              this.closeProfileModal();
            }
            this.fetchProfessionals()
          })
          .catch(error => {
            console.error('Error approving professional:', error);
            alert('Failed to approve professional. Please try again.');
          });
      }
    },
    
    blockProfessional(professionalId, closeModalAfter = false) {
      if (confirm('Are you sure you want to block this professional?')) {
        ApiService.blockProfessional(professionalId)
          .then(() => {
            alert('Professional blocked successfully!');
            
            // Update the professional's status in our data
            const index = this.professionals.findIndex(p => p.id === professionalId);
            if (index !== -1) {
              this.professionals[index].status = 'blocked';
            }
            
            // Update selected professional if in modal
            if (this.selectedProfessional && this.selectedProfessional.id === professionalId) {
              this.selectedProfessional.status = 'blocked';
            }
            
            if (closeModalAfter) {
              this.closeProfileModal();
            }
            this.fetchProfessionals()
          })
          .catch(error => {
            console.error('Error blocking professional:', error);
            alert('Failed to block professional. Please try again.');
          });
      }
    },
    
    unblockProfessional(professionalId, closeModalAfter = false) {
      if (confirm('Are you sure you want to unblock this professional?')) {
        ApiService.unblockProfessional(professionalId)
          .then(() => {
            alert('Professional unblocked successfully!');
            
            // Update the professional's status in our data
            const index = this.professionals.findIndex(p => p.id === professionalId);
            if (index !== -1) {
              this.professionals[index].status = 'approved';
            }
            
            // Update selected professional if in modal
            if (this.selectedProfessional && this.selectedProfessional.id === professionalId) {
              this.selectedProfessional.status = 'approved';
            }
            
            if (closeModalAfter) {
              this.closeProfileModal();
            }
            this.fetchProfessionals()
          })
          .catch(error => {
            console.error('Error unblocking professional:', error);
            alert('Failed to unblock professional. Please try again.');
          });
      }
    },
    
    closeProfileModal() {
      this.showProfileModal = false;
      this.selectedProfessional = null;
    },
    
    getServiceName(service) {
      if (typeof service === 'object' && service.name) {
        return service.name;
      }
      
      const foundService = this.services.find(s => s.id === (typeof service === 'object' ? service.id : service));
      return foundService ? foundService.name : `Service #${service}`;
    },
    
    getStatusClass(status) {
      switch(status) {
        case 'pending':
          return 'badge bg-warning';
        case 'approved':
          return 'badge bg-success';
        case 'blocked':
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