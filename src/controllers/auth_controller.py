from flask import request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity
import bcrypt
from src.config.database import get_db
from src.middleware.auth_middleware import get_current_user

def register():
    data = request.get_json()

    # Validation
    required = ["name", "email", "password", "role"]
    for field in required:
        if not data or not data.get(field):
            return jsonify({"success": False, "message": f"'{field}' is required"}), 400

    if data["role"] not in ["candidate", "recruiter", "admin"]:
        return jsonify({"success": False, "message": "Role must be: candidate, recruiter, or admin"}), 400

    if len(data["password"]) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters"}), 400

    db = get_db()
    try:
        # Check if email exists
        existing = db.execute("SELECT id FROM users WHERE email = ?", (data["email"],)).fetchone()
        if existing:
            return jsonify({"success": False, "message": "Email already registered"}), 409

        # Hash password
        password_hash = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        # Insert user
        cursor = db.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (data["name"], data["email"], password_hash, data["role"])
        )
        db.commit()
        user_id = cursor.lastrowid

        # Generate token
        token = create_access_token(identity=str(user_id))

        return jsonify({
            "success": True,
            "message": "User registered successfully",
            "data": {
                "id": user_id,
                "name": data["name"],
                "email": data["email"],
                "role": data["role"],
                "token": token
            }
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    db = get_db()
    try:
        user = db.execute("SELECT * FROM users WHERE email = ?", (data["email"],)).fetchone()

        if not user:
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        # Check password
        if not bcrypt.checkpw(data["password"].encode("utf-8"), user["password_hash"].encode("utf-8")):
            return jsonify({"success": False, "message": "Invalid email or password"}), 401

        token = create_access_token(identity=str(user["id"]))

        return jsonify({
            "success": True,
            "message": "Login successful",
            "data": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
                "token": token
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

def get_profile():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404

    return jsonify({
        "success": True,
        "data": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"]
        }
    })
