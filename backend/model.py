from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String, nullable=False)  # 'admin', 'professional', 'customer'
    
    # Relationship with Professional and Customer models
    professional = db.relationship('Professional', back_populates='user', uselist=False)
    customer = db.relationship('Customer', back_populates='user', uselist=False)

# Define Professional model
class Professional(db.Model):
    professional_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='professional')
    name = db.Column(db.String, nullable=False)
    service_type = db.Column(db.String, nullable=False)
    mobile = db.Column(db.String)
    exp = db.Column(db.String)
    pin = db.Column(db.Integer)
    created_date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.String)
    approved = db.Column(db.Boolean, default=False)
    blocked = db.Column(db.Boolean, default=False)

class Customer(db.Model):
    customer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='customer')
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    pin = db.Column(db.Integer, nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.now)
    blocked = db.Column(db.Boolean, default=False)

# Define Service model
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    time_req = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String)
    service_type = db.Column(db.String, nullable=False)

# Define ServiceRequest model
class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    professional_id = db.Column(db.Integer, db.ForeignKey('professional.professional_id'))
    req_date = db.Column(db.DateTime, default=datetime.now)
    comp_date = db.Column(db.DateTime)
    status = db.Column(db.String, default='requested')  # 'requested', 'assigned', 'closed'
    remarks = db.Column(db.String)

    # Relationship to Customer model
    customer = db.relationship('Customer', backref='service_requests')

    # Relationship to Service model
    service = db.relationship('Service', backref='service_requests')

    # Relationship to Professional model
    professional = db.relationship('Professional', backref='service_requests')

# Define Review model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String)
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    # Relationship to ServiceRequest model
    service_request = db.relationship('ServiceRequest', backref='reviews')
    
    # Relationship to Customer model
    customer = db.relationship('Customer', backref='reviews')