from flask import Blueprint, jsonify
from flask_restful import Api
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.resources import (
    UserRegistration, UserLogin, TokenRefresh,
    ServiceListResource, ServiceResource, ServiceRequestListResource, 
    ServiceRequestResource, ReviewListResource, UserListResource, 
    ProfessionalApprovalResource, CustomerBlockResource, ServiceTypeListResource,
    TestResource, NoAuthServiceCreate, NoAuthServiceRequestCreate,
    NoAuthProfessionalCreate, PopularServicesResource, ServiceRequestActionResource,
    ServiceRequestStatsResource, ServiceRequestScheduleResource,
    ProfessionalProfileResource, ProfessionalReviewsResource,
    AdminProfessionalsListResource, AdminCustomersListResource,
    AdminProfessionalBlockResource, AdminCustomerBlockResource
)
from backend.model import User
from backend.cache import get_cache_stats

api_bp = Blueprint('api', __name__)
api = Api(api_bp, prefix='/api')

# Cache status route
@api_bp.route('/cache-stats')
@jwt_required()
def cache_stats():
    # Ensure only admins can access cache stats
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    
    if not user or user.role != 'admin':
        return jsonify({
            'message': 'Admin access required'
        }), 403
    
    stats = get_cache_stats()
    if stats:
        return jsonify({
            'status': 'Redis cache is active',
            'stats': stats
        })
    else:
        return jsonify({
            'status': 'Redis cache is not available',
            'stats': None
        })

@api_bp.route('/cache-stats-public')
def cache_stats_public():
    """Public cache stats without authentication requirement"""
    try:
        stats = get_cache_stats() or {}
        
        # Get values with safer defaults
        redis_info = stats.get('redis', {})
        memory_info = stats.get('memory_cache', {})
        
        return jsonify({
            'status': 'ok',
            'active_cache': stats.get('active_cache', 'memory'),
            'memory_cache_keys': memory_info.get('total_keys', 0),
            'redis_available': (
                'redis' in stats and 
                not redis_info.get('error') and 
                redis_info.get('available', False) is not False
            ),
        })
    except Exception as e:
        # Return a graceful error response instead of 500
        return jsonify({
            'status': 'error',
            'message': f'Error fetching cache stats: {str(e)}',
            'active_cache': 'unknown',
            'redis_available': False
        }), 200  # Return 200 with error info instead of 500

# Auth routes
api.add_resource(UserRegistration, '/auth/register')
api.add_resource(UserLogin, '/auth/login')
api.add_resource(TokenRefresh, '/auth/refresh')

# Service routes
api.add_resource(ServiceListResource, '/services')
api.add_resource(ServiceResource, '/services/<int:service_id>')
api.add_resource(ServiceTypeListResource, '/service-types')
api.add_resource(PopularServicesResource, '/services/popular')

# Service request routes
api.add_resource(ServiceRequestListResource, '/service-requests')
api.add_resource(ServiceRequestResource, '/service-requests/<int:request_id>')
api.add_resource(ServiceRequestActionResource, '/service-requests/<int:request_id>/<status>')
api.add_resource(ServiceRequestStatsResource, '/service-requests/stats')
api.add_resource(ServiceRequestScheduleResource, '/service-requests/schedule')

# Review routes
api.add_resource(ReviewListResource, '/reviews', '/reviews/<int:service_request_id>')

# Professional routes
api.add_resource(ProfessionalProfileResource, '/professional/profile')

# Admin routes
api.add_resource(UserListResource, '/admin/users')
api.add_resource(AdminProfessionalsListResource, '/admin/professionals', '/admin/professionals/<int:professional_id>')
api.add_resource(AdminCustomersListResource, '/admin/customers', '/admin/customers/<int:customer_id>')
api.add_resource(ProfessionalApprovalResource, '/admin/professionals/<int:professional_id>')
api.add_resource(CustomerBlockResource, '/admin/customers/<int:customer_id>')
api.add_resource(AdminProfessionalBlockResource, '/admin/professionals/<int:professional_id>/block', '/admin/professionals/<int:professional_id>/unblock')
api.add_resource(AdminCustomerBlockResource, '/admin/customers/<int:customer_id>/block', '/admin/customers/<int:customer_id>/unblock')

# Test routes
api.add_resource(TestResource, '/test-jwt')
api.add_resource(NoAuthServiceCreate, '/test/create-service')
api.add_resource(NoAuthServiceRequestCreate, '/test/service-requests')
api.add_resource(NoAuthProfessionalCreate, '/test/professionals')
