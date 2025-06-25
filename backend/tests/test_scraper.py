import pytest
import requests
from unittest.mock import patch, Mock, MagicMock
from app.scraper import WebScraper, ScrapingResult


class TestWebScraper:
    """웹 스크래퍼 테스트"""
    
    def setup_method(self):
        """테스트 메서드 실행 전 설정"""
        self.scraper = WebScraper()
    
    def test_scraper_initialization(self):
        """스크래퍼 초기화 테스트"""
        assert self.scraper is not None
        assert hasattr(self.scraper, 'session')
        assert hasattr(self.scraper, 'search_urls')
        assert len(self.scraper.search_urls) > 0
    
    @patch('app.scraper.requests.Session.get')
    def test_fetch_page_success(self, mock_get):
        """페이지 가져오기 성공 테스트"""
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.text = "<html><body>Test content</body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # 테스트 실행
        result = self.scraper.fetch_page("https://test.com")
        
        # 검증
        assert result == "<html><body>Test content</body></html>"
        mock_get.assert_called_once()
    
    @patch('app.scraper.requests.Session.get')
    def test_fetch_page_failure(self, mock_get):
        """페이지 가져오기 실패 테스트"""
        # Mock에서 예외 발생
        mock_get.side_effect = Exception("Connection error")
        
        # 테스트 실행
        result = self.scraper.fetch_page("https://test.com")
        
        # 검증
        assert result is None
    
    def test_extract_product_info_with_valid_html(self):
        """유효한 HTML에서 상품 정보 추출 테스트"""
        html_content = """
        <div class="product">
            <h3 class="product-name">iPhone 15 Pro 128GB</h3>
            <span class="price">1,350,000원</span>
            <a href="/product/123">상품 보기</a>
        </div>
        <div class="product">
            <h3 class="product-name">갤럭시 S24 Ultra</h3>
            <span class="price">1,250,000원</span>
            <a href="/product/456">상품 보기</a>
        </div>
        """
        
        # 테스트 실행
        products = self.scraper.extract_product_info(html_content, "https://test.com")
        
        # 검증
        assert len(products) >= 1
        
        # 첫 번째 상품 검증
        product = products[0]
        assert product.name is not None
        assert len(product.name) > 0
        assert product.price is not None
        assert product.source == "온라인쇼핑몰"
    
    def test_extract_product_info_with_empty_html(self):
        """빈 HTML 테스트"""
        html_content = ""
        products = self.scraper.extract_product_info(html_content)
        
        assert products == []
    
    def test_extract_product_info_with_invalid_html(self):
        """유효하지 않은 HTML 테스트"""
        html_content = "<html><body>No products here</body></html>"
        products = self.scraper.extract_product_info(html_content)
        
        assert isinstance(products, list)
    
    @patch.object(WebScraper, 'fetch_page')
    @patch.object(WebScraper, 'extract_product_info')
    def test_search_products_success(self, mock_extract, mock_fetch):
        """상품 검색 성공 테스트"""
        # Mock 설정
        mock_fetch.return_value = "<html>Mock content</html>"
        
        # 가격 정보가 있는 상품 생성
        mock_product1 = ScrapingResult(
            name="iPhone 15 Pro",
            price="1,350,000원",
            url="https://test.com/1",
            source="쿠팡"
        )
        mock_product1._price_numeric = 1350000
        
        mock_product2 = ScrapingResult(
            name="iPhone 15 Pro (다른 판매자)",
            price="1,320,000원", 
            url="https://test.com/2",
            source="11번가"
        )
        mock_product2._price_numeric = 1320000
        
        mock_extract.return_value = [mock_product1, mock_product2]

        results = self.scraper.search_products("iPhone 15 Pro")
        
        assert len(results) >= 1
        # 가격순 정렬 확인 (최저가부터)
        if len(results) >= 2:
            assert results[0]._price_numeric <= results[1]._price_numeric
    
    def test_search_products_empty_query(self):
        """빈 검색어 테스트"""
        results = self.scraper.search_products("")
        assert results == []
        
        results = self.scraper.search_products(None)
        assert results == []
    
    def test_format_search_results_with_products(self):
        """상품이 있을 때 포맷팅 테스트"""
        # 가격 정보가 있는 상품 생성
        product1 = ScrapingResult(
            name="iPhone 15 Pro 128GB",
            price="1,350,000원",
            url="https://coupang.com/1",
            source="쿠팡",
            description="최신 iPhone"
        )
        product1._price_numeric = 1350000

        product2 = ScrapingResult(
            name="iPhone 15 Pro 256GB",
            price="1,550,000원",
            url="https://11st.co.kr/2", 
            source="11번가",
            description="대용량 모델"
        )
        product2._price_numeric = 1550000

        products = [product1, product2]
        result = self.scraper.format_search_results(products, "iPhone 15 Pro")
        
        # 새로운 포맷 검증
        assert "iPhone 15 Pro" in result
        assert "가격 비교 완료" in result
        assert "즉시 결정 가이드" in result
        assert "3초 가격 비교" in result
        assert "1,350,000원" in result
        assert "1,550,000원" in result
        assert "쿠팡" in result
        assert "11번가" in result
        assert "구매 결정 지원" in result
        assert "절약 효과" in result
        assert "구매 전 체크리스트" in result
        assert "5분 안에 최적의 선택" in result

    def test_format_search_results_empty(self):
        """상품이 없을 때 포맷팅 테스트"""
        result = self.scraper.format_search_results([], "존재하지않는상품")
        
        # 새로운 빈 결과 포맷 검증
        assert "검색 결과가 없습니다" in result
        assert "빠른 검색 개선 방법" in result
        assert "즉시 시도해보세요" in result
        assert "5초만에 다시 찾기" in result

    def test_format_search_results_without_price(self):
        """가격 정보가 없는 상품 포맷팅 테스트"""
        product = ScrapingResult(
            name="상품명만 있는 상품",
            price="가격 정보 없음",
            url="https://test.com",
            source="테스트몰"
        )
        # _price_numeric 속성이 없거나 0인 경우

        products = [product]
        result = self.scraper.format_search_results(products, "테스트")
        
        # 새로운 가격 없는 상품 포맷 검증
        assert "추가 확인 필요" in result
        assert "상품명만 있는 상품" in result
        assert "가격 확인 필요" in result

    def test_scraping_result_to_dict(self):
        """ScrapingResult 딕셔너리 변환 테스트"""
        result = ScrapingResult(
            name="테스트 상품",
            price="100,000원",
            url="https://test.com",
            source="테스트몰",
            description="테스트 설명"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["name"] == "테스트 상품"
        assert result_dict["price"] == "100,000원"
        assert result_dict["url"] == "https://test.com"
        assert result_dict["source"] == "테스트몰"
        assert result_dict["description"] == "테스트 설명"

    @patch('time.sleep')  # 테스트에서 실제 딜레이 방지
    @patch.object(WebScraper, 'fetch_page')
    def test_search_products_multiple_sources(self, mock_fetch, mock_sleep):
        """여러 쇼핑몰 검색 테스트"""
        mock_fetch.return_value = None  # 모든 요청이 실패하도록 설정
        
        results = self.scraper.search_products("iPhone")
        
        # fetch_page가 여러 번 호출되었는지 확인
        assert mock_fetch.call_count > 1
        assert isinstance(results, list)

    def test_price_extraction_patterns(self):
        """다양한 가격 패턴 추출 테스트"""
        html_patterns = [
            '<span class="price">150,000원</span>',
            '<div class="cost">200000원</div>',
            '<span class="sale-price">99,999원</span>',
            '<div data-price="300000">300,000원</div>',
        ]
        
        for pattern in html_patterns:
            html = f'<div class="product"><h3>상품</h3>{pattern}<a href="/test">링크</a></div>'
            products = self.scraper.extract_product_info(html)
            
            if products:
                assert products[0].price != "가격 정보 없음"


class TestScrapingResult:
    """스크래핑 결과 모델 테스트"""
    
    def test_scraping_result_creation(self):
        """스크래핑 결과 생성 테스트"""
        result = ScrapingResult(
            name="아이폰 15 Pro",
            price="1,200,000원",
            url="https://example.com/product/123",
            source="테스트쇼핑몰"
        )
        
        assert result.name == "아이폰 15 Pro"
        assert result.price == "1,200,000원"
        assert result.url == "https://example.com/product/123"
        assert result.source == "테스트쇼핑몰"
    
    def test_scraping_result_to_dict(self):
        """스크래핑 결과 딕셔너리 변환 테스트"""
        result = ScrapingResult(
            name="갤럭시 S24",
            price="900,000원",
            url="https://example.com/galaxy",
            source="온라인쇼핑"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["name"] == "갤럭시 S24"
        assert result_dict["price"] == "900,000원"
        assert result_dict["url"] == "https://example.com/galaxy"
        assert result_dict["source"] == "온라인쇼핑" 