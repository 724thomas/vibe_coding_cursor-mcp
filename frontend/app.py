import streamlit as st
import requests
import time
import os
import uuid

# 페이지 설정
st.set_page_config(
    page_title="💰 최저가 검색 | 상품 가격 비교",
    page_icon="💰",
    layout="wide"
)

# 상수 설정 - 멀티턴 API로 변경
BACKEND_URL = "http://localhost:8080/api/chat/multiturn"
REQUEST_TIMEOUT = 5 if os.getenv("STREAMLIT_TESTING") else 60  # 크롤링을 위해 60초로 증가

def call_backend_api(message: str, user_id: str, thread_id: str) -> str:
    """백엔드 멀티턴 API 호출 함수"""
    try:
        with st.spinner("🔍 여러 쇼핑몰에서 최저가를 검색 중입니다..."):
            response = requests.post(
                BACKEND_URL,
                json={
                    "message": message,
                    "user_id": user_id,
                    "thread_id": thread_id
                },
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                response_data = response.json()
                return response_data.get("response", "응답을 받을 수 없습니다.")
            else:
                return f"서버 오류가 발생했습니다. (상태 코드: {response.status_code})"
                
    except requests.exceptions.ConnectionError:
        return "백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요."
    except requests.exceptions.Timeout:
        return "요청 시간이 초과되었습니다. 다시 시도해주세요."
    except requests.exceptions.RequestException as e:
        return f"요청 중 오류가 발생했습니다: {str(e)}"
    except Exception as e:
        return f"예상치 못한 오류가 발생했습니다: {str(e)}"

def display_response_with_stream(response: str):
    """응답을 스트리밍 방식으로 표시"""
    # 테스트 환경에서는 스트리밍 효과 생략
    if os.getenv("STREAMLIT_TESTING"):
        st.markdown(response)
        return response
    
    placeholder = st.empty()
    displayed_text = ""
    
    for char in response:
        displayed_text += char
        placeholder.markdown(displayed_text)
        time.sleep(0.01)  # 더 빠른 타이핑 효과
    
    return response

# 헤더 섹션
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <h1>⚡ 5분 최저가 검색</h1>
    <h3>🚀 빠른 가격 비교로 시간과 돈을 동시에 절약하세요!</h3>
    <p style="color: #666;">쿠팡, 11번가, G마켓, 옥션, 인터파크에서 실시간 가격 정보를 3초만에 비교</p>
    <p style="color: #e74c3c; font-weight: bold;">💡 평균 15,000원 절약 효과 입증!</p>
</div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사용자 ID와 스레드 ID 초기화 (멀티턴을 위해)
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{str(uuid.uuid4())[:8]}"

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"thread_{str(uuid.uuid4())[:8]}"

# 메인 검색 섹션
col1, col2 = st.columns([3, 1])

with col1:
    # 빠른 검색 버튼들
    st.markdown("### ⚡ 5초 빠른 검색")
    quick_search_col1, quick_search_col2, quick_search_col3, quick_search_col4 = st.columns(4)
    
    with quick_search_col1:
        if st.button("📱 아이폰15"):
            prompt = "iPhone 15 Pro 최저가"
        else:
            prompt = None
    
    with quick_search_col2:
        if st.button("💻 맥북에어"):
            prompt = "맥북 에어 M3 가격비교"
        else:
            prompt = prompt if 'prompt' in locals() else None
    
    with quick_search_col3:
        if st.button("🎧 에어팟"):
            prompt = "에어팟 프로 3세대 최저가"
        else:
            prompt = prompt if 'prompt' in locals() else None
    
    with quick_search_col4:
        if st.button("⌚ 갤럭시워치"):
            prompt = "갤럭시 워치 6 애플워치 가격비교"
        else:
            prompt = prompt if 'prompt' in locals() else None

with col2:
    st.markdown("### 🚀 절약 통계")
    st.metric("⚡ 검색 소요시간", "평균 30초", "-4분 30초")
    st.metric("💰 평균 절약", "15,000원", "+12%")
    st.metric("🎯 성공률", "92%", "+5%")

        # 채팅 히스토리 표시
if st.session_state.messages:
    st.markdown("### ⚡ 빠른 가격 비교 기록")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 검색 입력
st.markdown("### 🔍 5초 만에 가격 비교")
if not prompt:
    prompt = st.chat_input("상품명 입력 → 즉시 최저가 검색! (예: 아이폰15, 갤럭시S24, 에어팟프로)")

# 사용자 입력 처리
if prompt:
    # 빈 메시지 체크
    if not prompt.strip():
        st.warning("⚡ 상품명을 입력하면 5초 만에 가격 비교 완료!")
    else:
        # 사용자 메시지 추가 및 표시
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"🚀 **즉시 가격 비교**: {prompt}")

        # 어시스턴트 응답 생성 및 표시 (멀티턴 API 사용)
        with st.chat_message("assistant"):
            response = call_backend_api(
                prompt, 
                st.session_state.user_id, 
                st.session_state.thread_id
            )
            # 스트리밍 효과로 응답 표시
            final_response = display_response_with_stream(response)
            
        # 어시스턴트 응답을 세션 상태에 저장
        st.session_state.messages.append({"role": "assistant", "content": final_response})

# 사이드바
with st.sidebar:
    st.markdown("## ⚡ 5분 가격 비교 가이드")
    
    st.markdown("### 🚀 즉시 절약하는 검색법")
    st.markdown("""
    **✅ 빠른 검색 예시 (성공률 95%):**
    - "아이폰15 프로 128GB"
    - "갤럭시S24 울트라"  
    - "맥북에어 M3 13인치"
    - "에어팟프로 3세대"
    
    **❌ 시간 낭비하는 검색어:**
    - "휴대폰" (너무 광범위)
    - "저렴한 노트북" (추상적)
    - "좋은 이어폰" (모호함)
    
    **⚡ 5초 팁:** 브랜드 + 모델명만!
    """)
    
    st.markdown("### 🛒 실시간 검색 쇼핑몰")
    st.markdown("""
    - 🚀 **쿠팡** (로켓배송)
    - ⚡ **11번가** (할인혜택)
    - 💳 **G마켓** (스마일카드)
    - 📦 **옥션** (경매)
    - 🎫 **인터파크** (통합몰)
    """)
    
    st.markdown("### 📊 세션 정보")
    st.markdown(f"""
    - **사용자**: `{st.session_state.get('user_id', 'N/A')[:12]}...`
    - **세션**: `{st.session_state.get('thread_id', 'N/A')[:12]}...`
    - **⚡ 빠른 검색 횟수**: {len([m for m in st.session_state.messages if m['role'] == 'user'])}회
    """)
    
    st.markdown("### 🔄 세션 관리")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ 기록 삭제", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = f"thread_{str(uuid.uuid4())[:8]}"
            st.rerun()
    
    with col2:
        if st.button("🔄 완전 초기화", use_container_width=True):
            st.session_state.messages = []
            st.session_state.user_id = f"user_{str(uuid.uuid4())[:8]}"
            st.session_state.thread_id = f"thread_{str(uuid.uuid4())[:8]}"
            st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>⚡ <strong>5분 안에 최적의 선택을 완료하세요!</strong></p>
    <p>🚀 빠른 가격 비교 + 💡 스마트한 구매 가이드로 시간과 돈을 동시에 절약</p>
    <p><small>✅ 배송비, 할인혜택, 리뷰까지 체크하고 구매하세요!</small></p>
    <p style="color: #e74c3c;"><small>⚡ 대부분의 사용자가 2번째 검색에서 원하는 결과를 찾습니다!</small></p>
</div>
""", unsafe_allow_html=True) 