from flask import Blueprint
from src.controllers.dashboard_controller import recruiter_dashboard, admin_dashboard
from src.middleware.auth_middleware import role_required

dashboard_bp = Blueprint("dashboard", __name__)

dashboard_bp.route("/recruiter", methods=["GET"])(role_required("recruiter")(recruiter_dashboard))
dashboard_bp.route("/admin", methods=["GET"])(role_required("admin")(admin_dashboard))
