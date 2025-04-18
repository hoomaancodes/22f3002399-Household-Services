<template>
  <div class="login mt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header bg-primary text-white">Login</div>
          <div class="card-body">
            <div v-if="message" class="alert" :class="successful ? 'alert-success' : 'alert-danger'">
              {{ message }}
            </div>
            <form @submit.prevent="handleLogin">
              <div class="form-group">
                <label for="email" class="form-label">Email</label>
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
                <label for="password" class="form-label">Password</label>
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
                  <span>Login</span>
                </button>
              </div>
            </form>
            <div class="mt-3 text-center">
              <p>Don't have an account? 
                <router-link to="/register" class="text-primary">Register as Customer</router-link> |
                <router-link to="/register-professional" class="text-secondary">Register as Professional</router-link>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AuthService from '@/services/AuthService';

export default {
  name: 'LoginPage',
  data() {
    return {
      user: {
        email: '',
        password: ''
      },
      loading: false,
      message: '',
      successful: false
    };
  },
  methods: {
    handleLogin() {
      this.message = '';
      this.loading = true;
      
      AuthService.login(this.user)
        .then(response => {
          this.successful = true;
          this.message = 'Login successful!';
          console.log(response.role)
          // Redirect based on role
          switch(response.role) {
            case 'admin':
              this.$router.push('/admin');
              break;
            case 'professional':
              this.$router.push('/professional');
              break;
            case 'customer':
              this.$router.push('/customer');
              break;
            default:
              this.$router.push('/');
          }
        })
        .catch(error => {
          this.successful = false;
          this.message = (error.response && error.response.data && error.response.data.message) ||
                        'Error occurred during login';
          console.error('Login error:', error);
        })
        .finally(() => {
          this.loading = false;
        });
    }
  }
};
</script> 