"""
Unit Tests for Smart Public Complaint & Grievance Redressal System
Tests cover: Authentication, Complaint submission, Status updates, Analytics
Run with: pytest tests/ -v
"""
import sys
import os
import json
import time
import pytest
import hashlib

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

# Use an in-memory / separate test DB
os.environ["TESTING"] = "1"
TEST_DB = os.path.join(os.path.dirname(__file__), "test_complaints.db")

# Patch DB path before importing app
import database
database.DB_PATH = TEST_DB

from main import app
from database import init_db, get_db
from auth import hash_password, verify_password, create_token, verify_token, generate_complaint_number

client = TestClient(app)


# ─── Fixtures ─────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True, scope="module")
def setup_test_db():
    """Setup fresh test database for all tests"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db()
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


@pytest.fixture(scope="module")
def citizen_token():
    """Get auth token for demo citizen"""
    resp = client.post("/api/auth/login", json={
        "email": "citizen@demo.in",
        "password": "Citizen@123"
    })
    assert resp.status_code == 200
    return resp.json()["token"]


@pytest.fixture(scope="module")
def admin_token():
    """Get auth token for admin"""
    resp = client.post("/api/auth/login", json={
        "email": "admin@smartgov.in",
        "password": "Admin@123"
    })
    assert resp.status_code == 200
    return resp.json()["token"]


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 1: Authentication Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestAuthentication:

    def test_01_health_check(self):
        """Test API health check endpoint"""
        resp = client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_02_register_new_citizen(self):
        """Test citizen registration with valid data"""
        resp = client.post("/api/auth/register", json={
            "full_name": "Test Citizen One",
            "email": "testcitizen1@test.com",
            "phone": "9876543001",
            "password": "Test@1234",
            "role": "citizen"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["role"] == "citizen"
        assert data["user"]["email"] == "testcitizen1@test.com"

    def test_03_register_duplicate_email_fails(self):
        """Test that registering with an existing email returns 409"""
        resp = client.post("/api/auth/register", json={
            "full_name": "Duplicate User",
            "email": "admin@smartgov.in",  # already exists
            "phone": "9000000099",
            "password": "Test@1234",
            "role": "citizen"
        })
        assert resp.status_code == 409
        assert "already registered" in resp.json()["detail"].lower()

    def test_04_register_weak_password_fails(self):
        """Test that short password is rejected"""
        resp = client.post("/api/auth/register", json={
            "full_name": "Weak Pass User",
            "email": "weakpass@test.com",
            "phone": "9000000098",
            "password": "123",  # too short
            "role": "citizen"
        })
        assert resp.status_code == 400
        assert "password" in resp.json()["detail"].lower()

    def test_05_login_valid_credentials(self):
        """Test login with valid credentials returns token"""
        resp = client.post("/api/auth/login", json={
            "email": "admin@smartgov.in",
            "password": "Admin@123"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["role"] == "admin"

    def test_06_login_invalid_password_fails(self):
        """Test login with wrong password returns 401"""
        resp = client.post("/api/auth/login", json={
            "email": "admin@smartgov.in",
            "password": "WrongPassword"
        })
        assert resp.status_code == 401
        assert "invalid" in resp.json()["detail"].lower()

    def test_07_login_nonexistent_email_fails(self):
        """Test login with non-existent email returns 401"""
        resp = client.post("/api/auth/login", json={
            "email": "nobody@nowhere.com",
            "password": "Test@1234"
        })
        assert resp.status_code == 401

    def test_08_get_profile_with_valid_token(self, citizen_token):
        """Test get current user profile with valid token"""
        resp = client.get("/api/auth/me", headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["user"]["email"] == "citizen@demo.in"
        assert data["user"]["role"] == "citizen"

    def test_09_get_profile_without_token_fails(self):
        """Test accessing protected endpoint without token fails"""
        resp = client.get("/api/auth/me")
        assert resp.status_code == 422  # Missing header

    def test_10_get_profile_invalid_token_fails(self):
        """Test accessing protected endpoint with invalid token fails"""
        resp = client.get("/api/auth/me", headers={"authorization": "Bearer invalidtoken123"})
        assert resp.status_code == 401


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 2: Complaint Submission & Retrieval Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestComplaints:

    @pytest.fixture(scope="class")
    def submitted_complaint_id(self, citizen_token):
        """Submit a test complaint and return its ID"""
        resp = client.post("/api/complaints", json={
            "title": "Water supply disrupted for 3 days",
            "description": "No water supply in our area since Monday. Pipes seem broken.",
            "category": "water",
            "department": "Water Supply",
            "location": "Sector 12, Block B, Near Main Market",
            "priority": "high"
        }, headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        return resp.json()["complaint_id"]

    def test_11_submit_valid_complaint(self, citizen_token):
        """Test submitting a valid complaint"""
        resp = client.post("/api/complaints", json={
            "title": "Street light not working",
            "description": "Multiple street lights on Highway 16 have been out for a week.",
            "category": "electricity",
            "department": "Electricity",
            "location": "Highway 16, Near Police Station",
            "priority": "medium"
        }, headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "complaint_number" in data
        assert data["complaint_number"].startswith("COMP-")
        assert "complaint_id" in data

    def test_12_submit_complaint_invalid_category_fails(self, citizen_token):
        """Test that invalid category is rejected"""
        resp = client.post("/api/complaints", json={
            "title": "Test complaint",
            "description": "Test description",
            "category": "invalid_category",
            "department": "Test Dept",
            "location": "Test Location",
            "priority": "medium"
        }, headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 400
        assert "category" in resp.json()["detail"].lower()

    def test_13_list_complaints_as_citizen(self, citizen_token):
        """Test citizen can list only their own complaints"""
        resp = client.get("/api/complaints", headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "complaints" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_14_list_complaints_as_admin(self, admin_token):
        """Test admin can list all complaints"""
        resp = client.get("/api/complaints", headers={"authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["total"] >= 1

    def test_15_list_complaints_with_status_filter(self, citizen_token):
        """Test filtering complaints by status"""
        resp = client.get("/api/complaints?status=submitted",
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        data = resp.json()
        for complaint in data["complaints"]:
            assert complaint["status"] == "submitted"

    def test_16_list_complaints_pagination(self, admin_token):
        """Test pagination in complaint listing"""
        resp = client.get("/api/complaints?page=1&limit=2",
                          headers={"authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["complaints"]) <= 2
        assert "total_pages" in data

    def test_17_get_specific_complaint(self, citizen_token, submitted_complaint_id):
        """Test getting a specific complaint with timeline"""
        resp = client.get(f"/api/complaints/{submitted_complaint_id}",
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "complaint" in data
        assert "timeline" in data
        assert len(data["timeline"]) >= 1

    def test_18_get_nonexistent_complaint_fails(self, citizen_token):
        """Test getting a non-existent complaint returns 404"""
        resp = client.get("/api/complaints/99999",
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 404


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 3: Status Update & Admin Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestStatusAndAdmin:

    @pytest.fixture(scope="class")
    def complaint_for_update(self, citizen_token):
        """Get a complaint ID to update"""
        resp = client.get("/api/complaints?limit=1",
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        complaints = resp.json()["complaints"]
        assert len(complaints) > 0
        return complaints[0]["id"]

    def test_19_admin_update_complaint_status(self, admin_token, complaint_for_update):
        """Test admin can update complaint status"""
        resp = client.put(f"/api/complaints/{complaint_for_update}/status",
                          json={"status": "acknowledged", "notes": "Received and assigned to team"},
                          headers={"authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True

    def test_20_citizen_cannot_update_status(self, citizen_token, complaint_for_update):
        """Test citizen cannot update complaint status"""
        resp = client.put(f"/api/complaints/{complaint_for_update}/status",
                          json={"status": "resolved", "notes": "Self-resolved"},
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 403
        assert "access denied" in resp.json()["detail"].lower()

    def test_21_invalid_status_value_fails(self, admin_token, complaint_for_update):
        """Test invalid status value is rejected"""
        resp = client.put(f"/api/complaints/{complaint_for_update}/status",
                          json={"status": "magic_status"},
                          headers={"authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 400

    def test_22_admin_list_users(self, admin_token):
        """Test admin can list all users"""
        resp = client.get("/api/admin/users",
                          headers={"authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "users" in data
        assert data["total"] >= 5  # seeded users

    def test_23_citizen_cannot_access_admin_users(self, citizen_token):
        """Test citizen cannot access admin user list"""
        resp = client.get("/api/admin/users",
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 403

    def test_24_analytics_dashboard_for_admin(self, admin_token):
        """Test admin can access analytics dashboard"""
        resp = client.get("/api/analytics/dashboard",
                          headers={"authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "summary" in data
        assert "total_complaints" in data["summary"]
        assert "category_stats" in data
        assert "department_stats" in data
        assert "monthly_trend" in data

    def test_25_citizen_cannot_access_analytics(self, citizen_token):
        """Test citizen cannot access analytics dashboard"""
        resp = client.get("/api/analytics/dashboard",
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 403

    def test_26_notifications_for_citizen(self, citizen_token):
        """Test citizen can retrieve their notifications"""
        resp = client.get("/api/notifications",
                          headers={"authorization": f"Bearer {citizen_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "notifications" in data
        assert "unread_count" in data


# ═══════════════════════════════════════════════════════════════════════════════
# TEST GROUP 4: Utility Function Unit Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestUtilityFunctions:

    def test_27_password_hashing_correctness(self):
        """Test password hashing and verification"""
        password = "MySecurePassword@2024"
        hashed = hash_password(password)
        assert hashed != password  # Must be hashed
        assert len(hashed) == 64  # SHA-256 hex length
        assert verify_password(password, hashed) is True
        assert verify_password("WrongPassword", hashed) is False

    def test_28_token_creation_and_verification(self):
        """Test JWT-like token creation and verification"""
        token = create_token(42, "test@example.com", "citizen")
        assert token is not None
        assert "." in token

        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == 42
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "citizen"

    def test_29_invalid_token_returns_none(self):
        """Test that tampered or invalid tokens return None"""
        assert verify_token("invalid.token.here") is None
        assert verify_token("completelyinvalid") is None
        assert verify_token("") is None

    def test_30_complaint_number_uniqueness(self):
        """Test complaint numbers are unique"""
        numbers = set()
        for _ in range(10):
            num = generate_complaint_number()
            time.sleep(0.002)  # small delay
            numbers.add(num)
        assert all(n.startswith("COMP-") for n in numbers)

    def test_31_full_complaint_workflow(self, citizen_token, admin_token):
        """Test complete complaint lifecycle: submit -> acknowledge -> resolve -> feedback"""
        # Step 1: Submit
        submit_resp = client.post("/api/complaints", json={
            "title": "Garbage not collected for 5 days",
            "description": "Garbage collection has stopped completely in our colony.",
            "category": "sanitation",
            "department": "Sanitation",
            "location": "Green Park Colony, Lane 4",
            "priority": "high"
        }, headers={"authorization": f"Bearer {citizen_token}"})
        assert submit_resp.status_code == 200
        complaint_id = submit_resp.json()["complaint_id"]

        # Step 2: Acknowledge
        ack_resp = client.put(f"/api/complaints/{complaint_id}/status",
                              json={"status": "acknowledged", "notes": "Team dispatched"},
                              headers={"authorization": f"Bearer {admin_token}"})
        assert ack_resp.status_code == 200

        # Step 3: In Progress
        prog_resp = client.put(f"/api/complaints/{complaint_id}/status",
                               json={"status": "in_progress", "notes": "Cleaning crew on site"},
                               headers={"authorization": f"Bearer {admin_token}"})
        assert prog_resp.status_code == 200

        # Step 4: Resolve
        res_resp = client.put(f"/api/complaints/{complaint_id}/status",
                              json={"status": "resolved", "notes": "Garbage collected, schedule restored"},
                              headers={"authorization": f"Bearer {admin_token}"})
        assert res_resp.status_code == 200

        # Step 5: Check timeline has 4 entries
        details_resp = client.get(f"/api/complaints/{complaint_id}",
                                  headers={"authorization": f"Bearer {citizen_token}"})
        assert details_resp.status_code == 200
        timeline = details_resp.json()["timeline"]
        assert len(timeline) >= 4

        # Step 6: Submit feedback
        feedback_resp = client.post(f"/api/complaints/{complaint_id}/feedback",
                                    json={"complaint_id": complaint_id, "rating": 4,
                                          "comment": "Quick resolution, thank you!"},
                                    headers={"authorization": f"Bearer {citizen_token}"})
        assert feedback_resp.status_code == 200

        print("\n✅ Full complaint lifecycle test passed!")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
