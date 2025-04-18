<template>
  <div class="customer-services">
    <PageHeader 
      title="Browse Services" 
      subtitle="Find the perfect service for your household needs">
    </PageHeader>
    
    <!-- Filter and Search -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-4">
            <label for="typeFilter" class="form-label">Filter by Type</label>
            <select v-model="typeFilter" class="form-select" id="typeFilter">
              <option value="">All Types</option>
              <option v-for="(type, index) in serviceTypes" :key="index" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          <div class="col-md-4">
            <label for="sortBy" class="form-label">Sort By</label>
            <select v-model="sortOption" class="form-select" id="sortBy">
              <option value="name_asc">Name (A-Z)</option>
              <option value="name_desc">Name (Z-A)</option>
              <option value="price_asc">Price (Low to High)</option>
              <option value="price_desc">Price (High to Low)</option>
              <option value="time_asc">Duration (Short to Long)</option>
              <option value="time_desc">Duration (Long to Short)</option>
            </select>
          </div>
          <div class="col-md-4">
            <label for="searchQuery" class="form-label">Search</label>
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                id="searchQuery" 
                v-model="searchQuery" 
                placeholder="Search services..."
              >
              <button class="btn btn-outline-secondary" type="button">
                <i class="fas fa-search"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Services List -->
    <div class="row">
      <div v-if="loading" class="col-12 text-center my-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>
      
      <div v-else-if="filteredServices.length === 0" class="col-12 text-center my-5">
        <p>No services found matching your criteria.</p>
        <p class="text-muted">Try adjusting your filters or search query.</p>
      </div>
      
      <div 
        v-else
        v-for="service in filteredServices" 
        :key="service.id" 
        class="col-md-4 mb-4"
      >
        <ServiceCard 
          :service="service" 
          @click="navigateToServiceRequest(service.id)"
        >
          <template v-slot:actions>
            <button 
              @click.stop="navigateToServiceRequest(service.id)" 
              class="btn btn-primary w-100 mt-3"
            >
              Request Service
            </button>
          </template>
        </ServiceCard>
      </div>
    </div>
    
    <!-- Popular Services Section -->
    <div v-if="!loading && popularServices.length > 0" class="mt-5">
      <div class="section-header">
        <h2>Popular Services</h2>
      </div>
      <div class="row mt-3">
        <div 
          v-for="service in popularServices" 
          :key="service.id" 
          class="col-md-4 mb-4"
        >
          <ServiceCard 
            :service="service"
            @click="navigateToServiceRequest(service.id)"
          >
            <template v-slot:actions>
              <div class="d-flex align-items-center mb-2">
                <span class="badge bg-accent me-2">
                  <i class="fas fa-star me-1"></i> Popular
                </span>
              </div>
              <button 
                @click.stop="navigateToServiceRequest(service.id)" 
                class="btn btn-accent w-100"
              >
                Request Service
              </button>
            </template>
          </ServiceCard>
        </div>
      </div>
    </div>
    
    <!-- Service Categories Section -->
    <div class="service-categories mt-5">
      <div class="section-header">
        <h2>Service Categories</h2>
      </div>
      
      <div class="row mt-3">
        <div 
          v-for="category in categoriesWithCount" 
          :key="category.name" 
          class="col-md-3 col-sm-6 mb-4"
        >
          <div 
            class="card category-card" 
            @click="setTypeFilter(category.name)"
          >
            <div class="card-body">
              <div class="category-icon">
                <i class="fas" :class="getCategoryIcon(category.name)"></i>
              </div>
              <div class="category-details">
                <h5>{{ category.name }}</h5>
                <span>{{ category.count }} services</span>
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
import PageHeader from '@/components/PageHeader.vue';
import ServiceCard from '@/components/ServiceCard.vue';

