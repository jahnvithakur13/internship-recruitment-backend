from flask import Blueprint
from src.controllers.auth_controller import register, login, get_profile
from src.middleware.auth_middleware import jwt_required_custom

auth_bp = Blueprint("auth", __name__)

auth_bp.route("/register", methods=["POST"])(register)
auth_bp.route("/login", methods=["POST"])(login)
auth_bp.route("/profile", methods=["GET"])(jwt_required_custom(get_profile))
