import pytest
from unittest.mock import Mock, patch
from app.multiturn_agent import MultiturnAgent


class TestMultiturnAgent:
    """멀티턴 에이전트 테스트"""
    
    @pytest.fixture
    def multiturn_agent(self):
        """멀티턴 에이전트 인스턴스 생성"""
        return MultiturnAgent()
    
    def test_agent_initialization(self, multiturn_agent):
        """에이전트 초기화 테스트"""
        assert multiturn_agent is not None
        assert multiturn_agent.agent is not None
        assert multiturn_agent.memory_manager is not None
    
    def test_search_with_memory_context(self, multiturn_agent):
        """메모리 컨텍스트를 활용한 검색 테스트"""
        user_id = "test_user_123"
        thread_id = "conversation_1"
        query = "피자 가격"
        
        # 이전 검색 기록 저장
        multiturn_agent.memory_manager.save_search_history(
            user_id, 
            {"text": "I love Italian food", "query": "pizza recommendations"}
        )
        
        # 멀티턴 검색 실행
        result = multiturn_agent.search_with_context(
            query=query,
            user_id=user_id,
            thread_id=thread_id
        )
        
        assert result is not None
        assert isinstance(result, str)
    
    def test_conversation_continuity(self, multiturn_agent):
        """대화 연속성 테스트"""
        user_id = "test_user_123"
        thread_id = "conversation_1"
        
        # 첫 번째 메시지
        first_result = multiturn_agent.search_with_context(
            query="최고의 피자집 추천해줘",
            user_id=user_id,
            thread_id=thread_id
        )
        
        # 두 번째 메시지 (컨텍스트 의존)
        second_result = multiturn_agent.search_with_context(
            query="그곳 가격은 어때?",
            user_id=user_id,
            thread_id=thread_id
        )
        
        assert first_result is not None
        assert second_result is not None
    
    def test_user_preference_learning(self, multiturn_agent):
        """사용자 선호도 학습 테스트"""
        user_id = "test_user_123"
        
        # 선호도 저장
        preferences = {"food_type": "Italian", "price_range": "medium"}
        multiturn_agent.save_user_preferences(user_id, preferences)
        
        # 선호도 조회
        saved_preferences = multiturn_agent.get_user_preferences(user_id)
        assert saved_preferences is not None
        assert saved_preferences["food_type"] == "Italian"
    
    def test_search_history_retrieval(self, multiturn_agent):
        """검색 히스토리 조회 테스트"""
        user_id = "test_user_123"
        search_data = {"text": "Looking for good pasta restaurants", "timestamp": "2024-01-01"}
        
        # 검색 히스토리 저장
        multiturn_agent.memory_manager.save_search_history(user_id, search_data)
        
        # 관련 검색 히스토리 조회
        history = multiturn_agent.get_relevant_search_history(user_id, "pasta")
        assert len(history) > 0 