import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def client():
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client


def assert_healthy(response):
    assert response.status_code == 200
    assert response.headers["content-type"].split(";", 1)[0] == "application/json"
    assert response.json() == {"status": "ok"}


def test_health_returns_exact_success_response(client):
    assert_healthy(client.get("/health"))


def test_health_is_public_without_redirects(client):
    assert "authorization" not in client.headers
    assert not client.cookies
    response = client.get("/health")
    assert "authorization" not in response.request.headers
    assert "cookie" not in response.request.headers
    assert not response.history
    assert_healthy(response)


def test_health_without_report_resources(client):
    # The test container has no report files, volumes or external network.
    # Scope review also verifies that no excluded resource is accessed.
    assert_healthy(client.get("/health"))


def test_three_consecutive_health_requests_are_independent(client):
    for _ in range(3):
        assert_healthy(client.get("/health"))
