import os
import uuid
from typing import Dict, List, Optional, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_core.runnables import RunnableConfig

from .memory import MemoryManager
from .scraper import WebScraper


class MultiturnAgent:
    """멀티턴 메모리 기능을 갖춘 상품 검색 에이전트"""
    
    def __init__(self):
        """멀티턴 에이전트 초기화"""
        self.memory_manager = MemoryManager()
        self.scraper = WebScraper()
        self.agent = self._create_agent()
    
    def _create_agent(self):
        """메모리 기능이 통합된 LangGraph React Agent 생성"""
        # Gemini LLM 모델 초기화
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "xx":
            # 테스트용 더미 응답
            return self._create_dummy_agent()
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=api_key
        )
        
        # DuckDuckGo 검색 Tool 초기화
        search_tool = DuckDuckGoSearchRun()
        tools = [search_tool]
        
        # 메모리 기반 시스템 프롬프트
        system_prompt = """
        당신은 상품 최저가 검색 전문 어시스턴트입니다.
        사용자의 이전 검색 기록과 선호도를 기억하고 개인화된 검색 결과를 제공합니다.
        실제 쇼핑몰에서 직접 크롤링하여 실시간 가격 정보를 제공합니다.
        
        사용자가 요청한 상품에 대해:
        1. 이전 검색 기록을 참고하여 개인화된 검색어 생성
        2. 사용자 선호도를 고려한 상품 추천
        3. 대화 컨텍스트를 유지하여 자연스러운 응답
        4. 실시간 상품명, 가격, 구매 링크 제공
        5. 여러 쇼핑몰 가격 비교
        
        친절하고 상세하게 답변해주세요.
        """
        
        # React Agent 생성 (메모리 기능 포함)
        agent = create_react_agent(
            llm,
            tools,
            prompt=system_prompt,
            checkpointer=self.memory_manager.checkpointer,
            store=self.memory_manager.store
        )
        
        return agent
    
    def _create_dummy_agent(self):
        """테스트용 더미 에이전트 생성"""
        class DummyAgent:
            def invoke(self, messages, config=None):
                return {
                    "messages": [
                        type('Message', (), {
                            'content': f"테스트 모드입니다. '{messages['messages'][0]['content']}' 검색 기능이 준비 중입니다."
                        })()
                    ]
                }
        return DummyAgent()
    
    def search_with_context(self, query: str, user_id: str, thread_id: str) -> str:
        """메모리 컨텍스트를 활용한 상품 검색"""
        if not query or query.strip() == "":
            return "검색어를 입력해주세요."
        
        try:
            # 사용자 선호도 및 검색 히스토리 조회
            user_preferences = self.get_user_preferences(user_id)
            search_history = self.get_relevant_search_history(user_id, query)
            
            # 컨텍스트 정보 구성
            context_info = self._build_context_info(user_preferences, search_history)
            
            # 먼저 직접 크롤링으로 상품 검색 시도
            products = self.scraper.search_products(query)
            
            if products:
                # 크롤링 결과가 있을 때
                crawling_result = self.scraper.format_search_results(products, query)
                
                # 메모리 컨텍스트와 함께 AI가 개인화된 응답 생성
                if context_info:
                    enhanced_query = f"""
                    크롤링 검색 결과:
                    {crawling_result}
                    
                    사용자 컨텍스트: {context_info}
                    
                    위 크롤링 결과를 바탕으로 사용자의 이전 검색 기록과 선호도를 고려하여 
                    개인화된 상품 추천과 설명을 제공해주세요.
                    """
                else:
                    enhanced_query = f"""
                    크롤링 검색 결과:
                    {crawling_result}
                    
                    위 검색 결과를 바탕으로 사용자에게 유용한 상품 정보와 구매 가이드를 제공해주세요.
                    """
                
                # AI가 크롤링 결과를 개인화하여 응답
                config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "user_id": user_id
                    }
                }
                
                result = self.agent.invoke({
                    "messages": [{"role": "user", "content": enhanced_query}]
                }, config)
                
                # 검색 결과 저장
                self._save_search_result(user_id, query, products)
                
                if result and "messages" in result and len(result["messages"]) > 0:
                    last_message = result["messages"][-1]
                    return last_message.content
                else:
                    return crawling_result  # AI 응답 실패 시 크롤링 결과 직접 반환
            
            else:
                # 크롤링 결과가 없을 때 DuckDuckGo 백업 검색
                enhanced_query = self._enhance_query_with_context(f"{query} 최저가 온라인쇼핑 구매", context_info)
                
                config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "user_id": user_id
                    }
                }
                
                result = self.agent.invoke({
                    "messages": [{"role": "user", "content": enhanced_query}]
                }, config)
                
                # 검색 결과 저장
                self._save_search_result(user_id, query, result)
                
                if result and "messages" in result and len(result["messages"]) > 0:
                    last_message = result["messages"][-1]
                    return last_message.content
                else:
                    return "검색 결과를 가져올 수 없습니다."
                
        except Exception as e:
            return f"검색 중 오류가 발생했습니다: {str(e)}"
    
    def save_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """사용자 선호도 저장"""
        return self.memory_manager.save_user_memory(user_id, {
            "preferences": preferences,
            "type": "user_preferences"
        })
    
    def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """사용자 선호도 조회"""
        memory = self.memory_manager.get_user_memory(user_id)
        if memory and "preferences" in memory:
            return memory["preferences"]
        return {}
    
    def get_relevant_search_history(self, user_id: str, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """관련 검색 히스토리 조회"""
        return self.memory_manager.search_memories(user_id, query, limit)
    
    def _build_context_info(self, preferences: Dict[str, Any], history: List[Dict[str, Any]]) -> str:
        """컨텍스트 정보 구성"""
        context_parts = []
        
        if preferences:
            pref_text = ", ".join([f"{k}: {v}" for k, v in preferences.items()])
            context_parts.append(f"사용자 선호도: {pref_text}")
        
        if history:
            history_text = "; ".join([item["value"].get("text", "") for item in history[:2]])
            context_parts.append(f"이전 검색: {history_text}")
        
        return " | ".join(context_parts)
    
    def _enhance_query_with_context(self, query: str, context: str) -> str:
        """컨텍스트를 포함한 검색 쿼리 생성"""
        if context:
            return f"{query}\n\n참고 정보: {context}"
        return query
    
    def _save_search_result(self, user_id: str, query: str, result: Any) -> None:
        """검색 결과 저장"""
        try:
            search_data = {
                "text": query,
                "query": query,
                "timestamp": str(uuid.uuid4()),
                "type": "search_result"
            }
            self.memory_manager.save_search_history(user_id, search_data)
        except Exception as e:
            print(f"검색 결과 저장 실패: {e}") 