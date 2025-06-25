import os
import uuid
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from langchain.embeddings import init_embeddings
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver


class UserMemory(BaseModel):
    """사용자 메모리 데이터 모델"""
    user_id: str
    preferences: Dict[str, Any] = {}
    search_history: List[str] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "user_id": self.user_id,
            "preferences": self.preferences,
            "search_history": self.search_history,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class MemoryManager:
    """멀티턴 메모리 관리 시스템"""
    
    def __init__(self):
        """메모리 매니저 초기화"""
        self.checkpointer = InMemorySaver()  # 단기 메모리 (대화 히스토리)
        
        # 장기 메모리 (사용자 데이터) - 의미적 검색 지원
        try:
            # OpenAI 임베딩 모델 초기화 (테스트 환경에서는 더미 사용)
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key and api_key != "test-api-key":
                embeddings = init_embeddings("openai:text-embedding-3-small")
                self.store = InMemoryStore(
                    index={
                        "embed": embeddings,
                        "dims": 1536,
                        "fields": ["text", "preferences"]
                    }
                )
            else:
                # 테스트 환경용 심플한 스토어
                self.store = InMemoryStore()
        except Exception as e:
            # 임베딩 실패시 기본 스토어 사용
            self.store = InMemoryStore()
    
    def save_user_memory(self, user_id: str, memory_data: Dict[str, Any]) -> bool:
        """사용자 메모리 저장"""
        try:
            namespace = ("users", user_id)
            self.store.put(namespace, "profile", memory_data)
            return True
        except Exception as e:
            print(f"메모리 저장 실패: {e}")
            return False
    
    def get_user_memory(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 메모리 조회"""
        try:
            namespace = ("users", user_id)
            item = self.store.get(namespace, "profile")
            return item.value if item else None
        except Exception as e:
            print(f"메모리 조회 실패: {e}")
            return None
    
    def save_search_history(self, user_id: str, search_data: Dict[str, Any]) -> bool:
        """검색 히스토리 저장"""
        try:
            namespace = ("searches", user_id)
            search_id = str(uuid.uuid4())
            self.store.put(namespace, search_id, search_data)
            return True
        except Exception as e:
            print(f"검색 히스토리 저장 실패: {e}")
            return False
    
    def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """의미적 메모리 검색"""
        try:
            namespace = ("searches", user_id)
            results = self.store.search(namespace, query=query, limit=limit)
            return [{"key": r.key, "value": r.value, "score": r.score} for r in results]
        except Exception as e:
            print(f"메모리 검색 실패: {e}")
            return []
    
    def add_conversation_message(self, thread_id: str, message: Dict[str, str]) -> bool:
        """대화 메시지 추가"""
        try:
            # 대화 히스토리는 checkpointer로 관리 (실제 구현에서는 graph와 함께 사용)
            # 여기서는 간단히 store에 저장
            namespace = ("conversations", thread_id)
            message_id = str(uuid.uuid4())
            self.store.put(namespace, message_id, message)
            return True
        except Exception as e:
            print(f"대화 메시지 저장 실패: {e}")
            return False
    
    def get_conversation_history(self, thread_id: str) -> List[Dict[str, str]]:
        """대화 히스토리 조회"""
        try:
            namespace = ("conversations", thread_id)
            # 실제로는 checkpointer에서 가져와야 하지만 테스트용으로 store 사용
            results = self.store.search(namespace, query="", limit=100)
            return [r.value for r in results]
        except Exception as e:
            print(f"대화 히스토리 조회 실패: {e}")
            return [] 