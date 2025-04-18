<template>
  <div class="admin-services">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Services Management</h2>
      <button class="btn btn-primary" @click="showAddServiceModal = true">
        <i class="fas fa-plus"></i> Add New Service
      </button>
    </div>
    
    <div class="card">
      <div class="card-body">
        <!-- Filter controls -->
        <div class="mb-4 d-flex">
          <div class="me-3" style="width: 200px;">
            <label for="typeFilter" class="form-label">Filter by Type</label>
            <select v-model="typeFilter" class="form-select" id="typeFilter">
              <option value="">All Types</option>
              <option v-for="(type, index) in serviceTypes" :key="index" :value="type">
                {{ type }}
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
              placeholder="Search by name..."
            >
          </div>
        </div>
        
        <!-- Services table -->
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="filteredServices.length === 0" class="text-center my-5">
          <p>No services found.</p>
          <button class="btn btn-primary" @click="showAddServiceModal = true">
            Add New Service
          </button>
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
                  <th @click="sortBy('service_type')" class="sortable">
                    Type
                    <i class="fas" :class="getSortIconClass('service_type')"></i>
                  </th>
                  <th @click="sortBy('price')" class="sortable">
                    Price
                    <i class="fas" :class="getSortIconClass('price')"></i>
                  </th>
                  <th @click="sortBy('time_req')" class="sortable">
                    Time (hours)
                    <i class="fas" :class="getSortIconClass('time_req')"></i>
                  </th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="service in filteredServices" :key="service.id">
                  <td>{{ service.id }}</td>
                  <td>{{ service.name }}</td>
                  <td>{{ service.service_type }}</td>
                  <td>${{ service.price }}</td>
                  <td>{{ service.time_req }}</td>
                  <td>{{ truncateText(service.description, 50) }}</td>
                  <td>
                    <button @click="editService(service)" class="btn btn-sm btn-primary me-1">
                      Edit
                    </button>
                    <button @click="confirmDeleteService(service.id)" class="btn btn-sm btn-danger">
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add/Edit Service Modal -->
    <div v-if="showServiceModal" class="modal-backdrop" @click="closeServiceModal"></div>
    <div v-if="showServiceModal" class="modal-container">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">{{ isEditMode ? 'Edit Service' : 'Add New Service' }}</h5>
          <button type="button" class="btn-close" @click="closeServiceModal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="saveService">
            <div class="mb-3">
              <label for="serviceName" class="form-label">Service Name</label>
              <input type="text" class="form-control" id="serviceName" v-model="currentService.name" required>
            </div>
            
            <div class="mb-3">
              <label for="serviceType" class="form-label">Service Type</label>
              <input type="text" class="form-control" id="serviceType" v-model="currentService.service_type" required>
            </div>
            
            <div class="mb-3">
              <label for="servicePrice" class="form-label">Price ($)</label>
              <input type="number" step="0.01" class="form-control" id="servicePrice" v-model="currentService.price" required>
            </div>
            
            <div class="mb-3">
              <label for="serviceTime" class="form-label">Time Required (hours)</label>
              <input type="number" step="0.5" class="form-control" id="serviceTime" v-model="currentService.time_req" required>
            </div>
            
            <div class="mb-3">
              <label for="serviceDescription" class="form-label">Description</label>
              <textarea class="form-control" id="serviceDescription" v-model="currentService.description" rows="3"></textarea>
            </div>
            
            <div class="d-flex justify-content-end">
              <button type="button" class="btn btn-secondary me-2" @click="closeServiceModal">Cancel</button>
              <button type="submit" class="btn btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-1"></span>
                {{ isEditMode ? 'Update' : 'Add' }} Service
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
  name: 'AdminServices',
  data() {
    return {
      services: [],
      serviceTypes: [],
      loading: false,
      saving: false,
      showServiceModal: false,
      showAddServiceModal: false,
      currentService: {
        name: '',
        service_type: '',
        price: '',
        time_req: '',
        description: ''
      },
      isEditMode: false,
      typeFilter: '',
      searchQuery: '',
      sortKey: 'id',
      sortOrder: 'asc'
    };
  },
  computed: {
    filteredServices() {
      let result = [...this.services];
      
      // Apply type filter
      if (this.typeFilter) {
        result = result.filter(service => service.service_type === this.typeFilter);
      }
      
      // Apply search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        result = result.filter(service => 
          service.name.toLowerCase().includes(query) || 
          service.description.toLowerCase().includes(query)
        );
      }
      
      // Apply sorting
      result.sort((a, b) => {
        let aValue = a[this.sortKey];
        let bValue = b[this.sortKey];
        
        // Handle numeric fields
        if (this.sortKey === 'price' || this.sortKey === 'time_req' || this.sortKey === 'id') {
          aValue = parseFloat(aValue);
          bValue = parseFloat(bValue);
        } else {
          // Handle string fields
          aValue = String(aValue).toLowerCase();
          bValue = String(bValue).toLowerCase();
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
    this.fetchServices();
    this.fetchServiceTypes();
    
    // Check URL for edit parameter
    const urlParams = new URLSearchParams(window.location.search);
    const editId = urlParams.get('edit');
    if (editId) {
      this.fetchServiceById(Number(editId));
    }
  },
  watch: {
    showAddServiceModal(newVal) {
      if (newVal) {
        this.isEditMode = false;
        this.currentService = {
          name: '',
          service_type: '',
          price: '',
          time_req: '',
          description: ''
        };
        this.showServiceModal = true;
      }
    }
  },
  methods: {
    fetchServices() {
      this.loading = true;
      ApiService.getServices()
        .then(response => {
          console.log(response.data)
          this.services = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching services:', error);
          alert('Failed to load services. Please try again.');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    fetchServiceTypes() {
      ApiService.getServiceTypes()
        .then(response => {
          this.serviceTypes = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching service types:', error);
        });
    },
    
    fetchServiceById(id) {
      this.loading = true;
      ApiService.getService(id)
        .then(response => {
          this.currentService = response.data;
          this.isEditMode = true;
          this.showServiceModal = true;
        })
        .catch(error => {
          console.error('Error fetching service:', error);
          alert('Failed to load service details. Please try again.');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    editService(service) {
      this.currentService = { ...service };
      this.isEditMode = true;
      this.showServiceModal = true;
    },
    
    saveService() {
      this.saving = true;
      
      if (this.isEditMode) {
        // Update existing service
        ApiService.updateService(this.currentService.id, this.currentService)
          .then(() => {
            alert('Service updated successfully!');
            this.fetchServices();
            this.closeServiceModal();
          })
          .catch(error => {
            console.error('Error updating service:', error);
            alert('Failed to update service. Please try again.');
          })
          .finally(() => {
            this.saving = false;
          });
      } else {
        // Create new service
        ApiService.createService(this.currentService)
          .then(() => {
            alert('Service created successfully!');
            this.fetchServices();
            this.closeServiceModal();
          })
          .catch(error => {
            console.error('Error creating service:', error);
            alert('Failed to create service. Please try again.');
          })
          .finally(() => {
            this.saving = false;
          });
      }
    },
    
    confirmDeleteService(serviceId) {
      if (confirm('Are you sure you want to delete this service?')) {
        ApiService.deleteService(serviceId)
          .then(() => {
            alert('Service deleted successfully!');
            this.fetchServices();
          })
          .catch(error => {
            console.error('Error deleting service:', error);
            alert('Failed to delete service. Please try again.');
          });
      }
    },
    
    closeServiceModal() {
      this.showServiceModal = false;
      this.showAddServiceModal = false;
    },
    
    sortBy(key) {
      // If already sorting by this key, toggle the order
      if (this.sortKey === key) {
        this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
      } else {
        // Otherwise, set the new key and default to ascending
        this.sortKey = key;
        this.sortOrder = 'asc';
      }
    },
    
    getSortIconClass(key) {
      if (this.sortKey !== key) {
        return 'fa-sort';
      }
      return this.sortOrder === 'asc' ? 'fa-sort-up' : 'fa-sort-down';
    },
    
    truncateText(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
  }
};
</script>

<style scoped>
.sortable {
  cursor: pointer;
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
  width: 500px;
  max-width: 90%;
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

.me-1 {
  margin-right: 0.25rem;
}

.me-2 {
  margin-right: 0.5rem;
}
</style> 