from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.config import VDB_DIRECTORY
from dotenv import load_dotenv
load_dotenv()

print("ChromaDB 데이터 확인 스크립트 시작...")

try:
    vectorstore = Chroma(
        collection_name="policy_collection_summary_added_openai_large",
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-large"),
        persist_directory=VDB_DIRECTORY
    )

    print("컬렉션에서 문서 5개를 가져옵니다...")
    retrieved_docs = vectorstore._collection.get(limit=5, include=["metadatas"])

    print("\n--- [DEBUG] ChromaDB 실제 데이터 확인 ---")

    if not retrieved_docs or not retrieved_docs.get('metadatas'):
        print("오류: ChromaDB에서 문서를 가져올 수 없습니다.")
    else:
        for i, metadata in enumerate(retrieved_docs['metadatas']):
            print(f"--- 문서 {i + 1} 메타데이터 ---")
            print(metadata)  # 메타데이터 전체를 출력

            # plcyNo 키가 있는지, 있다면 그 값과 타입을 확인
            if 'plcyNo' in metadata:
                plcy_no = metadata.get('plcyNo')
                print(f"  plcyNo 값: {plcy_no}")
                print(f"  plcyNo 타입: {type(plcy_no)}")
            else:
                print("  'plcyNo' 라는 키가 메타데이터에 없습니다.")
            print("-" * 25)

except Exception as e:
    print(f"\n스크립트 실행 중 오류 발생: {e}")