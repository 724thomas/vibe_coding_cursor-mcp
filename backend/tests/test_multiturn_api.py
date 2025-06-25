import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)


class TestMultiturnChatAPI:
    """멀티턴 채팅 API 테스트"""
    
    def test_multiturn_chat_endpoint_exists(self, client):
        """멀티턴 채팅 엔드포인트 존재 확인"""
        response = client.options("/api/chat/multiturn")
        assert response.status_code != 404
    
    def test_multiturn_chat_first_message(self, client):
        """첫 번째 메시지 처리 테스트"""
        payload = {
            "message": "최고의 피자집 추천해줘",
            "user_id": "test_user_123",
            "thread_id": "conversation_1"
        }
        
        response = client.post("/api/chat/multiturn", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "thread_id" in data
        assert data["thread_id"] == "conversation_1"
    
    def test_multiturn_chat_follow_up_message(self, client):
        """후속 메시지 처리 테스트 (컨텍스트 유지)"""
        user_id = "test_user_123"
        thread_id = "conversation_1"
        
        # 첫 번째 메시지
        first_payload = {
            "message": "이탈리안 음식점 추천해줘",
            "user_id": user_id,
            "thread_id": thread_id
        }
        first_response = client.post("/api/chat/multiturn", json=first_payload)
        assert first_response.status_code == 200
        
        # 후속 메시지 (컨텍스트 의존)
        follow_up_payload = {
            "message": "거기 가격은 어때?",
            "user_id": user_id,
            "thread_id": thread_id
        }
        follow_up_response = client.post("/api/chat/multiturn", json=follow_up_payload)
        assert follow_up_response.status_code == 200
        
        data = follow_up_response.json()
        assert "response" in data
        assert data["thread_id"] == thread_id
    
    def test_user_preferences_endpoint(self, client):
        """사용자 선호도 저장/조회 API 테스트"""
        user_id = "test_user_123"
        preferences = {
            "food_type": "Italian",
            "price_range": "medium",
            "location": "Seoul"
        }
        
        # 선호도 저장
        save_response = client.post(f"/api/users/{user_id}/preferences", json=preferences)
        assert save_response.status_code == 200
        
        # 선호도 조회
        get_response = client.get(f"/api/users/{user_id}/preferences")
        assert get_response.status_code == 200
        
        data = get_response.json()
        assert data["food_type"] == "Italian"
        assert data["price_range"] == "medium"
    
    def test_conversation_history_endpoint(self, client):
        """대화 히스토리 조회 API 테스트"""
        thread_id = "conversation_1"
        
        # 대화 히스토리 조회
        response = client.get(f"/api/chat/{thread_id}/history")
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
    
    def test_search_history_endpoint(self, client):
        """검색 히스토리 조회 API 테스트"""
        user_id = "test_user_123"
        
        response = client.get(f"/api/users/{user_id}/search-history")
        assert response.status_code == 200
        
        data = response.json()
        assert "history" in data
        assert isinstance(data["history"], list)
    
    def test_invalid_request_handling(self, client):
        """잘못된 요청 처리 테스트"""
        # 빈 메시지
        payload = {
            "message": "",
            "user_id": "test_user",
            "thread_id": "test_thread"
        }
        
        response = client.post("/api/chat/multiturn", json=payload)
        assert response.status_code == 400
        
        # 필수 필드 누락
        incomplete_payload = {
            "message": "test message"
            # user_id, thread_id 누락
        }
        
        response = client.post("/api/chat/multiturn", json=incomplete_payload)
        assert response.status_code == 422  # Pydantic validation error 