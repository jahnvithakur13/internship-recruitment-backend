from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from src.config.database import get_db

def apply_to_internship(internship_id):
    candidate_id = get_jwt_identity()
    data = request.get_json() or {}

    db = get_db()
    try:
        # Check internship exists and is open
        internship = db.execute("SELECT * FROM internships WHERE id = ?", (internship_id,)).fetchone()
        if not internship:
            return jsonify({"success": False, "message": "Internship not found"}), 404
        if internship["status"] != "open":
            return jsonify({"success": False, "message": "This internship is closed"}), 400

        # Check already applied
        existing = db.execute(
            "SELECT id FROM applications WHERE candidate_id = ? AND internship_id = ?",
            (candidate_id, internship_id)
        ).fetchone()
        if existing:
            return jsonify({"success": False, "message": "You have already applied to this internship"}), 409

        cursor = db.execute(
            "INSERT INTO applications (candidate_id, internship_id, resume_url) VALUES (?, ?, ?)",
            (candidate_id, internship_id, data.get("resume_url", ""))
        )
        db.commit()

        application = db.execute("SELECT * FROM applications WHERE id = ?", (cursor.lastrowid,)).fetchone()

        return jsonify({
            "success": True,
            "message": "Application submitted successfully",
            "data": dict(application)
        }), 201

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()

def my_applications():
    candidate_id = get_jwt_identity()
    db = get_db()
    try:
        rows = db.execute(
            """SELECT a.*, i.title, i.company, i.location, i.stipend
               FROM applications a
               JOIN internships i ON a.internship_id = i.id
               WHERE a.candidate_id = ?
               ORDER BY a.applied_at DESC""",
            (candidate_id,)
        ).fetchall()

        return jsonify({"success": True, "data": [dict(r) for r in rows]})
    finally:
        db.close()

def update_application_status(application_id):
    recruiter_id = get_jwt_identity()
    data = request.get_json()

    valid_statuses = ["applied", "shortlisted", "interview_scheduled", "rejected", "selected"]
    new_status = data.get("status") if data else None

    if not new_status or new_status not in valid_statuses:
        return jsonify({"success": False, "message": f"Status must be one of: {', '.join(valid_statuses)}"}), 400

    db = get_db()
    try:
        # Get application and verify ownership via internship
        row = db.execute(
            """SELECT a.*, i.recruiter_id FROM applications a
               JOIN internships i ON a.internship_id = i.id
               WHERE a.id = ?""",
            (application_id,)
        ).fetchone()

        if not row:
            return jsonify({"success": False, "message": "Application not found"}), 404
        if str(row["recruiter_id"]) != str(recruiter_id):
            return jsonify({"success": False, "message": "Access denied"}), 403

        db.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, application_id))
        db.commit()

        return jsonify({"success": True, "message": f"Application status updated to '{new_status}'"})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()
