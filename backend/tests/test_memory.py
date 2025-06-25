import pytest
import uuid
from unittest.mock import Mock, patch
from app.memory import MemoryManager, UserMemory


class TestMemoryManager:
    """메모리 시스템 테스트"""
    
    @pytest.fixture
    def memory_manager(self):
        """메모리 매니저 인스턴스 생성"""
        return MemoryManager()
    
    def test_memory_manager_initialization(self, memory_manager):
        """메모리 매니저 초기화 테스트"""
        assert memory_manager is not None
        assert memory_manager.checkpointer is not None
        assert memory_manager.store is not None
    
    def test_save_user_memory(self, memory_manager):
        """사용자 메모리 저장 테스트"""
        user_id = "test_user_123"
        memory_data = {"preference": "Italian food", "search_history": ["pizza", "pasta"]}
        
        result = memory_manager.save_user_memory(user_id, memory_data)
        assert result is True
    
    def test_get_user_memory(self, memory_manager):
        """사용자 메모리 조회 테스트"""
        user_id = "test_user_123"
        memory_data = {"preference": "Italian food", "search_history": ["pizza", "pasta"]}
        
        # 먼저 메모리 저장
        memory_manager.save_user_memory(user_id, memory_data)
        
        # 메모리 조회
        retrieved_memory = memory_manager.get_user_memory(user_id)
        assert retrieved_memory is not None
        assert retrieved_memory["preference"] == "Italian food"
    
    def test_search_memories(self, memory_manager):
        """메모리 검색 테스트"""
        user_id = "test_user_123"
        memory_data = {"text": "I love pizza and Italian food"}
        
        # 메모리 저장
        memory_manager.save_search_history(user_id, memory_data)
        
        # 의미적 검색 테스트
        results = memory_manager.search_memories(user_id, "food preferences")
        assert len(results) > 0
    
    def test_conversation_history(self, memory_manager):
        """대화 히스토리 관리 테스트"""
        thread_id = "conversation_1"
        user_message = {"role": "user", "content": "What's the best pizza place?"}
        
        result = memory_manager.add_conversation_message(thread_id, user_message)
        assert result is True
        
        history = memory_manager.get_conversation_history(thread_id)
        assert len(history) > 0
        assert history[0]["content"] == "What's the best pizza place?"


class TestUserMemory:
    """사용자 메모리 데이터 모델 테스트"""
    
    def test_user_memory_creation(self):
        """사용자 메모리 모델 생성 테스트"""
        memory = UserMemory(
            user_id="test_user",
            preferences={"food": "Italian"},
            search_history=["pizza", "pasta"]
        )
        assert memory.user_id == "test_user"
        assert memory.preferences["food"] == "Italian"
        assert len(memory.search_history) == 2
    
    def test_user_memory_dict_conversion(self):
        """사용자 메모리 딕셔너리 변환 테스트"""
        memory = UserMemory(
            user_id="test_user",
            preferences={"food": "Italian"},
            search_history=["pizza"]
        )
        memory_dict = memory.to_dict()
        assert isinstance(memory_dict, dict)
        assert memory_dict["user_id"] == "test_user" 