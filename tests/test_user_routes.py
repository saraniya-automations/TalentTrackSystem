import json
import pytest
from app import create_app
from app.models.user import User
from werkzeug.security import generate_password_hash
import uuid 

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def setup_test_users():
    """
    Setup fixture to create an Employee and Admin user before tests,
    and clean up after tests.
    """
    user_model = User()

    # Employee user
    emp_email = "testemployee@example.com"
    if user_model.get_by_email(emp_email):
        user_model.hard_delete_by_email(emp_email)
    user_model.add(
        name="Test Employee",
        email=emp_email,
        phone="0000000000",
        department="QA",
        role="Employee",
        password_hash=generate_password_hash("Password123")
    )

    # Admin user
    admin_email = "testadmin@example.com"
    if user_model.get_by_email(admin_email):
        user_model.hard_delete_by_email(admin_email)
    user_model.add(
        name="Test Admin",
        email=admin_email,
        phone="9999999999",
        department="HR",
        role="Admin",
        password_hash=generate_password_hash("AdminPassword123")
    )

    yield  # Run the tests

    # Cleanup after tests
    if (user := user_model.get_by_email(emp_email)):
        user_model.hard_delete_by_email(user['id'])
    if (user := user_model.get_by_email(admin_email)):
        user_model.hard_delete_by_email(user['id'])

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

def test_create_user_as_admin(client):
    import uuid
    # Log in as admin to get token
    login_res = client.post('/login', json={
        "email": "testadmin@example.com",
        "password": "AdminPassword123"
    })
    assert login_res.status_code == 200, f"Admin login failed: {login_res.get_json()}"
    data = login_res.get_json()
    token = data['access_token']

    # # Generate a unique email using uuid
    # unique_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"

    user_model = User()

    # Create new user
    response = client.post('/users',
        json={
            "name": "New User",
            "email": "test_user@example.com",  
            "phone": "1234567899",
            "department": "IT",
            "role": "Employee",
            "password": "Password123"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 201
    
    # Clean up created user after test
    if (user := user_model.get_by_email("test_user@example.com")):
        user_model.hard_delete_by_email(user['employee_id'])

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
    emp_id = user['id']
    response = client.delete(f'/users/{emp_id}',headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["message"] == "User deleted"

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
    emp_id = user['id']

    response = client.delete(f'/users/{emp_id}',headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403, f"Expected 403 Forbidden but got {response.status_code}"
    assert response.get_json()["error"] == "Unauthorized access"

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
        "name": "New User",
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
        "name": "New User",
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
        "name": "New User",
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

