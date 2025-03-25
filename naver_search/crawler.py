import os
import shutil
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def get_chrome_driver():
    """헤드리스 크롬 드라이버 설정 (Streamlit Cloud 호환)"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Streamlit Cloud의 Chrome 버전 확인
    try:
        chrome_version = subprocess.check_output(["chromium-browser", "--version"]).decode().strip()
        print(f"Detected Chrome version: {chrome_version}")
    except:
        print("Could not detect Chrome version")
    
    try:
        # Streamlit Cloud에서는 system Chromium과 ChromeDriver 사용
        driver = webdriver.Chrome(options=chrome_options)
        print("성공: 시스템 ChromeDriver 사용")
        return driver
    except Exception as e1:
        print(f"첫 번째 방법 실패: {str(e1)}")
        
        try:
            # 두 번째 방법: 명시적 경로 지정
            driver_path = "/usr/bin/chromedriver"
            if os.path.exists(driver_path):
                # 권한 확인 및 수정
                try:
                    os.chmod(driver_path, 0o755)  # 실행 권한 설정
                except:
                    pass
                    
                driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
                print("성공: 고정 경로 ChromeDriver 사용")
                return driver
            else:
                print(f"ChromeDriver가 {driver_path}에 존재하지 않음")
        except Exception as e2:
            print(f"두 번째 방법 실패: {str(e2)}")
            
            try:
                # 마지막 방법: WebDriver Manager 사용 시도
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("성공: WebDriverManager 사용")
                return driver
            except Exception as e3:
                error_message = f"Chrome 드라이버 초기화 실패:\n1) {str(e1)}\n2) {str(e2)}\n3) {str(e3)}"
                print(error_message)
                raise Exception(error_message)

def get_naver_keywords(search_query):
    """네이버 연관 검색어 크롤링"""
    driver = None
    try:
        driver = get_chrome_driver()
        
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
        try:
            related_keywords = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".api_subject_bx._related_box .keyword"))
            )
            for keyword in related_keywords:
                results["연관 검색어"].append(keyword.text)
            
        except:
            pass
        
        # 함께 많이 찾는 검색어 추출
        try:
            also_searched = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".Vswg4IEeZW7Er49y9Ynv.desktop_mode.api_subject_bx\
                                                     .sds-comps-text.sds-comps-text-ellipsis-1.sds-comps-text-type-body1.Z0vjYVhL1FzPk2dIMRIC"))
            )
            for keyword in also_searched:
                results["함께 많이 찾는 검색어"].append(keyword.text)
                
        except:
            pass
        
        # 인기주제 추출
        try:
            popular_topics = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "._0ar69x2aJ9m4OgcLLgB.desktop_mode.api_subject_bx\
                                                     .gtMPKdW185oeqQJX52p6.fds-comps-keyword-chip-text.KMVxnGU7z0BmkoiR0hFq"))
            )
            for topic in popular_topics:
                results["인기주제"].append(topic.text)
        except:
            pass
            
        return results  # 결과 반환
    except Exception as e:
        print(f"키워드 추출 중 오류 발생: {str(e)}")
        return []  # 오류 발생 시 빈 리스트 반환
    finally:
        # driver가 None이 아닌 경우에만 quit() 호출
        if driver is not None:
            try:
                driver.quit()
            except:
                pass

def create_keywords_dataframe(data):
    """데이터를 pandas DataFrame으로 변환"""
    max_length = max(len(data["연관 검색어"]), len(data["함께 많이 찾는 검색어"]), len(data["인기주제"]))
    
    df_data = {
        "연관검색어": data["연관 검색어"] + [''] * (max_length - len(data["연관 검색어"])),
        "함께 많이 찾는 검색어": data["함께 많이 찾는 검색어"] + [''] * (max_length - len(data["함께 많이 찾는 검색어"])),
        "인기주제": data["인기주제"] + [''] * (max_length - len(data["인기주제"]))
    }
    
    return pd.DataFrame(df_data) 