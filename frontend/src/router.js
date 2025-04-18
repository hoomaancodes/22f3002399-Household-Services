import Vue from 'vue';
import Router from 'vue-router';
import AuthService from './services/AuthService';

Vue.use(Router);

const router = new Router({
  mode: 'history',
  routes: [
    // Public routes
    {
      path: '/',
      name: 'home',
      component: () => import('./views/Home.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./views/Login.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('./views/Register.vue')
    },
    {
      path: '/register-professional',
      name: 'register-professional',
      component: () => import('./views/RegisterProfessional.vue')
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('./views/Search.vue'),
      meta: { requiresAuth: true }
    },
    
    
    {
      path: '/customer/services',
      name: 'customer-services',
      component: () => import('./views/customer/Services.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/service-requests',
      name: 'customer-service-requests',
      component: () => import('./views/customer/ServiceRequests.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/requests',
      name: 'customer-requests',
      component: () => import('./views/customer/Requests.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/request-service',
      name: 'customer-request-service',
      component: () => import('./views/customer/RequestService.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    {
      path: '/customer/profile',
      name: 'customer-profile',
      component: () => import('./views/customer/Profile.vue'),
      meta: { requiresAuth: true, role: 'customer' }
    },
    
    // Professional routes
    {
      path: '/professional',
      name: 'professional-dashboard',
      component: () => import('./views/professional/Dashboard.vue'),
      meta: { requiresAuth: true, role: 'professional' }
    },
    {
      path: '/professional/service-requests',
      name: 'professional-service-requests',
      component: () => import('./views/professional/ServiceRequests.vue'),
      meta: { requiresAuth: true, role: 'professional' }
    },
    {
      path: '/professional/profile',
      name: 'professional-profile',
      component: () => import('./views/professional/Profile.vue'),
      meta: { requiresAuth: true, role: 'professional' }
    },
    
    // Admin routes
    {
      path: '/admin',
      name: 'admin-dashboard',
      component: () => import('./views/admin/Dashboard.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/services',
      name: 'admin-services',
      component: () => import('./views/admin/Services.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/service-requests',
      name: 'admin-service-requests',
      component: () => import('./views/admin/ServiceRequests.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/professionals',
      name: 'admin-professionals',
      component: () => import('./views/admin/Professionals.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/customers',
      name: 'admin-customers',
      component: () => import('./views/admin/Customers.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    {
      path: '/admin/reports',
      name: 'admin-reports',
      component: () => import('./views/admin/Reports.vue'),
      meta: { requiresAuth: true, role: 'admin' }
    },
    
    // Catch-all route for 404
    {
      path: '*',
      redirect: '/'
    }
  ]
});

// Navigation guard
router.beforeEach((to, from, next) => {
  const currentUser = AuthService.getCurrentUser();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  
  // If route requires auth and user isn't logged in, redirect to login
  if (requiresAuth && !currentUser) {
    next('/login');
  } 
  // If route requires specific role
  else if (requiresAuth && to.meta.role && currentUser.role !== to.meta.role) {
    // Redirect to appropriate home page based on role
    switch(currentUser.role) {
      case 'admin':
        next('/admin');
        break;
      case 'professional':
        next('/professional');
        break;
      case 'customer':
        next('/customer');
        break;
      default:
        next('/login');
    }
  } 
  // If already logged in and trying to access login/register
  else if (currentUser && (to.path === '/login' || to.path === '/register' || to.path === '/register-professional')) {
    // Redirect to appropriate home page based on role
    switch(currentUser.role) {
      case 'admin':
        next('/admin');
        break;
      case 'professional':
        next('/professional');
        break;
      case 'customer':
        next('/customer');
        break;
      default:
        next('/');
    }
  } 
  else {
    next();
  }
});

export default router; 