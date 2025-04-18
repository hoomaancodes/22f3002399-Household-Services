<template>
  <div class="register">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">Register as Professional</div>
          <div class="card-body">
            <div v-if="message" class="alert" :class="successful ? 'alert-success' : 'alert-danger'">
              {{ message }}
            </div>
            <form @submit.prevent="handleRegister" v-if="!successful">
              <div class="form-group">
                <label for="name">Full Name</label>
                <input
                  v-model="user.name"
                  type="text"
                  class="form-control"
                  id="name"
                  name="name"
                  required
                />
              </div>
              
              <div class="form-group mt-3">
                <label for="email">Email</label>
                <input
                  v-model="user.email"
                  type="email"
                  class="form-control"
                  id="email"
                  name="email"
                  required
                />
              </div>
              
              <div class="form-group mt-3">
                <label for="service_type">Service Type</label>
                <select
                  v-model="user.service_type"
                  class="form-control"
                  id="service_type"
                  name="service_type"
                  required
                >
                  <option value="">Select Service Type</option>
                  <option v-for="(type, index) in serviceTypes" :key="index" :value="type">
                    {{ type }}
                  </option>
                </select>
              </div>
              
              <div class="form-group mt-3">
                <label for="address">Address</label>
                <input
                  v-model="user.address"
                  type="text"
                  class="form-control"
                  id="address"
                  name="address"
                  required
                />
              </div>
              
              <div class="form-group mt-3">
                <label for="pin">PIN Code</label>
                <input
                  v-model="user.pin"
                  type="number"
                  class="form-control"
                  id="pin"
                  name="pin"
                  required
                />
              </div>
              
              <div class="form-group mt-3">
                <label for="experience">Experience (Years)</label>
                <input
                  v-model="user.experience"
                  type="number"
                  class="form-control"
                  id="experience"
                  name="experience"
                  required
                />
              </div>
              
              <div class="form-group mt-3">
                <label for="password">Password</label>
                <input
                  v-model="user.password"
                  type="password"
                  class="form-control"
                  id="password"
                  name="password"
                  required
                />
              </div>
              
              <div class="form-group mt-4">
                <button class="btn btn-primary btn-block" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                  <span>Register</span>
                </button>
              </div>
            </form>
            
            <div class="mt-3 text-center" v-if="!successful">
              <p>Already have an account? <router-link to="/login">Login</router-link></p>
              <p>Are you a customer? <router-link to="/register">Register as Customer</router-link></p>
            </div>
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
  name: 'RegisterProfessional',
  data() {
    return {
      user: {
        name: '',
        email: '',
        password: '',
        address: '',
        pin: '',
        service_type: '',
        experience: '',
        role: 'professional'
      },
      serviceTypes: [],
      loading: false,
      message: '',
      successful: false
    };
  },
  created() {
    this.fetchServiceTypes();
  },
  methods: {
    fetchServiceTypes() {
      ApiService.getServiceTypes()
        .then(response => {
          this.serviceTypes = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching service types:', error);
          // Fallback to default service types
          this.serviceTypes = ['Plumbing', 'Electrical', 'Cleaning', 'Gardening', 'Painting', 'Carpentry'];
        });
    },
    handleRegister() {
      this.message = '';
      this.loading = true;
      
      AuthService.register(this.user)
        .then(() => {
          this.message = 'Registration successful! Please login after admin approval.';
          this.successful = true;
          
          // Redirect to login after a short delay
          setTimeout(() => {
            this.$router.push('/login');
          }, 3000);
        })
        .catch(error => {
          this.successful = false;
          this.message = (error.response && error.response.data && error.response.data.message) ||
                        'Error occurred during registration';
          console.error('Registration error:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
};
</script>

<style scoped>
.register {
  margin-top: 2rem;
}

.btn-block {
  display: block;
  width: 100%;
}
</style> 