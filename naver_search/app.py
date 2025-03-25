import streamlit as st
import pandas as pd
import time
from crawler import get_naver_keywords, create_keywords_dataframe
import base64
from io import BytesIO
import traceback

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

# 디버깅 로그 저장용 리스트
if 'debug_logs' not in st.session_state:
    st.session_state['debug_logs'] = []

def log_debug(message):
    """디버깅 정보 로깅"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    st.session_state['debug_logs'].append(log_message)
    print(log_message)  # 콘솔에도 출력

def to_excel(df):
    """데이터프레임을 엑셀 바이트로 변환"""
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        return output.getvalue()
    except Exception as e:
        log_debug(f"엑셀 변환 오류: {str(e)}")
        return None

def get_excel_download_link(df, filename="데이터.xlsx"):
    """엑셀 다운로드 링크 생성"""
    try:
        val = to_excel(df)
        if val is None:
            log_debug("엑셀 데이터 생성 실패")
            return "엑셀 다운로드 링크 생성 실패"
        
        b64 = base64.b64encode(val)
        return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}">엑셀 파일 다운로드</a>'
    except Exception as e:
        log_debug(f"다운로드 링크 생성 오류: {str(e)}")
        return "다운로드 링크 생성 실패"

def create_keywords_dataframe(related_keywords):
    """연관 검색어로 데이터프레임 생성"""
    try:
        if not related_keywords:
            log_debug("비어있는 키워드 목록으로 DataFrame 생성 시도")
            return pd.DataFrame()
        
        log_debug(f"DataFrame 생성: {len(related_keywords)}개 키워드")
        df = pd.DataFrame({
            '연관 검색어': related_keywords
        })
        return df
    except Exception as e:
        log_debug(f"DataFrame 생성 오류: {str(e)}")
        return pd.DataFrame()

# 검색 버튼이 클릭되었을 때
if submit_button and query:
    with st.spinner("네이버에서 데이터를 가져오는 중..."):
        try:
            # 데이터 가져오기
            log_debug("크롤링 함수 호출 시작")
            results = get_naver_keywords(query)
            log_debug(f"크롤링 완료: {len(results)}개 결과")
            st.session_state.search_results = results
            st.session_state.searched_query = query
            
            # 성공 메시지
            st.success(f"'{query}' 검색 결과가 성공적으로 로드되었습니다!")
            
        except Exception as e:
            error_details = traceback.format_exc()
            log_debug(f"오류 발생: {str(e)}")
            log_debug(f"오류 상세: {error_details}")
            st.error(f"오류가 발생했습니다: {str(e)}")

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

# 디버깅 섹션
st.markdown("---")
with st.expander("디버깅 정보"):
    # 모듈 가져오기 상태 표시
    st.text(f"크롤러 모듈 가져오기: {st.session_state.get('crawler_import', '정보 없음')}")
    
    # 테스트 버튼
    if st.button("테스트 실행"):
        # 디버깅 로그 초기화
        st.session_state['debug_logs'] = []
        
        # 테스트 키워드로 크롤링 실행
        test_keyword = "파이썬"
        log_debug(f"테스트 키워드: {test_keyword}")
        
        try:
            log_debug("테스트 크롤링 시작")
            results = get_naver_keywords(test_keyword)
            log_debug(f"테스트 크롤링 완료: {len(results)}개 결과")
            log_debug(f"반환된 결과: {results}")
        except Exception as e:
            error_details = traceback.format_exc()
            log_debug(f"테스트 중 오류 발생: {str(e)}")
            log_debug(f"오류 상세: {error_details}")
    
    # 로그 지우기 버튼
    if st.button("로그 지우기"):
        st.session_state['debug_logs'] = []
        st.experimental_rerun()
    
    # 디버깅 로그 표시
    st.text("=== 디버깅 로그 ===")
    for log in st.session_state['debug_logs']:
        st.text(log) 