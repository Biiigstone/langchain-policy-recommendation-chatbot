"""
정책 데이터 전처리를 위한 스크립트.

이 스크립트는 원본 데이터를 로드하여,
시멘틱 서칭에 유의미한 컬럼을 추출하고 자연어로 변환한 'document' 열을 생성한 후
결과를 CSV 파일로 저장하는 스크립트 입니다.

--- 사용한 컬럼 ---
plcyNm - 정책명
lclsfNm - 대분류명 (정책 분야)
mclsfNm - 중분류명 (정책 분야)
plcySprtCn - 정책 지원 내용
rgtrUpInstCdNm - 주관 기관명
plcyExplnCn - 정책 설명 내용
plcyKywdNm - 정책 키워드명

자격 조건 관련 컬럼:

sprtTrgtMinAge - 지원 대상 최소 나이
sprtTrgtMaxAge - 지원 대상 최대 나이
mrgSttsCd - 혼인 상태
jobCd - 취업 상태
schoolCd - 학력
plcyMajorCd - 정책 전공
addAplyQlfcCndCn - 추가 신청 자격 조건 내용

검색 정확도 및 임베딩 품딜을 위해 각 조건의 독립성을 보장하고, 제한이 없는 경우 제한이 없음을 명시하였음.

변환 예시 :
	document
8	정책명은 '청년 체인지 메이커 아카데미 운영'입니다.
주관 기관은 제주특별자치도입니다.
정책 분야는 '교육 > 미래역량강화'이며, '청년들을 대상으로 취,창업 역량강화 프로그램 및 문화예술 강연 등 다양한 주제로 편성한 정기적 강연 프로그램 운영'을 지원합니다.
상세 설명: 생애전환기 진로 설계 등으로 고민하는 청년에게 전문가 및 명사의 강연 참여기회 제공 주요 키워드는 교육지원입니다.
지원 요건 : 연령 제한 없이 지원 가능합니다., 혼인 상태와 관계없이 지원 가능합니다., 취업 상태와 관계없이 지원 가능합니다., 학력과 관계없이 지원 가능합니다., 전공과 관계없이 지원 가능합니다..

"""

import pandas as pd

def load_maps_from_excel(filepath):
    try:
        df_codes = pd.read_excel(filepath, sheet_name='코드정보')
        code_maps = {}
        for name, group in df_codes.groupby('분류'):
            if '코드' in group.columns and '코드내용' in group.columns:
                clean_group = group.dropna(subset=['코드', '코드내용'])
                code_maps[name] = dict(zip(clean_group['코드'].astype(str), clean_group['코드내용']))
        print("✅ Excel 파일에서 코드 정보 파싱 완료!")
        return code_maps
    except Exception as e:
        print(f"������ Excel 파일 처리 중 오류 발생: {e}")
        return None


