<template>
  <div class="professional-profile">
    <h2>My Professional Profile</h2>
    
    <div class="row mt-4">
      <div class="col-lg-4">
        <!-- Profile Navigation -->
        <div class="card mb-4">
          <div class="list-group list-group-flush">
            <a 
              href="#profile-section" 
              class="list-group-item list-group-item-action"
              :class="{ active: activeSection === 'profile' }"
              @click.prevent="activeSection = 'profile'"
            >
              <i class="fas fa-user me-2"></i> Personal Information
            </a>
            

           
          </div>
        </div>
        
        <!-- Account Summary -->
        <div class="card account-summary mb-4">
          <div class="card-body">
            <h5 class="card-title">Account Summary</h5>
            <div v-if="loadingProfile" class="text-center">
              <div class="spinner-border spinner-border-sm" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else class="account-info">
              <p><strong>Member Since:</strong> {{ formatDate(profile.created_date) }}</p>
              <p><strong>Service:</strong> {{ profile.service_type }}</p>
              <p><strong>Completed Jobs:</strong> {{ profile.completed_requests }}</p>
              <p>
                <strong>Status:</strong> 
                <span class="badge" :class="getStatusBadge(profile.approved?'approved':'blocked')">
                  {{ formatStatus(profile.status) }}
                </span>
              </p>
              <p><strong>Rating:</strong> {{ profile.average_rating }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="col-lg-8">
        <!-- Profile Information Section -->
        <div 
          id="profile-section" 
          class="card mb-4"
          v-show="activeSection === 'profile'"
        >
          <div class="card-header">
            <h5 class="card-title mb-0">Personal Information</h5>
          </div>
          <div class="card-body">
            <div v-if="loadingProfile" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <form v-else @submit.prevent="updateProfile">
              <div class="row mb-3">
                <div class="col-md-6">
                  <label for="firstName" class="form-label">Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="firstName" 
                    v-model="profile.name" 
                    required
                  >
                </div>
                
              </div>
              
              <div class="mb-3">
                <label for="email" class="form-label">Email</label>
                <input 
                  type="email" 
                  class="form-control" 
                  id="email" 
                  v-model="profile.email" 
                  required
                  disabled
                >
                <div class="form-text">Email cannot be changed. Contact support for assistance.</div>
              </div>
              
              <div class="mb-3">
                <label for="phone" class="form-label">PIN</label>
                <input 
                  type="tel" 
                  class="form-control" 
                  id="phone" 
                  v-model="profile.pin" 
                  required
                >
              </div>
              
              <div class="mb-3">
                <label for="bio" class="form-label">Professional Bio</label>
                <textarea 
                  class="form-control" 
                  id="bio" 
                  v-model="profile.description" 
                  rows="4"
                ></textarea>
                <div class="form-text">Tell customers about your experience and expertise.</div>
              </div>
              
              <div class="mb-3">
                <label for="experience" class="form-label">Years of Experience</label>
                <input 
                  type="number" 
                  class="form-control" 
                  id="experience" 
                  v-model="profile.experience" 
                  min="0"
                  required
                >
              </div>
              
              <div class="d-flex justify-content-end">
                <button 
                  type="submit" 
                  class="btn btn-primary" 
                  :disabled="updatingProfile"
                >
                  <span v-if="updatingProfile" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <!-- Services Offered Section -->
        <div 
          id="services-section" 
          class="card mb-4"
          v-show="activeSection === 'services'"
        >
          <div class="card-header">
            <h5 class="card-title mb-0">Services Offered</h5>
          </div>
          <div class="card-body">
            <div v-if="loadingServices" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else>
              <p class="text-muted mb-3">Select the services you offer to customers.</p>
              
              <div v-if="availableServices.length === 0" class="text-center my-4">
                <p>No services available to offer at this time.</p>
              </div>
              
              <div v-else class="service-selection">
                <div 
                  v-for="service in availableServices" 
                  :key="service.id" 
                  class="service-item mb-3"
                >
                  <div class="card">
                    <div class="card-body">
                      <div class="form-check">
                        <input 
                          type="checkbox" 
                          class="form-check-input" 
                          :id="`service-${service.id}`" 
                          v-model="selectedServices" 
                          :value="service.id"
                        >
                        <label class="form-check-label" :for="`service-${service.id}`">
                          <strong>{{ service.name }}</strong>
                        </label>
                      </div>
                      <p class="service-description text-muted ms-4">{{ service.description }}</p>
                      <div class="service-details ms-4">
                        <span class="badge bg-info me-2">
                          <i class="fas fa-tag me-1"></i> ${{ service.price }}
                        </span>
                        <span class="badge bg-secondary">
                          <i class="fas fa-clock me-1"></i> {{ service.time_req }} hours
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="d-flex justify-content-end mt-3">
                  <button 
                    class="btn btn-primary" 
                    @click="updateServices"
                    :disabled="updatingServices"
                  >
                    <span v-if="updatingServices" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Update Services
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Credentials Section -->
        <div 
          id="credentials-section" 
          class="card mb-4"
          v-show="activeSection === 'credentials'"
        >
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">Credentials & Certifications</h5>
            <button 
              class="btn btn-sm btn-primary"
              @click="showAddCredentialForm = true"
              v-if="!showAddCredentialForm"
            >
              <i class="fas fa-plus me-1"></i> Add Credential
            </button>
          </div>
          <div class="card-body">
            <div v-if="loadingCredentials" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="showAddCredentialForm" class="add-credential-form">
              <h6>Add New Credential</h6>
              <form @submit.prevent="addCredential">
                <div class="mb-3">
                  <label for="credentialName" class="form-label">Credential Name</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="credentialName" 
                    v-model="newCredential.name" 
                    required
                    placeholder="e.g., Certified Plumber, Master Electrician"
                  >
                </div>
                <div class="mb-3">
                  <label for="issuingOrganization" class="form-label">Issuing Organization</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    id="issuingOrganization" 
                    v-model="newCredential.issuer"
                    required
                  >
                </div>
                <div class="row mb-3">
                  <div class="col-md-6">
                    <label for="issueDate" class="form-label">Issue Date</label>
                    <input 
                      type="date" 
                      class="form-control" 
                      id="issueDate" 
                      v-model="newCredential.issue_date" 
                      required
                    >
                  </div>
                  <div class="col-md-6">
                    <label for="expiryDate" class="form-label">Expiry Date (if applicable)</label>
                    <input 
                      type="date" 
                      class="form-control" 
                      id="expiryDate" 
                      v-model="newCredential.expiry_date"
                    >
                  </div>
                </div>
                <div class="mb-3">
                  <label for="credentialDescription" class="form-label">Description (Optional)</label>
                  <textarea 
                    class="form-control" 
                    id="credentialDescription" 
                    v-model="newCredential.description" 
                    rows="2"
                  ></textarea>
                </div>
                <div class="d-flex justify-content-end">
                  <button 
                    type="button" 
                    class="btn btn-outline-secondary me-2"
                    @click="cancelAddCredential"
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit" 
                    class="btn btn-primary" 
                    :disabled="addingCredential"
                  >
                    <span v-if="addingCredential" class="spinner-border spinner-border-sm me-2" role="status"></span>
                    Save Credential
                  </button>
                </div>
              </form>
            </div>
            
            <div v-else-if="credentials.length === 0" class="text-center">
              <p>You haven't added any credentials yet.</p>
              <p class="text-muted">Adding professional credentials helps build trust with customers.</p>
              <button 
                class="btn btn-primary mt-2"
                @click="showAddCredentialForm = true"
              >
                <i class="fas fa-plus me-1"></i> Add Credential
              </button>
            </div>
            
            <div v-else>
              <div class="credential-list">
                <div v-for="credential in credentials" :key="credential.id" class="credential-item mb-3">
                  <div class="card">
                    <div class="card-body">
                      <div class="d-flex justify-content-between align-items-start">
                        <div>
                          <h6 class="mb-1">{{ credential.name }}</h6>
                          <p class="text-muted mb-1">{{ credential.issuer }}</p>
                          <p class="mb-1">
                            <small>
                              Issued: {{ formatDate(credential.issue_date) }}
                              <span v-if="credential.expiry_date">
                                | Expires: {{ formatDate(credential.expiry_date) }}
                              </span>
                            </small>
                          </p>
                          <p v-if="credential.description" class="credential-description">
                            {{ credential.description }}
                          </p>
                        </div>
                        <div class="credential-actions">
                          <button 
                            class="btn btn-sm btn-outline-danger"
                            @click="deleteCredential(credential)"
                            title="Delete Credential"
                          >
                            <i class="fas fa-trash"></i>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="d-flex justify-content-center mt-3">
                <button 
                  class="btn btn-primary"
                  @click="showAddCredentialForm = true"
                >
                  <i class="fas fa-plus me-1"></i> Add Another Credential
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Security Section -->
        <div 
          id="security-section" 
          class="card mb-4"
          v-show="activeSection === 'security'"
        >
          <div class="card-header">
            <h5 class="card-title mb-0">Security</h5>
          </div>
          <div class="card-body">
            <form @submit.prevent="changePassword">
              <div class="mb-3">
                <label for="currentPassword" class="form-label">Current Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="currentPassword" 
                  v-model="passwordData.current_password" 
                  required
                >
              </div>
              <div class="mb-3">
                <label for="newPassword" class="form-label">New Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="newPassword" 
                  v-model="passwordData.new_password" 
                  required
                  minlength="8"
                >
                <div class="form-text">Password must be at least 8 characters long.</div>
              </div>
              <div class="mb-3">
                <label for="confirmPassword" class="form-label">Confirm New Password</label>
                <input 
                  type="password" 
                  class="form-control" 
                  id="confirmPassword" 
                  v-model="passwordData.confirm_password" 
                  required
                >
                <div 
                  v-if="passwordData.new_password && passwordData.confirm_password && passwordData.new_password !== passwordData.confirm_password" 
                  class="form-text text-danger"
                >
                  Passwords do not match.
                </div>
              </div>
              <div class="d-flex justify-content-end">
                <button 
                  type="submit" 
                  class="btn btn-primary" 
                  :disabled="changingPassword || (passwordData.new_password !== passwordData.confirm_password)"
                >
                  <span v-if="changingPassword" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Change Password
                </button>
              </div>
            </form>
          </div>
        </div>
        
        <!-- Reviews Section -->
        <div 
          id="reviews-section" 
          class="card mb-4"
          v-show="activeSection === 'reviews'"
        >
          <div class="card-header">
            <h5 class="card-title mb-0">Customer Reviews</h5>
          </div>
          <div class="card-body">
            <div v-if="loadingReviews" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <div v-else-if="reviews.length === 0" class="text-center">
              <p>No reviews yet.</p>
              <p class="text-muted">Complete service requests to receive reviews from customers.</p>
            </div>
            <div v-else>
              <div class="reviews-overview mb-4">
                <div class="row">
                  <div class="col-md-4 text-center">
                    <div class="overall-rating">
                      <h2>{{ averageRating.toFixed(1) }}</h2>
                      <div class="rating-stars">
                        <i 
                          v-for="star in 5" 
                          :key="star" 
                          class="fas fa-star" 
                          :class="{ 'text-warning': star <= Math.round(averageRating) }"
                        ></i>
                      </div>
                      <p>{{ reviews.length }} reviews</p>
                    </div>
                  </div>
                  <div class="col-md-8">
                    <div class="rating-breakdown">
                      <div v-for="n in 5" :key="n" class="rating-bar mb-2">
                        <div class="d-flex align-items-center">
                          <div class="rating-label me-2">{{ 6-n }} stars</div>
                          <div class="progress flex-grow-1">
                            <div 
                              class="progress-bar bg-warning" 
                              :style="`width: ${getRatingPercentage(6-n)}%`"
                            ></div>
                          </div>
                          <div class="rating-count ms-2">{{ getRatingCount(6-n) }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="reviews-list">
                <div v-for="review in reviews" :key="review.id" class="review-item mb-3">
                  <div class="card">
                    <div class="card-body">
                      <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="rating-stars">
                          <i 
                            v-for="star in 5" 
                            :key="star" 
                            class="fas fa-star" 
                            :class="{ 'text-warning': star <= review.rating }"
                          ></i>
                        </div>
                        <div class="review-date text-muted">
                          {{ formatDate(review.created_at) }}
                        </div>
                      </div>
                      <h6 class="review-customer">{{ review.customer_name }}</h6>
                      <p class="review-service text-muted">{{ review.service_name }}</p>
                      <p class="review-text">{{ review.review || 'No written review provided.' }}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="text-center mt-3" v-if="hasMoreReviews">
                <button 
                  class="btn btn-outline-primary"
                  @click="loadMoreReviews"
                  :disabled="loadingMoreReviews"
                >
                  <span v-if="loadingMoreReviews" class="spinner-border spinner-border-sm me-2" role="status"></span>
                  Load More Reviews
                </button>
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
  name: 'ProfessionalProfile',
  data() {
    return {
      activeSection: 'profile',
      
      // Profile data
      profile: {
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        bio: '',
        years_of_experience: 0,
        status: 'pending',
        created_at: null,
        rating: null,
        services: []
      },
      loadingProfile: true,
      updatingProfile: false,
      
      // Services
      availableServices: [],
      selectedServices: [],
      loadingServices: true,
      updatingServices: false,
      
      // Credentials
      credentials: [],
      loadingCredentials: true,
      showAddCredentialForm: false,
      newCredential: this.getEmptyCredentialForm(),
      addingCredential: false,
      
      // Password
      passwordData: {
        current_password: '',
        new_password: '',
        confirm_password: ''
      },
      changingPassword: false,
      
      // Reviews
      reviews: [],
      loadingReviews: true,
      loadingMoreReviews: false,
      reviewsPage: 1,
      hasMoreReviews: false,
      
      // Stats
      stats: {
        total: 0,
        pending: 0,
        in_progress: 0,
        completed: 0,
        cancelled: 0
      }
    };
  },
  computed: {
    averageRating() {
      if (!this.reviews.length) return 0;
      const sum = this.reviews.reduce((total, review) => total + review.rating, 0);
      return sum / this.reviews.length;
    }
  },
  created() {
    this.fetchProfile();
    this.fetchServices();
   
    // Check for section in URL
    const section = this.$route.query.section;
    if (section && ['profile', 'services', 'credentials', 'security', 'reviews'].includes(section)) {
      this.activeSection = section;
    }
  },
  methods: {
    // Profile methods
    fetchProfile() {
      this.loadingProfile = true;
      
      ApiService.getProfessionalProfile()
        .then(response => {
          console.log(response.data)
          this.profile = response.data;
          
          // Initialize selected services from profile
          if (this.profile.services) {
            this.selectedServices = this.profile.services.map(service => service.id);
          }
        })
        .catch(error => {
          console.error('Error fetching profile:', error);
          alert('Failed to load your profile. Please try again.');
        })
        .finally(() => {
          this.loadingProfile = false;
        });
    },
    
    updateProfile() {
      this.updatingProfile = true;
      
      ApiService.updateProfessionalProfile(this.profile)
        .then(() => {
          alert('Profile updated successfully!');
        })
        .catch(error => {
          console.error('Error updating profile:', error);
          alert('Failed to update your profile. Please try again.');
        })
        .finally(() => {
          this.updatingProfile = false;
        });
    },
    
    // Services methods
    fetchServices() {
      this.loadingServices = true;
      
      ApiService.getServices()
        .then(response => {
          this.availableServices = response.data || [];
        })
        .catch(error => {
          console.error('Error fetching services:', error);
          alert('Failed to load available services. Please try again.');
        })
        .finally(() => {
          this.loadingServices = false;
        });
    },
    
    
    
  
    getEmptyCredentialForm() {
      return {
        name: '',
        issuer: '',
        issue_date: '',
        expiry_date: '',
        description: ''
      };
    },
    
    
    
    getRatingCount(rating) {
      return this.reviews.filter(review => review.rating === rating).length;
    },
    
    getRatingPercentage(rating) {
      if (!this.reviews.length) return 0;
      return (this.getRatingCount(rating) / this.reviews.length) * 100;
    },
    
    
    
    // Utility methods
    formatDate(dateString) {
      if (!dateString) return '';
      
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    },
    
    formatStatus(status) {
      const statusMap = {
        'pending': 'Pending Approval',
        'approved': 'Approved',
        'active': 'Active',
        'blocked': 'Blocked',
        'inactive': 'Inactive'
      };
      
      return statusMap[status] || status;
    },
    
    getStatusBadge(status) {
      const badgeMap = {
        'pending': 'bg-warning text-dark',
        'approved': 'bg-success',
        'active': 'bg-success',
        'blocked': 'bg-danger',
        'inactive': 'bg-secondary'
      };
      
      return badgeMap[status] || 'bg-secondary';
    }
  },
  watch: {
    activeSection(newSection) {
      // Update URL when section changes
      this.$router.replace({ 
        query: { ...this.$route.query, section: newSection }
      });
    }
  }
};
</script>

<style scoped>
.list-group-item.active {
  background-color: #f8f9fa;
  color: #0d6efd;
  border-color: rgba(0, 0, 0, 0.125);
  font-weight: 600;
}

.account-summary {
  background-color: #f8f9fa;
}

.account-info p {
  margin-bottom: 0.5rem;
}

.service-item .card {
  transition: transform 0.2s;
}

.service-item .card:hover {
  transform: translateY(-3px);
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);
}

.service-description {
  font-size: 0.875rem;
}

.credential-item .card,
.review-item .card {
  transition: transform 0.2s;
}

.credential-item .card:hover,
.review-item .card:hover {
  transform: translateY(-3px);
  box-shadow: 0 0.25rem 0.5rem rgba(0, 0, 0, 0.1);
}

.credential-actions {
  opacity: 0.7;
  transition: opacity 0.2s;
}

.credential-item:hover .credential-actions {
  opacity: 1;
}

.credential-description {
  font-size: 0.875rem;
  color: #6c757d;
}

.overall-rating h2 {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.rating-stars {
  font-size: 1.25rem;
  color: #dee2e6;
  margin-bottom: 0.5rem;
}

.rating-stars .text-warning {
  color: #ffc107 !important;
}

.rating-label {
  width: 60px;
}

.rating-count {
  width: 30px;
  text-align: right;
}

.review-customer {
  margin-bottom: 0.25rem;
}

.review-service {
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.review-text {
  font-style: italic;
  margin-bottom: 0;
}
</style> 