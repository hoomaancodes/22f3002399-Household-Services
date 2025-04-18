from flask import Flask
from werkzeug.security import generate_password_hash
from backend.config import Config
from backend.model import db, User

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_admin():
    with app.app_context():
        # Check if admin user exists
        admin = User.query.filter_by(email=Config.ADMIN_EMAIL).first()
        if not admin:
            # Create admin user
            admin = User(
                email=Config.ADMIN_EMAIL,
                password=generate_password_hash(Config.ADMIN_PASSWORD),
                role='admin',
                active=True
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created with email {Config.ADMIN_EMAIL}")
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    create_admin() 