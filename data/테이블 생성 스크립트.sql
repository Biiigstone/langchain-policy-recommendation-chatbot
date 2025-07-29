CREATE DATABASE `toyprj4` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

CREATE TABLE `education_level_codes` (
  `code` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `job_status_codes` (
  `code` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `major_codes` (
  `code` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `policies` (
  `policy_id` varchar(50) DEFAULT NULL,
  `policy_name` text,
  `policy_summary` text,
  `source_url` text,
  `min_age` int DEFAULT NULL,
  `max_age` int DEFAULT NULL,
  `income_min` int DEFAULT NULL,
  `income_max` int DEFAULT NULL,
  `biz_start_date` datetime DEFAULT NULL,
  `biz_end_date` datetime DEFAULT NULL,
  `aply_start_date` datetime DEFAULT NULL,
  `aply_end_date` datetime DEFAULT NULL,
  `marriage_status` varchar(10) DEFAULT NULL,
  `application_status` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `policy_categories` (
  `policy_id` varchar(50) DEFAULT NULL,
  `category_name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `policy_education_levels` (
  `policy_id` varchar(50) DEFAULT NULL,
  `education_level_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `policy_job_status` (
  `policy_id` varchar(50) DEFAULT NULL,
  `job_status_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `policy_keywords` (
  `policy_id` varchar(50) DEFAULT NULL,
  `keyword_name` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `policy_majors` (
  `policy_id` varchar(50) DEFAULT NULL,
  `major_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `policy_regions` (
  `policy_id` varchar(50) DEFAULT NULL,
  `region_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `policy_specializations` (
  `policy_id` varchar(50) DEFAULT NULL,
  `specialization_code` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `policy_subcategories` (
  `policy_id` varchar(50) DEFAULT NULL,
  `subcategory_name` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


CREATE TABLE `region_codes` (
  `code` varchar(10) NOT NULL,
  `sido` varchar(100) NOT NULL,
  `sigungu` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `specialization_codes` (
  `code` varchar(10) NOT NULL,
  `name` varchar(100) NOT NULL,
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;






