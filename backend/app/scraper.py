import requests
import re
import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ScrapingResult:
    """스크래핑 결과를 담는 데이터 클래스"""
    name: str
    price: str
    url: str
    source: str
    description: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "name": self.name,
            "price": self.price,
            "url": self.url,
            "source": self.source,
            "description": self.description
        }


class WebScraper:
    """웹 크롤링을 통한 상품 정보 수집기"""
    
    def __init__(self):
        """스크래퍼 초기화"""
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(self.headers)
        
        # 주요 쇼핑몰 검색 URL 패턴
        self.search_urls = {
            "쿠팡": "https://www.coupang.com/np/search?q={}",
            "11번가": "https://search.11st.co.kr/Search.tmall?method=getTotalSearchSeller&isGnb=Y&keyword={}",
            "G마켓": "http://browse.gmarket.co.kr/search?keyword={}",
            "옥션": "http://itemsearch.auction.co.kr/search?keyword={}",
            "인터파크": "http://shopping.interpark.com/search.do?keyword={}"
        }
    
    def fetch_page(self, url: str) -> Optional[str]:
        """웹 페이지 가져오기"""
        try:
            logger.info(f"페이지 요청 시작: {url}")
            response = self.session.get(url, timeout=5)  # 타임아웃을 5초로 단축
            response.raise_for_status()
            
            # 인코딩 설정
            if response.encoding:
                response.encoding = response.apparent_encoding
            
            logger.info(f"페이지 요청 성공: {url}")
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"페이지 가져오기 실패 {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"예상치 못한 오류 {url}: {e}")
            return None
    
    def extract_product_info(self, html_content: str, base_url: str = "") -> List[ScrapingResult]:
        """HTML에서 상품 정보 추출"""
        if not html_content:
            return []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            products = []
            
            # 다양한 상품 정보 선택자 패턴
            product_selectors = [
                # 일반적인 상품 컨테이너
                {'container': '.product', 'name': 'h2, h3, .product-name', 'price': '.price, .product-price', 'link': 'a'},
                {'container': '.product-item', 'name': 'h2, h3, .title', 'price': '.price, .cost', 'link': 'a'},
                {'container': '.item', 'name': '.name, .title, h3', 'price': '.price, .cost', 'link': 'a'},
                {'container': '.goods', 'name': '.goods-name, h3', 'price': '.price, .cost', 'link': 'a'},
                
                # 쿠팡 스타일
                {'container': '.search-product', 'name': '.name', 'price': '.price-value', 'link': 'a'},
                
                # 11번가 스타일  
                {'container': '.c_prd_item', 'name': '.prd_name', 'price': '.price_real', 'link': 'a'},
                
                # G마켓 스타일
                {'container': '.box__item-container', 'name': '.text__item', 'price': '.text_price', 'link': 'a'},
                
                # 일반적인 리스트 아이템
                {'container': 'li', 'name': 'h2, h3, .title, .name', 'price': '.price, .cost', 'link': 'a'},
                {'container': '.list-item', 'name': '.title, .name', 'price': '.price', 'link': 'a'}
            ]
            
            # 각 선택자 패턴으로 상품 정보 추출 시도
            for selector_config in product_selectors:
                containers = soup.select(selector_config['container'])
                
                for container in containers[:10]:  # 최대 10개까지만
                    try:
                        product_info = self._extract_single_product(container, selector_config, base_url)
                        if product_info and product_info.name and product_info.price:
                            products.append(product_info)
                    except Exception as e:
                        logger.debug(f"상품 정보 추출 오류: {e}")
                        continue
                
                # 상품을 찾았으면 다른 패턴은 시도하지 않음
                if products:
                    break
            
            return products[:5]  # 최대 5개 결과만 반환
            
        except Exception as e:
            logger.error(f"HTML 파싱 오류: {e}")
            return []
    
    def _extract_single_product(self, container, selector_config: Dict[str, str], base_url: str) -> Optional[ScrapingResult]:
        """단일 상품 정보 추출"""
        try:
            # 상품명 추출
            name_element = container.select_one(selector_config['name'])
            if not name_element:
                return None
            
            name = name_element.get_text(strip=True)
            if not name or len(name) < 2:
                return None
            
            # 가격 추출 개선
            price_element = container.select_one(selector_config['price'])
            if not price_element:
                # 가격이 없는 경우 다른 패턴으로 시도
                price_patterns = [
                    '.price', '.cost', '.amount', '[class*="price"]', '[class*="cost"]',
                    '.sale-price', '.final-price', '.current-price', '.product-price',
                    '[data-price]', '.price-now', '.price-real', '.price-value'
                ]
                for pattern in price_patterns:
                    price_element = container.select_one(pattern)
                    if price_element:
                        break
            
            price = "가격 정보 없음"
            price_numeric = 0
            if price_element:
                price_text = price_element.get_text(strip=True)
                # 가격에서 숫자만 추출하여 정렬을 위한 숫자값도 저장
                price_numbers = re.findall(r'[\d,]+', price_text)
                if price_numbers:
                    # 가장 큰 숫자를 가격으로 선택 (할인가가 아닌 정가를 피하기 위해)
                    numeric_values = [int(p.replace(',', '')) for p in price_numbers if len(p.replace(',', '')) >= 3]
                    if numeric_values:
                        price_numeric = min(numeric_values)  # 최소값을 실제 판매가로 추정
                        price = f"{price_numeric:,}원"
                elif re.search(r'\d', price_text):
                    price = price_text
            
            # 링크 추출
            link_element = container.select_one(selector_config['link'])
            url = ""
            if link_element and link_element.get('href'):
                href = link_element.get('href')
                if href.startswith('http'):
                    url = href
                elif base_url:
                    url = urljoin(base_url, href)
            
            # 설명 추출 (선택사항)
            description = ""
            desc_selectors = ['.description', '.summary', '.spec']
            for desc_sel in desc_selectors:
                desc_elem = container.select_one(desc_sel)
                if desc_elem:
                    description = desc_elem.get_text(strip=True)[:100]  # 최대 100자
                    break
            
            # 소스 판단
            source = "온라인쇼핑몰"
            if base_url:
                parsed_url = urlparse(base_url)
                domain = parsed_url.netloc.lower()
                if 'coupang' in domain:
                    source = "쿠팡"
                elif '11st' in domain:
                    source = "11번가"
                elif 'gmarket' in domain:
                    source = "G마켓"
                elif 'auction' in domain:
                    source = "옥션"
                elif 'interpark' in domain:
                    source = "인터파크"
            
            result = ScrapingResult(
                name=name,
                price=price,
                url=url,
                source=source,
                description=description
            )
            
            # 가격 정렬을 위한 숫자값 저장
            result._price_numeric = price_numeric
            
            return result
            
        except Exception as e:
            logger.debug(f"단일 상품 추출 오류: {e}")
            return None
    
    def search_products(self, query: str, max_results: int = 10) -> List[ScrapingResult]:
        """상품 검색 실행 - 가격 비교 강화"""
        if not query or not query.strip():
            return []
        
        all_products = []
        search_query = query.strip()
        
        # 더 많은 쇼핑몰에서 검색하여 가격 비교
        for source, url_pattern in self.search_urls.items():
            try:
                search_url = url_pattern.format(search_query.replace(' ', '+'))
                logger.info(f"{source}에서 검색 중: {search_url}")
                
                html_content = self.fetch_page(search_url)
                if html_content:
                    products = self.extract_product_info(html_content, search_url)
                    # 가격 정보가 있는 상품만 추가
                    valid_products = [p for p in products if hasattr(p, '_price_numeric') and p._price_numeric > 0]
                    all_products.extend(valid_products)
                
                # 요청 간 딜레이
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"{source} 검색 오류: {e}")
                continue
        
        # 결과 정리 및 중복 제거 (상품명 기준)
        unique_products = []
        seen_names = set()
        
        for product in all_products:
            # 상품명 정규화 (공백, 특수문자 제거)
            normalized_name = re.sub(r'[^\w가-힣]', '', product.name.lower())
            
            if normalized_name not in seen_names and len(normalized_name) > 2:
                seen_names.add(normalized_name)
                unique_products.append(product)
        
        # 가격순으로 정렬 (최저가부터)
        unique_products.sort(key=lambda x: getattr(x, '_price_numeric', float('inf')))
        
        return unique_products[:max_results]
    
    def format_search_results(self, products: List[ScrapingResult], query: str) -> str:
        """검색 결과를 사용자 중심의 의사결정 지원 형태로 포맷"""
        if not products:
            return f"""
🔍 **'{query}' 검색 결과가 없습니다.**

💡 **빠른 검색 개선 방법:**
⚡ **즉시 시도해보세요:**
- 더 구체적인 상품명: "{query} 128GB", "{query} 2024년"
- 브랜드명 추가: "삼성 {query}", "애플 {query}"
- 영문/한글 전환으로 재검색

🏃‍♂️ **5초만에 다시 찾기:**
- 핵심 키워드만 입력 (예: "아이폰15", "갤럭시S24")
- 숫자나 특수문자 제거하고 재시도
            """.strip()
        
        # 가격 정보가 있는 상품과 없는 상품 분리
        products_with_price = [p for p in products if hasattr(p, '_price_numeric') and p._price_numeric > 0]
        products_without_price = [p for p in products if not (hasattr(p, '_price_numeric') and p._price_numeric > 0)]
        
        # 결과 헤더 - 핵심 정보를 최상단에 노출
        result_text = f"🛒 **'{query}' 가격 비교 완료!** (총 {len(products)}개 발견)\n\n"
        
        if products_with_price:
            # 즉시 의사결정을 위한 핵심 정보 강조
            lowest_price = products_with_price[0]
            highest_price = products_with_price[-1] if len(products_with_price) > 1 else lowest_price
            
            # 🚀 즉시 결정 가이드
            result_text += "## 🚀 **즉시 결정 가이드**\n\n"
            result_text += f"💰 **추천 최저가**: {lowest_price.price} ← **{lowest_price.source}**\n"
            
            if len(products_with_price) > 1:
                price_diff = getattr(highest_price, '_price_numeric', 0) - getattr(lowest_price, '_price_numeric', 0)
                result_text += f"💡 **절약 효과**: 최대 {price_diff:,}원 절약 가능!\n"
                
                # 평균 가격 대비 절약 정보
                prices = [getattr(p, '_price_numeric', 0) for p in products_with_price]
                avg_price = sum(prices) / len(prices)
                savings_vs_avg = avg_price - getattr(lowest_price, '_price_numeric', 0)
                if savings_vs_avg > 0:
                    result_text += f"📊 **평균가 대비**: {savings_vs_avg:,.0f}원 저렴\n"
            
            result_text += "\n"
            
            # ⚡ 빠른 가격 비교표 - 스캔하기 쉬운 형태
            result_text += "## ⚡ **3초 가격 비교**\n\n"
            
            for i, product in enumerate(products_with_price[:5], 1):  # 상위 5개만 표시
                # 순위별 이모지와 가격 강조
                rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}위"
                
                # 가격 차이 표시 (2위부터)
                price_info = product.price
                if i > 1 and hasattr(product, '_price_numeric') and hasattr(lowest_price, '_price_numeric'):
                    price_diff = product._price_numeric - lowest_price._price_numeric
                    price_info += f" *(+{price_diff:,}원)*"
                
                result_text += f"{rank_emoji} **{product.source}**: {price_info}\n"
                
                # 상품명은 간단히 표시
                short_name = product.name[:30] + "..." if len(product.name) > 30 else product.name
                result_text += f"   📦 {short_name}\n\n"
            
            # 🎯 구매 결정 지원 정보
            if len(products_with_price) >= 2:
                result_text += "## 🎯 **구매 결정 지원**\n\n"
                
                # 가격대별 추천
                prices = [getattr(p, '_price_numeric', 0) for p in products_with_price]
                min_price = min(prices)
                max_price = max(prices)
                
                # 가격 분석
                result_text += f"💵 **가격 범위**: {min_price:,}원 ~ {max_price:,}원\n"
                
                if len(products_with_price) >= 3:
                    mid_idx = len(products_with_price) // 2
                    mid_product = products_with_price[mid_idx]
                    result_text += f"🎯 **중간 가격대**: {mid_product.price} ({mid_product.source})\n"
                
                # 쇼핑몰별 특징 힌트
                result_text += f"\n📝 **쇼핑 팁**:\n"
                unique_sources = list(set(p.source for p in products_with_price))
                if "쿠팡" in unique_sources:
                    result_text += "• 쿠팡: 로켓배송 빠른 배송 가능\n"
                if "11번가" in unique_sources:
                    result_text += "• 11번가: 할인 쿠폰 및 적립금 혜택\n"
                if "G마켓" in unique_sources:
                    result_text += "• G마켓: 스마일카드 추가 할인\n"
                
                result_text += "\n"
        
        # 가격 정보 없는 상품들 (간단히 처리)
        if products_without_price:
            result_text += "## 📋 **추가 확인 필요**\n\n"
            for product in products_without_price[:3]:  # 최대 3개만
                result_text += f"• **{product.name[:40]}...** ({product.source}) - 가격 확인 필요\n"
            result_text += "\n"
        
        # 💡 마지막 구매 전 체크리스트
        result_text += "## ✅ **구매 전 체크리스트**\n"
        result_text += "🚚 **배송비** 포함 최종 가격 확인\n"
        result_text += "🏷️ **할인 쿠폰** 및 적립금 혜택 확인\n"
        result_text += "⭐ **판매자 평점** 및 **상품 리뷰** 확인\n"
        result_text += "🛡️ **A/S 정책** 및 **교환/환불** 조건 확인\n\n"
        
        result_text += "⚡ **5분 안에 최적의 선택을 하셨습니다!**"
        
        return result_text 