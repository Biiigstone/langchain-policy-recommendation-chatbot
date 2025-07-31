🧠 고성능 정책 추천 RAG 챗봇 (Advanced RAG Chatbot for Policy Recommendation)
정형화된 API 응답 데이터를 기반으로, 사용자의 복잡한 자연어 질문에 대해 정확하고 신뢰성 있는 답변을 제공하는 고성능 RAG 챗봇 프로젝트입니다.

단순히 RAG 파이프라인을 구현하는 것을 넘어, 데이터의 본질적인 특성을 분석하고 LLM의 내재적 한계를 극복하기 위한 아키텍처 최적화에 중점을 두었습니다.

🚀 핵심 아키텍처 및 특징 (Key Architecture & Features)
본 프로젝트는 RAG의 성능이 검색(Retrieval)의 정확성과 생성(Generation)의 충실도에 의해 결정된다는 전제하에, 두 단계를 독립적으로 최적화하는 데이터 이원화(Dualization) 전략을 핵심 아키텍처로 채택했습니다.

1. 검색 최적화 (Retrieval Optimization)
사용자의 어떤 질문에도 가장 관련성 높은 '정책' 자체를 정확하게 찾아내기 위해 다음 전략을 사용합니다.

가. 의미론적 문서화 (Semantic Documentarization)
정형 데이터를 그대로 임베딩하는 대신, 사용자의 질문 의도를 예측하여 검색에 핵심적인 정보(정책명, 지원내용, 자격요건 등)만을 선별했습니다. 이를 시맨틱 검색에 유리한 자연스러운 설명문(document)으로 가공하여, 검색 정확도를 극대화했습니다.

효과: 불필요한 노이즈를 제거하고, 풍부한 문맥 정보를 제공하여 검색 품질 향상

나. 데이터 특성에 기반한 '청킹 배제' 전략
"하나의 정책은 완결된 하나의 의미 단위"라는 데이터 특성에 집중하여, 일반적인 청킹을 의도적으로 배제했습니다.

이유: 인위적인 청킹은 오히려 정책 정보의 유기적인 맥락을 파괴하여, 복합적인 질문에 대한 검색 성능을 저해할 수 있다고 판단했습니다. '의미론적 문서화' 과정이 이미 노이즈를 제거하는 **'논리적 청킹'**의 역할을 수행합니다.

2. 생성 최적화 (Generation Optimization)
검색된 정책에 대해, 정보 손실 없이 가장 정확하고 풍부한 답변을 생성하기 위해 다음 전략을 사용합니다.

가. 동적 컨텍스트 재구성 (Dynamic Context Re-generation)
검색과 생성에 사용되는 정보를 완전히 분리했습니다.

데이터 저장:

page_content: 검색용으로 가공된 document 저장 (오직 검색용)

metadata: 원본 데이터의 모든 컬럼 저장 (생성용 재료)

동적 재구성:

추론 시점, 검색된 문서의 metadata를 활용하여 LLM에게 전달할 최종 컨텍스트를 실시간으로 재구성합니다. 이 과정에서 검색용 문서에는 없었던 신청 URL 등의 모든 정보를 포함시켜 전달합니다.

효과: 검색의 정확도와 답변의 충실도를 동시에 달성

3. 'Lost in the Middle' 현상 완화 전략
LLM이 긴 컨텍스트의 중간 정보를 놓치는 내재적 한계를 극복하기 위해 다층적 방어 전략을 적용했습니다.

프롬프트 구조 최적화: 가장 중요한 정보인 재구성된 컨텍스트를 프롬프트의 가능한 마지막 단에 배치하여 LLM의 Attention을 확보합니다.

컨텍스트 길이 제어: Chat History의 길이를 최근 2개의 대화로 제한하여 전체 프롬프트의 길이를 제어하고, 핵심 정보가 중간에 묻힐 위험을 최소화합니다.

🛠️ 기술 스택 (Tech Stack)
Language: Python

Framework: FastAPI, LangChain

LLM: (사용한 모델명, e.g., OpenAI GPT-4, Google Gemini)

Embedding Model: (사용한 모델명, e.g., text-embedding-3-small, ko-sbert-nli)

Vector DB: (사용한 DB명, e.g., FAISS, ChromaDB)

⚙️ 설치 및 실행 (Setup & Run)
# 1. 저장소 클론
`git clone https://github.com/your-username/your-repo-name.git`
`cd your-repo-name`

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

# 3. 필요 패키지 설치
`pip install -r requirements.txt`

# 4. 환경 변수 설정
.env 파일을 생성하고 아래 내용을 채워주세요.
OPENAI_API_KEY="YOUR_API_KEY"

# 5. FastAPI 서버 실행
uvicorn main:app --reload

📈 향후 개선 과제 (Future Work)
Re-ranker 모델 도입: 검색된 문서들의 우선순위를 질문과의 관련도에 따라 다시 계산하여, 가장 중요한 문서를 선별하고 프롬프트의 최후미에 배치함으로써 'Lost in the Middle' 현상을 보다 직접적으로 해결.

전처리 자동화: '의미론적 문서화' 과정을 LLM을 활용하여 자동 생성하는 파이프라인을 구축하여, 데이터 확장성과 유지보수 효율성 증대.