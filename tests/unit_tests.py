import json
import pytest
from app import create_app
from app.models.user import User
from app.models.employee_profile import EmployeeProfile
from werkzeug.security import generate_password_hash
import uuid 

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


def test_create_user_as_admin(client):
    user_model = User()   
    profile_model = EmployeeProfile()

    if user_model.get_by_email("testadmin@example.com"):
        user_model.hard_delete_by_email("testadmin@example.com")
    if user_model.get_by_email("testemployee@example.com"):
        user_model.hard_delete_by_email("testemployee@example.com")

    user_model.add(
        name="Test Admin",
        email="testadmin@example.com",
        phone="9999999999",
        department="HR",
        role="Admin",
        password_hash=generate_password_hash("AdminPassword123")
    )

    profile_data = {
        "personal_details": {
            "first_name": "Jane",
            "middle_name": "K",
            "last_name": "Doe",
            "dob": "1992-05-10",
            "gender": "Female"
        },
        "contact_details": {
            "email": "testadmin@example.com",
            "phone": "2223334444",
            "address": "456 Main Street"
        },
        "emergency_contacts": [],
        "dependents": [],
        "job_details": {},
        "salary_details": {},
        "report_to": {},
        "qualifications": []
    }

    user = user_model.get_by_email("testadmin@example.com")
    profile_model.create_profile(user['employee_id'], profile_data)

    # Log in as admin to get token
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    assert login_res.status_code == 200, f"Admin login failed: {login_res.get_json()}"
    data = login_res.get_json()
    token = data['access_token']

