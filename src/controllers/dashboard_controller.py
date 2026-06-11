from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from src.config.database import get_db

def recruiter_dashboard():
    recruiter_id = get_jwt_identity()
    db = get_db()
    try:
        total_internships = db.execute(
            "SELECT COUNT(*) FROM internships WHERE recruiter_id = ?", (recruiter_id,)
        ).fetchone()[0]

        total_applicants = db.execute(
            """SELECT COUNT(*) FROM applications a
               JOIN internships i ON a.internship_id = i.id
               WHERE i.recruiter_id = ?""",
            (recruiter_id,)
        ).fetchone()[0]

        shortlisted = db.execute(
            """SELECT COUNT(*) FROM applications a
               JOIN internships i ON a.internship_id = i.id
               WHERE i.recruiter_id = ? AND a.status = 'shortlisted'""",
            (recruiter_id,)
        ).fetchone()[0]

        open_internships = db.execute(
            "SELECT COUNT(*) FROM internships WHERE recruiter_id = ? AND status = 'open'",
            (recruiter_id,)
        ).fetchone()[0]

        return jsonify({
            "success": True,
            "data": {
                "total_internships": total_internships,
                "open_internships": open_internships,
                "total_applicants": total_applicants,
                "shortlisted_candidates": shortlisted
            }
        })
    finally:
        db.close()

def admin_dashboard():
    db = get_db()
    try:
        total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_candidates = db.execute("SELECT COUNT(*) FROM users WHERE role = 'candidate'").fetchone()[0]
        total_recruiters = db.execute("SELECT COUNT(*) FROM users WHERE role = 'recruiter'").fetchone()[0]
        total_internships = db.execute("SELECT COUNT(*) FROM internships").fetchone()[0]
        total_applications = db.execute("SELECT COUNT(*) FROM applications").fetchone()[0]

        active_recruiters = db.execute(
            """SELECT COUNT(DISTINCT recruiter_id) FROM internships"""
        ).fetchone()[0]

        return jsonify({
            "success": True,
            "data": {
                "total_users": total_users,
                "total_candidates": total_candidates,
                "total_recruiters": total_recruiters,
                "active_recruiters": active_recruiters,
                "total_internships": total_internships,
                "total_applications": total_applications
            }
        })
    finally:
        db.close()
