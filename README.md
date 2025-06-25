# 💰 최저가 검색 | 상품 가격 비교 사이트

**여러 주요 쇼핑몰의 실시간 가격을 한 번에 비교하는 AI 기반 가격 검색 서비스**

## 🌟 주요 기능

### 🔍 실시간 가격 비교
- **다중 쇼핑몰 동시 검색**: 쿠팡, 11번가, G마켓, 옥션, 인터파크
- **최저가 자동 정렬**: 가격순으로 자동 정렬하여 최저가부터 표시
- **가격 차이 분석**: 최저가 대비 다른 쇼핑몰 가격 차이 계산

### 📊 가격 분석 리포트
- **가격 통계**: 최저가, 최고가, 평균가 자동 계산
- **절약 금액**: 쇼핑몰별 가격 차이로 절약 가능한 금액 표시
- **구매 가이드**: 가격 외 고려사항(배송비, 리뷰 등) 안내

### 🤖 AI 멀티턴 대화
- **이전 대화 기억**: 사용자의 이전 검색 기록과 선호도 학습
- **개인화 추천**: 대화 맥락을 고려한 상품 추천
- **연속 검색**: "앞서 말한 조건으로 다시 검색" 등 자연스러운 대화

## 🛠 기술 스택

### 백엔드
- **FastAPI**: RESTful API 서버
- **LangGraph**: AI 에이전트 및 멀티턴 대화 처리
- **Google Gemini**: 자연어 처리 및 응답 생성
- **BeautifulSoup4**: 웹 스크래핑 및 상품 정보 추출
- **Python 3.13**: 메인 개발 언어

### 프론트엔드
- **Streamlit**: 대화형 웹 인터페이스
- **실시간 채팅**: 스트리밍 응답 및 타이핑 효과

### 인프라
- **멀티쓰레딩**: 동시 쇼핑몰 크롤링
- **캐싱**: 검색 결과 임시 저장
- **오류 처리**: 견고한 예외 처리 및 백업 검색

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# 저장소 클론
git clone <repository-url>
cd vibe_coding_w2-1

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 2. 환경 변수 설정
```bash
# backend/.env 파일 생성
cp backend/env.example backend/.env

# Google API 키 설정 (필수)
export GOOGLE_API_KEY="your-gemini-api-key"
```

### 3. 서버 실행
```bash
# 백엔드 서버 실행 (터미널 1)
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 프론트엔드 실행 (터미널 2)
cd frontend
streamlit run app.py --server.port 8501
```

### 4. 서비스 접속
- **웹 인터페이스**: http://localhost:8501
- **API 문서**: http://localhost:8080/docs

## 💡 사용법

### 🎯 효과적인 검색 방법

**✅ 좋은 검색어 예시:**
- "iPhone 15 Pro 128GB"
- "삼성 갤럭시 S24 Ultra"
- "LG 그램 노트북 16인치"
- "에어팟 프로 3세대"

**❌ 피해야 할 검색어:**
- "폰" (너무 광범위)
- "싼 컴퓨터" (추상적)
- "좋은 제품" (모호함)

### 🔥 인기 검색어 버튼
웹 인터페이스에서 제공되는 인기 검색어 버튼을 클릭하면 즉시 검색이 실행됩니다:
- 📱 iPhone 15
- 💻 노트북
- 🎧 무선이어폰
- ⌚ 스마트워치

### 💬 자연스러운 대화
AI와 자연스럽게 대화하며 상품을 검색할 수 있습니다:
- "아까 검색한 iPhone 말고 삼성 제품으로 찾아줘"
- "더 저렴한 대안은 없을까?"
- "256GB 모델도 비교해줘"

## 📊 검색 결과 예시

