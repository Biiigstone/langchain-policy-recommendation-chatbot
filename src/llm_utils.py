'''
파서 함수 : 사용자의 질문을 받아 JSON 스키마에 맞춰 필터를 생성하는 함수.
'''

import json
from openai import OpenAI


def create_filter_from_query(client: OpenAI, user_query: str) -> dict:
    """
    사용자의 자연어 질문을 분석하고,
    정책 필터링에 사용할 구조화된 JSON(파이썬 딕셔너리)을 생성합니다.

    Args:
        client: 초기화된 OpenAI 클라이언트 객체
        user_query: 사용자의 원본 질문 문자열

    Returns:
        추출된 필터 정보가 담긴 딕셔너리
    """
    # LLM에게 전달할 시스템 프롬프트. 역할, 지시사항, 허용 값, JSON 스키마를 명시합니다.
    system_prompt = """
# ROLE
You are an expert at extracting key information for filtering South Korean youth policies from a user's query.

# INSTRUCTION
- Analyze the user's query and generate a JSON object that strictly follows the provided `JSON SCHEMA`.
- CRITICAL: When extracting regions, you MUST normalize them to their full official administrative names. (e.g., "서울", "서울시" -> "서울특별시" / "경기" -> "경기도" / "부산" -> "부산광역시" / "성남" -> "성남시" / "종로" -> "종로구")
- For fields with `ALLOWED VALUES`, you MUST choose from the provided list. If a user's term is a synonym, map it to the correct value (e.g., "실업자" -> "미취업").
- If a value is not mentioned, use `null` for single values or an empty list `[]` for array values.
- Do NOT make up values that are not in the `ALLOWED VALUES` list.
- Output ONLY the JSON object.

# ALLOWED VALUES
- 'job_status': ["재직자", "자영업자", "미취업자", "프리랜서", "일용근로자",
"(예비)창업자", "단기근로자", "영농종사자", "기타", "제한없음"]
- 'marriage_status': ["기혼", "미혼", "제한없음"]
- 'education_levels': ["고졸 미만", "고교 재학", "고졸 예정", "고교 졸업", "대학 재학", "대졸 예정",
"대학 졸업", "석·박사", "기타", "제한없음"]
- 'majors': ["인문계열", "사회계열", "상경계열", "이학계열", "공학계열", 
"예체능계열", "농산업계열", "기타", "제한없음"]
- 'categories': ["일자리", "주거", "교육", "복지문화", "참여권리"]
- 'subcategories': ["취업", "재직자", "창업", "주택 및 거주지", "기숙사",
"전월세 및 주거급여 지원", "미래역량강화", "교육비지원", "온라인교육", "취약계층 및 금융지원",
"건강", "예술인지원", "문화활동", "청년참여", "정책인프라구축", "청년국제교류", "권익보호"]
- 'specializations': ["중소기업", "여성", "기초생활수급자", "한부모가정", "장애인",
"농업인", "군인", "지역인재", "기타", "제한없음"]
- 'keywords': ["대출", "보조금", "바우처", "금리혜택", "교육지원", "맞춤형상담서비스",
"인턴", "벤처", "중소기업", "청년가장", "장기미취업청년", "공공임대주택",
"신용회복", "육아", "출산", "해외진출", "주거지원"]


# JSON SCHEMA
{
  "age": "number | null",
  "income": "number | null",
  "regions": ["string"],
  "job_status": ["string"],
  "marriage_status": "string | null",
  "education_levels": ["string"],
  "majors": ["string"],
  "categories": ["string"],
  "subcategories": ["string"],
  "specializations": ["string"],
  "keywords": ["string"]
}

# EXAMPLES
---
user_query: "서울 사는 25세 미취업자인데, 창업 지원금 좀 알아봐줘"
{
  "age": 25,
  "income": null,
  "regions": ["서울특별시"],
  "job_status": ["미취업자", "(예비)창업자"],
  "marriage_status": null,
  "education_levels": [],
  "majors": [],
  "categories": ["일자리"],
  "subcategories": ["창업"],
  "specializations": [],
  "keywords": ["보조금", "벤처"]
}
---
user_query: "강원 춘천에 거주하는 고졸 학력으로 지원 가능한 주거 대출 정책 있어?"
{
  "age": null,
  "income": null,
  "regions": ["강원특별자치도", "춘천시"],
  "job_status": [],
  "marriage_status": null,
  "education_levels": ["고교 졸업"],
  "majors": [],
  "categories": ["주거"],
  "subcategories": ["주택 및 거주지", "기숙사", "전월세 및 주거급여 지원"],
  "specializations": [],
  "keywords": ["대출"]
}
---
user_query: "목포에 사는 사람인데 석사 지원 정책같은거 있냐"
{
  "age": null,
  "income": null,
  "regions": ["전라남도", "목포시"],
  "job_status": [],
  "marriage_status": null,
  "education_levels": ["석·박사"],
  "majors": [],
  "categories": [],
  "subcategories": [],
  "specializations": [],
  "keywords": []
}

---
user_query: "전국 단위로 지원해주는 청년 창업 정책 알려줘"
{
  "age": null,
  "income": null,
  "regions": [],
  "job_status": ["(예비)창업자"],
  "marriage_status": null,
  "education_levels": [],
  "majors": [],
  "categories": ["일자리"],
  "subcategories": ["창업"],
  "specializations": [],
  "keywords": []
}
"""

    try:
        # OpenAI API 호출
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]
        )

        # 반환된 JSON 문자열을 파이썬 딕셔너리로 파싱
        result = json.loads(response.choices[0].message.content)
        return result

    except Exception as e:
        print(f"An error occurred: {e}")
        return {}


