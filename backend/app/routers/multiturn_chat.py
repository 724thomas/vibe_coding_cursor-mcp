from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from app.multiturn_agent import MultiturnAgent

router = APIRouter(prefix="/api", tags=["multiturn-chat"])

# 전역 에이전트 인스턴스 (심플하게 구현)
multiturn_agent = MultiturnAgent()


class MultiturnChatRequest(BaseModel):
    """멀티턴 채팅 요청 모델"""
    message: str
    user_id: str
    thread_id: str


class MultiturnChatResponse(BaseModel):
    """멀티턴 채팅 응답 모델"""
    response: str
    thread_id: str
    user_id: str


class UserPreferencesRequest(BaseModel):
    """사용자 선호도 요청 모델"""
    food_type: Optional[str] = None
    price_range: Optional[str] = None
    location: Optional[str] = None


@router.post("/chat/multiturn", response_model=MultiturnChatResponse)
async def multiturn_chat(request: MultiturnChatRequest):
    """멀티턴 채팅 엔드포인트"""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")
    
    try:
        # 멀티턴 에이전트로 검색 실행
        response = multiturn_agent.search_with_context(
            query=request.message,
            user_id=request.user_id,
            thread_id=request.thread_id
        )
        
        return MultiturnChatResponse(
            response=response,
            thread_id=request.thread_id,
            user_id=request.user_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"처리 중 오류가 발생했습니다: {str(e)}")


@router.post("/users/{user_id}/preferences")
async def save_user_preferences(user_id: str, preferences: UserPreferencesRequest):
    """사용자 선호도 저장"""
    try:
        # 선호도 딕셔너리 생성 (None이 아닌 값만 포함)
        prefs_dict = {k: v for k, v in preferences.model_dump().items() if v is not None}
        
        success = multiturn_agent.save_user_preferences(user_id, prefs_dict)
        if success:
            return {"message": "선호도가 저장되었습니다.", "preferences": prefs_dict}
        else:
            raise HTTPException(status_code=500, detail="선호도 저장에 실패했습니다.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류가 발생했습니다: {str(e)}")


@router.get("/users/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """사용자 선호도 조회"""
    try:
        preferences = multiturn_agent.get_user_preferences(user_id)
        return preferences if preferences else {}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류가 발생했습니다: {str(e)}")


@router.get("/chat/{thread_id}/history")
async def get_conversation_history(thread_id: str):
    """대화 히스토리 조회"""
    try:
        # 대화 히스토리 조회 (현재는 간단하게 구현)
        history = multiturn_agent.memory_manager.get_conversation_history(thread_id)
        return {"messages": history}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류가 발생했습니다: {str(e)}")


@router.get("/users/{user_id}/search-history")
async def get_search_history(user_id: str, limit: int = 10):
    """사용자 검색 히스토리 조회"""
    try:
        # 검색 히스토리 조회
        history = multiturn_agent.get_relevant_search_history(user_id, "", limit)
        return {"history": history}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류가 발생했습니다: {str(e)}")


@router.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "service": "multiturn-chat"} 