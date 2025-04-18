<template>
  <div class="professional-home">
    <h2>Professional Dashboard</h2>
    
    <div class="row mt-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h4>New Service Requests</h4>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="newRequests.length === 0" class="text-center">
              <p>No new service requests available at the moment.</p>
            </div>
            
            <div v-else>
              <div class="list-group">
                <div v-for="request in newRequests" :key="request.id" class="list-group-item">
                  <h5 class="mb-1">{{ request }}</h5>
                  <p class="mb-1"><strong>Customer:</strong> {{ request.customer_name }}</p>
                  <p class="mb-1"><strong>Date:</strong> {{ formatDate(request.req_date) }}</p>
                  <p class="mb-1"><strong>Status:</strong> {{ request.status }}</p>
                  
                  <div class="mt-2">
                    <button 
                      class="btn btn-success btn-sm me-2"
                      @click="acceptRequest(request.id)">
                      Accept
                    </button>
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
            <h4>Assigned Requests</h4>
          </div>
          <div class="card-body">
            <div v-if="loadingAssigned" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="assignedRequests.length === 0" class="text-center">
              <p>No assigned requests at the moment.</p>
            </div>
            
            <div v-else>
              <div class="list-group">
                <div v-for="request in assignedRequests" :key="request.id" class="list-group-item">
                  <h5 class="mb-1">{{ request.service_name }}</h5>
                  <p class="mb-1"><strong>Customer:</strong> {{ request.customer_name }}</p>
                  <p class="mb-1"><strong>Date:</strong> {{ formatDate(request.req_date) }}</p>
                  <p class="mb-1"><strong>Status:</strong> {{ request.status }}</p>
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
  name: 'ProfessionalHomePage',
  data() {
    return {
      allRequests: [],
      loading: false,
      loadingAssigned: false
    };
  },
  computed: {
    newRequests() {
      return this.allRequests.filter(req => req.status === 'requested');
    },
    assignedRequests() {
      return this.allRequests.filter(req => req.status === 'assigned');
    }
  },
  created() {
    this.fetchServiceRequests();
  },
  methods: {
    fetchServiceRequests() {
      this.loading = true;
      this.loadingAssigned = true;
      ApiService.getServiceRequests()
        .then(response => {
          console.log(response.data)
          this.allRequests = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching service requests:', error);
        })
        .finally(() => {
          this.loading = false;
          this.loadingAssigned = false;
        });
    },
    acceptRequest(requestId) {
      ApiService.updateServiceRequest(requestId, { action: 'accept' })
        .then(() => {
          alert('Service request accepted successfully!');
          this.fetchServiceRequests();
        })
        .catch(error => {
          console.error('Error accepting request:', error);
          alert('Failed to accept service request. Please try again.');
        });
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    }
  }
};
</script>

<style scoped>
.professional-home {
  margin-top: 1rem;
}

.card {
  margin-bottom: 1.5rem;
}

.me-2 {
  margin-right: 0.5rem;
}
</style> 