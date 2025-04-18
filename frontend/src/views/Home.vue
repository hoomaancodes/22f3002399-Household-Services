<template>
  <div class="home">
    <div class="jumbotron">
      <h1 class="display-4">Welcome to Household Services</h1>
      <p class="lead">We provide a variety of household services to meet your needs.</p>
      <hr class="my-4">
      <p>Browse our services or register to book a service today!</p>
      <div v-if="!currentUser" class="mt-4">
        <router-link to="/login" class="btn btn-primary mr-2">Login</router-link>
        <router-link to="/register" class="btn btn-accent mx-2">Register as Customer</router-link>
        <router-link to="/register-professional" class="btn btn-secondary ml-2">Join as Professional</router-link>
      </div>
    </div>

    <div class="section-header mt-5">
      <h2>Our Services</h2>
    </div>

    <div class="row mt-4">
      <div class="col-md-4" v-for="(serviceType, index) in serviceTypes" :key="index">
        <div class="card service-card">
          <div class="card-body">
            <h5 class="card-title">{{ serviceType }}</h5>
            <p class="card-text">Quality service for your home needs.</p>
            <router-link to="/login" class="btn btn-primary" v-if="!currentUser">Login to Book</router-link>
            <router-link :to="userHomeRoute" class="btn btn-primary" v-else>View Details</router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="section-header mt-5">
      <h2>Why Choose Us</h2>
    </div>

    <div class="row mt-4">
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <div class="display-4 text-accent">
              <i class="fas fa-user-check"></i>
            </div>
            <h4 class="mt-3">Verified Professionals</h4>
            <p>All our service professionals undergo thorough verification and training.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <div class="display-4 text-accent">
              <i class="fas fa-bolt"></i>
            </div>
            <h4 class="mt-3">Quick Service</h4>
            <p>Get your household services done quickly and efficiently.</p>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card">
          <div class="card-body text-center">
            <div class="display-4 text-accent">
              <i class="fas fa-shield-alt"></i>
            </div>
            <h4 class="mt-3">Satisfaction Guaranteed</h4>
            <p>We ensure 100% satisfaction with our quality service.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AuthService from '@/services/AuthService';
import ApiService from '@/services/ApiService';

export default {
  name: 'HomePage',
  data() {
    return {
      currentUser: null,
      serviceTypes: []
    };
  },
  created() {
    this.currentUser = AuthService.getCurrentUser();
    this.fetchServiceTypes();
  },
  computed: {
    userHomeRoute() {
      if (!this.currentUser) return '/login';
      
      switch(this.currentUser.role) {
        case 'admin':
          return '/admin';
        case 'professional':
          return '/professional';
        case 'customer':
          return '/customer';
        default:
          return '/';
      }
    }
  },
  methods: {
    fetchServiceTypes() {
      ApiService.getServiceTypes()
        .then(response => {
          this.serviceTypes = response.data || ['Plumbing', 'Electrical', 'Cleaning'];
        })
        .catch(error => {
          console.error('Error fetching service types:', error);
          // Fallback to default service types
          this.serviceTypes = ['Plumbing', 'Electrical', 'Cleaning', 'Gardening', 'Painting', 'Carpentry'];
        });
    }
  }
};
</script>

<style scoped>
.jumbotron {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 0.3rem;
  margin-bottom: 2rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.mx-2 {
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}
</style> 