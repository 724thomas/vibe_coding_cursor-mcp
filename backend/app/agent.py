import os
import re
from typing import Optional, List, Tuple
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from .scraper import WebScraper


def create_agent():
    """LangGraph React Agent를 생성합니다."""
    # Gemini LLM 모델 초기화
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        # 테스트 환경에서는 더미 키 사용
        api_key = "test-api-key"
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,  # 가격 정보는 정확성이 중요하므로 낮은 temperature
        google_api_key=api_key
    )
    
    # DuckDuckGo 검색 Tool 초기화 (백업용)
    search_tool = DuckDuckGoSearchRun()
    tools = [search_tool]
    
    # 가격 비교 전문 시스템 프롬프트  
    system_prompt = """
    당신은 **가격 비교 전문 AI 어시스턴트**입니다.
    
    **주요 기능:**
    🔍 여러 주요 쇼핑몰에서 실시간 가격 수집
    💰 최저가 및 가격 차이 분석
    📊 쇼핑몰별 가격 비교표 제공
    
    **검색 대상 쇼핑몰:**
    - 쿠팡, 11번가, G마켓, 옥션, 인터파크
    
    **응답 형식 (반드시 이 순서로):**
    1. 🥇 **최저가**: [가격] ([쇼핑몰명])
    2. 📊 **가격 비교표**:
       - 쇼핑몰A: [가격]
       - 쇼핑몰B: [가격] 
       - 쇼핑몰C: [가격]
    3. 💡 **가격 분석**:
       - 최고가 대비 절약금액
       - 평균 가격 대비 차이
    
    **중요 원칙:**
    - 가격 정보만 집중적으로 제공
    - 구매 방법이나 구매 링크는 제공하지 않음
    - 쇼핑몰별 가격 차이에만 집중
    - 정확한 가격 숫자만 표시 (원 단위)
    
    사용자가 상품을 검색하면 가격 비교 정보만 
    간결하고 명확하게 제공합니다.
    """
    
    # React Agent 생성
    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt
    )
    
    return agent


def search_products(query: Optional[str]) -> str:
    """가격 비교 중심의 상품 검색 함수"""
    if not query or query.strip() == "":
        return "검색할 상품명을 입력해주세요. (예: iPhone 15 Pro, 삼성 갤럭시 S24)"
    
    try:
        # 웹 스크래퍼로 실시간 가격 검색
        scraper = WebScraper()
        products = scraper.search_products(query, max_results=10)
        
        if products:
            # 크롤링 결과를 가격 비교 형태로 포맷팅
            return scraper.format_search_results(products, query)
        else:
            # 크롤링 결과가 없을 때 백업 검색으로 가격 비교
            search_tool = DuckDuckGoSearchRun()
            
            # 가격 비교 전용 검색 쿼리 생성
            enhanced_query = f"{query} 가격 쿠팡 11번가 G마켓 옥션 인터파크 최저가 비교"
            
            search_result = search_tool.run(enhanced_query)
            
            # 새로운 가격 추출 함수 사용
            prices = extract_prices_from_search(search_result, query)
            
            if prices:
                return format_price_comparison(prices, query)
            else:
                # 검색어를 바꿔서 한 번 더 시도
                fallback_query = f"{query} 최저가 온라인쇼핑몰 가격비교"
                fallback_result = search_tool.run(fallback_query)
                fallback_prices = extract_prices_from_search(fallback_result, query)
                
                if fallback_prices:
                    return format_price_comparison(fallback_prices, query)
                else:
                    return _get_no_results_message(query)
            
    except Exception as e:
        return f"""
❌ **검색 중 오류가 발생했습니다**

오류 내용: {str(e)}

🔄 **해결 방법:**
1. 잠시 후 다시 시도해보세요
2. 더 간단한 검색어로 시도해보세요
3. 브랜드명만으로 검색해보세요

💡 **검색 예시:**
- iPhone 15
- 갤럭시 S24
- 에어팟 프로
        """.strip()

def _get_no_results_message(query: str) -> str:
    """가격 비교 결과가 없을 때의 안내 메시지"""
    return f"""
🔍 **'{query}' 가격 비교 결과가 없습니다**

💡 **가격 비교 검색 개선 방법:**

**1. 검색어 수정:**
- 더 구체적으로: "{query} 128GB" 또는 "{query} 2024년"
- 브랜드 추가: "삼성 {query}" 또는 "애플 {query}"
- 영문/한글 변경: 한글 ↔ 영문으로 시도

**2. 유사 상품 가격 비교:**
- 비슷한 카테고리 상품으로 검색
- 상위 브랜드 상품으로 검색

**3. 인기 가격 비교 상품:**
- 📱 iPhone 15 Pro (가격비교)
- 💻 맥북 에어 M3 (가격비교)
- 🎧 에어팟 프로 3세대 (가격비교)
- ⌚ 갤럭시 워치 6 (가격비교)
- 📱 갤럭시 S24 Ultra (가격비교)

🔄 위 방법으로 다시 가격 비교를 시도해보세요!
    """.strip() 

