from flask import Flask
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

from backend.config import Config
from backend.model import db, User, Professional, Customer, Service, ServiceRequest, Review

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Service types and their corresponding services
SERVICE_TYPES = {
    "Plumbing": [
        {"name": "Leaky Faucet Repair", "price": 299, "time_req": 1, "description": "Fix leaking taps and faucets"},
        {"name": "Toilet Repair", "price": 499, "time_req": 2, "description": "Repair toilet flush, seat, or leakage"},
        {"name": "Pipe Fitting", "price": 599, "time_req": 3, "description": "Install or replace water pipes"}
    ],
    "Electrical": [
        {"name": "Switch Repair", "price": 199, "time_req": 1, "description": "Repair or replace switches"},
        {"name": "Fan Installation", "price": 399, "time_req": 2, "description": "Install ceiling or wall fans"},
        {"name": "Wiring Work", "price": 799, "time_req": 4, "description": "Fix electrical wiring issues"}
    ],
    "Cleaning": [
        {"name": "Home Deep Cleaning", "price": 1999, "time_req": 6, "description": "Complete house deep cleaning"},
        {"name": "Bathroom Cleaning", "price": 699, "time_req": 2, "description": "Thorough bathroom sanitization"},
        {"name": "Kitchen Cleaning", "price": 899, "time_req": 3, "description": "Complete kitchen cleaning and organizing"}
    ],
    "Carpentry": [
        {"name": "Furniture Repair", "price": 599, "time_req": 2, "description": "Fix broken furniture"},
        {"name": "Door Repair", "price": 499, "time_req": 2, "description": "Fix door hinges, handles or locks"},
        {"name": "Cabinet Installation", "price": 1299, "time_req": 4, "description": "Install new cabinets or shelves"}
    ],
    "Appliance Repair": [
        {"name": "AC Service", "price": 699, "time_req": 2, "description": "AC cleaning and maintenance"},
        {"name": "Refrigerator Repair", "price": 799, "time_req": 3, "description": "Fix refrigerator issues"},
        {"name": "Washing Machine Repair", "price": 699, "time_req": 3, "description": "Fix washing machine problems"}
    ]
}

# Professionals' data
PROFESSIONALS = [
    {"name": "Ravi Kumar", "email": "ravi@example.com", "mobile": "9876543210", "service_type": "Plumbing", "exp": "5 years", "pin": 400001, "description": "Expert plumber with 5+ years of experience"},
    {"name": "Amit Singh", "email": "amit@example.com", "mobile": "9876543211", "service_type": "Electrical", "exp": "7 years", "pin": 400002, "description": "Certified electrician specializing in home wiring"},
    {"name": "Priya Sharma", "email": "priya@example.com", "mobile": "9876543212", "service_type": "Cleaning", "exp": "3 years", "pin": 400003, "description": "Professional cleaner with attention to detail"},
    {"name": "Suresh Patel", "email": "suresh@example.com", "mobile": "9876543213", "service_type": "Carpentry", "exp": "10 years", "pin": 400004, "description": "Master carpenter with expertise in furniture making"},
    {"name": "Rajesh Verma", "email": "rajesh@example.com", "mobile": "9876543214", "service_type": "Appliance Repair", "exp": "6 years", "pin": 400005, "description": "Specialized in AC and refrigerator repairs"},
    {"name": "Deepak Joshi", "email": "deepak@example.com", "mobile": "9876543215", "service_type": "Plumbing", "exp": "4 years", "pin": 400006, "description": "Plumbing expert available 24/7 for emergencies"},
    {"name": "Neha Gupta", "email": "neha@example.com", "mobile": "9876543216", "service_type": "Electrical", "exp": "5 years", "pin": 400007, "description": "Specializes in electrical fault detection and repair"},
    {"name": "Vikram Reddy", "email": "vikram@example.com", "mobile": "9876543217", "service_type": "Cleaning", "exp": "2 years", "pin": 400008, "description": "Deep cleaning expert for homes and offices"},
    {"name": "Manoj Tiwari", "email": "manoj@example.com", "mobile": "9876543218", "service_type": "Carpentry", "exp": "8 years", "pin": 400009, "description": "Specialized in custom cabinet making"},
    {"name": "Kiran Shah", "email": "kiran@example.com", "mobile": "9876543219", "service_type": "Appliance Repair", "exp": "7 years", "pin": 400010, "description": "Washing machine and dishwasher repair specialist"}
]

