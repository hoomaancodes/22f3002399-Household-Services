<template>
  <div class="admin-home">
    <h2>Admin Dashboard</h2>
    
    <div class="row mt-4">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h4>Services</h4>
            <button class="btn btn-primary btn-sm" @click="showAddServiceModal = true">+ Add Service</button>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="services.length === 0" class="text-center">
              <p>No services available at the moment.</p>
            </div>
            
            <div v-else>
              <table class="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Type</th>
                    <th>Price</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="service in services" :key="service.id">
                    <td>{{ service.id }}</td>
                    <td>{{ service.name }}</td>
                    <td>{{ service.service_type }}</td>
                    <td>${{ service.price }}</td>
                    <td>
                      <button class="btn btn-sm btn-primary me-1">Edit</button>
                      <button class="btn btn-sm btn-danger">Delete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h4>Professionals</h4>
          </div>
          <div class="card-body">
            <div v-if="loadingProfessionals" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="professionals.length === 0" class="text-center">
              <p>No professionals registered at the moment.</p>
            </div>
            
            <div v-else>
              <table class="table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Service Type</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="professional in professionals" :key="professional.id">
                    <td>{{ professional.id }}</td>
                    <td>{{ professional.name }}</td>
                    <td>{{ professional.service_type }}</td>
                    <td>
                      <span v-if="professional.approved" class="badge bg-success">Approved</span>
                      <span v-else class="badge bg-warning">Pending</span>
                    </td>
                    <td>
                      <button 
                        v-if="!professional.approved" 
                        class="btn btn-sm btn-success me-1">
                        Approve
                      </button>
                      <button 
                        v-if="!professional.blocked" 
                        class="btn btn-sm btn-danger">
                        Block
                      </button>
                      <button 
                        v-else 
                        class="btn btn-sm btn-secondary">
                        Unblock
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Add Service Modal -->
    <div v-if="showAddServiceModal" class="modal-backdrop" @click="showAddServiceModal = false"></div>
    <div v-if="showAddServiceModal" class="modal-container">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add New Service</h5>
          <button type="button" class="btn-close" @click="showAddServiceModal = false"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="addService">
            <div class="mb-3">
              <label for="serviceName" class="form-label">Service Name</label>
              <input type="text" class="form-control" id="serviceName" v-model="newService.name" required>
            </div>
            <div class="mb-3">
              <label for="serviceType" class="form-label">Service Type</label>
              <input type="text" class="form-control" id="serviceType" v-model="newService.service_type" required>
            </div>
            <div class="mb-3">
              <label for="servicePrice" class="form-label">Price</label>
              <input type="number" step="0.01" class="form-control" id="servicePrice" v-model="newService.price" required>
            </div>
            <div class="mb-3">
              <label for="serviceTime" class="form-label">Time Required (hours)</label>
              <input type="number" step="0.5" class="form-control" id="serviceTime" v-model="newService.time_req" required>
            </div>
            <div class="mb-3">
              <label for="serviceDescription" class="form-label">Description</label>
              <textarea class="form-control" id="serviceDescription" v-model="newService.description"></textarea>
            </div>
            <div class="text-end">
              <button type="button" class="btn btn-secondary me-2" @click="showAddServiceModal = false">Close</button>
              <button type="submit" class="btn btn-primary">Add Service</button>
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
  name: 'AdminHomePage',
  data() {
    return {
      services: [],
      professionals: [],
      loading: false,
      loadingProfessionals: false,
      showAddServiceModal: false,
      newService: {
        name: '',
        service_type: '',
        price: '',
        time_req: '',
        description: ''
      }
    };
  },
  created() {
    this.fetchServices();
    // In a real implementation, you would fetch professionals here
    // This is a placeholder for demonstration
    this.professionals = [
      { id: 1, name: 'John Doe', service_type: 'Plumbing', approved: true, blocked: false },
      { id: 2, name: 'Jane Smith', service_type: 'Electrical', approved: false, blocked: false }
    ];
  },
  methods: {
    fetchServices() {
      this.loading = true;
      ApiService.getServices()
        .then(response => {
          this.services = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching services:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    addService() {
      // Placeholder implementation
      alert('Service would be added here in a real implementation');
      this.showAddServiceModal = false;
      // In a real implementation, you would call the API
      // ApiService.createService(this.newService)
    }
  }
};
</script>

<style scoped>
.admin-home {
  margin-top: 1rem;
}

.card {
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.me-1 {
  margin-right: 0.25rem;
}

.me-2 {
  margin-right: 0.5rem;
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
</style> 