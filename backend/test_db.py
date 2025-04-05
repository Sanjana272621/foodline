# test_db.py
import os
import sys
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import pytest
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our app modules
from main import app
from database import Base, get_db
from models import User, Gathering, Claim
from crud import pwd_context

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_food_donation.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use our test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create a test client
client = TestClient(app)

# Test data
test_donor = {
    "name": "Test Donor",
    "email": "donor@example.com",
    "password": "password123",
    "user_type": "donor",
    "latitude": 37.7749,
    "longitude": -122.4194
}

test_recipient = {
    "name": "Test Recipient",
    "email": "recipient@example.com",
    "password": "password123",
    "user_type": "recipient",
    "latitude": 37.7833,
    "longitude": -122.4167
}

test_gathering = {
    "food_details": "Leftover wedding cake and sandwiches",
    "available_from": (datetime.now() - timedelta(hours=1)).isoformat(),
    "available_to": (datetime.now() + timedelta(days=1)).isoformat(),
    "latitude": 37.7749,
    "longitude": -122.4194
}

# Setup and teardown
@pytest.fixture(scope="module")
def setup_database():
    # Create the database and tables
    Base.metadata.create_all(bind=engine)
    
    # Seed the database
    db = TestingSessionLocal()
    
    try:
        # Clear existing data
        db.query(Claim).delete()
        db.query(Gathering).delete()
        db.query(User).delete()
        
        # Create test users
        donor = User(
            name=test_donor["name"],
            email=test_donor["email"],
            password=pwd_context.hash(test_donor["password"]),
            user_type=test_donor["user_type"],
            latitude=test_donor["latitude"],
            longitude=test_donor["longitude"]
        )
        
        recipient = User(
            name=test_recipient["name"],
            email=test_recipient["email"],
            password=pwd_context.hash(test_recipient["password"]),
            user_type=test_recipient["user_type"],
            latitude=test_recipient["latitude"],
            longitude=test_recipient["longitude"]
        )
        
        db.add(donor)
        db.add(recipient)
        db.commit()
        
        # Get the created user IDs
        donor = db.query(User).filter(User.email == test_donor["email"]).first()
        recipient = db.query(User).filter(User.email == test_recipient["email"]).first()
        
        # Create a gathering
        gathering = Gathering(
            user_id=donor.id,
            food_details=test_gathering["food_details"],
            available_from=datetime.fromisoformat(test_gathering["available_from"]),
            available_to=datetime.fromisoformat(test_gathering["available_to"]),
            latitude=test_gathering["latitude"],
            longitude=test_gathering["longitude"],
            is_taken=False
        )
        
        db.add(gathering)
        db.commit()
        
    finally:
        db.close()
    
    yield
    
    # Teardown - remove test database
    os.remove("./test_food_donation.db")

# Test functions
def test_register_user(setup_database):
    # Test registration with new email
    new_user = {
        "name": "New User",
        "email": "new@example.com",
        "password": "password123",
        "user_type": "recipient",
        "latitude": 37.7,
        "longitude": -122.4
    }
    
    response = client.post("/users/register", json=new_user)
    assert response.status_code == 200
    assert response.json()["email"] == new_user["email"]
    
    # Test registration with existing email
    response = client.post("/users/register", json=test_donor)
    assert response.status_code == 400

