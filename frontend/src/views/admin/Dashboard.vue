<template>
  <div class="admin-dashboard">
    <h2>Admin Dashboard</h2>
    
    <div class="row mt-4">
      <!-- Statistics Cards -->
      <div class="col-md-3">
        <div class="card stats-card bg-primary text-white">
          <div class="card-body">
            <h5 class="card-title">Services</h5>
            <p class="card-text display-4">{{ stats.services }}</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card stats-card bg-success text-white">
          <div class="card-body">
            <h5 class="card-title">Professionals</h5>
            <p class="card-text display-4">{{ stats.professionals }}</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card stats-card bg-info text-white">
          <div class="card-body">
            <h5 class="card-title">Customers</h5>
            <p class="card-text display-4">{{ stats.customers }}</p>
          </div>
        </div>
      </div>
      
      <div class="col-md-3">
        <div class="card stats-card bg-warning text-dark">
          <div class="card-body">
            <h5 class="card-title">Service Requests</h5>
            <p class="card-text display-4">{{ stats.requests  }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Recent Requests -->
    <div class="row mt-4">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h4>Recent Service Requests</h4>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="recentRequests.length === 0" class="text-center">
              <p>No recent service requests</p>
            </div>
            
            <div v-else>
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Service</th>
                    <th>Customer</th>
                    <th>Professional</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in recentRequests" :key="request.id">
                    <td>{{ request.id }}</td>
                    <td>{{ request.service_name }}</td>
                    <td>{{ request.customer_name }}</td>
                    <td>{{ request.professional_name || 'Not assigned' }}</td>
                    <td>
                      <span 
                        class="badge" 
                        :class="getStatusClass(request.status)"
                      >
                        {{ request.status }}
                      </span>
                    </td>
                    <td>{{ formatDate(request.req_date) }}</td>
                  </tr>
                </tbody>
              </table>
              <div class="text-end">
                <router-link to="/admin/reports" class="btn btn-primary">View All</router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Approval Requests -->
      <div class="col-md-4">
        <div class="card">
          <div class="card-header">
            <h4>Pending Professionals</h4>
          </div>
          <div class="card-body">
            <div v-if="loadingProfessionals" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="pendingProfessionals.length === 0" class="text-center">
              <p>No pending professionals</p>
            </div>
            
            <div v-else>
              <div class="list-group">
                <div v-for="professional in pendingProfessionals" :key="professional.id" class="list-group-item">
                  <h5 class="mb-1">{{ professional.name }}</h5>
                  <p class="mb-1"><strong>Service Type:</strong> {{ professional.service_type }}</p>
                  <p class="mb-1"><strong>Experience:</strong> {{ professional.exp }} years</p>
                  <div class="d-flex justify-content-end mt-2">
                    <button 
                      class="btn btn-success btn-sm" 
                      @click="approveProfessional(professional.id)"
                    >
                      Approve
                    </button>
                  </div>
                </div>
              </div>
              <div class="text-end mt-3">
                <router-link to="/admin/professionals" class="btn btn-primary">View All</router-link>
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
  name: 'AdminDashboard',
  data() {
    return {
      stats: {
        services: 0,
        professionals: 0,
        customers: 0,
        requests: 0
      },
      recentRequests: [],
      pendingProfessionals: [],
      loading: false,
      loadingProfessionals: false
    };
  },
  created() {
    this.fetchDashboardData();
  },
  methods: {
    fetchDashboardData() {
      this.loading = true;
      this.loadingProfessionals = true;
      
      // Fetch service requests
      ApiService.getServiceRequests()
        .then(response => {
          const data = response.data || {};
          console.log(data);
          
          // Set the total count
          this.stats.requests = data.count || 0;
          
          // Get the requests array from the response
          const requestsArray = data.requests || [];
          
          // Get the 5 most recent requests
          this.recentRequests = requestsArray
            .sort((a, b) => new Date(b.req_date) - new Date(a.req_date))
            .slice(0, 5);
        })
        .catch(error => {
          console.error('Error fetching service requests:', error);
        })
        .finally(() => {
          this.loading = false;
        });
      
      // Fetch services count
      ApiService.getServices()
        .then(response => {
          const services = response.data || [];
          this.stats.services = services.length;
        })
        .catch(error => {
          console.error('Error fetching services:', error);
        });
      
      // Fetch users (professionals and customers)
      ApiService.getUsers()
        .then(response => {
          const users = response.data || [];
          
          // Count professionals and customers
          const professionals = users.filter(user => user.role === 'professional');
          const customers = users.filter(user => user.role === 'customer');
          
          this.stats.professionals = professionals.length;
          this.stats.customers = customers.length;
          
          // Get pending professionals
          this.pendingProfessionals = professionals
            .filter(user => user.professional && !user.professional.approved)
            .map(user => user.professional)
            .slice(0, 3); // Show only 3 latest
        })
        .catch(error => {
          console.error('Error fetching users:', error);
        })
        .finally(() => {
          this.loadingProfessionals = false;
        });
    },
    
    approveProfessional(professionalId) {
      ApiService.updateProfessionalStatus(professionalId, { approved: true })
        .then(() => {
          alert('Professional approved successfully!');
          this.fetchDashboardData();
        })
        .catch(error => {
          console.error('Error approving professional:', error);
          alert('Failed to approve professional. Please try again.');
        });
    },
    
    getStatusClass(status) {
      switch(status) {
        case 'requested':
          return 'bg-warning text-dark';
        case 'assigned':
          return 'bg-primary';
        case 'closed':
          return 'bg-success';
        default:
          return 'bg-secondary';
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
.stats-card {
  transition: transform 0.3s;
}
.stats-card:hover {
  transform: translateY(-5px);
}
</style> 