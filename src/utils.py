import tiktoken
import pandas as pd
from config import CODE_TABLE_FILE
# , model="text-embedding-3-large"
def count_tokens(text):
    # OpenAI 임베딩 모델들은 cl100k_base 인코딩 사용
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def load_code_table() -> dict[str, dict[str, str]]:
    try:
        df_codes = pd.read_excel(CODE_TABLE_FILE, sheet_name='코드정보')

        # 원본 컬럼명 확인 및 처리
        print(f"원본 컬럼명: {df_codes.columns.tolist()}")

        # Unnamed 컬럼 제거
        df_codes = df_codes[['분류', '코드', '코드내용']]
        print(f"처리 후 컬럼명: {df_codes.columns.tolist()}")

        # 데이터 샘플 출력
        print("데이터 샘플:")
        print(df_codes.head(10))

        # 분류 컬럼의 빈 값을 이전 값으로 채우기
        df_codes['분류'] = df_codes['분류'].ffill()

        CODE_TABLE_MAP = {}
        total_entries = 0

        for idx, row in df_codes.iterrows():
            category = row['분류']
            code = row['코드']
            value = row['코드내용']

            # NaN 값 체크
            if pd.isna(category) or pd.isna(code) or pd.isna(value):
                print(f"⚠️ Row {idx}: NaN 값 발견 - 건너뜁니다")
                continue

            # 코드를 문자열로 변환
            code_str = str(int(code)) if isinstance(code, float) else str(code)

            if category not in CODE_TABLE_MAP:
                CODE_TABLE_MAP[category] = {}

            # 원본 코드로 저장
            CODE_TABLE_MAP[category][code_str] = value
            total_entries += 1

            # 변형된 형태도 추가 (00 prefix + 0 suffix)
            padded_code = f"00{code_str}0"
            CODE_TABLE_MAP[category][padded_code] = value
            total_entries += 1

            # 다른 가능한 변형도 추가
            CODE_TABLE_MAP[category][f"0{code_str}"] = value  # 0 prefix만
            CODE_TABLE_MAP[category][f"{code_str}0"] = value  # 0 suffix만
            total_entries += 2

            # 디버깅: 처음 몇 개 항목의 변환 과정 출력
            if idx < 3:
                print(f"\n디버깅 - Row {idx}:")
                print(f"  원본: category='{category}', code='{code}' (type: {type(code)}), value='{value}'")
                print(f"  변환된 코드들:")
                print(f"    - '{code_str}' -> '{value}'")
                print(f"    - '{padded_code}' -> '{value}'")
                print(f"    - '0{code_str}' -> '{value}'")
                print(f"    - '{code_str}0' -> '{value}'")

        print(f"\n✅ 코드 테이블을 성공적으로 로드했습니다.")
        print(f"   - 카테고리 수: {len(CODE_TABLE_MAP)}개")
        print(f"   - 전체 엔트리 수: {total_entries}개")

        # 각 카테고리별 상세 정보
        print("\n로드된 카테고리별 정보:")
        for cat, codes in CODE_TABLE_MAP.items():
            print(f"\n  📁 {cat}: {len(codes)}개 코드")

            # 원본 코드만 필터링 (변형된 코드 제외)
            original_codes = [(k, v) for k, v in codes.items() if
                              not (k.startswith('00') or k.endswith('0') or (k.startswith('0') and len(k) == 6))]

            # 처음 3개 샘플 출력
            sample_codes = original_codes[:3]
            for c, v in sample_codes:
                print(f"    - {c}: {v}")
            if len(original_codes) > 3:
                print(f"    ... 외 {len(original_codes) - 3}개")

        # 테스트: 실제 데이터 형식으로 조회
        print("\n=== 코드 변환 테스트 ===")
        test_cases = [
            ('schoolCd', '0049010'),
            ('jobCd', '0013010'),
            ('sbizCd', '0014010'),
            ('schoolCd', '49001'),  # 원본 형태
            ('jobCd', '13001'),  # 원본 형태
        ]

        for category, code in test_cases:
            if category in CODE_TABLE_MAP and code in CODE_TABLE_MAP[category]:
                result = CODE_TABLE_MAP[category][code]
                print(f"✓ {category} - '{code}': '{result}'")
            else:
                print(f"✗ {category} - '{code}': 찾을 수 없음")
                # 해당 카테고리의 키들 일부 출력
                if category in CODE_TABLE_MAP:
                    keys = list(CODE_TABLE_MAP[category].keys())[:5]
                    print(f"    해당 카테고리의 키 샘플: {keys}")

        # 특정 카테고리의 모든 키 형태 확인 (디버깅용)
        print("\n=== schoolCd 카테고리의 모든 키 ===")
        if 'schoolCd' in CODE_TABLE_MAP:
            all_keys = sorted(CODE_TABLE_MAP['schoolCd'].keys())
            print(f"전체 {len(all_keys)}개 키:")
            for i, key in enumerate(all_keys):
                if i < 20:  # 처음 20개만 출력
                    print(f"  '{key}': '{CODE_TABLE_MAP['schoolCd'][key]}'")
                else:
                    print(f"  ... 외 {len(all_keys) - 20}개")
                    break
        return CODE_TABLE_MAP

    except FileNotFoundError:
        print("🚨 code_table.xlsx 파일을 찾을 수 없습니다.")
        CODE_TABLE_MAP = {}
        return CODE_TABLE_MAP
    except Exception as e:
        print(f"🚨 코드 테이블 로드 오류: {e}")
        import traceback
        traceback.print_exc()
        CODE_TABLE_MAP = {}
        return CODE_TABLE_MAP


    except Exception as e:
        print(f"🚨 코드 테이블 로드 오류: {e}")
        CODE_TABLE_MAP = {}

        # 디버깅을 위한 샘플 출력
        for cat, codes in CODE_TABLE_MAP.items():
            print(f"  - {cat}: {len(codes)}개 코드")
            # 첫 3개 코드만 샘플로 출력
            sample_codes = list(codes.items())[:3]
            for c, v in sample_codes:
                print(f"    {c}: {v}")
            if len(codes) > 3:
                print(f"    ... 외 {len(codes) - 3}개")

    except FileNotFoundError:
        print("🚨 code_table.xlsx 파일을 찾을 수 없습니다.")
        CODE_TABLE_MAP = {}
    except Exception as e:
        print(f"🚨 코드 테이블 로드 오류: {e}")
        CODE_TABLE_MAP = {}