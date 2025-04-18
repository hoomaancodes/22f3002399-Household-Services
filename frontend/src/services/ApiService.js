import axios from 'axios';
import AuthService from './AuthService';

const API_URL = 'http://localhost:5000/api/';

// Create an axios instance with a base URL
const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a request interceptor to include the auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = AuthService.getToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add a response interceptor to handle token refresh
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      // In a real application, you would implement token refresh here
      // For now, we'll just logout the user
      AuthService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default {
  // Services
  getServices() {
    return apiClient.get('services');
  },
  
  getService(id) {
    return apiClient.get(`services/${id}`);
  },

  createService(service) {
    return apiClient.post('services', service);
  },

  updateService(id, service) {
    return apiClient.put(`services/${id}`, service);
  },

  deleteService(id) {
    return apiClient.delete(`services/${id}`);
  },
  
  getServiceTypes() {
    return apiClient.get('service-types');
  },
  
  getPopularServices() {
    return apiClient.get('services/popular');
  },
  
  // Service Requests
  getServiceRequests(params) {
    return apiClient.get('service-requests', { params });
  },
  
  getServiceRequest(id) {
    return apiClient.get(`service-requests/${id}`);
  },
  
  createServiceRequest(serviceRequest) {
    return apiClient.post('service-requests', serviceRequest);
  },
  
  updateServiceRequest(id, data) {
    return apiClient.put(`service-requests/${id}`, data);
  },

  deleteServiceRequest(id) {
    return apiClient.delete(`service-requests/${id}`);
  },

  // Service Request Actions
  acceptServiceRequest(id) {
    return apiClient.post(`service-requests/${id}/${'accepted'}`);
  },

  rejectServiceRequest(id) {
    return apiClient.post(`service-requests/${id}/${'rejected'}`);
  },

  completeServiceRequest(id) {
    return apiClient.post(`service-requests/${id}/${'completed'}`);
  },
  
  
  // Reviews
  getReviews(serviceRequestId) {
    if (serviceRequestId) {
      return apiClient.get(`reviews/${serviceRequestId}`);
    }
    return apiClient.get('reviews');
  },

  createReview(review) {
    return apiClient.post('reviews', review);
  },
  
  rateServiceRequest(id, rating, review) {
    return apiClient.post(`service-requests/${id}/rate`, { rating, review });
  },

  // Users (Admin)
  getUsers() {
    return apiClient.get('admin/users');
  },

  // Professional Management (Admin)
  updateProfessionalStatus(id, data) {
    return apiClient.put(`admin/professionals/${id}`, data);
  },

  // Customer Management (Admin)
  updateCustomerStatus(id, data) {
    return apiClient.put(`admin/customers/${id}`, data);
  },
  
  // Admin Dashboard
  getDashboardStats() {
    return apiClient.get('admin/dashboard/stats');
  },
  
  getRecentServiceRequests() {
    return apiClient.get('admin/service-requests/recent');
  },
  
  getPendingProfessionals() {
    return apiClient.get('admin/professionals/pending');
  },
  
  approveProfessional(id) {
    return apiClient.post(`admin/professionals/${id}/approve`);
  },
  
  blockUser(id, reason) {
    return apiClient.post(`admin/users/${id}/block`, { reason });
  },
  
  unblockUser(id) {
    return apiClient.post(`admin/users/${id}/unblock`);
  },
  
  getAllProfessionals(params) {
    return apiClient.get('admin/professionals', { params });
  },
  
  getAllCustomers(params) {
    return apiClient.get('admin/customers', { params });
  },
  
  getAllServiceRequests(params) {
    return apiClient.get('admin/service-requests', { params });
  },

  // Professional Dashboard
  getProfessionalStats() {
    return apiClient.get('service-requests/stats');
  },

  getProfessionalRequests(params) {
    return apiClient.get('service-requests', { 
      params: { 
        role: 'professional',
        ...params
      } 
    });
  },
  
  getProfessionalServiceRequests(params) {
    return apiClient.get('professional/service-requests', { params });
  },
  
  getProfessionalDashboardStats() {
    return apiClient.get('professional/dashboard/stats');
  },
  
  getProfessionalServices() {
    return apiClient.get('professional/services');
  },
  
  updateProfessionalServices(services) {
    return apiClient.put('professional/services', { services });
  },

  getProfessionalSchedule(params) {
    return apiClient.get('service-requests/schedule', { params });
  },

  // Search
  searchServices(query, searchBy = '') {
    return apiClient.get('services', { 
      params: { 
        q: query,
        by: searchBy
      } 
    });
  },

  // Professional Profile
  getProfessionalProfile() {
    return apiClient.get('professional/profile');
  },

  updateProfessionalProfile(profileData) {
    return apiClient.put('professional/profile', profileData);
  },

  getProfessionalReviews(params) {
    return apiClient.get('professional/reviews', { params });
  },

  changePassword(passwordData) {
    return apiClient.put('auth/password', passwordData);
  },

  // Customer Profile
  getCustomerProfile() {
    return apiClient.get('customer/profile');
  },

  updateCustomerProfile(profileData) {
    return apiClient.put('customer/profile', profileData);
  },
  
  getCustomerDashboardStats() {
    return apiClient.get('customer/dashboard/stats');
  },
  
  getCustomerServiceRequests(params) {
    return apiClient.get('service-requests', { 
      params: { 
        role: 'customer',
        ...params
      } 
    });
  },

  getSavedAddresses() {
    return apiClient.get('customer/addresses');
  },

  addSavedAddress(addressData) {
    return apiClient.post('customer/addresses', addressData);
  },

  deleteSavedAddress(addressId) {
    return apiClient.delete(`customer/addresses/${addressId}`);
  },

  setDefaultAddress(addressId) {
    return apiClient.put(`customer/addresses/${addressId}/default`);
  },

  getCustomerActivity() {
    return apiClient.get('customer/activity');
  },

  getCustomerById(id) {
    return apiClient.get(`admin/customers/${id}`);
  },
  
  getCustomers() {
    return apiClient.get('admin/customers');
  },
  
  getProfessionals() {
    return apiClient.get('admin/professionals');
  },
  
  getProfessionalById(id) {
    return apiClient.get(`admin/professionals/${id}`);
  },
  
  blockCustomer(id) {
    return apiClient.post(`admin/customers/${id}/block`);
  },
  
  unblockCustomer(id) {
    return apiClient.post(`admin/customers/${id}/unblock`);
  },
  
  blockProfessional(id) {
    return apiClient.post(`admin/professionals/${id}/block`);
  },
  
  unblockProfessional(id) {
    return apiClient.post(`admin/professionals/${id}/unblock`);
  }
}; 