# metadata to context 포맷팅 함수
import pandas as pd
from functools import partial

# from langchain_core.documents import Document # 실제 LangChain 환경에서 사용
# from langchain_core.runnables import RunnableParallel, RunnablePassthrough # 실제 LCEL 구성 시 사용

# =================================================================
# 1. 엑셀 파일 로드 및 파싱하여 CODE_TABLE_MAP 생성
# =================================================================
CODE_TABLE_MAP = {}
excel_file_path = 'code_table.xlsx'  # .py 파일과 같은 위치에 있는 엑셀 파일명
sheet_name_to_read = '코드정보'  # 읽어올 시트 이름

try:
    # 엑셀 파일의 '코드정보' 시트에서 데이터를 읽어옵니다.
    df_codes = pd.read_excel(excel_file_path, sheet_name=sheet_name_to_read)

    # '분류' 열의 비어있는 값을 바로 위의 값으로 채웁니다 (엑셀의 병합된 셀 처리).
    df_codes['분류'] = df_codes['분류'].ffill()

    # 데이터프레임을 순회하며 코드 맵을 구성합니다.
    for _, row in df_codes.iterrows():
        category = row['분류']
        # 코드 값은 문자열로 변환하여 일관성을 유지합니다.
        code = str(row['코드'])
        value = row['코드내용']

        if category not in CODE_TABLE_MAP:
            CODE_TABLE_MAP[category] = {}
        CODE_TABLE_MAP[category][code] = value
    print(f"✅ 엑셀 파일('{excel_file_path}')을 성공적으로 로드하고 파싱했습니다.")

except FileNotFoundError:
    print(f"⚠️ 경고: '{excel_file_path}' 파일을 찾을 수 없습니다. 코드 변환이 비활성화됩니다.")
except Exception as e:
    print(f"������ 오류: 엑셀 파일 처리 중 오류 발생: {e}")

# metadata to context 포맷팅 함수


