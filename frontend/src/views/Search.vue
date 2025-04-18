<template>
  <div class="search">
    <div class="card">
      <div class="card-header">
        <h2>Search Services</h2>
      </div>
      <div class="card-body">
        <form @submit.prevent="searchServices" class="mb-4">
          <div class="row g-3">
            <div class="col-md-5">
              <label for="searchQuery" class="form-label">Search Query</label>
              <input
                type="text"
                class="form-control"
                id="searchQuery"
                v-model="searchQuery"
                placeholder="Enter search term"
                required
              />
            </div>
            <div class="col-md-4">
              <label for="searchBy" class="form-label">Search By</label>
              <select class="form-select" id="searchBy" v-model="searchBy">
                <option value="">All</option>
                <option value="name">Service Name</option>
                <option value="type">Service Type</option>
                <option value="pincode">Pin Code</option>
                <template v-if="isAdmin">
                  <option value="professional">Professional</option>
                  <option value="customer">Customer</option>
                </template>
              </select>
            </div>
            <div class="col-md-3 d-flex align-items-end">
              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                <span v-if="loading" class="spinner-border spinner-border-sm"></span>
                Search
              </button>
            </div>
          </div>
        </form>

        <div v-if="message" class="alert" :class="isError ? 'alert-danger' : 'alert-info'">
          {{ message }}
        </div>

        <div v-if="results.length > 0" class="search-results">
          <h3 class="mb-3">Search Results</h3>
          
          <!-- Service results -->
          <div v-if="searchBy === '' || searchBy === 'name' || searchBy === 'type' || searchBy === 'pincode'">
            <div class="row">
              <div class="col-md-4 mb-3" v-for="service in results" :key="service.id">
                <service-card :service="service">
                  <template v-slot:actions>
                    <button
                      v-if="isCustomer"
                      class="btn btn-primary"
                      @click="bookService(service.id)"
                    >
                      Book Service
                    </button>
                    <button
                      v-if="isAdmin"
                      class="btn btn-warning me-2"
                      @click="editService(service.id)"
                    >
                      Edit
                    </button>
                    <button
                      v-if="isAdmin"
                      class="btn btn-danger"
                      @click="confirmDeleteService(service.id)"
                    >
                      Delete
                    </button>
                  </template>
                </service-card>
              </div>
            </div>
          </div>

          <!-- Professional results (Admin only) -->
          <div v-if="searchBy === 'professional' && isAdmin">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Service Type</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="professional in results" :key="professional.id">
                  <td>{{ professional.id }}</td>
                  <td>{{ professional.name }}</td>
                  <td>{{ professional.email }}</td>
                  <td>{{ professional.service_type }}</td>
                  <td>
                    <span
                      class="badge"
                      :class="professional.approved ? 'bg-success' : 'bg-warning'"
                    >
                      {{ professional.approved ? 'Approved' : 'Pending' }}
                    </span>
                  </td>
                  <td>
                    <button
                      v-if="!professional.approved"
                      class="btn btn-sm btn-success me-1"
                      @click="approveProfessional(professional.id)"
                    >
                      Approve
                    </button>
                    <button
                      v-if="!professional.blocked"
                      class="btn btn-sm btn-danger"
                      @click="blockProfessional(professional.id)"
                    >
                      Block
                    </button>
                    <button
                      v-else
                      class="btn btn-sm btn-secondary"
                      @click="unblockProfessional(professional.id)"
                    >
                      Unblock
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Customer results (Admin only) -->
          <div v-if="searchBy === 'customer' && isAdmin">
            <table class="table table-striped">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Address</th>
                  <th>Pin</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="customer in results" :key="customer.id">
                  <td>{{ customer.id }}</td>
                  <td>{{ customer.name }}</td>
                  <td>{{ customer.email }}</td>
                  <td>{{ customer.address }}</td>
                  <td>{{ customer.pin }}</td>
                  <td>
                    <button
                      v-if="!customer.blocked"
                      class="btn btn-sm btn-danger"
                      @click="blockCustomer(customer.id)"
                    >
                      Block
                    </button>
                    <button
                      v-else
                      class="btn btn-sm btn-secondary"
                      @click="unblockCustomer(customer.id)"
                    >
                      Unblock
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
import AuthService from '@/services/AuthService';
import ServiceCard from '@/components/ServiceCard.vue';

