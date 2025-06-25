from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat

app = FastAPI(
    title="Chat API",
    description="간단한 채팅 API 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(chat.router)


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {"message": "Chat API Server"}


@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    # 의도적인 버그: 정의되지 않은 변수 참조
    server_status = undefined_variable  # NameError 발생
    return {"status": "healthy", "server": server_status}


@app.get("/test")
async def test_endpoint():
    """PR 테스트를 위한 새로운 엔드포인트"""
    return {
        "message": "PR 테스트 성공!",
        "feature": "새로운 테스트 엔드포인트",
        "version": "1.0.1"
    } 