```
💰 iPhone 15 Pro 가격 비교 결과 (총 5개)

## 🏆 최저가 순위

🥇 최저가: 1,350,000원 (쿠팡)

🥇 **iPhone 15 Pro 128GB 자급제**
💰 가격: 1,350,000원
🏪 판매처: 쿠팡
🛒 구매링크: https://coupang.com/...

🥈 **iPhone 15 Pro 128GB (정품)**
💰 가격: 1,380,000원
🏪 판매처: 11번가
🛒 구매링크: https://11st.co.kr/...
📊 최저가 대비 +30,000원

## 📊 가격 분석
• 최저가: 1,350,000원
• 최고가: 1,450,000원
• 평균가: 1,395,000원
• 가격 차이: 100,000원

💡 구매 팁: 가격 외에도 배송비, 할인 혜택, 리뷰 등을 종합적으로 고려하세요!
```

## 🏗 프로젝트 구조

```
vibe_coding_w2-1/
├── backend/                 # FastAPI 백엔드
│   ├── app/
│   │   ├── agent.py        # AI 에이전트 로직
│   │   ├── scraper.py      # 웹 스크래핑 엔진
│   │   ├── memory.py       # 멀티턴 메모리 관리
│   │   ├── models/         # 데이터 모델
│   │   └── routers/        # API 라우터
│   ├── tests/              # 테스트 코드
│   └── requirements.txt    # Python 의존성
├── frontend/               # Streamlit 프론트엔드
│   ├── app.py             # 메인 웹 인터페이스
│   └── requirements.txt   # 프론트엔드 의존성
└── docs/                  # 문서
```

## 🧪 테스트

```bash
# 백엔드 테스트 실행
cd backend
python -m pytest tests/ -v

# 특정 테스트 실행
python -m pytest tests/test_scraper.py::TestWebScraper::test_search_products_success -v

# 커버리지와 함께 테스트
python -m pytest tests/ --cov=app --cov-report=html
```

## 🔧 개발 원칙

### SOLID 원칙 준수
- **단일 책임**: 각 클래스와 함수는 하나의 명확한 책임
- **개방-폐쇄**: 확장에는 열려있고 수정에는 닫혀있는 구조
- **의존성 역전**: 추상화에 의존하는 설계

### TDD (테스트 주도 개발)
1. **테스트 작성** → 기능 구현 전 테스트 코드 작성
2. **기능 구현** → 테스트를 통과하는 최소한의 코드 작성
3. **리팩토링** → 테스트를 유지하며 코드 개선

### Clean Architecture
- **계층 분리**: 도메인, 애플리케이션, 인프라 계층 분리
- **의존성 방향**: 외부 계층이 내부 계층에 의존
- **테스트 용이성**: 각 계층별 독립적 테스트 가능

## 🛡️ 지원 쇼핑몰

| 쇼핑몰 | 지원 여부 | 특징 |
|--------|-----------|------|
| 🛒 쿠팡 | ✅ | 로켓배송, 다양한 카테고리 |
| 🏬 11번가 | ✅ | 할인 이벤트, 브랜드관 |
| 🎁 G마켓 | ✅ | 스마일카드, 적립금 |
| 📦 옥션 | ✅ | 경매, 중고거래 |
| 🛍️ 인터파크 | ✅ | 도서, 티켓 통합 |

## 📈 로드맵

### v1.1 (다음 버전)
- [ ] 가격 알림 기능
- [ ] 쇼핑몰별 리뷰 점수 통합
- [ ] 가격 변동 그래프

### v1.2 (미래 계획)
- [ ] 모바일 앱 대응
- [ ] 더 많은 쇼핑몰 지원
- [ ] 카테고리별 인기 상품

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 발생하거나 기능 요청이 있으시면:
- **이슈 등록**: GitHub Issues 활용
- **이메일**: support@pricecompare.com
- **문서**: [온라인 문서](https://docs.pricecompare.com)

---

💡 **구매 전 꼭 확인하세요!**
가격 외에도 배송비, 할인 혜택, 판매자 신뢰도, 리뷰 등을 종합적으로 고려하여 구매하시기 바랍니다.

*※ 실시간 가격 정보는 사이트별로 차이가 있을 수 있습니다.* 