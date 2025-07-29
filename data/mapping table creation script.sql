-- 학력 제한 매핑 테이블
CREATE TABLE policy_education_levels (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   education_code VARCHAR(10)
);

-- 직업 매핑 테이블
CREATE TABLE policy_job_status (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   job_status_code VARCHAR(10)
);

-- 전공 매핑 테이블
CREATE TABLE policy_majors (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   major_code VARCHAR(10)
);

-- 특화 매핑 테이블
CREATE TABLE policy_specializations (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   specialization_code VARCHAR(10)
);

-- 지역 매핑 테이블 (3자리 파싱)
CREATE TABLE policy_regions (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   region_code VARCHAR(3),
);

-- 정책 대분류 매핑 테이블 (자연어)
CREATE TABLE policy_categories (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   category_name VARCHAR(100)
);

-- 정책 중분류 매핑 테이블 (자연어)
CREATE TABLE policy_subcategories (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   subcategory_name VARCHAR(100)
);

-- 정책 키워드 매핑 테이블 (자연어)
CREATE TABLE policy_keywords (
   id INT AUTO_INCREMENT PRIMARY KEY,
   policy_id VARCHAR(255),
   keyword_name VARCHAR(100)
);