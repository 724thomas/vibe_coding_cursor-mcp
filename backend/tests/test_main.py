import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["server"] == "running"


def test_test_endpoint():
    """새로운 테스트 엔드포인트 테스트"""
    response = client.get("/test")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "feature" in data
    assert "version" in data
    assert data["version"] == "1.0.1"


def test_read_root():
    """루트 엔드포인트 테스트"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json() 