import json
import pytest
from app import create_app
from app.models.user import User
from app.models.employee_profile import EmployeeProfile
from werkzeug.security import generate_password_hash
import uuid 
from app.models.database import Database


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
#         user_model.hard_delete_by_email("testemployee@example.com")

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
    data = response.get_json()
    assert isinstance(data, dict), "Expected response to be a dictionary"
    assert 'items' in data, "Response should contain 'items' key"
    assert isinstance(data['items'], list), "'items' should be a list"
    for key in ['total', 'page', 'per_page', 'total_pages']:
        assert key in data, f"Missing pagination key: {key}"
    for user in data['items']:
        assert 'employee_id' in user, "Each user should have an employee_id"
        assert 'name' in user, "Each user should have a name"
        assert 'email' in user, "Each user should have an email"
        assert 'role' in user, "Each user should have a role"
        assert 'password_hash' not in user, "Password hash should not be exposed"
 

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
    assert isinstance(data, dict)
    assert 'error' in data
    assert data['error'] == "User with this email already exists."


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

def test_reset_password_invalid_token(client):
    payload = {
        "token": "nonexistent-token",
        "new_password": "NewPassword123"
    }
    res = client.post("/reset-password", json=payload)
    assert res.status_code == 400
    assert "error" in res.get_json()

def setup_test_users():
    user_model = User()
    db = Database()

    # Clean up test users
    for email in ["adminleave@example.com", "leaveuser@example.com"]:
        if user_model.get_by_email(email):
            user_model.hard_delete_by_email(email)

    # Create Admin
    admin_id, admin_emp_id = user_model.add(
        name="Admin User",
        email="adminleave@example.com",
        phone="9999999999",
        department="HR",
        role="Admin",
        password_hash=generate_password_hash("AdminPass123")
    )

    # Create Employee
    emp_id, emp_emp_id = user_model.add(
        name="Leave User",
        email="leaveuser@example.com",
        phone="1112223333",
        department="IT",
        role="Employee",
        password_hash=generate_password_hash("EmpPass123")
    )

    # Add leave balances
    db.conn.execute('''
        INSERT INTO leave_balances (employee_id, annual, casual, sick, maternity)
        VALUES (?, ?, ?, ?, ?)
    ''', (emp_emp_id, 5, 3, 2, 90))

    db.conn.execute('''
        INSERT INTO leave_balances (employee_id, annual, casual, sick, maternity)
        VALUES (?, ?, ?, ?, ?)
    ''', (admin_emp_id, 5, 3, 2, 90))

    db.conn.commit()

    return emp_emp_id, admin_emp_id

