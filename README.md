# 🚀 Internship & Recruitment Management Backend System

A REST API backend for managing internship applications, built with **Python + Flask + SQLite**.

## ⚙️ Tech Stack
- **Python 3.x** + Flask
- **SQLite** (zero-config database)
- **JWT Authentication** (flask-jwt-extended)
- **bcrypt** for password hashing
- Role-Based Access Control (Candidate / Recruiter / Admin)

---

## 🗂️ Folder Structure

```
internship-backend/
├── app.py                        # Entry point
├── requirements.txt
├── internship.db                 # Auto-created SQLite DB
└── src/
    ├── config/
    │   └── database.py           # DB connection + schema init
    ├── controllers/
    │   ├── auth_controller.py    # Register, login, profile
    │   ├── internship_controller.py
    │   ├── application_controller.py
    │   └── dashboard_controller.py
    ├── middleware/
    │   └── auth_middleware.py    # JWT + role guards
    └── routes/
        ├── auth_routes.py
        ├── internship_routes.py
        ├── application_routes.py
        └── dashboard_routes.py
```

---

## 🚀 Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/internship-backend.git
cd internship-backend
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the server
```bash
python app.py
```
Server runs at: `http://localhost:5000`

> The SQLite database (`internship.db`) is **auto-created** on first run. No setup needed!

---

## 🔐 Authentication Flow

1. Register with a role: `candidate`, `recruiter`, or `admin`
2. Login to receive a **JWT token**
3. Pass token in all protected requests:
   ```
   Authorization: Bearer <your_token>
   ```

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/register` | Public | Register new user |
| POST | `/auth/login` | Public | Login, get JWT |
| GET | `/auth/profile` | Any logged-in | View own profile |

### Internships
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/internships` | Public | List all (with filters) |
| GET | `/internships/:id` | Public | Get single internship |
| POST | `/internships` | Recruiter | Create internship |
| PUT | `/internships/:id` | Recruiter (owner) | Update internship |
| DELETE | `/internships/:id` | Recruiter (owner) | Delete internship |
| GET | `/internships/:id/applicants` | Recruiter (owner) | View applicants |
| POST | `/internships/:id/apply` | Candidate | Apply to internship |

### Applications
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/applications/my` | Candidate | My applications + status |
| PATCH | `/applications/:id/status` | Recruiter | Update application status |

### Dashboard
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/dashboard/recruiter` | Recruiter | Stats for recruiter |
| GET | `/dashboard/admin` | Admin | Platform-wide stats |

---

## 🔍 Search & Filter

```
GET /internships?location=remote&skills=python&status=open&page=1&limit=10&sort=deadline&order=asc
```

| Param | Description |
|-------|-------------|
| `location` | Filter by location (partial match) |
| `skills` | Filter by skills (partial match) |
| `status` | `open` or `closed` |
| `page` | Page number (default: 1) |
| `limit` | Results per page (default: 10) |
| `sort` | Sort by: `created_at`, `deadline`, `stipend`, `title` |
| `order` | `asc` or `desc` |

---

## 📊 Application Status Flow

```
applied → shortlisted → interview_scheduled → selected
                    ↘ rejected
```

---

## 🗄️ Database Schema (ER Diagram)

```
users
  id (PK), name, email, password_hash, role, created_at

internships
  id (PK), recruiter_id (FK→users), title, description,
  stipend, location, skills_required, deadline, status, created_at

applications
  id (PK), candidate_id (FK→users), internship_id (FK→internships),
  resume_url, status, applied_at
  UNIQUE(candidate_id, internship_id)
```

---

## 📬 Sample API Requests

### Register
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Your Name","email":"you@example.com","password":"pass123","role":"candidate"}'
```

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"pass123"}'
```

### Create Internship (Recruiter)
```bash
curl -X POST http://localhost:5000/internships \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"title":"Python Intern","description":"Build APIs","stipend":"8000","location":"remote","skills_required":"python,flask","deadline":"2025-09-01"}'
```

### Apply (Candidate)
```bash
curl -X POST http://localhost:5000/internships/1/apply \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"resume_url":"https://your-resume-link.com"}'
```

---

## 📝 Error Response Format

All errors follow this structure:
```json
{
  "success": false,
  "message": "Description of what went wrong"
}
```

---

## 👩‍💻 Author
**Jahnvi Singh** — B.Tech CS, IMS Engineering College  
GitHub: [@jahnvithakur13](https://github.com/jahnvithakur13)
