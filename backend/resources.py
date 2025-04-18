from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import (
    jwt_required, create_access_token, 
    create_refresh_token, get_jwt_identity,
    get_jwt
)
from werkzeug.security import generate_password_hash, check_password_hash
from backend.model import db, User, Professional, Customer, Service, ServiceRequest, Review
from backend.cache import cache_response, invalidate_cache_prefix
from datetime import datetime, timedelta

# Authentication Resources
class UserRegistration(Resource):
    def post(self):
        data = request.get_json()
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'User already exists'}, 400
            
        # Create new user based on role
        hashed_password = generate_password_hash(data['password'])
        new_user = User(
            email=data['email'],
            password=hashed_password,
            role=data['role']
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Create associated profile
            if data['role'] == 'professional':
                professional = Professional(
                    user_id=new_user.id,
                    name=data['name'],
                    service_type=data['service_type'],
                    exp=data.get('experience', ''),
                    pin=data.get('pin', 0),
                    description=data.get('description', '')
                )
                db.session.add(professional)
            
            elif data['role'] == 'customer':
                customer = Customer(
                    user_id=new_user.id,
                    name=data['name'],
                    address=data['address'],
                    pin=data['pin']
                )
                db.session.add(customer)
                
            db.session.commit()
            
            access_token = create_access_token(identity=str(new_user.id))
            refresh_token = create_refresh_token(identity=str(new_user.id))
            
            return {
                'message': 'User created successfully',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_id': new_user.id,
                'role': new_user.role
            }, 201
        
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500

class UserLogin(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not check_password_hash(user.password, data['password']):
            return {'message': 'Invalid credentials'}, 401
        
        if not user.active:
            return {'message': 'User is deactivated'}, 401
            
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.id,
            'role': user.role
        }, 200

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            current_user = get_jwt_identity()
            
            # Verify the user still exists and is active
            user = User.query.get(int(current_user))
            if not user or not user.active:
                return {'message': 'User is inactive or not found'}, 401
                
            # Create a fresh access token
            expires = timedelta(hours=1)
            new_access_token = create_access_token(
                identity=current_user,
                expires_delta=expires
            )
            
            return {
                'access_token': new_access_token,
                'message': 'Token refreshed successfully'
            }, 200
            
        except Exception as e:
            return {
                'message': f'Token refresh failed: {str(e)}',
                'error': 'invalid_token'
            }, 401

# Service Resources
class ServiceListResource(Resource):
    @cache_response(prefix="services:list", expire=600)  # Cache for 10 minutes
    def get(self):
        # Check if there are search parameters
        search_name = request.args.get('name')
        search_type = request.args.get('type')
        search_pin = request.args.get('pin')
        
        # Base query
        query = Service.query
        
        # Apply filters if provided
        if search_name:
            query = query.filter(Service.name.ilike(f'%{search_name}%'))
        if search_type:
            query = query.filter(Service.service_type.ilike(f'%{search_type}%'))
        if search_pin:
            # For pin search, find professionals in that area and their service types
            professionals = Professional.query.filter_by(pin=search_pin).all()
            if professionals:
                service_types = [p.service_type for p in professionals]
                query = query.filter(Service.service_type.in_(service_types))
        
        services = query.all()
        result = []
        for service in services:
            result.append({
                'id': service.id,
                'name': service.name,
                'price': service.price,
                'time_req': service.time_req,
                'description': service.description,
                'service_type': service.service_type,
                # Add availability info based on professional count
                'has_professionals': Professional.query.filter_by(
                    service_type=service.service_type, 
                    approved=True
                ).count() > 0
            })
        return result, 200
    
    @jwt_required()
    def post(self):
        # Check if user is admin
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        data = request.get_json()
        
        new_service = Service(
            name=data['name'],
            price=data['price'],
            time_req=data['time_req'],
            description=data.get('description', ''),
            service_type=data['service_type']
        )
        
        try:
            db.session.add(new_service)
            db.session.commit()
            # Invalidate service cache after adding a new service
            invalidate_cache_prefix("services:")
            return {
                'message': 'Service created successfully',
                'id': new_service.id
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500

class ServiceResource(Resource):
    @cache_response(prefix="services:detail", expire=600)  # Cache for 10 minutes
    def get(self, service_id):
        service = Service.query.get(service_id)
        if not service:
            return {'message': 'Service not found'}, 404
            
        return {
            'id': service.id,
            'name': service.name,
            'price': service.price,
            'time_req': service.time_req,
            'description': service.description,
            'service_type': service.service_type
        }, 200
    
    @jwt_required()
    def put(self, service_id):
        # Check if user is admin
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        service = Service.query.get(service_id)
        if not service:
            return {'message': 'Service not found'}, 404
            
        data = request.get_json()
        
        service.name = data.get('name', service.name)
        service.price = data.get('price', service.price)
        service.time_req = data.get('time_req', service.time_req)
        service.description = data.get('description', service.description)
        service.service_type = data.get('service_type', service.service_type)
        
        try:
            db.session.commit()
            # Invalidate specific service cache and service list cache
            invalidate_cache_prefix(f"services:detail:{service_id}")
            invalidate_cache_prefix("services:list")
            return {'message': 'Service updated successfully'}, 200
        except:
            db.session.rollback()
            return {'message': 'Something went wrong'}, 500
    
    @jwt_required()
    def delete(self, service_id):
        # Check if user is admin
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        service = Service.query.get(service_id)
        if not service:
            return {'message': 'Service not found'}, 404
            
        try:
            db.session.delete(service)
            db.session.commit()
            # Invalidate service caches
            invalidate_cache_prefix(f"services:detail:{service_id}")
            invalidate_cache_prefix("services:list")
            return {'message': 'Service deleted'}, 200
        except:
            db.session.rollback()
            return {'message': 'Something went wrong'}, 500

# Service Request Resources
class ServiceRequestListResource(Resource):
    @jwt_required()
    @cache_response(prefix="service_requests", expire=300)  # Cache for 5 minutes
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {'message': 'User not found'}, 404
            
        # Get filter parameters
        status_filter = request.args.get('status')
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        search_term = request.args.get('search')
        limit = request.args.get('limit', type=int)
        role_param = request.args.get('role')  # Role parameter
        
        # Convert date strings to datetime objects if provided
        from_date = None
        to_date = None
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                return {'message': 'Invalid from date format. Use YYYY-MM-DD'}, 400
                
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d')
                # Set to end of day
                to_date = to_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return {'message': 'Invalid to date format. Use YYYY-MM-DD'}, 400
                
        # Base query with filter by status if provided
        base_query = ServiceRequest.query
        
        if status_filter:
            base_query = base_query.filter_by(status=status_filter)
            
        # Apply date filters
        if from_date:
            base_query = base_query.filter(ServiceRequest.req_date >= from_date)
        if to_date:
            base_query = base_query.filter(ServiceRequest.req_date <= to_date)
        
        # Determine effective role - use the role parameter if valid, otherwise use the user's role
        effective_role = user.role
        if role_param in ['admin', 'professional', 'customer']:
            # If a role parameter is specified, ensure user is authorized
            if role_param != user.role and user.role != 'admin':
                return {'message': 'Unauthorized role access'}, 403
            effective_role = role_param
        
        # Apply role-specific filters
        if effective_role == 'admin':
            # Admin can see all service requests
            service_requests = base_query.all()
        elif effective_role == 'professional':
            # Professional can see requests assigned to them and open requests
            if user.role == 'professional':
                professional = Professional.query.filter_by(user_id=user.id).first()
                if not professional:
                    return {'message': 'Professional profile not found'}, 404
                    
                # If professional is approved, they can see requested services
                if professional.approved:
                    service_requests = base_query.filter(
                        (ServiceRequest.professional_id == professional.professional_id) | 
                        (ServiceRequest.status == 'requested')
                    ).all()
                else:
                    # If not approved, they can only see their own requests
                    service_requests = base_query.filter_by(
                        professional_id=professional.professional_id
                    ).all()
            else:
                # Admin viewing as professional sees all requests
                service_requests = base_query.all()
                    
        elif effective_role == 'customer':
            # Customer can see their own requests
            if user.role == 'customer':
                customer = Customer.query.filter_by(user_id=user.id).first()
                if not customer:
                    return {'message': 'Customer profile not found'}, 404
                    
                service_requests = base_query.filter_by(customer_id=customer.customer_id).all()
            else:
                # Admin viewing as customer sees all requests
                service_requests = base_query.all()
        else:
            return {'message': 'Invalid role'}, 400
        
        result = []
        for req in service_requests:
            try:
                # Check if service_id is valid before querying
                if req.service_id is None:
                    # Skip service requests with NULL service_id
                    continue
                    
                service = Service.query.get(req.service_id)
                
                # Skip if service doesn't exist
                if not service:
                    continue
                    
                customer = None
                if req.customer_id:
                    customer = Customer.query.get(req.customer_id)
                
                # Skip if doesn't match search term
                if search_term:
                    service_name = service.name.lower() if service else ""
                    customer_name = customer.name.lower() if customer else ""
                    remarks_text = req.remarks.lower() if req.remarks else ""
                    
                    if (search_term.lower() not in service_name and 
                        search_term.lower() not in customer_name and
                        search_term.lower() not in remarks_text):
                        continue
                
                req_data = {
                    'id': req.id,
                    'service_id': req.service_id,
                    'service_name': service.name if service else None,
                    'service_type': service.service_type if service else None,
                    'customer_id': req.customer_id,
                    'price': service.price if service else None,
                    'customer_name': customer.name if customer else None,
                    'customer_address': customer.address if customer else None,
                    'customer_pin': customer.pin if customer else None,
                    'req_date': req.req_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'status': req.status,
                    'duration': service.time_req if service else None,
                    'remarks': req.remarks
                }
                
                if req.professional_id:
                    professional = Professional.query.get(req.professional_id)
                    req_data['professional_id'] = req.professional_id
                    req_data['professional_name'] = professional.name if professional else None
                
                if req.comp_date:
                    req_data['comp_date'] = req.comp_date.strftime('%Y-%m-%d %H:%M:%S')
                
                # Check if the request has reviews
                has_review = Review.query.filter_by(service_request_id=req.id).first() is not None
                req_data['has_review'] = has_review
                
                result.append(req_data)
            except Exception as e:
                # Skip problematic requests instead of failing the entire request
                print(f"Error processing request {req.id}: {str(e)}")
                continue
        
        # For professionals, prioritize requested (available) services first in the result
        if effective_role == 'professional':
            result.sort(key=lambda x: 0 if x['status'] == 'requested' else 1)
            
        # Apply limit if provided
        if limit and isinstance(limit, int) and limit > 0:
            result = result[:limit]
            
        return {
            'count': len(result),
            'requests': result
        }, 200
    
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'customer':
            return {'message': 'Customer access required'}, 403
            
        customer = Customer.query.filter_by(user_id=user.id).first()
        if not customer:
            return {'message': 'Customer profile not found'}, 404
            
        data = request.get_json()
        
        new_request = ServiceRequest(
            service_id=data['service_id'],
            customer_id=customer.customer_id,
            status='requested',
            remarks=data.get('remarks', '')
        )
        
        try:
            db.session.add(new_request)
            db.session.commit()
            # Invalidate service request cache
            invalidate_cache_prefix("service_requests")
            return {
                'message': 'Service request created successfully',
                'id': new_request.id
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500

class ServiceRequestResource(Resource):
    @jwt_required()
    @cache_response(prefix="service_request:detail", expire=300)  # Cache for 5 minutes
    def get(self, request_id):
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'message': 'Service request not found'}, 404
            
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {'message': 'User not found'}, 401
            
        # Authorization check
        if user.role == 'admin':
            # Admin can view any request
            pass
        elif user.role == 'customer':
            customer = Customer.query.filter_by(user_id=user.id).first()
            if not customer:
                return {'message': 'Customer profile not found'}, 404
                
            if service_request.customer_id != customer.customer_id:
                return {'message': 'Unauthorized access'}, 403
        elif user.role == 'professional':
            professional = Professional.query.filter_by(user_id=user.id).first()
            if not professional:
                return {'message': 'Professional profile not found'}, 404
                
            # Professionals can see either:
            # 1. Requests assigned to them
            # 2. Requests with 'requested' status that are available for pickup
            if service_request.professional_id != professional.professional_id and service_request.status != 'requested':
                return {'message': 'Unauthorized access'}, 403
        else:
            return {'message': 'Invalid user role'}, 403
        
        service = Service.query.get(service_request.service_id)
        customer = Customer.query.get(service_request.customer_id)
        
        result = {
            'id': service_request.id,
            'service_id': service_request.service_id,
            'service_name': service.name if service else None,
            'service_type':service.service_type,
            'duration':service.time_req,
            'price':service.price,
            'customer_id': service_request.customer_id,
            'customer_name': customer.name if customer else None,
            'address':customer.address,
            'req_date': service_request.req_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': service_request.status,
            'remarks': service_request.remarks
        }
        
        if service_request.professional_id:
            professional = Professional.query.get(service_request.professional_id)
            result['professional_id'] = service_request.professional_id
            result['professional_name'] = professional.name if professional else None
        
        if service_request.comp_date:
            result['comp_date'] = service_request.comp_date.strftime('%Y-%m-%d %H:%M:%S')
            
        return result, 200
    
    @jwt_required()
    def put(self, request_id):
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'message': 'Service request not found'}, 404
            
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {'message': 'User not found'}, 401
        
        data = request.get_json()
        
        # Different update permissions based on role
        if user.role == 'admin':
            # Admin can update any field
            for key, value in data.items():
                if hasattr(service_request, key) and key not in ['id', 'service_id', 'customer_id']:
                    setattr(service_request, key, value)
                    
        elif user.role == 'professional':
            professional = Professional.query.filter_by(user_id=user.id).first()
            if not professional:
                return {'message': 'Professional profile not found'}, 404
                
            if service_request.professional_id != professional.professional_id and service_request.status != 'requested':
                return {'message': 'Unauthorized access'}, 403
                
            # Professional can accept/reject a request or update remarks if assigned
            if data.get('action') == 'accept' and service_request.status == 'requested':
                service_request.professional_id = professional.professional_id
                service_request.status = 'assigned'
                
            elif data.get('action') == 'complete' and service_request.status == 'assigned' and service_request.professional_id == professional.professional_id:
                # Professionals can mark a request as ready for customer to close
                service_request.status = 'ready_to_close'
                service_request.remarks = data.get('remarks', service_request.remarks)
                
            elif service_request.professional_id == professional.professional_id:
                # Can only update remarks if assigned to this professional
                if 'remarks' in data:
                    service_request.remarks = data['remarks']
                    
        elif user.role == 'customer':
            customer = Customer.query.filter_by(user_id=user.id).first()
            if not customer:
                return {'message': 'Customer profile not found'}, 404
                
            if service_request.customer_id != customer.customer_id:
                return {'message': 'Unauthorized access'}, 403
                
            # Customer can update service request details
            if service_request.status == 'requested':
                # Can update remarks and scheduled date if still in requested state
                if 'remarks' in data:
                    service_request.remarks = data['remarks']
                
                if 'scheduled_date' in data:
                    try:
                        scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d %H:%M:%S')
                        service_request.req_date = scheduled_date
                    except ValueError:
                        return {'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}, 400
            
            # Customer can close the request or update remarks
            if (data.get('action') == 'close' or data.get('status') == 'closed') and (service_request.status == 'assigned' or service_request.status == 'ready_to_close'):
                service_request.status = 'closed'
                service_request.comp_date = datetime.now()
                
            if 'remarks' in data:
                service_request.remarks = data['remarks']
                
        try:
            db.session.commit()
            # Invalidate service request caches
            invalidate_cache_prefix(f"service_request:detail:{request_id}")
            invalidate_cache_prefix("service_requests")
            
            # Return updated service request details
            return {
                'message': 'Service request updated successfully',
                'id': service_request.id,
                'status': service_request.status,
                'remarks': service_request.remarks,
                'req_date': service_request.req_date.strftime('%Y-%m-%d %H:%M:%S'),
                'comp_date': service_request.comp_date.strftime('%Y-%m-%d %H:%M:%S') if service_request.comp_date else None
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500
    
    @jwt_required()
    def delete(self, request_id):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if user.role not in ['admin', 'customer']:
            return {'message': 'Unauthorized access'}, 403
            
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'message': 'Service request not found'}, 404
            
        if user.role == 'customer':
            customer = Customer.query.filter_by(user_id=user.id).first()
            if service_request.customer_id != customer.customer_id:
                return {'message': 'Unauthorized access'}, 403
                
            # Customers can only delete requests in 'requested' status
            if service_request.status != 'requested':
                return {'message': 'Cannot delete assigned or closed requests'}, 400
        
        try:
            db.session.delete(service_request)
            db.session.commit()
            # Invalidate service request caches
            invalidate_cache_prefix(f"service_request:detail:{request_id}")
            invalidate_cache_prefix("service_requests")
            return {'message': 'Service request deleted'}, 200
        except:
            db.session.rollback()
            return {'message': 'Something went wrong'}, 500

# Review Resources
class ReviewListResource(Resource):
    @cache_response(prefix="reviews", expire=600)  # Cache for 10 minutes
    def get(self, service_request_id=None):
        if service_request_id:
            reviews = Review.query.filter_by(service_request_id=service_request_id).all()
        else:
            reviews = Review.query.all()
            
        result = []
        for review in reviews:
            customer = Customer.query.get(review.customer_id)
            result.append({
                'id': review.id,
                'service_request_id': review.service_request_id,
                'customer_id': review.customer_id,
                'customer_name': customer.name if customer else None,
                'rating': review.rating,
                'comment': review.comment,
                'date_created': review.date_created.strftime('%Y-%m-%d %H:%M:%S')
            })
            
        return result, 200
    
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'customer':
            return {'message': 'Customer access required'}, 403
            
        customer = Customer.query.filter_by(user_id=user.id).first()
        if not customer:
            return {'message': 'Customer profile not found'}, 404
            
        data = request.get_json()
        
        # Check if service request exists and is closed
        service_request = ServiceRequest.query.get(data['service_request_id'])
        if not service_request:
            return {'message': 'Service request not found'}, 404
            
        if service_request.customer_id != customer.customer_id:
            return {'message': 'Unauthorized access'}, 403
            
        if service_request.status != 'closed':
            return {'message': 'Can only review closed service requests'}, 400
            
        # Check if already reviewed
        existing_review = Review.query.filter_by(
            service_request_id=data['service_request_id'],
            customer_id=customer.customer_id
        ).first()
        
        if existing_review:
            return {'message': 'Service request already reviewed'}, 400
            
        new_review = Review(
            service_request_id=data['service_request_id'],
            customer_id=customer.customer_id,
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        
        try:
            db.session.add(new_review)
            db.session.commit()
            # Invalidate review caches
            invalidate_cache_prefix("reviews")
            return {
                'message': 'Review submitted successfully',
                'id': new_review.id
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500

# User Management Resources (Admin)
class UserListResource(Resource):
    @jwt_required()
    @cache_response(prefix="admin:users", expire=300)  # Cache for 5 minutes
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        # Get search parameters
        search_role = request.args.get('role')
        search_name = request.args.get('name')
        search_email = request.args.get('email')
        search_service_type = request.args.get('service_type')
        search_status = request.args.get('status')  # active, blocked, pending
        
        # Base query
        users_query = User.query
        
        # Apply filters
        if search_role:
            users_query = users_query.filter_by(role=search_role)
            
        if search_email:
            users_query = users_query.filter(User.email.ilike(f'%{search_email}%'))
            
        # Get all users first before additional filtering
        users = users_query.all()
        result = []
        
        for user in users:
            # Skip if doesn't match status filter
            if search_status:
                if search_status == 'active' and not user.active:
                    continue
                if search_status == 'blocked' and user.active:
                    continue
                    
            user_data = {
                'id': user.id,
                'email': user.email,
                'role': user.role,
                'active': user.active
            }
            
            include_user = True
            
            if user.role == 'professional':
                professional = Professional.query.filter_by(user_id=user.id).first()
                if professional:
                    user_data['professional'] = {
                        'id': professional.professional_id,
                        'name': professional.name,
                        'service_type': professional.service_type,
                        'experience': professional.exp,
                        'approved': professional.approved,
                        'blocked': professional.blocked
                    }
                    
                    # Apply professional specific filters
                    if search_name and search_name.lower() not in professional.name.lower():
                        include_user = False
                    if search_service_type and search_service_type != professional.service_type:
                        include_user = False
                    if search_status == 'pending' and professional.approved:
                        include_user = False
                    
            elif user.role == 'customer':
                customer = Customer.query.filter_by(user_id=user.id).first()
                if customer:
                    user_data['customer'] = {
                        'id': customer.customer_id,
                        'name': customer.name,
                        'address': customer.address,
                        'pin': customer.pin,
                        'blocked': customer.blocked
                    }
                    
                    # Apply customer specific filters
                    if search_name and search_name.lower() not in customer.name.lower():
                        include_user = False
            
            if include_user:
                result.append(user_data)
            
        return result, 200

class ProfessionalApprovalResource(Resource):
    @jwt_required()
    def get(self, professional_id):
        """Get detailed professional profile for admin review"""
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        professional = Professional.query.get(professional_id)
        if not professional:
            return {'message': 'Professional not found'}, 404
            
        # Get user details
        user_details = User.query.get(professional.user_id)
        
        # Get service requests data
        service_requests = ServiceRequest.query.filter_by(professional_id=professional_id).all()
        requests_data = []
        
        for req in service_requests:
            service = Service.query.get(req.service_id)
            customer = Customer.query.get(req.customer_id)
            
            req_data = {
                'id': req.id,
                'service_name': service.name if service else None,
                'customer_name': customer.name if customer else None,
                'status': req.status,
                'date': req.req_date.strftime('%Y-%m-%d %H:%M:%S'),
                'completed': req.comp_date.strftime('%Y-%m-%d %H:%M:%S') if req.comp_date else None
            }
            requests_data.append(req_data)
            
        # Get reviews data
        reviews = []
        for req in service_requests:
            req_reviews = Review.query.filter_by(service_request_id=req.id).all()
            for review in req_reviews:
                customer = Customer.query.get(review.customer_id)
                reviews.append({
                    'id': review.id,
                    'rating': review.rating,
                    'comment': review.comment,
                    'date': review.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                    'customer_name': customer.name if customer else None
                })
                
        # Calculate average rating
        avg_rating = 0
        if reviews:
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
        
        result = {
            'id': professional.professional_id,
            'user_id': professional.user_id,
            'email': user_details.email if user_details else None,
            'name': professional.name,
            'service_type': professional.service_type,
            'experience': professional.exp,
            'description': professional.description,
            'pin': professional.pin,
            'approved': professional.approved,
            'blocked': professional.blocked,
            'created_date': professional.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'service_requests': {
                'total': len(service_requests),
                'completed': len([r for r in service_requests if r.status == 'closed']),
                'recent': requests_data[:5]  # Show only 5 most recent requests
            },
            'reviews': {
                'total': len(reviews),
                'average_rating': round(avg_rating, 1),
                'recent': reviews[:5]  # Show only 5 most recent reviews
            }
        }
        
        return result, 200
            
    @jwt_required()
    def put(self, professional_id):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        professional = Professional.query.get(professional_id)
        if not professional:
            return {'message': 'Professional not found'}, 404
            
        data = request.get_json()
        
        # Track what changes were made
        changes = []
        
        if 'approved' in data:
            previous = professional.approved
            professional.approved = data['approved']
            changes.append(f"Approval status changed from {previous} to {data['approved']}")
            
        if 'blocked' in data:
            previous = professional.blocked
            professional.blocked = data['blocked']
            # Also update the user's active status
            professional.user.active = not data['blocked']
            changes.append(f"Block status changed from {previous} to {data['blocked']}")
            
        if 'notes' in data:
            # Optional admin notes about approval/rejection
            professional.description = f"{professional.description}\n\nAdmin Note: {data['notes']}"
            changes.append("Added admin notes")
            
        try:
            db.session.commit()
            # Invalidate relevant caches
            invalidate_cache_prefix("admin:users")
            return {
                'message': 'Professional status updated successfully',
                'changes': changes,
                'id': professional.professional_id,
                'approved': professional.approved,
                'blocked': professional.blocked,
                'user_status': 'active' if professional.user.active else 'inactive'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500

class CustomerBlockResource(Resource):
    @jwt_required()
    def get(self, customer_id):
        """Get detailed customer profile for admin review"""
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'message': 'Customer not found'}, 404
            
        # Get user details
        user_details = User.query.get(customer.user_id)
        
        # Get service requests data
        service_requests = ServiceRequest.query.filter_by(customer_id=customer_id).all()
        requests_data = []
        
        for req in service_requests:
            service = Service.query.get(req.service_id)
            professional = Professional.query.get(req.professional_id) if req.professional_id else None
            
            req_data = {
                'id': req.id,
                'service_name': service.name if service else None,
                'professional_name': professional.name if professional else None,
                'status': req.status,
                'date': req.req_date.strftime('%Y-%m-%d %H:%M:%S'),
                'completed': req.comp_date.strftime('%Y-%m-%d %H:%M:%S') if req.comp_date else None
            }
            requests_data.append(req_data)
            
        # Get reviews written by customer
        reviews = Review.query.filter_by(customer_id=customer_id).all()
        reviews_data = []
        
        for review in reviews:
            req = ServiceRequest.query.get(review.service_request_id)
            service_name = 'Unknown Service'
            if req:
                service = Service.query.get(req.service_id) if req else None
                if service:
                    service_name = service.name
                
            reviews_data.append({
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'date': review.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                'service': service_name
            })
            
        result = {
            'id': customer.customer_id,
            'user_id': customer.user_id,
            'email': user_details.email if user_details else None,
            'name': customer.name,
            'address': customer.address,
            'pin': customer.pin,
            'blocked': customer.blocked,
            'created_date': customer.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'service_requests': {
                'total': len(service_requests),
                'completed': len([r for r in service_requests if r.status == 'closed']),
                'recent': requests_data[:5]  # Show only 5 most recent requests
            },
            'reviews': {
                'total': len(reviews_data),
                'average_given': round(sum(r['rating'] for r in reviews_data) / len(reviews_data), 1) if reviews_data else 0,
                'recent': reviews_data[:5]  # Show only 5 most recent reviews
            }
        }
        
        return result, 200
        
    @jwt_required()
    def put(self, customer_id):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'message': 'Customer not found'}, 404
            
        data = request.get_json()
        
        # Track what changes were made
        changes = []
        
        if 'blocked' in data:
            previous = customer.blocked
            customer.blocked = data['blocked']
            # Also update the user's active status
            customer.user.active = not data['blocked']
            changes.append(f"Block status changed from {previous} to {data['blocked']}")
            
        if 'reason' in data:
            # Optional admin notes about block reason
            # Create a note in the database or log it
            changes.append(f"Block reason: {data['reason']}")
            
        try:
            db.session.commit()
            # Invalidate relevant caches
            invalidate_cache_prefix("admin:users")
            return {
                'message': 'Customer status updated successfully',
                'changes': changes,
                'id': customer.customer_id,
                'blocked': customer.blocked,
                'user_status': 'active' if customer.user.active else 'inactive'
            }, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500

# Service Type Resource
class ServiceTypeListResource(Resource):
    @cache_response(prefix="service_types", expire=1800)  # Cache for 30 minutes
    def get(self):
        service_types = db.session.query(Service.service_type).distinct().all()
        return [type[0] for type in service_types], 200

class PopularServicesResource(Resource):
    @cache_response(prefix="services:popular", expire=600)  # Cache for 10 minutes
    def get(self):
        """
        Get popular services based on the number of service requests and ratings
        """
        try:
            # Get all services
            all_services = Service.query.all()
            
            # Calculate popularity based on request counts and review ratings
            popular_services = []
            
            for service in all_services:
                # Count service requests for this service
                request_count = ServiceRequest.query.filter_by(service_id=service.id).count()
                
                # Calculate average rating from reviews for this service's requests
                service_requests = ServiceRequest.query.filter_by(service_id=service.id).all()
                
                total_rating = 0
                rating_count = 0
                
                for sr in service_requests:
                    reviews = Review.query.filter_by(service_request_id=sr.id).all()
                    for review in reviews:
                        total_rating += review.rating
                        rating_count += 1
                
                avg_rating = total_rating / rating_count if rating_count > 0 else 0
                
                # Calculate popularity score (simple formula combining requests and ratings)
                popularity_score = (request_count * 0.7) + (avg_rating * 0.3 * 10)  # Scale rating impact
                
                popular_services.append({
                    'id': service.id,
                    'name': service.name,
                    'price': service.price,
                    'time_req': service.time_req,
                    'description': service.description,
                    'service_type': service.service_type,
                    'request_count': request_count,
                    'avg_rating': round(avg_rating, 1) if rating_count > 0 else None,
                    'popularity_score': round(popularity_score, 2)
                })
            
            # Sort by popularity score in descending order and take top 5
            popular_services.sort(key=lambda x: x['popularity_score'], reverse=True)
            return popular_services[:5], 200
            
        except Exception as e:
            return {
                'message': f'Error fetching popular services: {str(e)}'
            }, 500

class ServiceRequestActionResource(Resource):
    @jwt_required()
    def post(self, request_id,status):
        """
        Endpoint for professionals to accept, reject, or complete service requests
        """
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        # Ensure user is a professional
        if not user or user.role != 'professional':
            return {'message': 'Professional access required'}, 403
            
        # Get the professional profile
        professional = Professional.query.filter_by(user_id=user.id).first()
        if not professional:
            return {'message': 'Professional profile not found'}, 404
            
        # Check if professional is approved
        if not professional.approved:
            return {'message': 'Your profile is pending approval'}, 403
            
        # Get the service request
        service_request = ServiceRequest.query.get(request_id)
        if not service_request:
            return {'message': 'Service request not found'}, 404
            
        
        if status not in ['accepted', 'rejected', 'completed']:
            return {'message': 'Invalid action. Use "accept", "reject", or "complete"'}, 400
        
        try:
            # Action based on current status
            if status == 'accepted':
                # Can only accept requests in 'requested' status
                if service_request.status != 'requested':
                    return {'message': 'This request is no longer available'}, 400
                    
                # Assign the professional to the request
                service_request.professional_id = professional.professional_id
                service_request.status = 'assigned'
                
               
                db.session.commit()
                
                # Get customer and service details for response
                customer = Customer.query.get(service_request.customer_id)
                
                # Add null check for service_id
                service = None
                if service_request.service_id:
                    service = Service.query.get(service_request.service_id)
                
                # Invalidate caches
                invalidate_cache_prefix("service_requests")
                invalidate_cache_prefix(f"service_request:detail:{request_id}")
                
                return {
                    'message': 'Service request accepted successfully',
                    'request_id': request_id,
                    'status': 'assigned',
                    'customer': {
                        'name': customer.name if customer else 'Unknown',
                        'address': customer.address if customer else 'Unknown',
                        'pin': customer.pin if customer else 'Unknown'
                    },
                    'service': {
                        'name': service.name if service else 'Unknown',
                        'time_required': service.time_req if service else 'Unknown'
                    }
                }, 200
                
            elif status == 'rejected':
                # Can only reject requests in 'requested' status
                if service_request.status != 'requested':
                    return {'message': 'This request is no longer available'}, 400
                    
                
                return {
                    'message': 'Service request rejected',
                    'request_id': request_id,
                    'status': service_request.status,
                    'rejection_reason': "NA"
                }, 200
                
            elif status == 'complete':
                # Can only complete requests assigned to this professional
                if service_request.status != 'assigned' or service_request.professional_id != professional.professional_id:
                    return {'message': 'You cannot complete this request'}, 403
                    
                # Mark as ready for customer to close
                service_request.status = 'ready_to_close'
                
                # Add completion notes if provided
                
                db.session.commit()
                
                # Invalidate caches
                invalidate_cache_prefix("service_requests")
                invalidate_cache_prefix(f"service_request:detail:{request_id}")
                
                return {
                    'message': 'Service marked as complete. Waiting for customer confirmation.',
                    'request_id': request_id,
                    'status': 'ready_to_close'
                }, 200
                
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error processing request: {str(e)}'}, 500

class TestResource(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        if user:
            return {'message': 'JWT is working', 'user_id': current_user_id, 'role': user.role}, 200
        return {'message': 'User not found'}, 404

class NoAuthServiceCreate(Resource):
    def post(self):
        data = request.get_json()
        
        new_service = Service(
            name=data['name'],
            price=data['price'],
            time_req=data['time_req'],
            description=data.get('description', ''),
            service_type=data['service_type']
        )
        
        try:
            db.session.add(new_service)
            db.session.commit()
            return {
                'message': 'Service created successfully',
                'id': new_service.id
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500

class NoAuthServiceRequestCreate(Resource):
    def post(self):
        data = request.get_json()
        
        # Get or create the user and customer
        email = data.get('customer_email', 'customer@example.com')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create a new user
            user = User(
                email=email,
                password=generate_password_hash('password123'),
                role='customer',
                active=True
            )
            db.session.add(user)
            db.session.commit()
            
            # Create a new customer
            customer = Customer(
                user_id=user.id,
                name=data.get('customer_name', 'Test Customer'),
                address=data.get('customer_address', '123 Main St'),
                pin=data.get('customer_pin', 400001)
            )
            db.session.add(customer)
            db.session.commit()
        else:
            # Get existing customer
            customer = Customer.query.filter_by(user_id=user.id).first()
            if not customer:
                return {'message': 'Customer profile not found'}, 404
            
        new_request = ServiceRequest(
            service_id=data['service_id'],
            customer_id=customer.customer_id,
            status='requested',
            remarks=data.get('remarks', '')
        )
        
        try:
            db.session.add(new_request)
            db.session.commit()
            return {
                'message': 'Service request created successfully',
                'id': new_request.id
            }, 201
        except Exception as e:
            db.session.rollback()
            return {'message': f'Something went wrong: {str(e)}'}, 500
            
    def get(self):
        # Return all service requests
        service_requests = ServiceRequest.query.all()
        result = []
        for req in service_requests:
            service = Service.query.get(req.service_id)
            customer = Customer.query.get(req.customer_id)
            
            req_data = {
                'id': req.id,
                'service_id': req.service_id,
                'service_name': service.name if service else None,
                'customer_id': req.customer_id,
                'customer_name': customer.name if customer else None,
                'req_date': req.req_date.strftime('%Y-%m-%d %H:%M:%S'),
                'status': req.status,
                'remarks': req.remarks
            }
            
            if req.professional_id:
                professional = Professional.query.get(req.professional_id)
                req_data['professional_id'] = req.professional_id
                req_data['professional_name'] = professional.name if professional else None
            
            if req.comp_date:
                req_data['comp_date'] = req.comp_date.strftime('%Y-%m-%d %H:%M:%S')
                
            result.append(req_data)
            
        return result, 200

class NoAuthProfessionalCreate(Resource):
    def post(self):
        data = request.get_json()
        
        # Get or create the user and professional
        email = data.get('email', 'professional@example.com')
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create a new user
            user = User(
                email=email,
                password=generate_password_hash('password123'),
                role='professional',
                active=True
            )
            db.session.add(user)
            db.session.commit()
            
            # Create a new professional
            professional = Professional(
                user_id=user.id,
                name=data.get('name', 'Test Professional'),
                mobile=data.get('mobile', '9876543210'),
                service_type=data.get('service_type', 'Plumbing'),
                approved=True
            )
            db.session.add(professional)
            db.session.commit()
            
            return {
                'message': 'Professional created successfully',
                'id': professional.professional_id
            }, 201
        else:
            # Get existing professional
            professional = Professional.query.filter_by(user_id=user.id).first()
            if not professional:
                # Create professional profile
                professional = Professional(
                    user_id=user.id,
                    name=data.get('name', 'Test Professional'),
                    mobile=data.get('mobile', '9876543210'),
                    service_type=data.get('service_type', 'Plumbing'),
                    approved=True
                )
                db.session.add(professional)
                db.session.commit()
                
                return {
                    'message': 'Professional profile created successfully',
                    'id': professional.professional_id
                }, 201
            else:
                return {
                    'message': 'Professional already exists',
                    'id': professional.professional_id
                }, 200
                
    def get(self):
        # Return all professionals
        professionals = Professional.query.all()
        result = []
        for prof in professionals:
            user = User.query.get(prof.user_id)
            
            prof_data = {
                'id': prof.professional_id,
                'user_id': prof.user_id,
                'email': user.email if user else None,
                'name': prof.name,
                'mobile': prof.mobile,
                'service_type': prof.service_type,
                'approved': prof.approved
            }
            
            result.append(prof_data)
            
        return result, 200

class ServiceRequestStatsResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {'message': 'User not found'}, 404
            
        if user.role == 'admin':
            # Admin can see all stats
            total_requests = ServiceRequest.query.count()
            pending_requests = ServiceRequest.query.filter_by(status='requested').count()
            assigned_requests = ServiceRequest.query.filter_by(status='assigned').count()
            completed_requests = ServiceRequest.query.filter_by(status='closed').count()
            
            # Get recent activity
            recent_requests = ServiceRequest.query.order_by(ServiceRequest.req_date.desc()).limit(5).all()
            recent_activity = []
            for req in recent_requests:
                # Add null check for service_id
                service_name = 'Unknown Service'
                if req.service_id:
                    service = Service.query.get(req.service_id)
                    if service:
                        service_name = service.name
                
                customer = Customer.query.get(req.customer_id)
                activity = {
                    'id': req.id,
                    'service': service_name,
                    'customer': customer.name if customer else 'Unknown Customer',
                    'status': req.status,
                    'date': req.req_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                recent_activity.append(activity)
            
            return {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'assigned_requests': assigned_requests,
                'completed_requests': completed_requests,
                'recent_activity': recent_activity
            }, 200
            
        elif user.role == 'professional':
            # Professional can see their own stats
            professional = Professional.query.filter_by(user_id=user.id).first()
            if not professional:
                return {'message': 'Professional profile not found'}, 404
                
            total_requests = ServiceRequest.query.filter_by(professional_id=professional.professional_id).count()
            pending_requests = ServiceRequest.query.filter_by(
                professional_id=professional.professional_id,
                status='assigned'
            ).count()
            completed_requests = ServiceRequest.query.filter_by(
                professional_id=professional.professional_id,
                status='closed'
            ).count()
            
            # Get recent activity
            recent_requests = ServiceRequest.query.filter_by(
                professional_id=professional.professional_id
            ).order_by(ServiceRequest.req_date.desc()).limit(5).all()
            
            recent_activity = []
            for req in recent_requests:
                # Add null check for service_id
                service_name = 'Unknown Service'
                if req.service_id:
                    service = Service.query.get(req.service_id)
                    if service:
                        service_name = service.name
                
                customer = Customer.query.get(req.customer_id)
                activity = {
                    'id': req.id,
                    'service': service_name,
                    'customer': customer.name if customer else 'Unknown Customer',
                    'status': req.status,
                    'date': req.req_date.strftime('%Y-%m-%d %H:%M:%S')
                }
                recent_activity.append(activity)
            
            return {
                'total_requests': total_requests,
                'pending_requests': pending_requests,
                'completed_requests': completed_requests,
                'recent_activity': recent_activity
            }, 200
            
        else:
            return {'message': 'Unauthorized access'}, 403

class ServiceRequestScheduleResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return {'message': 'User not found'}, 404
            
        if user.role != 'professional':
            return {'message': 'Professional access required'}, 403
            
        professional = Professional.query.filter_by(user_id=user.id).first()
        if not professional:
            return {'message': 'Professional profile not found'}, 404
            
        # Get date parameter from query string
        date_str = request.args.get('date')
        if not date_str:
            return {'message': 'Date parameter is required'}, 400
            
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return {'message': 'Invalid date format. Use YYYY-MM-DD'}, 400
            
        # Get all service requests for the professional on the specified date
        requests = ServiceRequest.query.filter(
            ServiceRequest.professional_id == professional.professional_id,
            ServiceRequest.status == 'assigned',
            db.func.date(ServiceRequest.req_date) == target_date
        ).all()
        
        schedule = []
        for req in requests:
            service = Service.query.get(req.service_id)
            customer = Customer.query.get(req.customer_id)
            schedule.append({
                'id': req.id,
                'service': service.name if service else 'Unknown Service',
                'customer': customer.name if customer else 'Unknown Customer',
                'time': req.req_date.strftime('%H:%M'),
                'status': req.status,
                'remarks': req.remarks
            })
            
        return {'schedule': schedule}, 200

class ProfessionalProfileResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'professional':
            return {'message': 'Professional access required'}, 403
            
        professional = Professional.query.filter_by(user_id=user.id).first()
        if not professional:
            return {'message': 'Professional profile not found'}, 404
            
        # Get service requests statistics
        total_requests = ServiceRequest.query.filter_by(professional_id=professional.professional_id).count()
        completed_requests = ServiceRequest.query.filter_by(
            professional_id=professional.professional_id,
            status='closed'
        ).count()
        
        # Calculate average rating
        reviews = Review.query.join(ServiceRequest).filter(
            ServiceRequest.professional_id == professional.professional_id
        ).all()
        
        avg_rating = 0
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
            
        return {
            'id': professional.professional_id,
            'created_date':professional.created_date.strftime('%Y-%m-%d %H:%M:%S'),
            'name': professional.name,
            'email': user.email,
            'service_type': professional.service_type,
            'experience': professional.exp,
            'description': professional.description,
            'pin': professional.pin,
            'approved': professional.approved,
            'blocked': professional.blocked,
            'total_requests': total_requests,
            'completed_requests': completed_requests,
            'average_rating': round(avg_rating, 1)
        }, 200
        
    @jwt_required()
    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'professional':
            return {'message': 'Professional access required'}, 403
            
        professional = Professional.query.filter_by(user_id=user.id).first()
        if not professional:
            return {'message': 'Professional profile not found'}, 404
            
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            professional.name = data['name']
        if 'service_type' in data:
            professional.service_type = data['service_type']
        if 'experience' in data:
            professional.exp = data['experience']
        if 'description' in data:
            professional.description = data['description']
        if 'pin' in data:
            professional.pin = data['pin']
            
        try:
            db.session.commit()
            return {'message': 'Profile updated successfully'}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating profile: {str(e)}'}, 500

class ProfessionalReviewsResource(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'professional':
            return {'message': 'Professional access required'}, 403
            
        professional = Professional.query.filter_by(user_id=user.id).first()
        if not professional:
            return {'message': 'Professional profile not found'}, 404
            
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 5, type=int)
        
        # Get reviews for the professional's service requests
        reviews = Review.query.join(ServiceRequest).filter(
            ServiceRequest.professional_id == professional.professional_id
        ).order_by(Review.date_created.desc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        result = []
        for review in reviews.items:
            customer = Customer.query.get(review.customer_id)
            service_request = ServiceRequest.query.get(review.service_request_id)
            service = Service.query.get(service_request.service_id) if service_request else None
            
            result.append({
                'id': review.id,
                'rating': review.rating,
                'comment': review.comment,
                'date': review.date_created.strftime('%Y-%m-%d %H:%M:%S'),
                'customer': customer.name if customer else 'Unknown Customer',
                'service': service.name if service else 'Unknown Service'
            })
            
        return {
            'reviews': result,
            'total': reviews.total,
            'pages': reviews.pages,
            'current_page': reviews.page
        }, 200

class AdminProfessionalsListResource(Resource):
    @jwt_required()
    @cache_response(prefix="admin:professionals", expire=300)  # Cache for 5 minutes
    def get(self, professional_id=None):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
        
        # If professional_id is provided, return details for a single professional
        if professional_id:
            professional = Professional.query.get(professional_id)
            if not professional:
                return {'message': 'Professional not found'}, 404
                
            # Get the user info
            pro_user = User.query.get(professional.user_id)
            if not pro_user:
                return {'message': 'User not found'}, 404
                
            # Get service requests count
            total_requests = ServiceRequest.query.filter_by(professional_id=professional.professional_id).count()
            completed_requests = ServiceRequest.query.filter_by(
                professional_id=professional.professional_id,
                status='closed'
            ).count()
            
            # Get reviews and calculate average rating
            reviews = Review.query.join(ServiceRequest).filter(
                ServiceRequest.professional_id == professional.professional_id
            ).all()
            
            avg_rating = 0
            if reviews:
                avg_rating = sum(review.rating for review in reviews) / len(reviews)
                
            # Get recent service requests
            recent_requests = ServiceRequest.query.filter_by(
                professional_id=professional.professional_id
            ).order_by(ServiceRequest.req_date.desc()).limit(5).all()
            
            recent_requests_data = []
            for req in recent_requests:
                service = Service.query.get(req.service_id)
                customer = Customer.query.get(req.customer_id)
                recent_requests_data.append({
                    'id': req.id,
                    'service': service.name if service else 'Unknown Service',
                    'customer': customer.name if customer else 'Unknown Customer',
                    'date': req.req_date.strftime('%Y-%m-%d %H:%M'),
                    'status': req.status
                })
                
            return {
                'id': professional.professional_id,
                'user_id': professional.user_id,
                'name': professional.name,
                'email': pro_user.email,
                'service_type': professional.service_type,
                'experience': professional.exp,
                'description': professional.description,
                'pin': professional.pin,
                'mobile':professional.mobile,
                'approved': professional.approved,
                'blocked': professional.blocked,
                'active': pro_user.active,
                'created_date': professional.created_date.strftime('%Y-%m-%d'),
                'stats': {
                    'total_requests': total_requests,
                    'completed_requests': completed_requests,
                    'average_rating': round(avg_rating, 1)
                },
                'recent_requests': recent_requests_data
            }, 200
        
        # Otherwise, return list of all professionals
        # Get search parameters
        search_name = request.args.get('name')
        search_service_type = request.args.get('service_type')
        search_status = request.args.get('status')  # approved, pending, blocked
        
        # Get all professionals
        professionals_list = Professional.query.all()
        result = []
        
        for professional in professionals_list:
            # Get the user info
            pro_user = User.query.get(professional.user_id)
            if not pro_user:
                continue
                
            # Apply filters
            if search_name and search_name.lower() not in professional.name.lower():
                continue
                
            if search_service_type and search_service_type != professional.service_type:
                continue
                
            if search_status:
                if search_status == 'approved' and not professional.approved:
                    continue
                if search_status == 'pending' and professional.approved:
                    continue
                if search_status == 'blocked' and not professional.blocked:
                    continue
            
            # Get service requests count
            total_requests = ServiceRequest.query.filter_by(professional_id=professional.professional_id).count()
            completed_requests = ServiceRequest.query.filter_by(
                professional_id=professional.professional_id,
                status='closed'
            ).count()
            
            # Get reviews and calculate average rating
            reviews = Review.query.join(ServiceRequest).filter(
                ServiceRequest.professional_id == professional.professional_id
            ).all()
            
            avg_rating = 0
            if reviews:
                avg_rating = sum(review.rating for review in reviews) / len(reviews)
                
            result.append({
                'id': professional.professional_id,
                'user_id': professional.user_id,
                'name': professional.name,
                'email': pro_user.email,
                'service_type': professional.service_type,
                'description':professional.description,
                'experience': professional.exp,
                'pin': professional.pin,
                'mobile':professional.mobile,
                'approved': professional.approved,
                'blocked': professional.blocked,
                'active': pro_user.active,
                'created_date': professional.created_date.strftime('%Y-%m-%d'),
                'stats': {
                    'total_requests': total_requests,
                    'completed_requests': completed_requests,
                    'average_rating': round(avg_rating, 1)
                }
            })
            
        # Sort by creation date (newest first)
        result.sort(key=lambda x: x['created_date'], reverse=True)
        
        return {
            'total': len(result),
            'professionals': result
        }, 200
    
class AdminCustomersListResource(Resource):
    @jwt_required()
    @cache_response(prefix="admin:customers", expire=300)  # Cache for 5 minutes
    def get(self, customer_id=None):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        # If customer_id is provided, return details for a single customer
        if customer_id:
            customer = Customer.query.get(customer_id)
            if not customer:
                return {'message': 'Customer not found'}, 404
                
            # Get the user info
            cust_user = User.query.get(customer.user_id)
            if not cust_user:
                return {'message': 'User not found'}, 404
                
            # Get service requests count
            total_requests = ServiceRequest.query.filter_by(customer_id=customer.customer_id).count()
            completed_requests = ServiceRequest.query.filter_by(
                customer_id=customer.customer_id,
                status='closed'
            ).count()
            
            # Get reviews count and average rating given
            reviews = Review.query.filter_by(customer_id=customer.customer_id).all()
            reviews_count = len(reviews)
            avg_rating_given = 0
            if reviews:
                avg_rating_given = sum(review.rating for review in reviews) / len(reviews)
                
            # Get recent service requests
            recent_requests = ServiceRequest.query.filter_by(
                customer_id=customer.customer_id
            ).order_by(ServiceRequest.req_date.desc()).limit(5).all()
            
            recent_requests_data = []
            for req in recent_requests:
                service = Service.query.get(req.service_id)
                professional = Professional.query.get(req.professional_id) if req.professional_id else None
                recent_requests_data.append({
                    'id': req.id,
                    'service': service.name if service else 'Unknown Service',
                    'professional': professional.name if professional else 'Unassigned',
                    'date': req.req_date.strftime('%Y-%m-%d %H:%M'),
                    'status': req.status
                })
                
            return {
                'id': customer.customer_id,
                'user_id': customer.user_id,
                'name': customer.name,
                'email': cust_user.email,
                'address': customer.address,
                'pin': customer.pin,
                'blocked': customer.blocked,
                'active': cust_user.active,
                'created_date': customer.created_date.strftime('%Y-%m-%d'),
                'stats': {
                    'total_requests': total_requests,
                    'completed_requests': completed_requests,
                    'reviews_count': reviews_count,
                    'average_rating_given': round(avg_rating_given, 1)
                },
                'recent_requests': recent_requests_data
            }, 200
        
        # Otherwise, return list of all customers
        # Get search parameters
        search_name = request.args.get('name')
        search_pin = request.args.get('pin')
        search_status = request.args.get('status')  # active, blocked
        
        # Get all customers
        customers_list = Customer.query.all()
        result = []
        
        for customer in customers_list:
            # Get the user info
            cust_user = User.query.get(customer.user_id)
            if not cust_user:
                continue
                
            # Apply filters
            if search_name and search_name.lower() not in customer.name.lower():
                continue
                
            if search_pin and str(search_pin) != str(customer.pin):
                continue
                
            if search_status:
                if search_status == 'active' and customer.blocked:
                    continue
                if search_status == 'blocked' and not customer.blocked:
                    continue
            
            # Get service requests count
            total_requests = ServiceRequest.query.filter_by(customer_id=customer.customer_id).count()
            completed_requests = ServiceRequest.query.filter_by(
                customer_id=customer.customer_id,
                status='closed'
            ).count()
            
            # Get reviews count
            reviews_count = Review.query.filter_by(customer_id=customer.customer_id).count()
                
            result.append({
                'id': customer.customer_id,
                'user_id': customer.user_id,
                'name': customer.name,
                'email': cust_user.email,
                'address': customer.address,
                'pin': customer.pin,
                'blocked': customer.blocked,
                'active': cust_user.active,
                'created_date': customer.created_date.strftime('%Y-%m-%d'),
                'stats': {
                    'total_requests': total_requests,
                    'completed_requests': completed_requests,
                    'reviews_count': reviews_count
                }
            })
            
        # Sort by creation date (newest first)
        result.sort(key=lambda x: x['created_date'], reverse=True)
        
        return {
            'total': len(result),
            'customers': result
        }, 200

class AdminProfessionalBlockResource(Resource):
    @jwt_required()
    def post(self, professional_id):
        # Verify admin access
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        # Get the professional
        professional = Professional.query.get(professional_id)
        if not professional:
            return {'message': 'Professional not found'}, 404
            
        # Check if this is a block or unblock request based on endpoint
        is_block = request.path.endswith('/block')
        
        if is_block:
            # Block the professional
            professional.blocked = True
            message = 'Professional blocked successfully'
        else:
            # Unblock the professional
            professional.blocked = False
            message = 'Professional unblocked successfully'
            
        try:
            db.session.commit()
            # Invalidate cache
            invalidate_cache_prefix("admin:professionals")
            return {'message': message}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating professional status: {str(e)}'}, 500

class AdminCustomerBlockResource(Resource):
    @jwt_required()
    def post(self, customer_id):
        # Verify admin access
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403
            
        # Get the customer
        customer = Customer.query.get(customer_id)
        if not customer:
            return {'message': 'Customer not found'}, 404
            
        # Check if this is a block or unblock request based on endpoint
        is_block = request.path.endswith('/block')
        
        if is_block:
            # Block the customer
            customer.blocked = True
            message = 'Customer blocked successfully'
        else:
            # Unblock the customer
            customer.blocked = False
            message = 'Customer unblocked successfully'
            
        try:
            db.session.commit()
            # Invalidate cache
            invalidate_cache_prefix("admin:customers")
            return {'message': message}, 200
        except Exception as e:
            db.session.rollback()
            return {'message': f'Error updating customer status: {str(e)}'}, 500
