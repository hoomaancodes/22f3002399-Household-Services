# Household Services API

A comprehensive REST API backend for a household services application that allows customers to request services, professionals to accept and fulfill service requests, and admins to manage users and services.

## Features

- **User Management**: Registration and authentication for customers, professionals, and administrators
- **JWT-based Authentication**: Secure API endpoints with JWT token-based authentication
- **Service Management**: Create, read, update, and delete services
- **Service Request Workflow**: Full lifecycle of service requests from creation to completion
- **Review System**: Customers can review completed services
- **Role-based Access Control**: Different permissions for customers, professionals, and administrators

## API Endpoints

### Authentication

- `POST /api/auth/register`: Register a new user (customer, professional)
- `POST /api/auth/login`: Login and get JWT tokens
- `POST /api/auth/refresh`: Refresh access token

### Services

- `GET /api/services`: Get all services
- `POST /api/services`: Create a new service (admin only)
- `GET /api/services/<id>`: Get service details
- `PUT /api/services/<id>`: Update a service (admin only)
- `DELETE /api/services/<id>`: Delete a service (admin only)
- `GET /api/service-types`: Get all service types

### Service Requests

- `GET /api/service-requests`: Get service requests (filtered by user role)
- `POST /api/service-requests`: Create a new service request (customer only)
- `GET /api/service-requests/<id>`: Get service request details
- `PUT /api/service-requests/<id>`: Update a service request status
- `DELETE /api/service-requests/<id>`: Delete a service request

### Reviews

- `GET /api/reviews`: Get all reviews
- `GET /api/reviews/<service_request_id>`: Get reviews for a specific service request
- `POST /api/reviews`: Create a new review (customer only)

### Admin

- `GET /api/admin/users`: Get all users (admin only)
- `PUT /api/admin/professionals/<id>`: Approve/block a professional (admin only)
- `PUT /api/admin/customers/<id>`: Block a customer (admin only)

## Tech Stack

- **Flask**: Web framework
- **Flask-RESTful**: REST API framework
- **Flask-JWT-Extended**: JWT authentication
- **Flask-SQLAlchemy**: ORM for database operations
- **SQLite**: Database

## Setup and Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`

## Testing

Several test scripts are provided to test the functionality of the API:

- `test_service_request.py`: Test service request creation
- `test_professional.py`: Test professional registration and listing
- `test_jwt_endpoints.py`: Test JWT protected endpoints
- `test_professional_accept.py`: Test professional accepting a service request
- `test_customer_complete.py`: Test customer completing a service request and adding a review 