# Cursor와 MCP로 프로젝트 개발하기
https://wonjoon.gitbook.io/joons-til/ai/vibecoding/project-development-using-cursor-and-mcp

![image](https://github.com/user-attachments/assets/86782d39-c1b6-4e32-a7da-3b91c3c24099)

<br><br>
<div></div>

# 🤖 Vibe Coding Practice - AI 채팅 시스템

> AI 기반 상품 최저가 검색 채팅 시스템을 위한 실습 프로젝트

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.0+-red.svg)](https://streamlit.io)
[![Tests](https://github.com/724thomas/vibe_coding_practice/actions/workflows/test.yml/badge.svg)](https://github.com/724thomas/vibe_coding_practice/actions/workflows/test.yml)

## 📋 프로젝트 개요

이 프로젝트는 **LangGraph**와 **Google Gemini**를 활용한 AI 기반 상품 최저가 검색 채팅 시스템입니다. 사용자가 상품명을 입력하면 AI가 웹 검색을 통해 최저가 정보와 구매 링크를 제공합니다.

### ✨ 주요 기능

- 🔍 **AI 상품 검색**: Google Gemini 모델을 사용한 지능형 상품 검색
- 🌐 **실시간 웹 검색**: DuckDuckGo를 통한 실시간 가격 정보 수집
- 💬 **채팅 인터페이스**: Streamlit 기반의 직관적인 채팅 UI
- 🚀 **FastAPI 백엔드**: 고성능 비동기 API 서버
- 🧪 **완전한 테스트 커버리지**: pytest 기반의 포괄적인 테스트
- 🤖 **GitHub Actions**: 자동화된 CI/CD 파이프라인

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    HTTP     ┌─────────────────┐    LangGraph    ┌─────────────────┐
│   Frontend      │ ◄────────► │   Backend       │ ◄─────────────► │   AI Agent      │
│  (Streamlit)    │             │  (FastAPI)      │                 │  (Gemini+Tools) │
└─────────────────┘             └─────────────────┘                 └─────────────────┘
                                          │
                                          ▼
                                ┌─────────────────┐
                                │   External      │
                                │   Services      │
                                │ (DuckDuckGo)    │
                                └─────────────────┘
```

## 🚀 빠른 시작

### 필수 요구사항

- Python 3.9 이상
- Google API Key (Gemini)

### 1. 저장소 클론

```bash
git clone https://github.com/724thomas/vibe_coding_practice.git
cd vibe_coding_practice
```

### 2. 백엔드 설정

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 환경 변수 설정
cp env.example .env
# .env 파일에서 GOOGLE_API_KEY 설정
```

### 3. 프론트엔드 설정

```bash
cd ../frontend

# 패키지 설치
pip install -r requirements.txt
```

### 4. 서버 실행

#### 백엔드 서버 시작

```bash
cd backend
python run.py
# 또는
uvicorn app.main:app --reload
```

서버가 실행되면 다음 주소에서 확인 가능:
- API 문서: http://localhost:8000/docs
- 백엔드 상태: http://localhost:8000/health

#### 프론트엔드 실행

```bash
cd frontend
streamlit run app.py
```

웹 브라우저에서 http://localhost:8501 접속

## 📁 프로젝트 구조

```
vibe_coding_practice/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py         # FastAPI 메인 앱
│   │   ├── agent.py        # LangGraph AI Agent
│   │   ├── config.py       # 설정 관리
│   │   ├── models/         # 데이터 모델
│   │   └── routers/        # API 라우터
│   ├── tests/              # 테스트 코드
│   ├── requirements.txt    # Python 패키지 의존성
│   └── run.py             # 서버 실행 스크립트
├── frontend/               # Streamlit 프론트엔드
│   ├── app.py             # 메인 Streamlit 앱
│   └── requirements.txt   # 프론트엔드 패키지
├── docs/                  # 프로젝트 문서
├── .github/               # GitHub 설정
│   ├── workflows/         # GitHub Actions
│   ├── ISSUE_TEMPLATE/    # 이슈 템플릿
│   └── pull_request_template.md
├── .cursor/rules/         # 개발 가이드라인
├── .gitignore
└── README.md
```

## 🧪 테스트

### 전체 테스트 실행

```bash
cd backend
python -m pytest tests/ -v
```

### 커버리지 리포트

```bash
python -m pytest tests/ --cov=app --cov-report=html
```

커버리지 리포트는 `htmlcov/index.html`에서 확인 가능

## 🔧 API 문서

### 주요 엔드포인트

- `GET /health` - 서버 상태 확인
- `POST /chat/search` - 상품 검색 API

### API 사용 예시

```python
import requests

# 상품 검색 요청
response = requests.post(
    "http://localhost:8000/chat/search",
    json={"message": "아이폰 15 최저가"}
)

result = response.json()
print(result["response"])
```

## 🤖 GitHub Actions

자동화된 워크플로우가 설정되어 있습니다:

### CI/CD 파이프라인
- ✅ **테스트 자동 실행** (Python 3.9-3.12)
- 📊 **코드 커버리지** 리포트
- 🔍 **코드 품질 검사** (flake8)

### PR/이슈 자동화
- 💬 **자동 댓글 생성**
- 🏷️ **라벨 자동 할당**
- 👥 **담당자 자동 지정**
- 🔍 **자동 코드 리뷰**

## 🛠️ 개발 가이드

### 개발 원칙
- **SOLID 원칙** 준수
- **Clean Architecture** 구조
- **TDD(Test-Driven Development)** 적용

### 브랜치 전략
- `main`: 프로덕션 브랜치
- `feature/*`: 새 기능 개발
- `bugfix/*`: 버그 수정
- `hotfix/*`: 긴급 수정

### 커밋 메시지 규칙
```
타입(스코프): 간단한 설명

- feat: 새 기능
- fix: 버그 수정
- docs: 문서 업데이트
- test: 테스트 추가/수정
- refactor: 리팩터링
```

## 🔐 환경 변수

`backend/.env` 파일에 다음 환경 변수를 설정하세요:

```env
# Google API 설정
GOOGLE_API_KEY=your_google_api_key_here

# 서버 설정
HOST=localhost
PORT=8000
DEBUG=true
```

## 🤝 기여하기

1. 이 저장소를 Fork
2. 새 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'feat: Add amazing feature'`)
4. 브랜치에 Push (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해 주세요.

- 📧 **이슈 생성**: [GitHub Issues](https://github.com/724thomas/vibe_coding_practice/issues)
- 💬 **토론**: [GitHub Discussions](https://github.com/724thomas/vibe_coding_practice/discussions)

---

## 🏆 주요 기술 스택

| 분야 | 기술 |
|------|------|
| **백엔드** | FastAPI, Python 3.9+ |
| **AI/ML** | LangGraph, LangChain, Google Gemini |
| **프론트엔드** | Streamlit |
| **테스팅** | pytest, unittest.mock |
| **CI/CD** | GitHub Actions |
| **검색** | DuckDuckGo Search API |

## 📈 성능 최적화

- **비동기 처리**: FastAPI의 async/await 활용
- **캐싱**: 검색 결과 캐싱으로 응답 속도 향상
- **에러 핸들링**: 견고한 예외 처리 및 재시도 로직
- **모니터링**: 로깅 및 헬스체크 엔드포인트

---

**Happy Coding! 🚀** 
