<template>
  <div class="request-service">
    <h2>Request a Service</h2>
    
    <div class="card mt-4">
      <div class="card-body">
        <div v-if="loading" class="text-center my-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <form v-else @submit.prevent="submitRequest" class="service-request-form">
          <div class="row">
            <!-- Service Selection -->
            <div class="col-md-12 mb-4">
              <h4>Select a Service</h4>
              
              <div v-if="services.length === 0" class="alert alert-info">
                No services available. Please try again later.
              </div>
              
              <div v-else class="service-categories mb-3">
                <div class="d-flex align-items-center mb-2">
                  <label class="me-3">Filter by type:</label>
                  <div class="btn-group">
                    <button 
                      type="button" 
                      class="btn" 
                      :class="selectedCategory === '' ? 'btn-primary' : 'btn-outline-primary'"
                      @click="selectedCategory = ''"
                    >
                      All
                    </button>
                    <button 
                      v-for="category in serviceCategories" 
                      :key="category"
                      type="button" 
                      class="btn" 
                      :class="selectedCategory === category ? 'btn-primary' : 'btn-outline-primary'"
                      @click="selectedCategory = category"
                    >
                      {{ category }}
                    </button>
                  </div>
                </div>
                
                <div class="input-group">
                  <span class="input-group-text"><i class="fas fa-search"></i></span>
                  <input 
                    type="text" 
                    class="form-control" 
                    placeholder="Search services..." 
                    v-model="searchQuery"
                  >
                </div>
              </div>
              
              <div class="services-grid">
                <div v-if="filteredServices.length === 0" class="text-center my-4">
                  <p>No services match your search criteria.</p>
                </div>
                
                <div 
                  v-for="service in filteredServices" 
                  :key="service.id"
                  class="service-card"
                  :class="{ 'selected': selectedService && selectedService.id === service.id }"
                  @click="selectService(service)"
                >
                  <div class="service-card-header">
                    <h5>{{ service.name }}</h5>
                    <span class="service-type">{{ service.service_type }}</span>
                  </div>
                  <div class="service-card-body">
                    <p>{{ truncateText(service.description, 100) }}</p>
                    <div class="service-details">
                      <div class="price">${{ service.price }}</div>
                      <div class="time">{{ service.time_req }} hrs</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-if="selectedService" class="selected-service mt-3">
                <div class="alert alert-primary">
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>Selected Service:</strong> {{ selectedService.name }} 
                      <span class="ms-2 badge bg-info">{{ selectedService.service_type }}</span>
                    </div>
                    <div>
                      <span class="me-3">${{ selectedService.price }}</span>
                      <button type="button" class="btn-close" @click="selectedService = null"></button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Request Details -->
            <div class="col-md-12 mb-4">
              <h4>Request Details</h4>
              
              <div class="mb-3">
                <label for="addressInput" class="form-label">Service Address</label>
                <textarea 
                  v-model="requestForm.address" 
                  class="form-control" 
                  id="addressInput" 
                  rows="2" 
                  placeholder="Enter the address where the service should be performed"
                  required
                ></textarea>
              </div>
              
              <div class="row">
                <div class="col-md-6 mb-3">
                  <label for="scheduleDateInput" class="form-label">Preferred Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    id="scheduleDateInput" 
                    v-model="requestForm.scheduleDate"
                    required
                    :min="minDate"
                  >
                </div>
                <div class="col-md-6 mb-3">
                  <label for="scheduleTimeInput" class="form-label">Preferred Time</label>
                  <select 
                    class="form-select" 
                    id="scheduleTimeInput" 
                    v-model="requestForm.scheduleTime"
                    required
                  >
                    <option value="" disabled>Select time</option>
                    <option v-for="time in availableTimes" :key="time.value" :value="time.value">
                      {{ time.label }}
                    </option>
                  </select>
                </div>
              </div>
              
              <div class="mb-3">
                <label for="descriptionInput" class="form-label">Additional Details</label>
                <textarea 
                  v-model="requestForm.description" 
                  class="form-control" 
                  id="descriptionInput" 
                  rows="3" 
                  placeholder="Provide any additional details or special requirements"
                ></textarea>
              </div>
            </div>
          </div>
          
          <div class="card mb-4">
            <div class="card-header bg-light">
              <h5 class="mb-0">Request Summary</h5>
            </div>
            <div class="card-body">
              <div v-if="!selectedService" class="text-center text-muted py-3">
                Please select a service to see the summary.
              </div>
              
              <div v-else>
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Service:</strong> {{ selectedService.name }}</p>
                    <p><strong>Type:</strong> {{ selectedService.service_type }}</p>
                    <p><strong>Estimated Time:</strong> {{ selectedService.time_req }} hours</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Price:</strong> ${{ selectedService.price }}</p>
                    <p v-if="requestForm.scheduleDate && requestForm.scheduleTime">
                      <strong>Scheduled For:</strong> 
                      {{ formatScheduleDateTime(requestForm.scheduleDate, requestForm.scheduleTime) }}
                    </p>
                    <p><strong>Address:</strong> {{ requestForm.address || 'Not specified' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="d-flex justify-content-between">
            <router-link to="/customer/dashboard" class="btn btn-outline-secondary">
              Cancel
            </router-link>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="!canSubmit || submitting"
            >
              <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
              Submit Request
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
  name: 'RequestService',
  data() {
    return {
      loading: true,
      submitting: false,
      services: [],
      selectedService: null,
      selectedCategory: '',
      searchQuery: '',
      requestForm: {
        address: '',
        scheduleDate: '',
        scheduleTime: '',
        description: ''
      },
      availableTimes: [
        { value: '09:00', label: '9:00 AM' },
        { value: '10:00', label: '10:00 AM' },
        { value: '11:00', label: '11:00 AM' },
        { value: '12:00', label: '12:00 PM' },
        { value: '13:00', label: '1:00 PM' },
        { value: '14:00', label: '2:00 PM' },
        { value: '15:00', label: '3:00 PM' },
        { value: '16:00', label: '4:00 PM' },
        { value: '17:00', label: '5:00 PM' }
      ]
    };
  },
  computed: {
    serviceCategories() {
      const categories = [...new Set(this.services.map(service => service.service_type))];
      return categories.sort();
    },
    
    filteredServices() {
      if (!this.services.length) return [];
      
      let filtered = [...this.services];
      
      // Apply category filter
      if (this.selectedCategory) {
        filtered = filtered.filter(service => service.service_type === this.selectedCategory);
      }
      
      // Apply search query
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase();
        filtered = filtered.filter(service => 
          service.name.toLowerCase().includes(query) || 
          service.description.toLowerCase().includes(query) ||
          service.service_type.toLowerCase().includes(query)
        );
      }
      
      return filtered;
    },
    
    minDate() {
      const today = new Date();
      const tomorrow = new Date(today);
      tomorrow.setDate(today.getDate() + 1);
      return tomorrow.toISOString().split('T')[0];
    },
    
    canSubmit() {
      return this.selectedService && 
             this.requestForm.address && 
             this.requestForm.scheduleDate && 
             this.requestForm.scheduleTime;
    }
  },
  created() {
    this.fetchServices();
    
    // Check if there's a service ID in the query params
    const serviceId = this.$route.query.service;
    if (serviceId) {
      this.preSelectService(Number(serviceId));
    }
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
          alert('Failed to load services. Please try again.');
        })
        .finally(() => {
          this.loading = false;
        });
    },
    
    preSelectService(serviceId) {
      ApiService.getService(serviceId)
        .then(response => {
          this.selectedService = response.data;
        })
        .catch(error => {
          console.error('Error fetching service details:', error);
        });
    },
    
    selectService(service) {
      this.selectedService = service;
    },
    
    submitRequest() {
      if (!this.canSubmit) return;
      
      this.submitting = true;
      
      // Combine date and time into a datetime string
      const scheduleDateTime = `${this.requestForm.scheduleDate}T${this.requestForm.scheduleTime}:00`;
      
      const requestData = {
        service_id: this.selectedService.id,
        address: this.requestForm.address,
        scheduled_at: scheduleDateTime,
        description: this.requestForm.description
      };
      
      ApiService.createServiceRequest(requestData)
        .then(response => {
          alert('Service request submitted successfully!');
          this.$router.push({
            path: '/customer/requests',
            query: { new: response.data.id }
          });
        })
        .catch(error => {
          console.error('Error submitting service request:', error);
          alert('Failed to submit service request. Please try again.');
        })
        .finally(() => {
          this.submitting = false;
        });
    },
    
    formatScheduleDateTime(date, time) {
      if (!date || !time) return '';
      
      const dateTime = new Date(`${date}T${time}`);
      const options = {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      };
      
      return dateTime.toLocaleDateString(undefined, options);
    },
    
    truncateText(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
    }
  }
};
</script>

<style scoped>
.service-categories {
  margin-bottom: 20px;
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.service-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  background-color: #fff;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.1);
  border-color: #ccc;
}

.service-card.selected {
  border-color: #0d6efd;
  box-shadow: 0 0 0 2px rgba(13, 110, 253, 0.25);
  background-color: #f8f9ff;
}

.service-card-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.service-card-header h5 {
  margin: 0;
  font-size: 1.1rem;
}

.service-type {
  display: inline-block;
  font-size: 0.8rem;
  color: #6c757d;
  margin-top: 5px;
}

.service-card-body {
  padding: 15px;
}

.service-details {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  font-weight: bold;
}

.price {
  color: #0d6efd;
}

.time {
  color: #6c757d;
}

.card {
  border: none;
  box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
  margin-bottom: 30px;
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0,0,0,0.125);
  padding: 1rem;
}

.me-2 {
  margin-right: 0.5rem;
}

.me-3 {
  margin-right: 1rem;
}

.ms-2 {
  margin-left: 0.5rem;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

.mt-3 {
  margin-top: 1rem;
}

.mt-4 {
  margin-top: 1.5rem;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
  border-width: 0.2em;
}
</style> 