from flask import Blueprint
from src.controllers.internship_controller import (
    create_internship, get_internships, get_internship,
    update_internship, delete_internship, get_applicants
)
from src.middleware.auth_middleware import role_required, jwt_required_custom

internship_bp = Blueprint("internships", __name__)

# Public - anyone can browse
internship_bp.route("", methods=["GET"])(get_internships)
internship_bp.route("/<int:internship_id>", methods=["GET"])(get_internship)

# Recruiters only
internship_bp.route("", methods=["POST"])(role_required("recruiter")(create_internship))
internship_bp.route("/<int:internship_id>", methods=["PUT"])(role_required("recruiter")(update_internship))
internship_bp.route("/<int:internship_id>", methods=["DELETE"])(role_required("recruiter")(delete_internship))
internship_bp.route("/<int:internship_id>/applicants", methods=["GET"])(role_required("recruiter")(get_applicants))

# Candidates applying
from src.controllers.application_controller import apply_to_internship
internship_bp.route("/<int:internship_id>/apply", methods=["POST"])(role_required("candidate")(apply_to_internship))