def test_login(setup_database):
    # Test valid login
    response = client.post(
        "/users/token",
        data={"username": test_donor["email"], "password": test_donor["password"]}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # Test invalid password
    response = client.post(
        "/users/token",
        data={"username": test_donor["email"], "password": "wrong_password"}
    )
    assert response.status_code == 401
    
    # Test non-existent user
    response = client.post(
        "/users/token",
        data={"username": "nonexistent@example.com", "password": "password123"}
    )
    assert response.status_code == 401

def test_get_profile(setup_database):
    # Login to get token
    response = client.post(
        "/users/token",
        data={"username": test_donor["email"], "password": test_donor["password"]}
    )
    token = response.json()["access_token"]
    
    # Get user profile with token
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_donor["email"]

def test_create_gathering(setup_database):
    # Login as donor
    response = client.post(
        "/users/token",
        data={"username": test_donor["email"], "password": test_donor["password"]}
    )
    token = response.json()["access_token"]
    
    # Create a gathering
    new_gathering = {
        "food_details": "Fresh pizzas from party",
        "available_from": (datetime.now() - timedelta(hours=1)).isoformat(),
        "available_to": (datetime.now() + timedelta(days=1)).isoformat(),
        "latitude": 37.77,
        "longitude": -122.41
    }
    
    response = client.post(
        "/gatherings/",
        json=new_gathering,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["food_details"] == new_gathering["food_details"]
    
    # Try to create a gathering as recipient (should fail)
    response = client.post(
        "/users/token",
        data={"username": test_recipient["email"], "password": test_recipient["password"]}
    )
    token = response.json()["access_token"]
    
    response = client.post(
        "/gatherings/",
        json=new_gathering,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_view_gatherings(setup_database):
    # Login as recipient
    response = client.post(
        "/users/token",
        data={"username": test_recipient["email"], "password": test_recipient["password"]}
    )
    token = response.json()["access_token"]
    
    # View available gatherings
    response = client.get(
        "/gatherings/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert len(response.json()) > 0
    
    # View nearby gatherings
    response = client.get(
        f"/gatherings/nearby?latitude={test_recipient['latitude']}&longitude={test_recipient['longitude']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    
    # Try to view gatherings as donor (should fail)
    response = client.post(
        "/users/token",
        data={"username": test_donor["email"], "password": test_donor["password"]}
    )
    token = response.json()["access_token"]
    
    response = client.get(
        "/gatherings/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_claim_flow(setup_database):
    # Login as recipient
    response = client.post(
        "/users/token",
        data={"username": test_recipient["email"], "password": test_recipient["password"]}
    )
    recipient_token = response.json()["access_token"]
    
    # Get available gatherings
    response = client.get(
        "/gatherings/",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    assert response.status_code == 200
    gatherings = response.json()
    assert len(gatherings) > 0
    
    # Claim a gathering
    claim_data = {
        "gathering_id": gatherings[0]["id"]
    }
    
    response = client.post(
        "/claims/",
        json=claim_data,
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    assert response.status_code == 200
    claim_id = response.json()["id"]
    
    # Verify gathering is now taken
    response = client.get(
        f"/gatherings/{gatherings[0]['id']}",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_taken"] == True
    
    # View recipient's claims
    response = client.get(
        "/claims/my-claims",
        headers={"Authorization": f"Bearer {recipient_token}"}
    )
    assert response.status_code == 200
    claims = response.json()
    assert len(claims) > 0
    
    # Login as donor
    response = client.post(
        "/users/token",
        data={"username": test_donor["email"], "password": test_donor["password"]}
    )
    donor_token = response.json()["access_token"]
    
    # Donor checks claims for their gatherings
    response = client.get(
        "/claims/for-my-gatherings",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    assert response.status_code == 200
    donor_claims = response.json()
    assert len(donor_claims) > 0
    
    # Update claim status to collected
    response = client.put(
        f"/claims/{claim_id}/status?status=collected",
        headers={"Authorization": f"Bearer {donor_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "collected"

def test_create_another_claim(setup_database):
    # Login as donor
    response = client.post(
        "/users/token",
        data={"username": test_donor["email"], "password": test_donor["password"]}
    )
    token = response.json()["access_token"]
    
    # Create a new gathering
    new_gathering = {
        "food_details": "Leftover birthday cake",
        "available_from": (datetime.now() - timedelta(hours=1)).isoformat(),
        "available_to": (datetime.now() + timedelta(days=1)).isoformat(),
        "latitude": 37.77,
        "longitude": -122.41
    }
    
    response = client.post(
        "/gatherings/",
        json=new_gathering,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    gathering_id = response.json()["id"]
    
    # Login as recipient
    response = client.post(
        "/users/token",
        data={"username": test_recipient["email"], "password": test_recipient["password"]}
    )
    token = response.json()["access_token"]
    
    # Claim the gathering
    claim_data = {
        "gathering_id": gathering_id
    }
    
    response = client.post(
        "/claims/",
        json=claim_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    claim_id = response.json()["id"]
    
    # Cancel the claim
    response = client.put(
        f"/claims/{claim_id}/status?status=cancelled",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"
    
    # Verify gathering is available again
    response = client.get(
        f"/gatherings/{gathering_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_taken"] == False

if __name__ == "__main__":
    # Run tests manually if not using pytest
    pytest.main(["-xvs", __file__])