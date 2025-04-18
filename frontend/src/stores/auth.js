import { reactive } from 'vue';
import AuthService from '@/services/AuthService';

// Create a reactive state
const state = reactive({
  user: AuthService.getCurrentUser(),
  isAuthenticated: !!AuthService.getCurrentUser()
});

// Create a store
export function useAuthStore() {
  // Actions
  function login(user) {
    return AuthService.login(user)
      .then(data => {
        state.user = data;
        state.isAuthenticated = true;
        return data;
      });
  }

  function logout() {
    AuthService.logout();
    state.user = null;
    state.isAuthenticated = false;
  }

  function register(user) {
    return AuthService.register(user);
  }

  function refreshUser() {
    state.user = AuthService.getCurrentUser();
    state.isAuthenticated = !!state.user;
  }

  // Return readonly state and actions
  return {
    // State (readonly)
    get user() { return state.user; },
    get isAuthenticated() { return state.isAuthenticated; },
    
    // Actions
    login,
    logout,
    register,
    refreshUser
  };
} 