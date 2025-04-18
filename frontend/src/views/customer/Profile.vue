<template>
  <div class="customer-profile">
    <PageHeader 
      title="Profile" 
      subtitle="View and update your personal information">
    </PageHeader>
    
    <div class="profile-content" v-if="customer">
      <div class="card">
        <div class="card-body">
          <div class="form-group">
            <label class="form-label">Name</label>
            <input type="text" class="form-control" v-model="customer.name" :disabled="!isEditing">
          </div>
          <div class="form-group mt-3">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" v-model="customer.email" disabled>
          </div>
          <div class="form-group mt-3">
            <label class="form-label">Phone</label>
            <input type="tel" class="form-control" v-model="customer.phone" :disabled="!isEditing">
          </div>
          <div class="form-group mt-3">
            <label class="form-label">Address</label>
            <textarea class="form-control" v-model="customer.address" :disabled="!isEditing"></textarea>
          </div>
          <div class="mt-4">
            <button v-if="!isEditing" @click="startEditing" class="btn btn-primary">Edit Profile</button>
            <template v-else>
              <button @click="saveProfile" class="btn btn-accent me-2">Save Changes</button>
              <button @click="cancelEditing" class="btn btn-secondary">Cancel</button>
            </template>
          </div>
        </div>
      </div>
      
      <div class="card mt-4">
        <div class="card-body">
          <div class="section-header">
            <h3>Change Password</h3>
          </div>
          <div class="form-group">
            <label class="form-label">Current Password</label>
            <input type="password" class="form-control" v-model="passwordData.currentPassword">
          </div>
          <div class="form-group mt-3">
            <label class="form-label">New Password</label>
            <input type="password" class="form-control" v-model="passwordData.newPassword">
          </div>
          <div class="form-group mt-3">
            <label class="form-label">Confirm New Password</label>
            <input type="password" class="form-control" v-model="passwordData.confirmPassword">
          </div>
          <div class="mt-4">
            <button @click="changePassword" class="btn btn-primary">Change Password</button>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';
import PageHeader from '@/components/PageHeader.vue';

export default {
  name: 'CustomerProfile',
  components: {
    PageHeader
  },
  data() {
    return {
      customer: null,
      isEditing: false,
      originalCustomer: null,
      passwordData: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      isLoading: false
    }
  },
  created() {
    this.loadProfile();
  },
  methods: {
    loadProfile() {
      this.isLoading = true;
      ApiService.getCustomerProfile()
        .then(response => {
          this.customer = response.data;
          this.isLoading = false;
        })
        .catch(error => {
          console.error('Error loading profile:', error);
          this.isLoading = false;
        });
    },
    startEditing() {
      this.originalCustomer = { ...this.customer };
      this.isEditing = true;
    },
    cancelEditing() {
      this.customer = { ...this.originalCustomer };
      this.isEditing = false;
    },
    saveProfile() {
      this.isLoading = true;
      ApiService.updateCustomerProfile(this.customer)
        .then(() => {
          this.isEditing = false;
          this.isLoading = false;
          alert('Profile updated successfully');
        })
        .catch(error => {
          console.error('Error updating profile:', error);
          this.isLoading = false;
          alert('Failed to update profile');
        });
    },
    changePassword() {
      if (this.passwordData.newPassword !== this.passwordData.confirmPassword) {
        alert('New passwords do not match');
        return;
      }
      
      this.isLoading = true;
      ApiService.changePassword(this.passwordData)
        .then(() => {
          this.passwordData = {
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
          };
          this.isLoading = false;
          alert('Password changed successfully');
        })
        .catch(error => {
          console.error('Error changing password:', error);
          this.isLoading = false;
          alert('Failed to change password');
        });
    }
  }
}
</script>

<style scoped>
.customer-profile {
  max-width: 800px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  font-weight: bold;
}

.btn {
  margin-right: 0.5rem;
}
</style>