# Customers' data
CUSTOMERS = [
    {"name": "Ananya Desai", "email": "ananya@example.com", "address": "123 Juhu Beach Road, Mumbai", "pin": 400049},
    {"name": "Rahul Khanna", "email": "rahul@example.com", "address": "456 Bandra West, Mumbai", "pin": 400050},
    {"name": "Sonia Malhotra", "email": "sonia@example.com", "address": "789 Andheri East, Mumbai", "pin": 400069},
    {"name": "Karan Mehra", "email": "karan@example.com", "address": "101 Powai, Mumbai", "pin": 400076},
    {"name": "Divya Kapoor", "email": "divya@example.com", "address": "202 Worli, Mumbai", "pin": 400018},
    {"name": "Vivek Nair", "email": "vivek@example.com", "address": "303 Dadar, Mumbai", "pin": 400014},
    {"name": "Pooja Sharma", "email": "pooja@example.com", "address": "404 Goregaon, Mumbai", "pin": 400063},
    {"name": "Arjun Mehta", "email": "arjun@example.com", "address": "505 Malad, Mumbai", "pin": 400064},
    {"name": "Meera Patel", "email": "meera@example.com", "address": "606 Borivali, Mumbai", "pin": 400092},
    {"name": "Rohan Jain", "email": "rohan@example.com", "address": "707 Kandivali, Mumbai", "pin": 400067}
]

def populate_database():
    with app.app_context():
        # Drop all tables and recreate
        db.drop_all()
        db.create_all()
        print("Database tables created")
        
        # Create admin user
        import create_admin
        create_admin.create_admin()
        
        # Create services by type
        services_map = {}  # To store service IDs for later use
        for service_type, services in SERVICE_TYPES.items():
            for service_data in services:
                service = Service(
                    name=service_data["name"],
                    price=service_data["price"],
                    time_req=service_data["time_req"],
                    description=service_data["description"],
                    service_type=service_type
                )
                db.session.add(service)
                db.session.flush()  # Get ID before commit
                
                # Store the service in our map
                if service_type not in services_map:
                    services_map[service_type] = []
                services_map[service_type].append(service)
        
        db.session.commit()
        print("Services created")
        
        # Create professionals
        professionals = []
        for prof_data in PROFESSIONALS:
            # Create user first
            user = User(
                email=prof_data["email"],
                password=generate_password_hash("password123"),  # Standard password for testing
                role="professional",
                active=True
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Then create professional profile
            professional = Professional(
                user_id=user.id,
                name=prof_data["name"],
                service_type=prof_data["service_type"],
                mobile=prof_data["mobile"],
                exp=prof_data["exp"],
                pin=prof_data["pin"],
                description=prof_data["description"],
                approved=True,  # All pre-approved for testing
                blocked=False
            )
            db.session.add(professional)
            db.session.flush()  # Get professional ID
            professionals.append(professional)
        
        db.session.commit()
        print("Professionals created")
        
        # Create customers
        customers = []
        for cust_data in CUSTOMERS:
            # Create user first
            user = User(
                email=cust_data["email"],
                password=generate_password_hash("password123"),  # Standard password for testing
                role="customer",
                active=True
            )
            db.session.add(user)
            db.session.flush()  # Get user ID
            
            # Then create customer profile
            customer = Customer(
                user_id=user.id,
                name=cust_data["name"],
                address=cust_data["address"],
                pin=cust_data["pin"],
                blocked=False
            )
            db.session.add(customer)
            db.session.flush()  # Get customer ID
            customers.append(customer)
        
        db.session.commit()
        print("Customers created")
        
        # Create service requests with various statuses
        statuses = ["requested", "assigned", "closed"]
        service_requests = []
        
        # Create some service requests from the past 30 days
        for _ in range(25):
            # Pick a random customer, service, and professional
            customer = random.choice(customers)
            service_type = random.choice(list(services_map.keys()))
            service = random.choice(services_map[service_type])
            
            # Filter professionals by service type
            eligible_professionals = [p for p in professionals if p.service_type == service_type]
            professional = random.choice(eligible_professionals) if eligible_professionals else None
            
            # Generate a random date within the past 30 days
            days_ago = random.randint(0, 30)
            req_date = datetime.now() - timedelta(days=days_ago)
            
            # Determine status
            status = random.choice(statuses)
            
            # For assigned and closed, add a professional
            professional_id = None
            comp_date = None
            if status in ["assigned", "closed"]:
                professional_id = professional.professional_id
                
                # For closed requests, add completion date
                if status == "closed":
                    # Complete between 1 and 3 days after request
                    comp_date = req_date + timedelta(days=random.randint(1, 3))
            
            # Create service request
            service_request = ServiceRequest(
                service_id=service.id,
                customer_id=customer.customer_id,
                professional_id=professional_id,
                req_date=req_date,
                comp_date=comp_date,
                status=status,
                remarks=f"Need {service.name} service at {customer.address}"
            )
            
            db.session.add(service_request)
            db.session.flush()  # Get service request ID
            service_requests.append(service_request)
            
            # For closed requests, add a review
            if status == "closed":
                rating = random.randint(3, 5)  # Generally positive reviews
                review = Review(
                    service_request_id=service_request.id,
                    customer_id=customer.customer_id,
                    rating=rating,
                    comment=f"{'Excellent' if rating == 5 else 'Good' if rating == 4 else 'Satisfactory'} service by {professional.name}. {'Would recommend!' if rating >= 4 else ''}",
                    date_created=comp_date + timedelta(hours=random.randint(1, 24))
                )
                db.session.add(review)
        
        db.session.commit()
        print("Service requests and reviews created")
        
        print("Database populated successfully!")

if __name__ == "__main__":
    populate_database() 