# 후보 정책들 필터링

import mysql.connector
from mysql.connector import Error
from config import DB_CONNECTION_INFO

def get_db_connection():
    return mysql.connector.connect(**DB_CONNECTION_INFO)

def _get_all_related_region_codes(cursor, region_names: list) -> list:
    """
    지역명 리스트를 받아 관련된 모든 지역 코드(시/도 및 하위 시/군/구)를 반환합니다.
    """
    if not region_names:
        return []
    all_codes = set()
    region_regex = '|'.join(region_names)

    query = "SELECT code FROM region_codes WHERE sido REGEXP %s OR sigungu REGEXP %s"
    cursor.execute(query, (region_regex, region_regex))
    results = cursor.fetchall()
    for row in results:
        all_codes.add(row[0])

    return list(all_codes)


def get_rdb_candidate_ids(db_connection, filters: dict) -> list:
    """
    [최소 조건 버전] 기간과 지역 필터만을 사용하여 RDB에서 1차 후보군을 조회합니다.
    """
    try:
        cursor = db_connection.cursor()

        base_query = "SELECT DISTINCT p.policy_id FROM policies p"
        joins = set()
        where_conditions = []
        params = []

        # 1. 신청 기간 필터
        application_date_condition = """
        (p.application_status = '상시' OR 
         (p.application_status = '특정 기간' AND CURDATE() BETWEEN DATE(p.aply_start_date) AND DATE(p.aply_end_date)))
        """
        where_conditions.append(application_date_condition.strip())

        # 2. 사업 기간 필터
        biz_date_condition = "(p.biz_end_date IS NULL OR CURDATE() <= DATE(p.biz_end_date))"
        where_conditions.append(biz_date_condition)

        # 3. 지역 필터
        if filters.get("regions"):
            region_codes = _get_all_related_region_codes(cursor, filters["regions"])
            if region_codes:
                joins.add("JOIN policy_regions pr ON p.policy_id = pr.policy_id")
                placeholders = ', '.join(['%s'] * len(region_codes))
                where_conditions.append(f"pr.region_code IN ({placeholders})")
                params.extend(region_codes)

        # 최종 쿼리 조립
        final_query = base_query
        if joins:
            final_query += " " + " ".join(list(joins))
        if where_conditions:
            final_query += " WHERE (" + ") AND (".join(where_conditions) + ")"
        final_query += ";"

        # 디버깅을 위해 쿼리 템플릿과 파라미터를 별도로 출력
        print("--- Generated SQL Query (Simplified) ---")
        print(final_query)
        print("\n--- SQL Parameters ---")
        print(params)

        # 쿼리 실행
        cursor.execute(final_query, params)
        candidate_ids = [str(item[0]) for item in cursor.fetchall()]
        return candidate_ids

    except Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()