#     user_model = User()

    # Create new user
    response = client.post('/users',
        json={
            "name": "Create User as Admin",
            "email": "testemployee@example.com",  
            "phone": "1234567899",
            "department": "IT",
            "role": "Employee",
            "password": "Password123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    
#     # Clean up created user after test
#     if (user := user_model.get_by_email("testemployee@example.com")):
        # user_model.hard_delete_by_email("testemployee@example.com")

def test_login_success(client):
    payload = {
        "email": "testemployee@example.com",
        "password": "Password123"
    }
    response = client.post('/login', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    data = response.get_json()
    assert "access_token" in data, "access_token missing in response"
    assert data["message"] == "Login successful"

def test_login_failure(client):
    payload = {
        "email": "testemployee@example.com",
        "password": "WrongPassword"
    }
    response = client.post('/login', data=json.dumps(payload), content_type='application/json')
    assert response.status_code == 401, f"Expected 401 Unauthorized but got {response.status_code}"
    data = response.get_json()
    assert "error" in data, "error message missing in response"

def test_get_all_users(client):
    response = client.get('/users')
    assert response.status_code == 200, f"Expected 200 OK but got {response.status_code}"
    users = response.get_json()
    assert isinstance(users, list), "Expected response to be a list"


def test_employee_cannot_delete_user(client):
    # Login as employee user
    login_res = client.post('/login', json={
        "email": "testemployee@example.com",
        "password": "Password123"
    })
    
    assert login_res.status_code == 200, f"Employee login failed: {login_res.get_json()}"
    data = login_res.get_json()
    token = data['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test employee user should exist for deletion test"
    emp_id = user['employee_id']

    response = client.delete(f'/users/{emp_id}',headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403, f"Expected 403 Forbidden but got {response.status_code}"
    assert response.get_json()["error"] == "Unauthorized access"

def test_update_user_as_employee(client):
    # Employee login
    login_res = client.post('/login', json={
        "email": "testemployee@example.com",
        "password": "Password123"
    })
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test user should exist before update"

    emp_id = user['employee_id']

    # Attempt to update user details (should be forbidden if role restrictions exist)
    update_data = {
        "name": "Update User as Employee",
        "email": 'testemployee@example.com',
        "role": "Employee",
        "password": "Password123",
        "department": "Finance",
        "status": "Active",
        "phone": "4445556666"
    }
    response = client.put(f'/users/{emp_id}',
                          json=update_data,
                          headers={"Authorization": f"Bearer {token}"})
    # Expect 403 Forbidden or similar if employees can't update others
    assert response.status_code in [403, 401]

def test_update_user_invalid_data(client):
    # Admin login
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test user should exist before update"

    emp_id = user['employee_id']

    # Update with invalid data (e.g., invalid email format)
    invalid_data = {
        "email": "not-an-email",
        "name": "User",
        "role": "Employee",
        "password": "Password123",
        "department": "Finance",
        "status": "Active",
        "phone": "4445556666"
    }
    response = client.put(f'/users/{emp_id}',
                          json=invalid_data,
                          headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    assert "email" in data["errors"]
    assert data["errors"]["email"] == ["Not a valid email address."]
    

def test_create_user_missing_fields(client):
    # Admin login
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test user should exist before update"

    # Missing required 'email' field
    incomplete_user = {
        "name": "Incomplete User",
        "phone": "1234567890",
        # "email" is missing
        "department": "IT",
        "role": "Employee",
        "password": "Password123"
    }
    response = client.post('/users', json=incomplete_user,
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    assert "email" in data["errors"]
    assert data["errors"]["email"] == ["Missing data for required field."]

def test_create_user_invalid_email(client):
    # Admin login
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']
    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test user should exist before update"

    invalid_email_user = {
        "name": "Invalid Email User",
        "email": "invalid-email-format",
        "phone": "1234567890",
        "department": "IT",
        "role": "Employee",
        "password": "Password123"
    }
    response = client.post('/users', json=invalid_email_user,
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    data = response.get_json()
    assert "errors" in data
    assert "email" in data["errors"]
    assert data["errors"]["email"] == ["Not a valid email address."]

def test_create_user_duplicate_email(client):
    # Admin login
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })

    token = login_res.get_json()['access_token']
    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test user should exist before update"

    new_user = {
        "name": "New Duplicate",
        "email": "testemployee@example.com",
        "phone": "1234567890",
        "department": "IT",
        "role": "Employee",
        "password": "Password123"
    }
    response = client.post('/users', json=new_user,
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    data = response.get_json()
    assert isinstance(data, list)
    assert "error" in data[0]
    assert data[0]["error"] == "User with this email already exists."


def test_access_protected_endpoint_without_token(client):
    payload = {
        "name": "User",
        "email": "testemployee@example.com",
        "phone": "1234567890",
        "department": "IT",
        "role": "Employee",
        "password": "Password123"
    }

    response = client.post('/users', json=payload)  # Correct usage
    assert response.status_code == 401 


def test_access_protected_endpoint_with_malformed_token(client):
    headers = {"Authorization": "Bearer malformed.token.value"}
    payload = {
        "name": "User",
        "email": "testemployee@example.com",
        "phone": "1234567890",
        "department": "IT",
        "role": "Employee",
        "password": "Password123"
    }

    response = client.post('/users', json=payload, headers=headers) 
    assert response.status_code == 422  


def test_employee_access_admin_endpoint(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "testemployee@example.com",
        "password": "Password123"
    })
    token = login_res.get_json()['access_token']

    # Try to create a user (admin-only endpoint)
    new_user = {
        "name": "Forbidden User",
        "email": "forbidden@example.com",
        "phone": "1234567890",
        "department": "IT",
        "role": "Employee",
        "password": "Password123"
    }
    response = client.post('/users', json=new_user,
                           headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    data = response.get_json()
    assert "error" in data




def test_update_user_as_admin(client):
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test user should exist before update"

    emp_id = user['employee_id']
    update_data = {
        "name": "Update User as Admin",
        "email": 'testemployee@example.com',
        "role": "Employee",
        "password": "Password123",
        "phone": "1112223333",
        "department": "Finance",
        "status": "Active"
    }
    response = client.put(f'/users/{emp_id}',
                        json=update_data,
                        headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data and data["message"] == "User updated"
    # Clean up created user after test
    # if (user := user_model.get_by_email("testemployee@example.com")):
    #     user_model.hard_delete_by_email("testemployee@example.com")

def test_manual_attendance_request(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "testemployee@example.com",
        "password": "Password123"
    })
    token = login_res.get_json()['access_token']

    payload = {
        "date": "2024-06-25",
        "punch_in": "09:00",
        "punch_out": "17:00",
        "reason": "Missed punch due to network error"
    }

    res = client.post('/attendance/manual', json=payload,
                      headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 201
    assert res.get_json()["message"] == "Manual attendance request submitted"

def test_admin_get_pending_requests(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    res = client.get('/attendance/requests', headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_get_my_attendance_records(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "testemployee@example.com",
        "password": "Password123"
    })
    token = login_res.get_json()['access_token']

    res = client.get('/attendance/my-records?start_date=2024-06-01&end_date=2024-06-30',
                     headers={"Authorization": f"Bearer {token}"})
    
    assert res.status_code == 200
    assert isinstance(res.get_json(), list)

def test_soft_delete_user_sets_status_to_inactive(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    # assert user is not None
    emp_id = user['employee_id']

    res = client.put(f'/users/{emp_id}/status', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    updated = user_model.get_by_employee_id(emp_id)
    assert updated['status'] == 'Inactive'

def test_create_user_email_case_insensitive_duplicate(client):
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None

    # Attempt to create duplicate with different case
    payload = {
        "name": "Duplicate Email",
        "email": "TESTEMPLOYEE@EXAMPLE.COM",  # same as existing but uppercase
        "phone": "1234567890",
        "department": "IT",
        "role": "Employee",
        "password": "Password123"
    }
    res = client.post('/users', json=payload,
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 400


def test_delete_user_as_admin(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    assert login_res.status_code == 200, f"Admin login failed: {login_res.get_json()}"
    data = login_res.get_json()
    token = data['access_token']

    user_model = User()
    user = user_model.get_by_email("testemployee@example.com")
    assert user is not None, "Test employee user should exist for deletion test"
    emp_id = user['employee_id']
    response = client.delete(f'/users/{emp_id}',headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["message"] == "User deleted"


def test_profile_deleted_when_user_deleted(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    # Create a new user
    new_email = "deletetest@example.com"
    user_model = User()
    profile_model = EmployeeProfile()

    if user_model.get_by_email(new_email):
        user_model.hard_delete_by_email(new_email)

    create_res = client.post('/users',
        json={
            "name": "Delete Test",
            "email": new_email,
            "phone": "9998887777",
            "department": "IT",
            "role": "Employee",
            "password": "Password123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert create_res.status_code == 201
    employee_id = create_res.get_json()["id"]

    # Make sure profile was created
    profile = profile_model.get_by_employee_id(employee_id)
    assert profile is not None, "Profile should exist before deletion"

    # Now delete the user
    delete_res = client.delete(f'/users/{employee_id}', headers={"Authorization": f"Bearer {token}"})
    assert delete_res.status_code == 200
    assert delete_res.get_json()["message"] == "User deleted"

    # Verify profile is deleted
    profile = profile_model.get_by_employee_id(employee_id)
    assert profile is None, "Profile should be deleted when user is deleted"




def test_reset_password_invalid_token(client):
    payload = {
        "token": "nonexistent-token",
        "new_password": "NewPassword123"
    }
    res = client.post("/reset-password", json=payload)
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_admin_approve_attendance(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    # Fetch a pending request first
    res = client.get('/attendance/requests', headers={"Authorization": f"Bearer {token}"})
    
    if pending := res.get_json():
        record_id = pending[0]["id"]
        approve_res = client.put(f"/attendance/approve/{record_id}",
                                 headers={"Authorization": f"Bearer {token}"})
        assert approve_res.status_code == 200
        assert approve_res.get_json()["message"] == "Attendance request approved"
    else:
        pytest.skip("No pending requests to approve")


def test_admin_reject_attendance(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']

    res = client.get('/attendance/requests', headers={"Authorization": f"Bearer {token}"})
    pending = res.get_json()
    
    if pending:
        record_id = pending[0]["id"]
        reject_payload = {"rejection_reason": "Time mismatch"}
        reject_res = client.put(f"/attendance/reject/{record_id}",
                                json=reject_payload,
                                headers={"Authorization": f"Bearer {token}"})
        assert reject_res.status_code == 200
        assert reject_res.get_json()["message"] == "Attendance request rejected"
    # else:
    #     pytest.skip("No pending requests to reject")