def test_apply_leave_and_check_balance(client):
    emp_emp_id, _ = setup_test_users()

    # Login as Employee
    login_res = client.post('/login', json={"email": "leaveuser@example.com", "password": "EmpPass123"})
    token = login_res.get_json()['access_token']

    # Check balance before
    res = client.get('/leave/balance', headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.get_json()['annual'] == 5

    # Apply leave
    apply = client.post('/leave/apply',
        json={"leave_type": "annual", "start_date": "2025-07-01", "end_date": "2025-07-02", "reason": "Personal"},
        headers={"Authorization": f"Bearer {token}"})
    assert apply.status_code == 201
    assert apply.get_json()['days'] == 2

    # Check balance after
    after = client.get('/leave/balance', headers={"Authorization": f"Bearer {token}"})
    assert after.status_code == 200
    assert after.get_json()['annual'] == 3  # 5 - 2

def test_admin_can_approve_employee_leave(client):
    emp_emp_id, admin_emp_id = setup_test_users()

    # Employee applies for leave
    emp_login = client.post('/login', json={"email": "leaveuser@example.com", "password": "EmpPass123"})
    emp_token = emp_login.get_json()['access_token']

    apply = client.post('/leave/apply',
        json={"leave_type": "casual", "start_date": "2025-07-03", "end_date": "2025-07-03", "reason": "Day off"},
        headers={"Authorization": f"Bearer {emp_token}"})
    leave_id = apply.get_json()['leave_id']

    # Admin logs in and approves
    admin_login = client.post('/login', json={"email": "adminleave@example.com", "password": "AdminPass123"})
    admin_token = admin_login.get_json()['access_token']

    approve = client.put(f'/leave/{leave_id}/status',
        json={"status": "Approved"},
        headers={"Authorization": f"Bearer {admin_token}"})
    assert approve.status_code == 200
    assert approve.get_json()['message'] == "Leave approved successfully."

def test_admin_cannot_approve_own_leave(client):
    _, admin_emp_id = setup_test_users()

    # Admin logs in and applies leave
    admin_login = client.post('/login', json={"email": "adminleave@example.com", "password": "AdminPass123"})
    admin_token = admin_login.get_json()['access_token']

    apply = client.post('/leave/apply',
        json={"leave_type": "sick", "start_date": "2025-07-05", "end_date": "2025-07-06", "reason": "Flu"},
        headers={"Authorization": f"Bearer {admin_token}"})
    leave_id = apply.get_json()['leave_id']

    # Admin tries to approve their own leave
    approve = client.put(f'/leave/{leave_id}/status',
        json={"status": "Approved"},
        headers={"Authorization": f"Bearer {admin_token}"})
    assert approve.status_code == 403
    assert "cannot approve their own" in approve.get_json()['error'].lower()

def test_employee_cannot_approve_leave(client):
    emp_emp_id, _ = setup_test_users()

    # Login as Employee
    emp_login = client.post('/login', json={"email": "leaveuser@example.com", "password": "EmpPass123"})
    emp_token = emp_login.get_json()['access_token']

    # Try to approve a leave (invalid permission)
    approve = client.put('/leave/999/status',
        json={"status": "Approved"},
        headers={"Authorization": f"Bearer {emp_token}"})
    assert approve.status_code == 403 or approve.status_code == 401

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

# def test_delete_user_as_admin(client):
    # Login as admin
    # login_res = client.post('/login', json={
    #     "email": "adminleave@example.com",
    #     "password": "AdminPass123"
    # })
    # assert login_res.status_code == 200, f"Admin login failed: {login_res.get_json()}"
    # data = login_res.get_json()
    # token = data['access_token']

    # # Create a new user
    # new_email = "deletetest1@example.com"
    # user_model = User()
    # profile_model = EmployeeProfile()

    # if user_model.get_by_email(new_email):
    #     user_model.hard_delete_by_email(new_email)

    # create_res = client.post('/users',
    #     json={
    #         "name": "Delete Test",
    #         "email": new_email,
    #         "phone": "9998887777",
    #         "department": "IT",
    #         "role": "Employee",
    #         "password": "Password123"
    #     },
    #     headers={"Authorization": f"Bearer {token}"}
    # )
    # assert create_res.status_code == 201
    # employee_id = create_res.get_json()["id"]

    # # Make sure profile was created
    # profile = profile_model.get_by_employee_id(employee_id)
    # assert profile is not None, "Profile should exist before deletion"

    # user_model = User()
    # user = user_model.get_by_email("leaveuser@example.com")
    # assert user is not None, "Test employee user should exist for deletion test"
    # emp_id = user['employee_id']
    # response = client.delete(f'/users/{emp_id}',headers={"Authorization": f"Bearer {token}"})
    # assert response.status_code == 200
    # assert response.get_json()["message"] == "User deleted"

def test_delete_user_as_admin(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "adminleave@example.com",
        "password": "AdminPass123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

    # Create and then delete the same user
    new_email = "deletetest1@example.com"
    user_model = User()
    profile_model = EmployeeProfile()

    # Cleanup if test failed previously
    if user_model.get_by_email(new_email):
        user_model.hard_delete_by_email(new_email)

    # Create new user
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

    # Verify profile exists
    profile = profile_model.get_by_employee_id(employee_id)
    assert profile is not None

    # Delete the user we just created
    response = client.delete(f'/users/{employee_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.get_json()["message"] == "User deleted"

    # Verify user is really deleted
    user = user_model.get_by_email(new_email)
    assert user is None

def test_profile_deleted_when_user_deleted(client):
     # Login as admin
    login_res = client.post('/login', json={
        "email": "adminleave@example.com",
        "password": "AdminPass123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

    # Create and then delete the same user
    new_email = "deletetest1@example.com"
    user_model = User()
    profile_model = EmployeeProfile()

    # Cleanup if test failed previously
    if user_model.get_by_email(new_email):
        user_model.hard_delete_by_email(new_email)

    # Create new user
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

#     # Make sure profile was created
    profile = profile_model.get_by_employee_id(employee_id)
    assert profile is not None, "Profile should exist before deletion"

    # Now delete the user
    delete_res = client.delete(f'/users/{employee_id}', headers={"Authorization": f"Bearer {token}"})
    assert delete_res.status_code == 200
    assert delete_res.get_json()["message"] == "User deleted"

    # Verify profile is deleted
    profile = profile_model.get_by_employee_id(employee_id)
    assert profile is None, "Profile should be deleted when user is deleted"

def test_inactive_user_cannot_login(client):
    email = "inactiveuser1@example.com"
    user_model = User()
    # Clean up if exists
    user = user_model.get_by_email(email)
    if user:
        user_model.hard_delete_by_email(user['email'])
    from app.service import user_service
    # Create user with status = Inactive via service
    user_service.create_user({
        "name": "Inactive User",
        "email": email,
        "phone": "0000000000",
        "department": "IT",
        "role": "Employee",
        "password": "SomePassword123",
        "status": "Inactive"
    })

    # Try to log in
    login_res = client.post('/login', json={
        "email": email,
        "password": "SomePassword123"
    })

    assert login_res.status_code == 403
    assert login_res.get_json()["error"] == "User account is inactive"

def test_add_salary_records_success(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "adminleave@example.com",
        "password": "AdminPass123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("leaveuser@example.com")
    assert user is not None, "Test employee user should exist for salary record test"
    emp_id = user['employee_id']

    # Add salary record
    salary_data = {
        "employee_id": emp_id,  # Use the actual employee ID
        "salary_month": "2025-06",
        "basic_salary": 5000,
        "bonus": 500,
        "deductions": 200,
        "currency": "NZD",
        "pay_frequency": "Monthly",
        "direct_deposit_amount": 5300
    }
    response = client.post('/salary/add',
        json=salary_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Debugging: Print the response if it fails
    if response.status_code != 201:
        print("Error response:", response.json)
    
    assert response.status_code == 201
    assert response.json['message'] == "Salary record added successfully"

def test_add_salary_record_unauthorized(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "leaveuser@example.com",
        "password": "EmpPass123"
    })
    assert login_res.status_code == 200
    employee_token = login_res.get_json()['access_token']
    employee_id = login_res.get_json()['employee_id']

    data = {
        "employee_id": employee_id,
        "salary_month": "2025-06",
        "basic_salary": 5000
    }
    response = client.post('/salary/add',
        json=data,
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 403 or response.status_code == 401

def test_view_my_salary_records(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "leaveuser@example.com",
        "password": "EmpPass123"
    })
    assert login_res.status_code == 200
    employee_token = login_res.get_json()['access_token']
    response = client.get('/salary/my-records',
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_view_my_salary_records_with_month(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "leaveuser@example.com",
        "password": "EmpPass123"
    })
    assert login_res.status_code == 200
    employee_token = login_res.get_json()['access_token']

    response = client.get('/salary/my-records?month=2025-06',
        headers={"Authorization": f"Bearer {employee_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json, (list, dict))

def test_employee_download_payslip(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "leaveuser@example.com",
        "password": "EmpPass123"
    })
    assert login_res.status_code == 200
    employee_token = login_res.get_json()['access_token']

    response = client.get(
        '/salary/my-records/payslip?month=2025-06',
        headers={"Authorization": f"Bearer {employee_token}"}
    )

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'

def test_admin_view_employee_salary_records(client):
    # Step 1: Login as admin
    login_res = client.post('/login', json={
        "email": "adminleave@example.com",
        "password": "AdminPass123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

    # Step 2: Get employee record
    user_model = User()
    user = user_model.get_by_email("leaveuser@example.com")
    assert user is not None
    emp_id = user['employee_id']

    # Step 3: View salary records for that employee for a specific month
    month = "2025-06"
    res_with_month = client.get(
        f'/salary/employee/{emp_id}?month={month}',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_with_month.status_code == 200
    assert "salary_month" in res_with_month.get_json() or "message" in res_with_month.get_json()

    # Step 4: View all salary records for that employee
    res_all = client.get(
        f'/salary/employee/{emp_id}',
        headers={"Authorization": f"Bearer {token}"}
    )
    assert res_all.status_code == 200
    assert isinstance(res_all.get_json(), list)

def test_export_salary_records_pdf_success(client):
    # Step 1: Login as admin
    login_res = client.post('/login', json={
        "email": "adminleave@example.com",
        "password": "AdminPass123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

    user_model = User()
    user = user_model.get_by_email("leaveuser@example.com")
    assert user is not None
    emp_id = user['employee_id']

    params = {
        'month': '2025-06',
        'employee_id': emp_id
    }

    # Step 2: Call the PDF export route with optional filters
    response = client.get(
        '/salary/export-pdf',
        query_string=params,  # Safer than string concatenation
        headers={"Authorization": f"Bearer {token}"}
    )

    # Step 3: Check response
    assert response.status_code == 200
    assert response.mimetype == 'application/pdf'
    assert 'attachment; filename=salary_records_export.pdf' in response.headers.get('Content-Disposition', '')

    # Optional: check if content is not empty
    assert response.data[:4] == b'%PDF'  # PDF files start with "%PDF"

def test_export_salary_records_pdf_unauthorized(client):
    # No token provided
    response = client.get('/salary/export-pdf?month=2025-06&employee_id=EMP002')

    assert response.status_code == 401
    assert b"Missing Authorization Header" in response.data or b"Token" in response.data

def test_export_salary_records_pdf_no_data_found(client):
    # Login as admin
    login_res = client.post('/login', json={
        "email": "adminleave@example.com",
        "password": "AdminPass123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

     # Call with invalid filters (e.g., no records for the given month or employee)
    response = client.get(
        '/salary/export-pdf?month=2099-01&employee_id=NONEXISTENT',
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.get_json()['message'] == "No records found"

def test_salary_countdown_success(client):
    login_res = client.post('/login', json={
        "email": "leaveuser@example.com",
        "password": "EmpPass123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

    response = client.get('/salary/countdown', headers={
        "Authorization": f"Bearer {token}"
    })

    assert response.status_code == 200
    data = response.get_json()

    assert "days_remaining" in data
    assert "expected_amount" in data
    assert "pay_frequency" in data

def test_search_attendance_by_name_and_period(client):
    # Admin login
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    assert login_res.status_code == 200
    token = login_res.get_json()['access_token']

    # Sample search query
    response = client.get(
        '/attendance/search?name=update&start_date=2024-06-01&end_date=2024-06-30',
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.get_json()

    assert isinstance(data, list)
    if data:
        for record in data:
            assert "employee_id" in record
            assert "date" in record
            assert "status" in record
            assert "name" in record

def test_manual_attendance_request_admin(client):
    # Login as employee
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    token = login_res.get_json()['access_token']
    payload = {
        "date": "2025-06-25",
        "punch_in": "09:30",
        "punch_out": "17:30",
        "reason": "Missed punch due to lost card"
    }
    res = client.post('/attendance/manual', json=payload,
                      headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    assert res.get_json()["message"] == "Manual attendance request submitted"

    # Login as admin
    login_res = client.post('/login', json={
        "email": "adminleave@example.com",
        "password": "AdminPass123"
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

