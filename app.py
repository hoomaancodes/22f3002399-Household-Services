from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.config import Config
from backend.model import db
from backend.routes import api_bp
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions with CORS configuration
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
jwt = JWTManager(app)
db.init_app(app)

# Register blueprints
app.register_blueprint(api_bp)

# Initialize Redis cache (indirectly)
with app.app_context():
    try:
        from backend.cache import REDIS_AVAILABLE
        if REDIS_AVAILABLE:
            logger.info("Redis cache initialized successfully")
        else:
            logger.warning("Redis cache is not available - caching is disabled")
    except ImportError:
        logger.warning("Redis cache module could not be imported")

# JWT error handlers
@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({"message": "invalid_token", "error": str(error)}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({"message": "missing_token", "error": str(error)}), 401

@jwt.expired_token_loader
def expired_token_callback(header, payload):
    return jsonify({"message": "token_expired", "error": "Token has expired"}), 401

@jwt.revoked_token_loader
def revoked_token_callback(header, payload):
    return jsonify({"message": "revoked_token", "error": "Token has been revoked"}), 401

@jwt.needs_fresh_token_loader
def needs_fresh_token_callback(header, payload):
    return jsonify({"message": "fresh_token_required", "error": "Fresh token required"}), 401

# General error handler
@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({"message": "error", "error": str(e)}), 500

# Create all database tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True) 