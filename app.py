from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from src.config.database import init_db
from src.routes.auth_routes import auth_bp
from src.routes.internship_routes import internship_bp
from src.routes.application_routes import application_bp
from src.routes.dashboard_routes import dashboard_bp
import logging

app = Flask(__name__)

# Config
app.config["JWT_SECRET_KEY"] = "super-secret-jwt-key-change-in-production"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

jwt = JWTManager(app)

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(internship_bp, url_prefix="/internships")
app.register_blueprint(application_bp, url_prefix="/applications")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")

# Global error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "message": "Route not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "message": "Method not allowed"}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "message": "Internal server error"}), 500

# Root
@app.route("/")
def index():
    return jsonify({
        "success": True,
        "message": "Internship & Recruitment Management API",
        "version": "1.0.0",
        "docs": "/docs"
    })

if __name__ == "__main__":
    init_db()
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
