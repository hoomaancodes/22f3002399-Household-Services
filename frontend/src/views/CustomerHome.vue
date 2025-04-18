<template>
  <div class="customer-home">
    <h2>Customer Dashboard</h2>
    
    <div class="row mt-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h4>Available Services</h4>
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
              <div class="row">
                <div class="col-md-6 mb-3" v-for="service in services" :key="service.id">
                  <div class="card h-100">
                    <div class="card-body">
                      <h5 class="card-title">{{ service.name }}</h5>
                      <p class="card-text">{{ service.description || 'No description available' }}</p>
                      <p><strong>Type:</strong> {{ service.service_type }}</p>
                      <p><strong>Price:</strong> ${{ service.price }}</p>
                      <p><strong>Time Required:</strong> {{ service.time_req }} hours</p>
                      <button @click="bookService(service.id)" class="btn btn-primary">Book Service</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h4>My Service Requests</h4>
          </div>
          <div class="card-body">
            <div v-if="loadingRequests" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="serviceRequests.length === 0" class="text-center">
              <p>You haven't requested any services yet.</p>
            </div>
            
            <div v-else>
              <div class="list-group">
                <div v-for="request in serviceRequests" :key="request.id" class="list-group-item">
                  <h5 class="mb-1">{{ request.service_name }}</h5>
                  <p class="mb-1"><strong>Status:</strong> {{ request.status }}</p>
                  <p class="mb-1"><strong>Date:</strong> {{ formatDate(request.req_date) }}</p>
                  <p v-if="request.professional_name" class="mb-1">
                    <strong>Professional:</strong> {{ request.professional_name }}
                  </p>
                  
                  <div class="mt-2">
                    <button 
                      v-if="request.status === 'requested'" 
                      @click="cancelRequest(request.id)"
                      class="btn btn-danger btn-sm">
                      Cancel
                    </button>
                    
                    <button 
                      v-if="request.status === 'assigned'" 
                      @click="closeRequest(request.id)"
                      class="btn btn-success btn-sm">
                      Mark as Complete
                    </button>
                  </div>
                </div>
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

export default {
  name: 'CustomerHomePage',
  data() {
    return {
      services: [],
      serviceRequests: [],
      loading: false,
      loadingRequests: false,
      message: ''
    };
  },
  created() {
    this.fetchServices();
    this.fetchServiceRequests();
  },
  methods: {
    fetchServices() {
      this.loading = true;
      ApiService.getServices()
        .then(response => {
          this.services = response.data;
        })
        .catch(error => {
          console.error('Error fetching services:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    fetchServiceRequests() {
      this.loadingRequests = true;
      ApiService.getServiceRequests()
        .then(response => {
          this.serviceRequests = response.data;
        })
        .catch(error => {
          console.error('Error fetching service requests:', error);
        })
        .finally(() => {
          this.loadingRequests = false;
        });
    },
    bookService(serviceId) {
      const serviceRequest = {
        service_id: serviceId
      };
      
      ApiService.createServiceRequest(serviceRequest)
        .then(() => {
          alert('Service booked successfully!');
          this.fetchServiceRequests();
        })
        .catch(error => {
          console.error('Error booking service:', error);
          alert('Failed to book service. Please try again.');
        });
    },
    cancelRequest(requestId) {
      if (confirm('Are you sure you want to cancel this service request?')) {
        ApiService.updateServiceRequest(requestId, { status: 'cancelled' })
          .then(() => {
            alert('Service request cancelled successfully!');
            this.fetchServiceRequests();
          })
          .catch(error => {
            console.error('Error cancelling request:', error);
            alert('Failed to cancel service request. Please try again.');
          });
      }
    },
    closeRequest(requestId) {
      if (confirm('Are you sure you want to mark this service as complete?')) {
        ApiService.updateServiceRequest(requestId, { status: 'closed' })
          .then(() => {
            alert('Service request marked as complete!');
            this.fetchServiceRequests();
          })
          .catch(error => {
            console.error('Error closing request:', error);
            alert('Failed to close service request. Please try again.');
          });
      }
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
  }
};
</script>

<style scoped>
.customer-home {
  margin-top: 1rem;
}

.card {
  margin-bottom: 1.5rem;
}

.list-group-item {
  margin-bottom: 0.5rem;
}
</style> 