def create_final_document(row, code_maps):
    """
    데이터 행(row)과 코드맵을 기반으로 시멘틱 서칭을 위한 document를 생성합니다.
    '제한 없음' 키워드를 명시적으로 처리하여 검색 품질을 높입니다.
    """
    def get_code_name(code_type, code):
        if pd.notna(code) and code_maps:
            first_code = str(code).split(',')[0].strip()
            return code_maps.get(code_type, {}).get(first_code)
        return None

    # --- 기본 정보 구성 ---
    policy_name = row.get('plcyNm', '이름 정보 없음')
    category = f"{row.get('lclsfNm', '')} > {row.get('mclsfNm', '')}"
    support_content = row.get('plcySprtCn', '지원 내용 정보 없음').strip()

    parts = [f"정책명은 '{policy_name}'입니다."]

    if pd.notna(row.get('rgtrUpInstCdNm')):
        parts.append(f"주관 기관은 {row.get('rgtrUpInstCdNm')}입니다.")

    parts.append(f"정책 분야는 '{category}'이며, '{support_content}'을 지원합니다.")

    if pd.notna(row.get('plcyExplnCn')) and str(row.get('plcyExplnCn')).strip():
        parts.append(f"상세 설명: {row['plcyExplnCn'].strip()}")
    if pd.notna(row.get('plcyKywdNm')) and str(row.get('plcyKywdNm')).strip():
        parts.append(f"주요 키워드는 {row['plcyKywdNm']}입니다.")

    # --- 자격 조건 구성 ---
    conditions = []
    unrestricted_keywords = ['관계없음', '제한없음', '학력무관', '무관', '기타']

    # 나이
    min_age, max_age = row.get('sprtTrgtMinAge'), row.get('sprtTrgtMaxAge')
    if pd.notna(max_age) and max_age > 0:
        age_condition = f"만 {int(max_age)}세 이하의 청년"
        if pd.notna(min_age) and min_age > 0:
            age_condition = f"만 {int(min_age)}세에서 {int(max_age)}세 사이의 청년"
        conditions.append(age_condition)
    else:
        conditions.append("연령 제한 없이 지원 가능합니다.")

    # 결혼 상태
    mrg_name = get_code_name('mrgSttsCd', row.get('mrgSttsCd'))
    if mrg_name:
        if mrg_name not in unrestricted_keywords:
            conditions.append(f"혼인 상태는 '{mrg_name}'이어야 합니다.")
        else:
            conditions.append("혼인 상태와 관계없이 지원 가능합니다.")
    else:
        conditions.append("혼인 상태와 관계없이 지원 가능합니다.")

    # 취업 상태
    job_name = get_code_name('jobCd', row.get('jobCd'))
    if job_name:
        if job_name not in unrestricted_keywords:
            conditions.append(f"취업 상태는 '{job_name}'이어야 합니다.")
        else:
            conditions.append("취업 상태와 관계없이 지원 가능합니다.")
    else:
        conditions.append("취업 상태와 관계없이 지원 가능합니다.")

    # 학력
    edu_name = get_code_name('schoolCd', row.get('schoolCd'))
    if edu_name:
        if edu_name not in unrestricted_keywords:
            conditions.append(f"학력 조건은 '{edu_name}'입니다.")
        else:
            conditions.append("학력과 관계없이 지원 가능합니다.")
    else:
        conditions.append("학력과 관계없이 지원 가능합니다.")

    # 전공
    major_name = get_code_name('plcyMajorCd', row.get('plcyMajorCd'))
    if major_name:
        if major_name not in unrestricted_keywords:
            conditions.append(f"전공은 '{major_name}' 관련이어야 합니다.")
        else:
            conditions.append("전공과 관계없이 지원 가능합니다.")
    else:
        conditions.append("전공과 관계없이 지원 가능합니다.")

    # 추가 자격
    if pd.notna(row.get('addAplyQlfcCndCn')) and str(row.get('addAplyQlfcCndCn')).strip():
        conditions.append(f"추가 자격 요건 : {row['addAplyQlfcCndCn'].strip()}")

    # 최종 조건 문장 조합
    if conditions:
        parts.append("지원 요건: " + ", ".join(filter(None, conditions)) + ".")
    else:
        parts.append("특별한 자격 조건 없이 지원 가능합니다.")

    # --- 신청 방법 ---
    # if pd.notna(row.get('plcyAplyMthdCn')) and str(row.get('plcyAplyMthdCn')).strip():
    #     parts.append(f"신청 방법은 {row['plcyAplyMthdCn'].strip()}입니다.")

    return " ".join(parts)


if __name__ == '__main__':
    POLICY_CSV_PATH = '../data/policy_data.csv'
    CODE_EXCEL_PATH = '../data/code_table.xlsx'
    OUTPUT_CSV_PATH = '../data/policies_with_documents_final2.csv'

    try:
        df_raw = pd.read_csv(POLICY_CSV_PATH, encoding='utf-8')
        print(f"✅ 원본 CSV 데이터 '{POLICY_CSV_PATH}' 로딩 성공!")
    except FileNotFoundError:
        print(f"������ 오류: '{POLICY_CSV_PATH}' 파일을 찾을 수 없습니다.")
        exit()

    df_raw['sprtTrgtMinAge'] = pd.to_numeric(df_raw['sprtTrgtMinAge'], errors='coerce')
    df_raw['sprtTrgtMaxAge'] = pd.to_numeric(df_raw['sprtTrgtMaxAge'], errors='coerce')

    code_maps = load_maps_from_excel(CODE_EXCEL_PATH)

    if code_maps:
        print("\n문서 생성을 시작합니다...")
        df_raw['document'] = df_raw.apply(lambda row: create_final_document(row, code_maps), axis=1)
        print("✅ 최종 자연어 설명문 생성 완료!")
        df_raw.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8-sig')
        print(f"\n✅ 모든 문서가 포함된 최종 결과가 '{OUTPUT_CSV_PATH}' 파일로 저장되었습니다.")
    else:
        print("\n\n������ 코드맵 로딩 실패로 전체 프로세스를 중단합니다.")