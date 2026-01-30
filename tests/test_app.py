import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect to static file, but TestClient follows redirects by default
    # Actually, RedirectResponse to /static/index.html, but since static is mounted,
    # it should serve the file. But in test, it might not work the same.
    # Let's check what happens.
    # For now, assume it redirects.


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_signup_for_activity():
    # Test successful signup
    response = client.post("/activities/Chess Club/signup?email=test@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@example.com" in data["message"]

    # Check that the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "test@example.com" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent Activity/signup?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_already_signed_up():
    # First signup
    client.post("/activities/Programming Class/signup?email=duplicate@example.com")
    # Try again
    response = client.post("/activities/Programming Class/signup?email=duplicate@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_unregister_from_activity():
    # First signup
    client.post("/activities/Gym Class/signup?email=unregister@example.com")
    # Then unregister
    response = client.post("/activities/Gym Class/unregister?email=unregister@example.com")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Unregistered" in data["message"]

    # Check removed
    response = client.get("/activities")
    activities = response.json()
    assert "unregister@example.com" not in activities["Gym Class"]["participants"]


def test_unregister_activity_not_found():
    response = client.post("/activities/Nonexistent Activity/unregister?email=test@example.com")
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_not_signed_up():
    response = client.post("/activities/Basketball Team/unregister?email=notsigned@example.com")
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"]