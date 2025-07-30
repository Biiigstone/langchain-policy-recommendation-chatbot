"""
설정값 및 상수 정의
"""
import os
from typing import Dict, Any

# 디렉토리 경로
VDB_DIRECTORY = "../vectorDB/chroma_db_policy"
CODE_TABLE_FILE = "../data/code_table.xlsx"
COLLECTION_NAME = 'policy_collection_summary_added_openai_large_0730'

# 데이터베이스 연결 정보
DB_CONNECTION_INFO: Dict[str, Any] = {
    'host': 'localhost',
    'database': 'toyprj4',
    'user': 'root',
    'password': '1234'
}

# OpenAI 설정
OPENAI_MODEL = "gpt-4o"
OPENAI_TEMPERATURE = 0

# 메모리 설정
MEMORY_K = 2  # 최근 k개의 상호작용 기억

# Streamlit 설정
PAGE_TITLE = "나만의 정책 분석 챗봇"
PAGE_ICON = "🤖"
CHAT_TITLE = "🤖 청년 정책 추천 챗 봇"