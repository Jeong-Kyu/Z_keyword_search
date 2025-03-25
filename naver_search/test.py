from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def get_naver_keywords(search_query):
    # 크롬 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 브라우저를 표시하지 않음
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # 웹드라이버 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 결과 저장용 딕셔너리
    results = {
        "연관 검색어": [],
        "함께 많이 찾는 검색어": [],
        "인기주제": []
    }

    # 네이버 검색 페이지 접속
    url = f"https://search.naver.com/search.naver?query={search_query}"
    driver.get(url)
    
    # 페이지 로딩 대기
    time.sleep(2)
    
# 연관검색어 추출
    related_keywords = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".main_pack .sc_new.cs_common_module.case_normal.color_5._fe_soccer"))
    )
    for keyword in related_keywords:
        results["연관 검색어"].append(keyword.text)
    print(related_keywords)
# 함께 많이 찾는 검색어 추출
    also_searched = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Vswg4IEeZW7Er49y9Ynv.desktop_mode.api_subject_bx\
                                                .sds-comps-text.sds-comps-text-ellipsis-1.sds-comps-text-type-body1.Z0vjYVhL1FzPk2dIMRIC"))
    )
    for keyword in also_searched:
        results["함께 많이 찾는 검색어"].append(keyword.text)
    print(also_searched)
# 인기주제 추출
    popular_topics = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "._0ar69x2aJ9m4OgcLLgB.desktop_mode.api_subject_bx\
                                                .gtMPKdW185oeqQJX52p6.fds-comps-keyword-chip-text.KMVxnGU7z0BmkoiR0hFq"))
    )
    for topic in popular_topics:
        results["인기주제"].append(topic.text)
    print(popular_topics)

if __name__ == "__main__":
    get_naver_keywords("리버풀")