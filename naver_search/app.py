import streamlit as st
import pandas as pd
import time
from crawler import get_naver_keywords, create_keywords_dataframe
import base64
from io import BytesIO
# 배포 환경을 위한 추가 패키지
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# 페이지 설정
st.set_page_config(
    page_title="네이버 검색어 분석기",
    page_icon="🔍",
    layout="wide"
)

# 제목 및 소개
st.title("네이버 검색어 분석기 🔍")
st.markdown("""
이 앱은 네이버에서 특정 검색어에 대한 연관 정보를 추출합니다:
* **연관 검색어**
* **함께 많이 찾는 검색어**
* **인기주제**

사용방법: 아래 입력창에 검색어를 입력하고 '분석하기' 버튼을 클릭하세요.
""")

# 검색어 입력 섹션
with st.form(key="search_form"):
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("검색어 입력", placeholder="분석할 키워드를 입력하세요")
    with col2:
        submit_button = st.form_submit_button(label="분석하기")

# 결과를 세션 상태에 저장
if "search_results" not in st.session_state:
    st.session_state.search_results = None
    st.session_state.searched_query = None

# 엑셀 다운로드 함수
def get_excel_download_link(df, filename="keywords_data.xlsx"):
    """DataFrame을 엑셀 파일로 변환하고 다운로드 링크 생성"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Keywords')
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">엑셀 파일 다운로드</a>'
    return href

# 전역 변수로 디버깅 정보 저장
debug_logs = []

def log_debug(message):
    """디버깅 정보 로깅"""
    debug_logs.append(message)

# 검색 버튼이 클릭되었을 때
if submit_button and query:
    with st.spinner("네이버에서 데이터를 가져오는 중..."):
        try:
            # 데이터 가져오기
            results = get_naver_keywords(query)
            st.session_state.search_results = results
            st.session_state.searched_query = query
            
            # 성공 메시지
            st.success(f"'{query}' 검색 결과가 성공적으로 로드되었습니다!")
            
        except Exception as e:
            st.error(f"오류 발생: {str(e)}")

# 검색 결과가 있으면 표시
if st.session_state.search_results:
    st.subheader(f"'{st.session_state.searched_query}' 검색 결과")
    
    # 데이터프레임 생성
    df = create_keywords_dataframe(st.session_state.search_results)
    
    # 탭 생성
    tab1, tab2 = st.tabs(["카드 보기", "표 보기"])
    
    with tab1:
        # 3개의 열로 데이터 표시
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("연관 검색어")
            if st.session_state.search_results["연관 검색어"]:
                for keyword in st.session_state.search_results["연관 검색어"]:
                    st.markdown(f"- {keyword}")
            else:
                st.info("연관 검색어가 없습니다.")
        
        with col2:
            st.subheader("함께 많이 찾는 검색어")
            if st.session_state.search_results["함께 많이 찾는 검색어"]:
                for keyword in st.session_state.search_results["함께 많이 찾는 검색어"]:
                    st.markdown(f"- {keyword}")
            else:
                st.info("함께 많이 찾는 검색어가 없습니다.")
        
        with col3:
            st.subheader("인기주제")
            if st.session_state.search_results["인기주제"]:
                for topic in st.session_state.search_results["인기주제"]:
                    st.markdown(f"- {topic}")
            else:
                st.info("인기주제가 없습니다.")
    
    with tab2:
        # 테이블 보기
        st.dataframe(df, use_container_width=True)
    
    # 다운로드 버튼
    st.markdown("---")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("검색 결과를 엑셀 파일로 다운로드하세요:")
    
    with col2:
        filename = f"{st.session_state.searched_query}_keywords.xlsx"
        excel_link = get_excel_download_link(df, filename)
        st.markdown(excel_link, unsafe_allow_html=True)

# 페이지 하단 정보
st.markdown("---")
st.markdown("© 네이버 검색어 분석기 | 데이터는 네이버로부터 수집됩니다.")

def main():
    # 디버깅 섹션 추가 (항상 표시)
    st.subheader("디버깅 정보")
    if st.button("테스트 실행"):
        # 디버깅 로그 초기화
        global debug_logs
        debug_logs = []
        
        # 테스트 키워드로 크롤링 실행
        test_keyword = "파이썬"
        log_debug(f"테스트 키워드: {test_keyword}")
        
        try:
            from crawler import get_naver_keywords
            results = get_naver_keywords(test_keyword)
            log_debug(f"반환된 결과: {results}")
        except Exception as e:
            log_debug(f"에러 발생: {str(e)}")
    
    # 디버깅 로그 표시
    for log in debug_logs:
        st.text(log)

    # 검색어 입력 필드 등 기존 코드
    
    # 디버깅 섹션 추가
    with st.expander("디버깅 정보"):
        if st.button("디버깅 테스트 실행"):
            debug_info = []
            # 디버깅 함수로 수정 (출력 대신 리스트에 정보 추가)
            def debug_print(info):
                debug_info.append(info)
                
            # 여기서 크롤링 코드 실행하고 debug_print 함수 사용
            # ... 크롤링 코드 ...
            
            # 디버깅 정보 표시
            for info in debug_info:
                st.text(info) 