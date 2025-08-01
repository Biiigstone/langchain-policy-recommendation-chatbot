'''
파서 함수 : 사용자의 질문을 받아 JSON 스키마에 맞춰 필터를 생성하는 함수.
'''

import json
from openai import OpenAI
import pandas as pd
from utils import count_tokens


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

# --- 이 코드로 전체 format_docs 함수를 교체하세요 ---

# pandas import가 필요할 수 있으므로 상단에 추가하는 것을 권장합니다.

def format_docs(docs: list, code_map: dict) -> str:
    """
    (수정 완료) Retriever의 Document 리스트와 코드 테이블을 받아,
    모든 metadata 필드를 활용하여 LLM이 이해하기 좋은 상세한 Markdown 형식으로 변환합니다.
    값이 없는 필드는 출력하지 않고, 쉼표로 구분된 다중 코드 값을 올바르게 처리합니다.
    """

    # --- Helper Functions ---
    def get_code_value(category: str, code) -> str:
        """코드 테이블(code_map)을 조회하여 코드에 해당하는 명칭을 반환합니다."""
        if not category or pd.isna(code) or code == '':
            return ""

        code_str = str(code).strip()  # 앞뒤 공백 제거
        if code_str.endswith('.0'):
            code_str = code_str[:-2]

        # 1. 직접 매칭 시도
        if code_str in code_map.get(category, {}):
            return code_map[category][code_str]

        # 2. 앞의 00과 뒤의 0을 제거하고 시도 (0049010 -> 49001)
        if code_str.startswith('00') and code_str.endswith('0'):
            clean_code = code_str[2:-1]
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
            sample_keys = list(code_map[category].keys())[:5]
            print(f"   카테고리 '{category}'의 키 샘플: {sample_keys}")
        return f"코드({code_str})"

    # ✅ 새로 추가된 헬퍼 함수
    def get_multiple_code_values(category: str, codes_str: str) -> str:
        """쉼표로 구분된 코드 문자열을 받아 각각의 명칭으로 변환 후 다시 합칩니다."""
        if not isinstance(codes_str, str) or not codes_str:
            return ""

        individual_codes = [code.strip() for code in codes_str.split(',')]
        resolved_names = [get_code_value(category, code) for code in individual_codes]
        return ", ".join(filter(None, resolved_names))

    def format_date(date_str: str) -> str:
        """'YYYYMMDD' 형식의 문자열을 'YYYY-MM-DD'로 변환합니다."""
        date_str = str(date_str).strip()
        if date_str and len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        return date_str

    def format_bool(bool_str: str) -> str:
        if bool_str == 'Y': return '예'
        if bool_str == 'N': return '아니오'
        return ''

    # --- Main Loop ---
    formatted_strings = []
    for i, doc in enumerate(docs):
        meta = doc.metadata
        doc_string = f"--- [문서 {i + 1}: {meta.get('plcyNm', '제목 없음')}] ---\n"
        sections = {}

        # 기본 정보 (수정 없음)
        basic_info = []
        if meta.get('plcyNo'): basic_info.append(f"- **정책 ID**: {meta.get('plcyNo')}")
        if meta.get('plcyNm'): basic_info.append(f"- **정책명**: {meta.get('plcyNm')}")
        # ... (이하 기본 정보, 지원 내용, 신청 및 기간 섹션은 이전과 동일하게 유지)
        if meta.get('plcyExplnCn'): basic_info.append(f"- **정책 요약**: {meta.get('plcyExplnCn')}")
        if meta.get('lclsfNm') and meta.get('mclsfNm'): basic_info.append(
            f"- **분류**: {meta.get('lclsfNm')} > {meta.get('mclsfNm')}")
        if meta.get('plcyKywdNm'): basic_info.append(f"- **정책 키워드**: {meta.get('plcyKywdNm')}")
        if basic_info: sections["기본 정보"] = basic_info

        support_info = []
        if meta.get('plcySprtCn'): support_info.append(f"- **상세 지원 내용**: \n{meta.get('plcySprtCn')}")
        if get_code_value('plcyPvsnMthdCd', meta.get('plcyPvsnMthdCd')): support_info.append(
            f"- **지원 방식**: {get_code_value('plcyPvsnMthdCd', meta.get('plcyPvsnMthdCd'))}")
        if format_bool(meta.get('sprtSclLmtYn')): support_info.append(
            f"- **지원 규모 제한 여부**: {format_bool(meta.get('sprtSclLmtYn'))}")
        if support_info: sections["지원 내용"] = support_info

        apply_info = []
        if meta.get('bizPrdBgngYmd') or meta.get('bizPrdEndYmd'): apply_info.append(
            f"- **사업 기간**: {format_date(meta.get('bizPrdBgngYmd'))} ~ {format_date(meta.get('bizPrdEndYmd'))}")
        if meta.get('bizPrdEtcCn'): apply_info.append(f"- **사업 기간 설명**: {meta.get('bizPrdEtcCn')}")
        if meta.get('aplyYmd'): apply_info.append(f"- **지원 기간**: {meta.get('aplyYmd')}")
        if meta.get('plcyAplyMthdCn'): apply_info.append(f"- **신청 방법**: {meta.get('plcyAplyMthdCn')}")
        if meta.get('aplyUrlAddr'): apply_info.append(f"- **신청 사이트**: {meta.get('aplyUrlAddr')}")
        if meta.get('sbmsnDcmntCn'): apply_info.append(f"- **제출 서류**: {meta.get('sbmsnDcmntCn')}")
        if apply_info: sections["신청 및 기간"] = apply_info

        # 지원 대상 조건 (✅ 이 부분이 핵심 수정 지점)
        target_info = []
        if meta.get('sprtTrgtAgeLmtYn') == 'Y' and (meta.get('sprtTrgtMinAge') or meta.get('sprtTrgtMaxAge')):
            target_info.append(
                f"- **연령**: 만 {int(float(meta.get('sprtTrgtMinAge', 0)))}세 ~ 만 {int(float(meta.get('sprtTrgtMaxAge', 0)))}세")

        # ✅ get_multiple_code_values 함수를 사용하도록 수정
        if meta.get('schoolCd'):
            school_names = get_multiple_code_values('schoolCd', meta.get('schoolCd'))
            if school_names: target_info.append(f"- **학력**: {school_names}")

        if meta.get('mrgSttsCd'):
            mrg_status_names = get_multiple_code_values('mrgSttsCd', meta.get('mrgSttsCd'))
            if mrg_status_names: target_info.append(f"- **혼인 상태**: {mrg_status_names}")

        if meta.get('jobCd'):
            job_names = get_multiple_code_values('jobCd', meta.get('jobCd'))
            if job_names: target_info.append(f"- **직업 상태**: {job_names}")

        if meta.get('sbizCd'):
            sbiz_names = get_multiple_code_values('sbizCd', meta.get('sbizCd'))
            if sbiz_names: target_info.append(f"- **특화 분야**: {sbiz_names}")

        # ... (소득 조건 로직은 이전 코드와 동일하게 유지)
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

        # 기관 정보 (수정 없음)
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
    print(result)  # 최종 포맷팅된 context 출력
    print(count_tokens(result))
    return result
