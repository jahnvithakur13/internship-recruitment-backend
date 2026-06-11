from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from src.config.database import get_db

def create_internship():
    data = request.get_json()
    recruiter_id = get_jwt_identity()

    required = ["title", "description"]
    for field in required:
        if not data or not data.get(field):
            return jsonify({"success": False, "message": f"'{field}' is required"}), 400

    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO internships 
               (recruiter_id, title, description, stipend, location, skills_required, deadline, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                recruiter_id,
                data["title"],
                data["description"],
                data.get("stipend", ""),
                data.get("location", ""),
                data.get("skills_required", ""),
                data.get("deadline", ""),
                data.get("status", "open")
            )
        )
        db.commit()

        internship = db.execute("SELECT * FROM internships WHERE id = ?", (cursor.lastrowid,)).fetchone()

        return jsonify({
            "success": True,
            "message": "Internship created successfully",
            "data": dict(internship)
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

def get_internships():
    db = get_db()
    try:
        # Query params for filtering
        location = request.args.get("location", "")
        skills = request.args.get("skills", "")
        status = request.args.get("status", "")
        sort = request.args.get("sort", "created_at")
        order = request.args.get("order", "desc").upper()
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 10))
        offset = (page - 1) * limit

        # Validate sort field to prevent SQL injection
        allowed_sort = ["created_at", "deadline", "stipend", "title"]
        if sort not in allowed_sort:
            sort = "created_at"
        if order not in ["ASC", "DESC"]:
            order = "DESC"

        # Build query
        query = "SELECT i.*, u.name as recruiter_name FROM internships i JOIN users u ON i.recruiter_id = u.id WHERE 1=1"
        params = []

        if location:
            query += " AND LOWER(i.location) LIKE ?"
            params.append(f"%{location.lower()}%")
        if skills:
            query += " AND LOWER(i.skills_required) LIKE ?"
            params.append(f"%{skills.lower()}%")
        if status:
            query += " AND i.status = ?"
            params.append(status)

        # Count total
        count_query = f"SELECT COUNT(*) FROM ({query})"
        total = db.execute(count_query, params).fetchone()[0]

        # Add sort and pagination
        query += f" ORDER BY i.{sort} {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = db.execute(query, params).fetchall()
        internships = [dict(row) for row in rows]

        return jsonify({
            "success": True,
            "data": internships,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": (total + limit - 1) // limit
            }
        })

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

def get_internship(internship_id):
    db = get_db()
    try:
        row = db.execute(
            "SELECT i.*, u.name as recruiter_name FROM internships i JOIN users u ON i.recruiter_id = u.id WHERE i.id = ?",
            (internship_id,)
        ).fetchone()
        if not row:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        return jsonify({"success": True, "data": dict(row)})
    finally:
        db.close()

def update_internship(internship_id):
    data = request.get_json()
    recruiter_id = get_jwt_identity()

    db = get_db()
    try:
        internship = db.execute("SELECT * FROM internships WHERE id = ?", (internship_id,)).fetchone()
        if not internship:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        if str(internship["recruiter_id"]) != str(recruiter_id):
            return jsonify({"success": False, "message": "You can only update your own internships"}), 403

        db.execute(
            """UPDATE internships SET 
               title = ?, description = ?, stipend = ?, location = ?,
               skills_required = ?, deadline = ?, status = ?
               WHERE id = ?""",
            (
                data.get("title", internship["title"]),
                data.get("description", internship["description"]),
                data.get("stipend", internship["stipend"]),
                data.get("location", internship["location"]),
                data.get("skills_required", internship["skills_required"]),
                data.get("deadline", internship["deadline"]),
                data.get("status", internship["status"]),
                internship_id
            )
        )
        db.commit()

        updated = db.execute("SELECT * FROM internships WHERE id = ?", (internship_id,)).fetchone()
        return jsonify({"success": True, "message": "Internship updated", "data": dict(updated)})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

def delete_internship(internship_id):
    recruiter_id = get_jwt_identity()
    db = get_db()
    try:
        internship = db.execute("SELECT * FROM internships WHERE id = ?", (internship_id,)).fetchone()
        if not internship:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        if str(internship["recruiter_id"]) != str(recruiter_id):
            return jsonify({"success": False, "message": "You can only delete your own internships"}), 403

        db.execute("DELETE FROM internships WHERE id = ?", (internship_id,))
        db.commit()
        return jsonify({"success": True, "message": "Internship deleted successfully"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

def get_applicants(internship_id):
    recruiter_id = get_jwt_identity()
    db = get_db()
    try:
        internship = db.execute("SELECT * FROM internships WHERE id = ?", (internship_id,)).fetchone()
        if not internship:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        if str(internship["recruiter_id"]) != str(recruiter_id):
            return jsonify({"success": False, "message": "Access denied"}), 403

        rows = db.execute(
            """SELECT a.*, u.name, u.email FROM applications a
               JOIN users u ON a.candidate_id = u.id
               WHERE a.internship_id = ?
               ORDER BY a.applied_at DESC""",
            (internship_id,)
        ).fetchall()

        return jsonify({"success": True, "data": [dict(r) for r in rows]})
    finally:
        db.close()
