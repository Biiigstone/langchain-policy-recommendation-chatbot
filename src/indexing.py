'''
인덱싱 스크립트

page_content로 사용한 컬럼 : document

--- metadata로 사용한 컬럼 ---
정책 기본 정보
plcyNo: 정책번호
plcyNm: 정책명
plcyKywdNm: 정책키워드명
plcyExplnCn: 정책설명내용
lclsfNm: 정책대분류명
mclsfNm: 정책중분류명
plcySprtCn: 정책지원내용
plcyPvsnMthdCd: 정책제공방법코드

기관 정보
rgtrInstCdNm: 등록기관코드명

기간 정보
aplyPrdSeCd: 신청기간구분코드
bizPrdSeCd: 사업기간구분코드
bizPrdBgngYmd: 사업기간시작일자
bizPrdEndYmd: 사업기간종료일자
bizPrdEtcCn: 사업기간기타내용
aplyYmd: 신청기간
frstRegDt: 최초등록일시
lastMdfcnDt: 최종수정일시

신청 및 방법 정보

plcyAplyMthdCn: 정책신청방법내용
srngMthdCn: 심사방법내용
sbmsnDcmntCn: 제출서류내용
aplyUrlAddr: 신청URL주소

지원 조건
sprtSclLmtYn: 지원규모제한여부
sprtTrgtMinAge: 지원대상최소연령
sprtTrgtMaxAge: 지원대상최대연령
sprtTrgtAgeLmtYn: 지원대상연령제한여부
mrgSttsCd: 결혼상태코드
earnMinAmt: 소득최소금액
earnMaxAmt: 소득최대금액
earnEtcCn: 소득기타내용
addAplyQlfcCndCn: 추가신청자격조건내용
ptcpPrpTrgtCn: 참여제안대상내용

요건 코드(타겟)
zipCd: 정책거주지역코드
plcyMajorCd: 정책전공요건코드
jobCd: 정책취업요건코드
schoolCd: 정책학력요건코드
sbizCd: 정책특화요건코드

기타
etcMttrCn: 기타사항내용
refUrlAddr1: 참고URL주소1
refUrlAddr2: 참고URL주소2


'''

import csv
import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

import utils