def format_docs(docs: list, code_map: dict) -> str:
    """
    (최종본) Retriever의 Document 리스트와 코드 테이블을 받아,
    모든 metadata 필드를 활용하여 LLM이 이해하기 좋은 상세한 Markdown 형식으로 변환합니다.
    값이 없는 필드는 출력하지 않아 안정성을 높였습니다.
    """

    # --- Helper Functions ---
    def get_code_value(category: str, code) -> str:
        """코드 테이블(code_map)을 조회하여 코드에 해당하는 명칭을 반환합니다."""
        if not category or pd.isna(code) or code == '':
            return ""

        code_str = str(code)
        if code_str.endswith('.0'):
            code_str = code_str[:-2]

        # 디버깅 출력 (필요시 주석 해제)
        # print(f"[DEBUG] get_code_value - category: {category}, code: {code_str}")

        # 1. 직접 매칭 시도
        if code_str in code_map.get(category, {}):
            return code_map[category][code_str]

        # 2. 앞의 00과 뒤의 0을 제거하고 시도 (0049010 -> 49001)
        if code_str.startswith('00') and code_str.endswith('0'):
            clean_code = code_str[2:-1]  # 00xxxxx0 -> xxxxx
            if clean_code in code_map.get(category, {}):
                return code_map[category][clean_code]

        # 3. 앞의 0들을 모두 제거하고 시도 (0049010 -> 49010)
        clean_code = code_str.lstrip('0')
        if clean_code in code_map.get(category, {}):
            return code_map[category][clean_code]

        # 4. 뒤의 0을 제거하고 시도 (49010 -> 4901)
        if code_str.endswith('0'):
            clean_code = code_str[:-1]
            if clean_code in code_map.get(category, {}):
                return code_map[category][clean_code]

            # 5. 앞의 0도 제거하고 뒤의 0도 제거 (0049010 -> 4901)
            clean_code = code_str.lstrip('0')[:-1]
            if clean_code in code_map.get(category, {}):
                return code_map[category][clean_code]

        # 6. 코드를 찾을 수 없는 경우 디버깅 정보 출력
        print(f"⚠️ 코드를 찾을 수 없음 - category: {category}, code: {code_str}")
        if category in code_map:
            # 해당 카테고리의 키 샘플 출력
            sample_keys = list(code_map[category].keys())[:5]
            print(f"   카테고리 '{category}'의 키 샘플: {sample_keys}")

        return f"코드({code_str})"

    def format_date(date_str: str) -> str:
        """'YYYYMMDD' 형식의 문자열을 'YYYY-MM-DD'로 변환합니다."""
        if date_str and isinstance(date_str, str) and len(date_str) == 8:
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        return date_str

    def format_bool(bool_str: str) -> str:
        """'Y'는 '예', 'N'은 '아니오'로 변환합니다."""
        if bool_str == 'Y': return '예'
        if bool_str == 'N': return '아니오'
        return ''

    # --- Main Loop ---
    formatted_strings = []
    for i, doc in enumerate(docs):
        meta = doc.metadata
        doc_string = f"--- [문서 {i + 1}: {meta.get('plcyNm', '제목 없음')}] ---\n"

        # 각 섹션의 내용을 동적으로 구성
        sections = {}

        # 기본 정보
        basic_info = []
        if meta.get('plcyNo'): basic_info.append(f"- **정책 ID**: {meta.get('plcyNo')}")
        if meta.get('plcyNm'): basic_info.append(f"- **정책명**: {meta.get('plcyNm')}")
        if meta.get('plcyExplnCn'): basic_info.append(f"- **정책 요약**: {meta.get('plcyExplnCn')}")
        if meta.get('lclsfNm') and meta.get('mclsfNm'): basic_info.append(
            f"- **분류**: {meta.get('lclsfNm')} > {meta.get('mclsfNm')}")
        if meta.get('plcyKywdNm'): basic_info.append(f"- **정책 키워드**: {meta.get('plcyKywdNm')}")
        if basic_info: sections["기본 정보"] = basic_info

        # 지원 내용
        support_info = []
        if meta.get('plcySprtCn'): support_info.append(f"- **상세 지원 내용**: \n{meta.get('plcySprtCn')}")
        if get_code_value('plcyPvsnMthdCd', meta.get('plcyPvsnMthdCd')): support_info.append(
            f"- **지원 방식**: {get_code_value('plcyPvsnMthdCd', meta.get('plcyPvsnMthdCd'))}")
        if format_bool(meta.get('sprtSclLmtYn')): support_info.append(
            f"- **지원 규모 제한 여부**: {format_bool(meta.get('sprtSclLmtYn'))}")
        if support_info: sections["지원 내용"] = support_info

        # 신청 및 기간
        apply_info = []
        if meta.get('bizPrdBgngYmd') or meta.get('bizPrdEndYmd'): apply_info.append(
            f"- **사업 기간**: {format_date(meta.get('bizPrdBgngYmd'))} ~ {format_date(meta.get('bizPrdEndYmd'))}")
        if meta.get('bizPrdEtcCn'): apply_info.append(f"- **사업 기간 설명**: {meta.get('bizPrdEtcCn')}")
        if meta.get('aplyYmd'): apply_info.append(f"- **지원 기간**: {meta.get('aplyYmd')}")
        if meta.get('plcyAplyMthdCn'): apply_info.append(f"- **신청 방법**: {meta.get('plcyAplyMthdCn')}")
        if meta.get('aplyUrlAddr'): apply_info.append(f"- **신청 사이트**: {meta.get('aplyUrlAddr')}")
        if meta.get('sbmsnDcmntCn'): apply_info.append(f"- **제출 서류**: {meta.get('sbmsnDcmntCn')}")
        if apply_info: sections["신청 및 기간"] = apply_info

        # 지원 대상 조건
        target_info = []
        if meta.get('sprtTrgtAgeLmtYn') == 'Y':
            min_age = int(float(meta.get('sprtTrgtMinAge', 0)))
            max_age = int(float(meta.get('sprtTrgtMaxAge', 0)))

            if min_age == 0 and max_age == 0:
                target_info.append("- **연령**: 연령 무관")
            elif min_age == 0 and max_age > 0:
                target_info.append(f"- **연령**: 만 {max_age}세 이하")
            elif min_age > 0 and max_age == 0:
                target_info.append(f"- **연령**: 만 {min_age}세 이상")
            else:
                target_info.append(f"- **연령**: 만 {min_age}세 ~ 만 {max_age}세")
        elif meta.get('sprtTrgtAgeLmtYn') == 'N':
            target_info.append("- **연령**: 연령 무관")
        # if meta.get('zipCd'): target_info.append(f"- **거주지**: {meta.get('zipCd')}")
        if get_code_value('schoolCd', meta.get('schoolCd')): target_info.append(
            f"- **학력**: {get_code_value('schoolCd', meta.get('schoolCd'))}")
        if get_code_value('mrgSttsCd', meta.get('mrgSttsCd')): target_info.append(
            f"- **혼인 상태**: {get_code_value('mrgSttsCd', meta.get('mrgSttsCd'))}")
        if get_code_value('jobCd', meta.get('jobCd')): target_info.append(
            f"- **직업 상태**: {get_code_value('jobCd', meta.get('jobCd'))}")
        if get_code_value('sbizCd', meta.get('sbizCd')): target_info.append(
            f"- **특화 분야**: {get_code_value('sbizCd', meta.get('sbizCd'))}")

        # if meta.get('earnMinAmt') or meta.get('earnMaxAmt'): target_info.append(f"- **소득 조건**: 최저 {meta.get('earnMinAmt', '0')}원 ~ 최고 {meta.get('earnMaxAmt', '0')}원")

        min_earn_str = meta.get('earnMinAmt', '0.0')
        max_earn_str = meta.get('earnMaxAmt', '0.0')
        min_earn = float(min_earn_str) if min_earn_str else 0.0
        max_earn = float(max_earn_str) if max_earn_str else 0.0
        if min_earn == 0.0 and max_earn == 0.0:
            target_info.append("- **소득 조건**: 소득 무관")
        else:
            target_info.append(f"- **소득 조건**: 최저 {min_earn_str}원 ~ 최고 {max_earn_str}원")

        if meta.get('addAplyQlfcCndCn'): target_info.append(f"- **추가 자격 조건**: {meta.get('addAplyQlfcCndCn')}")
        if target_info: sections["지원 대상 조건"] = target_info

        # 기관 정보
        org_info = []
        if meta.get('rgtrUpInstCdNm'): org_info.append(f"- **주관 기관**: {meta.get('rgtrUpInstCdNm')}")
        if meta.get('operInstCdNm'): org_info.append(f"- **운영 기관**: {meta.get('operInstCdNm')}")
        if meta.get('refUrlAddr1'): org_info.append(f"- **참고 사이트 1**: {meta.get('refUrlAddr1')}")
        if meta.get('refUrlAddr2'): org_info.append(f"- **참고 사이트 2**: {meta.get('refUrlAddr2')}")
        if org_info: sections["기관 정보"] = org_info

        # 만들어진 섹션들을 최종 문자열에 추가
        for title, content_list in sections.items():
            doc_string += f"\n### {title}\n"
            doc_string += "\n".join(content_list)

        formatted_strings.append(doc_string)

    result = "\n\n".join(formatted_strings)

    # 디버깅용 출력
    print(f"\n--- Retrieved {len(docs)} documents ---")
    for i, doc in enumerate(docs):
        print(f"Doc {i + 1}: {doc.metadata.get('plcyNm', 'Unknown')} (ID: {doc.metadata.get('plcyNo', 'Unknown')})")
    print("----------------------------\n")
    print(result)
    return result