export default {
  name: 'CustomerServices',
  components: {
    PageHeader,
    ServiceCard
  },
  data() {
    return {
      services: [],
      popularServices: [],
      serviceTypes: [],
      loading: true,
      typeFilter: '',
      searchQuery: '',
      sortOption: 'name_asc'
    };
  },
  computed: {
    filteredServices() {
      if (!this.services.length) return [];
      
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
          service.description.toLowerCase().includes(query) ||
          service.service_type.toLowerCase().includes(query)
        );
      }
      
      // Apply sorting
      const [field, direction] = this.sortOption.split('_');
      result.sort((a, b) => {
        let comparison = 0;
        
        if (field === 'name') {
          comparison = a.name.localeCompare(b.name);
        } else if (field === 'price') {
          comparison = a.price - b.price;
        } else if (field === 'time') {
          comparison = a.time_req - b.time_req;
        }
        
        return direction === 'asc' ? comparison : -comparison;
      });
      
      return result;
    },
    categoriesWithCount() {
      const categoryMap = {};
      
      this.services.forEach(service => {
        const type = service.service_type;
        if (!categoryMap[type]) {
          categoryMap[type] = { name: type, count: 0 };
        }
        categoryMap[type].count++;
      });
      
      return Object.values(categoryMap);
    }
  },
  methods: {
    navigateToServiceRequest(serviceId) {
      this.$router.push(`/customer/request-service?service=${serviceId}`);
    },
    fetchServices() {
      this.loading = true;
      ApiService.getServices()
        .then(response => {
          this.services = response.data;
          
          // Extract unique service types
          const types = new Set();
          this.services.forEach(service => {
            if (service.service_type) {
              types.add(service.service_type);
            }
          });
          this.serviceTypes = [...types];
        })
        .catch(error => {
          console.error('Error fetching services:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    fetchPopularServices() {
      ApiService.getPopularServices()
        .then(response => {
          this.popularServices = response.data;
        })
        .catch(error => {
          console.error('Error fetching popular services:', error);
        });
    },
    truncateText(text, maxLength) {
      if (!text) return '';
      return text.length > maxLength ? text.substr(0, maxLength) + '...' : text;
    },
    setTypeFilter(type) {
      this.typeFilter = type;
      // Scroll to services list
      const servicesElement = document.querySelector('.customer-services');
      if (servicesElement) {
        servicesElement.scrollIntoView({ behavior: 'smooth' });
      }
    },
    getCategoryIcon(category) {
      const iconMap = {
        'Plumbing': 'fa-wrench',
        'Electrical': 'fa-bolt',
        'Cleaning': 'fa-broom',
        'Gardening': 'fa-leaf',
        'Painting': 'fa-paint-roller',
        'Carpentry': 'fa-hammer',
        'Moving': 'fa-truck',
        'Renovation': 'fa-hard-hat'
      };
      
      return iconMap[category] || 'fa-tools';
    }
  },
  created() {
    this.fetchServices();
    this.fetchPopularServices();
  }
};
</script>

<style scoped>
.service-card {
  transition: transform 0.3s, box-shadow 0.3s;
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
  overflow: hidden;
}

.service-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
}

.service-card .card-header {
  background-color: #f8f9fa;
  padding: 1rem;
  border-bottom: none;
  position: relative;
}

.service-type {
  position: absolute;
  top: 1rem;
  right: 1rem;
  font-size: 0.75rem;
}

.service-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
  font-weight: 600;
}

.service-price {
  color: #28a745;
}

.service-time {
  color: #6c757d;
}

.popular-service-card {
  background-color: #f8f9fa;
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
  position: relative;
  overflow: hidden;
}

.popular-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #ffc107;
  color: #343a40;
  font-size: 0.75rem;
  padding: 0.25rem 0.75rem;
  font-weight: 600;
  border-bottom-left-radius: 0.5rem;
}

.category-card {
  display: flex;
  align-items: center;
  padding: 1rem;
  background-color: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
}

.category-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.15);
}

.category-icon {
  width: 3rem;
  height: 3rem;
  background-color: #e9ecef;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-size: 1.25rem;
  color: #495057;
}

.category-details h5 {
  margin-bottom: 0.25rem;
  font-size: 1rem;
}

.category-details span {
  font-size: 0.875rem;
  color: #6c757d;
}

.card-footer {
  background-color: transparent;
  border-top: 1px solid rgba(0,0,0,0.125);
  padding: 1rem;
}
</style> 