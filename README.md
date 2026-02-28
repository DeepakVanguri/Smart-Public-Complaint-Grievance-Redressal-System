# 🏛️ Smart Public Complaint & Grievance Redressal System

> **E-Governance Platform** · Digitizing civic grievance management with transparency and accountability

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite)](https://sqlite.org)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python)](https://python.org)
[![Tests](https://img.shields.io/badge/Tests-31%20Unit%20Tests-success)](./backend/tests/)

---

## 📋 Problem Statement

Government bodies receive large volumes of public complaints related to civic issues — water supply, electricity, sanitation, and infrastructure. Most existing systems are manual or poorly digitized, leading to delayed responses, lack of transparency, and inefficient tracking.

SmartGov provides a **centralized, API-driven digital grievance redressal platform** that enables citizens to register complaints, track status in real-time, and allows administrators to manage issues with accountability and analytics.

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| 🔐 **Role-Based Auth** | JWT-secured auth with Citizen, Admin, Department Staff roles |
| 📝 **Complaint Registration** | Easy form-based complaint submission with categories |
| 📡 **Real-Time Tracking** | Timeline-based status updates from submission to resolution |
| 📊 **Analytics Dashboard** | Charts for trends, resolution rate, department performance |
| 🔔 **Smart Notifications** | Real-time alerts on status changes |
| ⭐ **Citizen Feedback** | Rating system for resolved complaints |
| 👥 **User Management** | Admin panel to manage all users and staff |

---

## 🏗️ Architecture

```
Smart Public Complaint/
├── backend/                    # FastAPI Python Backend
│   ├── main.py                 # Main app with all API routes
│   ├── database.py             # SQLite DB setup & initialization
│   ├── auth.py                 # JWT auth & password hashing
│   ├── requirements.txt        # Python dependencies
│   ├── tests/
│   │   └── test_system.py      # 31 unit & integration tests
│   └── uploads/                # Complaint attachments
│
├── frontend/                   # Vanilla HTML/CSS/JS Frontend
│   ├── index.html              # Landing page
│   ├── login.html              # Login (Citizen/Admin/Staff)
│   ├── register.html           # Registration with role selection
│   ├── css/
│   │   └── styles.css          # Complete design system
│   ├── js/
│   │   └── app.js              # API client & utilities
│   ├── citizen/
│   │   ├── dashboard.html      # Citizen dashboard
│   │   ├── submit.html         # Submit new complaint
│   │   └── my-complaints.html  # View all complaints
│   └── admin/
│       ├── dashboard.html      # Admin analytics dashboard
│       └── complaints.html     # Manage all complaints
│
└── README.md
```

### Architecture Diagram

```
  ┌─────────────────────────────────────────────────────────┐
  │                    CLIENT (Browser)                      │
  │  ┌───────────┐  ┌──────────────┐  ┌────────────────┐   │
  │  │  Citizen  │  │    Admin     │  │ Dept. Staff    │   │
  │  │  Portal   │  │  Dashboard   │  │    Panel       │   │
  │  └─────┬─────┘  └──────┬───────┘  └───────┬────────┘   │
  └────────│───────────────│──────────────────│─────────────┘
           │               │                  │
           └───────────────▼──────────────────┘
                     HTTP/REST API
           ┌─────────────────────────────────────┐
           │         FastAPI Backend              │
           │  ┌────────────────────────────────┐  │
           │  │        API Routes              │  │
           │  │  /auth  /complaints  /analytics│  │
           │  │  /admin  /notifications        │  │
           │  └───────────────┬────────────────┘  │
           │                  │                   │
           │  ┌───────────────▼────────────────┐  │
           │  │         SQLite Database        │  │
           │  │  users | complaints | timeline │  │
           │  │  feedback | notifications      │  │
           │  └────────────────────────────────┘  │
           └─────────────────────────────────────┘
```

---

## 🚀 REST API Endpoints (10+)

### Authentication
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/auth/register` | Register new user | ❌ Public |
| `POST` | `/api/auth/login` | Login & get JWT token | ❌ Public |
| `GET` | `/api/auth/me` | Get current user profile | ✅ Required |

### Complaints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `POST` | `/api/complaints` | Submit new complaint | ✅ Citizen |
| `GET` | `/api/complaints` | List complaints (role-filtered) | ✅ Any |
| `GET` | `/api/complaints/{id}` | Get complaint + timeline | ✅ Any |
| `PUT` | `/api/complaints/{id}/status` | Update status | ✅ Admin/Staff |
| `POST` | `/api/complaints/{id}/feedback` | Submit feedback | ✅ Citizen |
| `POST` | `/api/complaints/{id}/upload` | Upload attachment | ✅ Any |

### Analytics & Admin
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/api/analytics/dashboard` | Full analytics data | ✅ Admin/Staff |
| `GET` | `/api/admin/users` | List all users | ✅ Admin |
| `GET` | `/api/admin/staff` | List staff members | ✅ Admin/Staff |
| `GET` | `/api/notifications` | Get user notifications | ✅ Any |
| `PUT` | `/api/notifications/{id}/read` | Mark notification read | ✅ Any |
| `GET` | `/api/health` | Health check | ❌ Public |

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- pip

### 1. Clone & Setup

```bash
# Clone the repository
git clone <repo-url>
cd "Smart Public Complaint"

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Run the Backend Server

```bash
cd backend
python main.py
```

Server starts at **http://localhost:8000**

API Documentation: **http://localhost:8000/api/docs**

### 3. Access the Application

Open your browser and navigate to: **http://localhost:8000**

Or open `frontend/index.html` directly in your browser.

### 4. Run Tests

```bash
cd backend
pytest tests/test_system.py -v
```

---

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| 👤 Citizen | `citizen@demo.in` | `Citizen@123` |
| 🛡️ Admin | `admin@smartgov.in` | `Admin@123` |
| ⚙️ Water Staff | `water@smartgov.in` | `Staff@123` |
| ⚡ Electricity | `electric@smartgov.in` | `Staff@123` |
| 🗑️ Sanitation | `sanitation@smartgov.in` | `Staff@123` |

---

## 🧪 Tests Overview

**31 Unit & Integration Tests** covering:

| Test Group | Tests | Description |
|------------|-------|-------------|
| Authentication | 10 | Register, login, token validation, access control |
| Complaints | 8 | Submit, list, filter, get detail, edge cases |
| Status & Admin | 9 | Status update, role checks, analytics, notifications |
| Utility Functions | 4 | Password hashing, token crypto, complaint numbers |
| Full Lifecycle | 1 | End-to-end: Submit → Acknowledge → Resolve → Feedback |

Run tests:
```bash
pytest tests/test_system.py -v --tb=short
```

---

## 🎨 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | **Python + FastAPI** |
| Database | **SQLite** (no external DB needed) |
| Auth | **HMAC-signed JWT-like tokens** |
| Frontend | **Vanilla HTML + CSS + JavaScript** |
| Styling | **Custom Dark Design System** |
| Testing | **pytest + httpx (TestClient)** |

---

## 📊 Judging Rubric Alignment

| Criteria | Implementation |
|----------|---------------|
| **Innovation** | Real-time notifications, step tracker, analytics charts, role-based UX |
| **Technical Depth** | FastAPI, RBAC JWT, SQLite, 10+ endpoints, 31 tests |
| **API Design** | RESTful, versioned `/api/`, proper HTTP codes, documented |
| **Testing** | 31 tests: unit + integration + lifecycle workflow |
| **UI/UX** | Dark glassmorphism design, responsive, animations, premium |
| **Real-World Impact** | Actual civic issue workflow modeled accurately |

---

## 🌿 Git Branch Strategy

```
main          ← Production-ready code
dev           ← Integration branch
feature/auth  ← Authentication features
feature/api   ← REST API endpoints
feature/ui    ← Frontend development
feature/tests ← Test suite
```

---

## 👥 Team

Smart Public Complaint & Grievance Redressal System  
Built for the E-Governance Innovation Hackathon 2024

---

*"Making civic engagement simple, transparent, and accountable."*
