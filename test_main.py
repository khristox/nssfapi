from fastapi.testclient import TestClient
from main import app
from sqlmodel import SQLModel, Session, create_engine
import uuid
import pytest

# Use a separate in-memory database for tests
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, echo=False)

# Recreate tables for each test session
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

client = TestClient(app)

def generate_unique_id():
    """Generate a pseudo-unique national_id for tests"""
    return f"UG{uuid.uuid4().hex[:8]}"

def test_create_member():
    national_id = generate_unique_id()
    response = client.post("/members/", json={
        "name": "Alice",
        "national_id": national_id,
        "date_joined": "2023-01-01"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Alice"
    assert data["national_id"] == national_id

def test_add_contribution():
    national_id = generate_unique_id()
    member_resp = client.post("/members/", json={
        "name": "Bob",
        "national_id": national_id,
        "date_joined": "2023-02-01"
    })
    assert member_resp.status_code == 200
    member_id = member_resp.json()["id"]

    contrib_resp = client.post("/contributions/", json={
        "member_id": member_id,
        "amount": 100.0,
        "month": "2023-10"
    })
    assert contrib_resp.status_code == 200
    data = contrib_resp.json()
    assert data["amount"] == 100.0
    assert data["member_id"] == member_id

def test_duplicate_national_id():
    # Generate a unique national_id
    national_id = generate_unique_id()

    # First insertion should succeed
    response1 = client.post("/members/", json={
        "name": "Charlie",
        "national_id": national_id,
        "date_joined": "2023-03-01"
    })
    assert response1.status_code == 200
    data1 = response1.json()
    assert data1["national_id"] == national_id

    # Second insertion with the same national_id should fail
    response2 = client.post("/members/", json={
        "name": "Duplicate Charlie",
        "national_id": national_id,
        "date_joined": "2023-03-02"
    })
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]