export default {
  name: 'SearchPage',
  components: {
    ServiceCard
  },
  data() {
    return {
      searchQuery: '',
      searchBy: '',
      results: [],
      loading: false,
      message: '',
      isError: false,
      currentUser: null
    };
  },
  computed: {
    isAdmin() {
      return this.currentUser && this.currentUser.role === 'admin';
    },
    isCustomer() {
      return this.currentUser && this.currentUser.role === 'customer';
    },
    isProfessional() {
      return this.currentUser && this.currentUser.role === 'professional';
    }
  },
  created() {
    this.currentUser = AuthService.getCurrentUser();
  },
  methods: {
    searchServices() {
      this.loading = true;
      this.message = '';
      this.results = [];

      ApiService.searchServices(this.searchQuery, this.searchBy)
        .then(response => {
          this.results = response.data;
          if (this.results.length === 0) {
            this.message = 'No results found for your search.';
          }
        })
        .catch(error => {
          console.error('Error searching:', error);
          this.isError = true;
          this.message = 'An error occurred while searching. Please try again.';
        })
        .finally(() => {
          this.loading = false;
        });
    },
    bookService(serviceId) {
      ApiService.createServiceRequest({ service_id: serviceId })
        .then(() => {
          alert('Service booked successfully!');
        })
        .catch(error => {
          console.error('Error booking service:', error);
          alert('Failed to book service. Please try again.');
        });
    },
    editService(serviceId) {
      this.$router.push(`/admin/services?edit=${serviceId}`);
    },
    confirmDeleteService(serviceId) {
      if (confirm('Are you sure you want to delete this service?')) {
        ApiService.deleteService(serviceId)
          .then(() => {
            alert('Service deleted successfully!');
            this.searchServices(); // Refresh the search
          })
          .catch(error => {
            console.error('Error deleting service:', error);
            alert('Failed to delete service. Please try again.');
          });
      }
    },
    approveProfessional(professionalId) {
      ApiService.updateProfessionalStatus(professionalId, { approved: true })
        .then(() => {
          alert('Professional approved successfully!');
          this.searchServices(); // Refresh the search
        })
        .catch(error => {
          console.error('Error approving professional:', error);
          alert('Failed to approve professional. Please try again.');
        });
    },
    blockProfessional(professionalId) {
      ApiService.updateProfessionalStatus(professionalId, { blocked: true })
        .then(() => {
          alert('Professional blocked successfully!');
          this.searchServices(); // Refresh the search
        })
        .catch(error => {
          console.error('Error blocking professional:', error);
          alert('Failed to block professional. Please try again.');
        });
    },
    unblockProfessional(professionalId) {
      ApiService.updateProfessionalStatus(professionalId, { blocked: false })
        .then(() => {
          alert('Professional unblocked successfully!');
          this.searchServices(); // Refresh the search
        })
        .catch(error => {
          console.error('Error unblocking professional:', error);
          alert('Failed to unblock professional. Please try again.');
        });
    },
    blockCustomer(customerId) {
      ApiService.updateCustomerStatus(customerId, { blocked: true })
        .then(() => {
          alert('Customer blocked successfully!');
          this.searchServices(); // Refresh the search
        })
        .catch(error => {
          console.error('Error blocking customer:', error);
          alert('Failed to block customer. Please try again.');
        });
    },
    unblockCustomer(customerId) {
      ApiService.updateCustomerStatus(customerId, { blocked: false })
        .then(() => {
          alert('Customer unblocked successfully!');
          this.searchServices(); // Refresh the search
        })
        .catch(error => {
          console.error('Error unblocking customer:', error);
          alert('Failed to unblock customer. Please try again.');
        });
    }
  }
};
</script>

<style scoped>
.search {
  max-width: 1200px;
  margin: 0 auto;
}
.search-results {
  margin-top: 2rem;
}
.me-1 {
  margin-right: 0.25rem;
}
.me-2 {
  margin-right: 0.5rem;
}
</style> 