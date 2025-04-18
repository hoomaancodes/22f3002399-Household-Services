<template>
  <nav class="navbar navbar-expand-lg navbar-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">Household Services</router-link>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          
          <!-- Admin Links -->
          <template v-if="isAdmin">
            <li class="nav-item">
              <router-link class="nav-link" to="/admin">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/services">Services</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/professionals">Professionals</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/customers">Customers</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/admin/reports">Reports</router-link>
            </li>
          </template>
          
          <!-- Professional Links -->
          <template v-if="isProfessional">
            <li class="nav-item">
              <router-link class="nav-link" to="/professional">Dashboard</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/professional/service-requests">Service Requests</router-link>
            </li>
          
            <li class="nav-item">
              <router-link class="nav-link" to="/professional/profile">My Profile</router-link>
            </li>
          </template>
          
          <!-- Customer Links -->
          <template v-if="isCustomer">
            
            <li class="nav-item">
              <router-link class="nav-link" to="/customer/services">Browse Services</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/customer/requests">My Requests</router-link>
            </li>
            
          </template>

          <!-- Visible to all logged in users -->
          <li class="nav-item" v-if="isLoggedIn">
            <router-link class="nav-link" to="/search">Search</router-link>
          </li>
        </ul>
        
        <ul class="navbar-nav">
          <template v-if="isLoggedIn">
            <li class="nav-item">
              <span class="nav-link">Welcome, {{ currentUser.role | capitalize }}</span>
            </li>
            <li class="nav-item">
              <a class="nav-link" href="#" @click.prevent="logout">Logout</a>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Register</router-link>
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import AuthService from '@/services/AuthService';

export default {
  name: 'NavbarComponent',
  data() {
    return {
      currentUser: null
    };
  },
  computed: {
    isLoggedIn() {
      return this.currentUser !== null;
    },
    isAdmin() {
      return this.currentUser && this.currentUser.role === 'admin';
    },
    isProfessional() {
      return this.currentUser && this.currentUser.role === 'professional';
    },
    isCustomer() {
      return this.currentUser && this.currentUser.role === 'customer';
    }
  },
  methods: {
    logout() {
      AuthService.logout();
      this.currentUser = null;
      this.$router.push('/login');
    }
  },
  created() {
    this.currentUser = AuthService.getCurrentUser();
  },
  watch: {
    $route() {
      this.currentUser = AuthService.getCurrentUser();
    }
  },
  filters: {
    capitalize(value) {
      if (!value) return '';
      return value.charAt(0).toUpperCase() + value.slice(1);
    }
  }
};
</script> 