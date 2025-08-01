# src/chains.py

from functools import partial

# LangChain 및 외부 모듈 import
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableWithMessageHistory

# 프로젝트 내부 모듈 import
from config import VDB_DIRECTORY, OPENAI_MODEL, OPENAI_TEMPERATURE
from database import get_db_connection, get_rdb_candidate_ids
from llm_utils import create_filter_from_query, format_docs
from retriever import semantic_search
from memory import get_session_history
from prompts import TEMPLATE_WITH_HISTORY, TEMPLATE_WITH_HISTORY_FOR_R


def create_final_chain(openai_client, code_map):
    """
    RAG 애플리케이션의 모든 체인을 조립하고 최종 실행 가능한 체인을 반환합니다.
    """
    # 0. 모델, 파서, 포맷터 정의
    model = ChatOpenAI(model=OPENAI_MODEL, temperature=OPENAI_TEMPERATURE)
    output_parser = StrOutputParser()
    formatted_docs_func = partial(format_docs, code_map=code_map)

    # 1. Retrieval 체인 정의
    # base_retrieval_chain = (
    #         RunnableLambda(lambda q: {"query": q})
    #         | RunnablePassthrough.assign(filters=lambda x: create_filter_from_query(openai_client, x["query"]))
    #         | RunnablePassthrough.assign(
    #     candidate_ids=lambda x: get_rdb_candidate_ids(get_db_connection(), x["filters"]))
    #         | RunnableLambda(lambda x: semantic_search(
    #     candidate_ids=x["candidate_ids"],
    #     original_query=x["query"],
    #     extracted_filters=x["filters"],
    #     vdb_directory=VDB_DIRECTORY
    # ))
    # )

    rephrase_question_chain = (
        TEMPLATE_WITH_HISTORY_FOR_R
        | model
        | output_parser
    )

    base_retrieval_chain = (
            RunnableLambda(lambda q: {"query": q})
            | RunnablePassthrough.assign(filters=lambda x: create_filter_from_query(openai_client, x["query"]))
            | RunnablePassthrough.assign(
        candidate_ids=lambda x: (
            # get_rdb_candidate_ids 함수를 실행하고 결과를 ids 변수에 저장
            ids := get_rdb_candidate_ids(get_db_connection(), x["filters"]),

            # --- 디버깅 출력 ---
            print("--- [DEBUG] 체인 중간 데이터 확인 ---"),
            print(f"RDB에서 가져온 ID 개수: {len(ids)}"),
            print(f"ID 리스트 앞 5개: {ids[:5] if ids else '없음'}"),
            print(f"첫 번째 ID의 타입: {type(ids[0]) if ids else 'ID 없음'}"),
            print("---------------------------------"),
            # --- 디버깅 출력 끝 ---

            # 최종적으로 ids를 반환
            ids
        )[-1]  # 튜플의 마지막 요소인 ids를 최종 결과로 사용
    )
            | RunnableLambda(lambda x: semantic_search(
        candidate_ids=x["candidate_ids"],
        original_query=x["query"],
        extracted_filters=x["filters"],
        vdb_directory=VDB_DIRECTORY
    ))
    )

    conversational_retrieval_chain = rephrase_question_chain | base_retrieval_chain

    # 2. 핵심 RAG 체인 조립
    rag_core_chain = (
            {
                "documents": conversational_retrieval_chain,
                "question": lambda x: x["question"],
                "chat_history": lambda x: x["chat_history"],
            }
            | RunnablePassthrough.assign(
        context=(lambda x: formatted_docs_func(x["documents"]))
    )
            | TEMPLATE_WITH_HISTORY
            | model
            | output_parser
    )

    # 3. 메모리 기능을 포함한 최종 체인 반환
    final_chain_with_memory = RunnableWithMessageHistory(
        rag_core_chain,
        get_session_history,
        input_messages_key="question",
        history_messages_key="chat_history",
    )
    return final_chain_with_memory