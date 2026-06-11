from flask import Blueprint
from src.controllers.application_controller import my_applications, update_application_status
from src.middleware.auth_middleware import role_required

application_bp = Blueprint("applications", __name__)

# Candidates
application_bp.route("/my", methods=["GET"])(role_required("candidate")(my_applications))

# Recruiters
application_bp.route("/<int:application_id>/status", methods=["PATCH"])(role_required("recruiter")(update_application_status))