def extract_prices_from_search(search_result: str, query: str) -> List[Tuple[str, int, str]]:
    """검색 결과에서 쇼핑몰별 가격 정보 추출"""
    # 쇼핑몰별 가격 패턴들
    mall_patterns = [
        (r'쿠팡[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', '쿠팡'),
        (r'11번가[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', '11번가'),
        (r'G마켓[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', 'G마켓'),
        (r'지마켓[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', 'G마켓'),  # 지마켓도 G마켓으로
        (r'옥션[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', '옥션'),
        (r'인터파크[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', '인터파크'),
        (r'롯데[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', '롯데온'),
        (r'SSG[^0-9]*?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)[^0-9]*?원', 'SSG'),
    ]
    
    # 일반 가격 패턴들 (쇼핑몰 근처에서)
    general_patterns = [
        r'가격\s*:\s*(\d{1,3}(?:,\d{3})*)\s*원',
        r'(\d{1,3}(?:,\d{3})*)\s*원',
        r'최저가\s*(\d{1,3}(?:,\d{3})*)\s*원',
    ]
    
    found_prices = []
    
    # 1. 쇼핑몰별 명시적 가격 찾기
    for pattern, mall_name in mall_patterns:
        matches = re.findall(pattern, search_result, re.IGNORECASE)
        for price_str in matches:
            try:
                price_num = int(price_str.replace(',', ''))
                # 합리적인 가격 범위 필터링 (1천원 ~ 1억원)
                if 1000 <= price_num <= 100000000:
                    found_prices.append((mall_name, price_num, f"{price_num:,}원"))
            except:
                continue
    
    # 2. 일반 가격 패턴에서 추가 추출 (쇼핑몰명 없이)
    if len(found_prices) < 3:  # 쇼핑몰별 가격이 부족하면 일반 가격도 추가
        for pattern in general_patterns:
            matches = re.findall(pattern, search_result)
            for price_str in matches:
                try:
                    price_num = int(price_str.replace(',', ''))
                    if 1000 <= price_num <= 100000000:
                        # 이미 찾은 가격과 중복 체크
                        if not any(abs(price_num - p[1]) < 1000 for p in found_prices):
                            found_prices.append(("온라인쇼핑", price_num, f"{price_num:,}원"))
                except:
                    continue
    
    # 3. 가격순 정렬 (저렴한 순)
    found_prices.sort(key=lambda x: x[1])
    
    # 4. 중복 제거 (비슷한 가격은 하나만)
    unique_prices = []
    for mall, price, price_str in found_prices:
        # 기존 가격과 5% 이내 차이면 중복으로 간주
        is_duplicate = any(abs(price - existing[1]) / max(price, existing[1]) < 0.05 
                          for existing in unique_prices)
        if not is_duplicate:
            unique_prices.append((mall, price, price_str))
    
    return unique_prices[:5]  # 최대 5개까지


def format_price_comparison(prices: List[Tuple[str, int, str]], query: str) -> str:
    """가격 비교 결과를 사용자 요구 형태로 포맷팅"""
    if not prices:
        return f"""
🔍 **'{query}' 가격 정보를 찾을 수 없습니다**

⚡ **5초 만에 해결하는 방법:**
- 더 구체하게: "{query} 128GB" / "{query} 2024"
- 브랜드 추가: "삼성 {query}" / "애플 {query}"  
- 영문↔한글 변경해보세요

🔄 **다시 시도해보세요!**
        """.strip()
    
    result = f"💰 **'{query}' 가격 비교** (저렴한 순)\n\n"
    
    for i, (mall, price_num, price_str) in enumerate(prices, 1):
        result += f"{i}. **{mall}** {price_str}\n"
    
    # 절약 효과 계산
    if len(prices) > 1:
        min_price = prices[0][1]
        max_price = prices[-1][1]
        savings = max_price - min_price
        result += f"\n💡 **절약 효과**: 최대 {savings:,}원 절약 가능!\n"
    
    result += f"\n✅ **구매 전 체크**: 배송비, 할인쿠폰, 리뷰 확인하세요!"
    
    return result 