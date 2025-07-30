
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import COLLECTION_NAME, VDB_DIRECTORY

def semantic_search(
        candidate_ids: list,
        original_query: str,
        extracted_filters: dict,
        vdb_directory: str,
        k: int = 5,
        fetch_k: int = 20,
        lambda_mult: float = 1.0
) -> list:
    '''
    전달받은 필터를 통해 사용자의 질문을 증강하고, 후보 인덱스 내에서만 R을 수행하여 검색 정확도를 높여 시멘틱 서칭을 수행하는 함수입니다.
    Args:
        candidate_ids (list): 검색할 후보 ID 목록입니다.
        original_query (str): 원본 검색 쿼리 문자열입니다.
        extracted_filters (dict): 추출된 필터 정보 딕셔너리입니다.
        vdb_directory (str): 벡터 데이터베이스 디렉토리 경로입니다.
        k (int, optional): 반환할 상위 검색 결과의 개수입니다. 기본값은 5입니다.
        fetch_k (int, optional): 유사도 검색을 위해 가져올 초기 결과의 개수입니다. 기본값은 20입니다.
        lambda_mult (float, optional): 재정렬(reranking) 시 사용되는 람다 값입니다. 기본값은 0.7입니다.
    '''
    if not candidate_ids:
        return []

    # 1. 보강된 검색어 생성
    boost_keywords = []
    # soft_filter_keys = ["job_status", "education_levels", "keywords", "categories"]
    soft_filter_keys = []
    for key in soft_filter_keys:
        if extracted_filters.get(key):
            boost_keywords.extend(extracted_filters[key])

    synthetic_query = original_query + " " + " ".join(list(set(boost_keywords)))
    print(f"\n--- Generated Vector Search Query ---\n{synthetic_query}\n")

    # 2. 임베딩 모델 및 ChromaDB 로드
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embedding_model,
        persist_directory=VDB_DIRECTORY
    )

    # 3. 필터가 적용된 Retriever 생성
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": k,
            "fetch_k": fetch_k,
            "lambda_mult": lambda_mult,
            "filter": {'plcyNo': {'$in': candidate_ids}}
        }
    )

    # 4. Retriever 실행 및 Document 리스트 반환
    docs = retriever.invoke(synthetic_query)

    return docs