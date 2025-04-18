<template>
  <div class="professional-dashboard">
    <h2>Professional Dashboard</h2>
    
    <!-- Stats Cards -->
    <div class="row mt-4">
      
      <div class="col-md-3 mb-4">
        <div class="card bg-success text-white h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-uppercase">Assigned</h6>
                <h3 class="mb-0">{{ stats.pending_requests  }}</h3>
              </div>
              <i class="fas fa-spinner fa-2x"></i>
            </div>
          </div>
          <div class="card-footer d-flex align-items-center justify-content-between">
            <router-link to="/professional/service-requests" class="text-white">
              <span>View Active Jobs</span>
              <i class="fas fa-angle-right ms-1"></i>
            </router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-3 mb-4">
        <div class="card bg-info text-white h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h6 class="text-uppercase">Completed</h6>
                <h3 class="mb-0">{{ stats.completed || 0 }}</h3>
              </div>
              <i class="fas fa-check-circle fa-2x"></i>
            </div>
          </div>
          <div class="card-footer d-flex align-items-center justify-content-between">
            <router-link to="/professional/service-requests" class="text-white">
              <span>View Completed</span>
              <i class="fas fa-angle-right ms-1"></i>
            </router-link>
          </div>
        </div>
      </div>
      
     
    </div>
    
    <!-- Recent Service Requests -->
    <div class="card mt-4">
      <div class="card-header bg-white">
        <div class="d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Recent Service Requests</h5>
          <router-link to="/professional/service-requests" class="btn btn-sm btn-primary">
            View All
          </router-link>
        </div>
      </div>
      <div class="card-body">
        <div v-if="loadingRequests" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="recentRequests.length === 0" class="text-center my-5">
          <p>No service requests available.</p>
          <p class="text-muted">New service requests will appear here.</p>
        </div>
        
        <div v-else>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Service</th>
                  <th>Customer</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="request in recentRequests" :key="request.id">
                  <td>#{{ request.id }}</td>
                  <td>{{ request.service_name }}</td>
                  <td>{{ request.customer_name }}</td>
                  <td>{{ formatDate(request.created_at) }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(request.status)">
                      {{ request.status }}
                    </span>
                  </td>
                  <td>
                    <router-link 
                      :to="`/professional/service-requests`" 
                      class="btn btn-sm btn-outline-primary me-1"
                    >
                      <i class="fas fa-eye"></i>
                    </router-link>
                    <button 
                      v-if="request.status === 'requested'"
                      @click="acceptRequest(request.id)" 
                      class="btn btn-sm btn-outline-success me-1"
                    >
                      <i class="fas fa-check"></i>
                    </button>
                    <button 
                      v-if="request.status === 'requested'"
                      @click="rejectRequest(request.id)" 
                      class="btn btn-sm btn-outline-danger"
                    >
                      <i class="fas fa-times"></i>
                    </button>
                    <button 
                      v-if="request.status === 'assigned'"
                      @click="completeRequest(request.id)" 
                      class="btn btn-sm btn-outline-success"
                    >
                      <i class="fas fa-check-double"></i>
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
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
  name: 'ProfessionalDashboard',
  data() {
    return {
      stats: {
        pending: 0,
        inProgress: 0,
        completed: 0,
        rating: null
      },
      recentRequests: [],
      todaySchedule: [],
      loadingRequests: false,
      loadingSchedule: false
    };
  },
  created() {
    this.fetchDashboardData();
    this.fetchRecentRequests();
    this.fetchTodaySchedule();
  },
  methods: {
    fetchDashboardData() {
      ApiService.getProfessionalStats()
        .then(response => {

          this.stats = response.data;
        })
        .catch(error => {
          console.error('Error fetching professional stats:', error);
        });
    },
    
    fetchRecentRequests() {
      this.loadingRequests = true;
      ApiService.getProfessionalRequests({ limit: 5 })
        .then(response => {
          this.recentRequests = response.data.requests || [];
        })
        .catch(error => {
          console.error('Error fetching recent requests:', error);
        })
        .finally(() => {
          this.loadingRequests = false;
        });
    },
    
    fetchTodaySchedule() {
      this.loadingSchedule = true;
      
      // Get today's date in YYYY-MM-DD format
      const today = new Date();
      const dateString = today.toISOString().split('T')[0];
      
      ApiService.getProfessionalSchedule({ date: dateString })
        .then(response => {
          this.todaySchedule = response.data.schedule || [];
        })
        .catch(error => {
          console.error('Error fetching today\'s schedule:', error);
        })
        .finally(() => {
          this.loadingSchedule = false;
        });
    },
    
    acceptRequest(requestId) {
      if (confirm('Are you sure you want to accept this service request?')) {
        ApiService.acceptServiceRequest(requestId)
          .then(() => {
            alert('Service request accepted successfully!');
            
            // Update the request status in our list
            const index = this.recentRequests.findIndex(r => r.id === requestId);
            if (index !== -1) {
              this.recentRequests[index].status = 'in_progress';
            }
            
            // Refresh dashboard data
            this.fetchDashboardData();
          })
          .catch(error => {
            console.error('Error accepting request:', error);
            alert('Failed to accept request. Please try again.');
          });
      }
    },
    
    rejectRequest(requestId) {
      if (confirm('Are you sure you want to reject this service request?')) {
        ApiService.rejectServiceRequest(requestId)
          .then(() => {
            alert('Service request rejected successfully!');
            
            // Update the request status in our list
            const index = this.recentRequests.findIndex(r => r.id === requestId);
            if (index !== -1) {
              this.recentRequests.splice(index, 1);
            }
            
            // Refresh dashboard data
            this.fetchDashboardData();
          })
          .catch(error => {
            console.error('Error rejecting request:', error);
            alert('Failed to reject request. Please try again.');
          });
      }
    },
    
    completeRequest(requestId) {
      if (confirm('Are you sure you want to mark this service request as completed?')) {
        ApiService.completeServiceRequest(requestId)
          .then(() => {
            alert('Service request completed successfully!');
            
            // Update the request status in our lists
            const requestsIndex = this.recentRequests.findIndex(r => r.id === requestId);
            if (requestsIndex !== -1) {
              this.recentRequests[requestsIndex].status = 'completed';
            }
            
            const scheduleIndex = this.todaySchedule.findIndex(r => r.id === requestId);
            if (scheduleIndex !== -1) {
              this.todaySchedule[scheduleIndex].status = 'completed';
            }
            
            // Refresh dashboard data
            this.fetchDashboardData();
          })
          .catch(error => {
            console.error('Error completing request:', error);
            alert('Failed to complete request. Please try again.');
          });
      }
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
    
    formatTime(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    },
    
    truncateText(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
  border: none;
}

.card-footer {
  background-color: rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.25rem;
  border-top: none;
}

.card-header {
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  padding: 1rem;
}

.schedule-timeline {
  position: relative;
  padding-left: 20px;
}

.schedule-timeline:before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #e9ecef;
}

.schedule-item {
  position: relative;
  padding-bottom: 25px;
  display: flex;
  align-items: flex-start;
}

.schedule-time {
  width: 90px;
  font-weight: bold;
  padding-right: 15px;
  color: #495057;
}

.schedule-card {
  flex: 1;
  background: #f8f9fa;
  border-radius: 0.25rem;
  padding: 15px;
  border-left: 4px solid #007bff;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.schedule-header h6 {
  margin: 0;
}

.schedule-content p {
  margin-bottom: 0.5rem;
}

.schedule-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
}

.badge {
  text-transform: capitalize;
  padding: 0.5em 0.75em;
}

.me-1 {
  margin-right: 0.25rem;
}

.ms-1 {
  margin-left: 0.25rem;
}

.ms-2 {
  margin-left: 0.5rem;
}
</style> 