def create_documents_from_csv(csv_file_path: str) -> list[Document]:
    """
    CSV 파일에서 정책 정보를 읽어와
    LangChain의 Document 객체 리스트로 변환합니다.

    - 각 row는 하나의 정책 데이터를 나타냅니다.
    - 서술형 정보는 page_content로 조합합니다.
    - 정형 정보는 metadata로 저장합니다.
    """

    documents = []

    try:
        # UTF-8 인코딩으로 CSV 파일을 엽니다.
        with open(csv_file_path, mode='r', encoding='utf-8-sig') as csvfile:
            # 각 row를 딕셔너리 형태로 읽어옵니다.
            reader = csv.DictReader(csvfile)

            for row in reader:
                # 1. page_content 구성: 검색의 대상이 될 자연어 텍스트
                page_content = row.get('document')

                # 2. metadata 구성: 필터링 및 출처 표시에 사용할 정형 데이터
                # 항상 원본값 그대로
                metadata = {
                    # 정책 기본 정보
                    "plcyNo": row.get('plcyNo', '정보 없음'),
                    "plcyNm": row.get('plcyNm', '정보 없음'),
                    "plcyKywdNm": row.get('plcyKywdNm', '정보 없음'),
                    "plcyExplnCn": row.get('plcyExplnCn', '정보 없음'),
                    "lclsfNm": row.get('lclsfNm', '정보 없음'),
                    "mclsfNm": row.get('mclsfNm', '정보 없음'),
                    "plcySprtCn": row.get('plcySprtCn', '정보 없음'),
                    "plcyPvsnMthdCd": row.get('plcyPvsnMthdCd', '정보 없음'),

                    # 기관 정보
                    "rgtrUpInstCdNm": row.get('rgtrUpInstCdNm', '정보 없음'),

                    # 기간 정보
                    "aplyPrdSeCd": row.get('aplyPrdSeCd', '정보 없음'),
                    "bizPrdSeCd": row.get('bizPrdSeCd', '정보 없음'),
                    "bizPrdBgngYmd": row.get('bizPrdBgngYmd', '정보 없음'),
                    "bizPrdEndYmd": row.get('bizPrdEndYmd', '정보 없음'),
                    "bizPrdEtcCn": row.get('bizPrdEtcCn', '정보 없음'),
                    "aplyYmd": row.get('aplyYmd', '정보 없음'),
                    "frstRegDt": row.get('frstRegDt', '정보 없음'),
                    "lastMdfcnDt": row.get('lastMdfcnDt', '정보 없음'),

                    # 신청 및 방법
                    "plcyAplyMthdCn": row.get('plcyAplyMthdCn', '정보 없음'),
                    "srngMthdCn": row.get('srngMthdCn', '정보 없음'),
                    "sbmsnDcmntCn": row.get('sbmsnDcmntCn', '정보 없음'),
                    "aplyUrlAddr": row.get('aplyUrlAddr', '정보 없음'),

                    # 지원 조건
                    "sprtSclLmtYn": row.get('sprtSclLmtYn', '정보 없음'),
                    "sprtTrgtMinAge": row.get('sprtTrgtMinAge', '정보 없음'),
                    "sprtTrgtMaxAge": row.get('sprtTrgtMaxAge', '정보 없음'),
                    "sprtTrgtAgeLmtYn": row.get('sprtTrgtAgeLmtYn', '정보 없음'),
                    "mrgSttsCd": row.get('mrgSttsCd', '정보 없음'),
                    "earnMinAmt": row.get('earnMinAmt', '정보 없음'),
                    "earnMaxAmt": row.get('earnMaxAmt', '정보 없음'),
                    "earnEtcCn": row.get('earnEtcCn', '정보 없음'),
                    "addAplyQlfcCndCn": row.get('addAplyQlfcCndCn', '정보 없음'),
                    "ptcpPrpTrgtCn": row.get('ptcpPrpTrgtCn', '정보 없음'),

                    # 요건 코드(target, 대상)
                    "zipCd": row.get('zipCd', '정보 없음'),
                    "plcyMajorCd": row.get('plcyMajorCd', '정보 없음'),
                    "jobCd": row.get('jobCd', '정보 없음'),
                    "schoolCd": row.get('schoolCd', '정보 없음'),
                    "sbizCd": row.get('sbizCd', '정보 없음'),

                    # 기타
                    "etcMttrCn": row.get('etcMttrCn', '정보 없음'),
                    "refUrlAddr1": row.get('refUrlAddr1', '정보 없음'),
                    "refUrlAddr2": row.get('refUrlAddr2', '정보 없음'),

                }

                documents.append(Document(page_content=page_content.strip(), metadata=metadata))

    except FileNotFoundError:
        print(f"오류: '{csv_file_path}' 파일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    return documents

def setup_vectorstore(collection_name: str, embedding_model, persist_directory: str):
    # "policy_collection_augmented_summary_added_openai_large"
    # "./chroma_db_policy"
    vectorstore = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        persist_directory=persist_directory
    )
    return vectorstore


def add_to_chroma_in_batches(docs: list[Document], batch_size: int = 100):
    """문서 리스트를 배치로 나누어 ChromaDB에 추가합니다."""

    # 전체 문서 리스트를 batch_size만큼 건너뛰며 반복
    for i in range(0, len(docs), batch_size):
        # 현재 처리할 배치 슬라이싱
        batch = docs[i:i + batch_size]

        # 현재 배치만 DB에 추가
        vectorstore.add_documents(documents=batch)

        # 진행 상황 출력
        print(f"Batch {i // batch_size + 1}/{(len(docs) - 1) // batch_size + 1} 처리 완료 ({len(batch)}개 문서 추가)")


if __name__ == '__main__':

    COLLECTION_NAME = "policy_collection_summary_added_openai_large_0730"
    VECTOR_DB_PATH = '../vectorDB/chroma_db_policy'
    CSV_PATH = '../data/policies_with_documents_final2.csv'

    load_dotenv()

    # 임베딩 모델 준비
    # embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=os.getenv("OPENAI_API_KEY"))

    # Chroma DB 준비
    vectorstore = setup_vectorstore(COLLECTION_NAME, embedding_model, VECTOR_DB_PATH)

    docs = create_documents_from_csv(CSV_PATH)

    avg = 0
    for i in docs:
        token_count = utils.count_tokens(i.page_content)
        avg += token_count
        if token_count >= 1000:
            print(f'토큰 수 1000 이상! 토큰 수 : {token_count}')

    print(f'총 토큰 수 : {avg}')

    try:
        add_to_chroma_in_batches(docs, 200)
    except Exception as e:
        print('문서 임베딩 중 오류 발생!')
        print(e)
