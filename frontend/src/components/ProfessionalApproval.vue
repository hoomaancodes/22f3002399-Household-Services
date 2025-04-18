<template>
  <div class="professional-approval">
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="!professional" class="alert alert-warning">
      Professional profile not found.
    </div>
    
    <div v-else class="card">
      <div class="card-header">
        <h5 class="mb-0">Professional Profile Review</h5>
      </div>
      
      <div class="card-body">
        <div class="row">
          <div class="col-md-4">
            <div class="profile-summary">
              <div class="text-center mb-3">
                <div class="avatar-placeholder">
                  <i class="fas fa-user-tie fa-5x text-secondary"></i>
                </div>
                <h5 class="mt-3">{{ professional.name }}</h5>
                <p class="text-muted">{{ professional.service_type }}</p>
                <div class="badge" :class="getStatusBadgeClass(professional.status)">
                  {{ formatStatus(professional.status) }}
                </div>
              </div>
              
              <div class="profile-details mt-4">
                <div class="detail-item">
                  <i class="fas fa-envelope text-secondary me-2"></i>
                  <span>{{ professional.email }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-phone text-secondary me-2"></i>
                  <span>{{ professional.phone }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-map-marker-alt text-secondary me-2"></i>
                  <span>{{ professional.address }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-calendar-alt text-secondary me-2"></i>
                  <span>Joined: {{ formatDate(professional.created_at) }}</span>
                </div>
                <div class="detail-item">
                  <i class="fas fa-briefcase text-secondary me-2"></i>
                  <span>Experience: {{ professional.experience }} years</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="col-md-8">
            <div class="professional-documents mb-4">
              <h6>Verification Documents</h6>
              <div class="documents-list">
                <div v-if="professional.documents && professional.documents.length > 0">
                  <div v-for="(doc, index) in professional.documents" :key="index" class="document-item card mb-2">
                    <div class="card-body p-2">
                      <div class="d-flex justify-content-between align-items-center">
                        <div>
                          <i class="fas fa-file-alt me-2"></i>
                          <span>{{ doc.name }}</span>
                        </div>
                        <button class="btn btn-sm btn-outline-primary" @click="viewDocument(doc)">
                          View
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="text-muted">
                  No verification documents provided.
                </div>
              </div>
            </div>
            
            <div class="professional-description mb-4">
              <h6>Description</h6>
              <p>{{ professional.description || 'No description provided.' }}</p>
            </div>
            
            <div class="admin-notes mb-4">
              <h6>Admin Notes</h6>
              <textarea 
                v-model="adminNotes" 
                class="form-control" 
                rows="3" 
                placeholder="Add notes about this professional..."
              ></textarea>
            </div>
            
            <div class="approval-actions d-flex justify-content-end">
              <button 
                v-if="professional.status === 'pending'"
                @click="rejectProfessional" 
                class="btn btn-danger me-2"
                :disabled="processing"
              >
                <span v-if="processing && actionType === 'reject'" class="spinner-border spinner-border-sm me-1"></span>
                Reject
              </button>
              
              <button 
                v-if="professional.status === 'pending'"
                @click="approveProfessional" 
                class="btn btn-success me-2"
                :disabled="processing"
              >
                <span v-if="processing && actionType === 'approve'" class="spinner-border spinner-border-sm me-1"></span>
                Approve
              </button>
              
              <button 
                v-if="professional.status === 'approved'"
                @click="blockProfessional" 
                class="btn btn-warning me-2"
                :disabled="processing"
              >
                <span v-if="processing && actionType === 'block'" class="spinner-border spinner-border-sm me-1"></span>
                Block
              </button>
              
              <button 
                v-if="professional.status === 'blocked'"
                @click="unblockProfessional" 
                class="btn btn-primary me-2"
                :disabled="processing"
              >
                <span v-if="processing && actionType === 'unblock'" class="spinner-border spinner-border-sm me-1"></span>
                Unblock
              </button>
              
              <button 
                @click="$emit('close')" 
                class="btn btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Document Viewer Modal -->
    <div v-if="showDocumentModal" class="modal-backdrop" @click="closeDocumentModal"></div>
    <div v-if="showDocumentModal" class="modal-container">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h5 class="modal-title">{{ selectedDocument.name }}</h5>
          <button type="button" class="btn-close" @click="closeDocumentModal"></button>
        </div>
        <div class="modal-body text-center">
          <!-- This would display the document - for demo we'll just show a placeholder -->
          <div class="document-placeholder">
            <i class="fas fa-file-alt fa-5x mb-3"></i>
            <p>Document preview would appear here</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ApiService from '@/services/ApiService';

export default {
  name: 'ProfessionalApproval',
  props: {
    professionalId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      professional: null,
      loading: true,
      processing: false,
      actionType: null,
      adminNotes: '',
      showDocumentModal: false,
      selectedDocument: null
    };
  },
  methods: {
    async fetchProfessionalDetails() {
      this.loading = true;
      try {
        const response = await ApiService.get(`/professionals/${this.professionalId}`);
        this.professional = response.data;
        this.adminNotes = this.professional.admin_notes || '';
      } catch (error) {
        console.error('Error fetching professional details:', error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },
    formatStatus(status) {
      if (!status) return '';
      return status.charAt(0).toUpperCase() + status.slice(1);
    },
    getStatusBadgeClass(status) {
      const statusClasses = {
        'pending': 'bg-warning',
        'approved': 'bg-success',
        'rejected': 'bg-danger',
        'blocked': 'bg-dark'
      };
      return statusClasses[status] || 'bg-secondary';
    },
    async updateProfessionalStatus(status) {
      this.processing = true;
      this.actionType = status;
      try {
        await ApiService.put(`/professionals/${this.professionalId}/status`, {
          status,
          admin_notes: this.adminNotes
        });
        
        // Update local status
        this.professional.status = status;
        this.professional.admin_notes = this.adminNotes;
        
        this.$emit('status-updated', {
          id: this.professionalId,
          status,
          admin_notes: this.adminNotes
        });
      } catch (error) {
        console.error(`Error updating professional status to ${status}:`, error);
      } finally {
        this.processing = false;
        this.actionType = null;
      }
    },
    approveProfessional() {
      this.updateProfessionalStatus('approved');
    },
    rejectProfessional() {
      if (confirm('Are you sure you want to reject this professional?')) {
        this.updateProfessionalStatus('rejected');
      }
    },
    blockProfessional() {
      if (confirm('Are you sure you want to block this professional?')) {
        this.updateProfessionalStatus('blocked');
      }
    },
    unblockProfessional() {
      this.updateProfessionalStatus('approved');
    },
    viewDocument(doc) {
      this.selectedDocument = doc;
      this.showDocumentModal = true;
    },
    closeDocumentModal() {
      this.showDocumentModal = false;
      this.selectedDocument = null;
    }
  },
  created() {
    this.fetchProfessionalDetails();
  },
  watch: {
    professionalId() {
      this.fetchProfessionalDetails();
    }
  }
}
</script>

<style scoped>
.professional-approval {
  position: relative;
}
.avatar-placeholder {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background-color: #f8f9fc;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}
.profile-details {
  margin-top: 1.5rem;
}
.detail-item {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}
.documents-list {
  margin-top: 1rem;
}
.document-placeholder {
  padding: 2rem;
  background-color: #f8f9fc;
  border-radius: 0.25rem;
  color: #858796;
}
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1050;
}
.modal-container {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1060;
  width: 80%;
  max-width: 700px;
}
.modal-content {
  background: white;
  border-radius: 0.3rem;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #dee2e6;
}
.modal-body {
  padding: 1rem;
}
</style> 