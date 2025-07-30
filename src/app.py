# src/app.py

import streamlit as st
import uuid
from openai import OpenAI
from dotenv import load_dotenv

# 설정 및 내부 모듈 import
from config import PAGE_TITLE, PAGE_ICON, CHAT_TITLE
from utils import load_code_table
from chains import create_final_chain


# --- 1. 앱 구성 요소 초기화 (캐싱 사용) ---
@st.cache_resource
def initialize_components():
    """앱 구성 요소 초기화 - 한 번만 실행됨"""
    load_dotenv()
    openai_client = OpenAI()
    code_table_map = load_code_table()
    # 조립된 최종 체인을 생성하여 반환
    final_chain = create_final_chain(openai_client, code_table_map)
    return final_chain

# --- 2. 페이지 설정 및 체인 로드 ---
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON)
st.title(CHAT_TITLE)

# 초기화 함수를 호출하여 최종 체인을 가져옵니다.
final_chain_with_memory = initialize_components()


# --- 3. Streamlit UI 및 상호작용 로직 ---

# 세션 상태 초기화
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 대화 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("어떤 청년 정책이 궁금하신가요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성 및 표시
    with st.chat_message("assistant"):
        response_stream = final_chain_with_memory.stream(
            {"question": prompt},
            config={"configurable": {"session_id": st.session_state.session_id}}
        )
        full_response = st.write_stream(response_stream)

    st.session_state.messages.append({"role": "assistant", "content": full_response})