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

def get_naver_keywords(query):
    """네이버 연관 검색어 크롤링 (디버깅 버전)"""
    driver = None
    try:
        driver = get_chrome_driver()
        
        # 사람처럼 보이기 위한 User-Agent 설정
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
        
        # 네이버 접속
        print(f"[디버깅] 네이버 접속 시도: {query}")
        url = f"https://search.naver.com/search.naver?query={query}"
        driver.get(url)
        
        # 현재 URL 확인 (리다이렉트 여부 확인)
        current_url = driver.current_url
        print(f"[디버깅] 현재 URL: {current_url}")
        
        # 페이지 제목 확인 (봇 감지 페이지인지 확인)
        page_title = driver.title
        print(f"[디버깅] 페이지 제목: {page_title}")
        
        # 페이지 소스 일부분 확인
        source_sample = driver.page_source[:1000]
        print(f"[디버깅] 페이지 소스 샘플: {source_sample}")
        
        # 봇 감지 관련 텍스트 확인
        bot_indicators = ["로봇", "자동화", "비정상적인", "robot", "captcha", "unusual", "automated"]
        for indicator in bot_indicators:
            if indicator in driver.page_source:
                print(f"[디버깅] 봇 감지 가능성: '{indicator}' 텍스트 발견")
        
        # 점진적 대기 후 요소 확인
        wait_times = [3, 5, 8, 10]
        for wait in wait_times:
            time.sleep(wait)
            elements = driver.find_elements(By.CSS_SELECTOR, "._related_keyword_ul ._related_keyword_item")
            print(f"[디버깅] {wait}초 대기 후 요소 수: {len(elements)}")
            if elements:
                break
        
        # 나머지 로직 계속
        keywords = []
        for element in elements:
            keywords.append(element.text.strip())
        
        print(f"[디버깅] 최종 추출된 키워드: {keywords}")
        return keywords
        
    except Exception as e:
        print(f"[디버깅] 예외 발생: {str(e)}")
        # 예외 발생 시 스크린샷 저장 (가능한 경우)
        if driver:
            try:
                screenshot_path = f"error_screenshot_{int(time.time())}.png"
                driver.save_screenshot(screenshot_path)
                print(f"[디버깅] 스크린샷 저장됨: {screenshot_path}")
            except:
                pass
        return []
    finally:
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