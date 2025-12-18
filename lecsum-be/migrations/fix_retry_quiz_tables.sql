-- 재시험 테이블 재생성 마이그레이션 (외래키 순환 참조 해결)

-- 1. 외래키 체크 비활성화 (순환 참조 문제 해결)
SET FOREIGN_KEY_CHECKS=0;

-- 2. 기존 테이블 삭제
DROP TABLE IF EXISTS retry_quiz_item;
DROP TABLE IF EXISTS retry_quiz_set;

-- 3. attempt 테이블에서 retry_quiz_set_id 관련 제약조건 및 컬럼 제거 (존재하는 경우)
ALTER TABLE attempt DROP FOREIGN KEY IF EXISTS fk_attempt_retry_quiz_set;
ALTER TABLE attempt DROP COLUMN IF EXISTS retry_quiz_set_id;

-- 4. 외래키 체크 재활성화
SET FOREIGN_KEY_CHECKS=1;

-- 5. attempt 테이블 수정 (quiz_set_id를 nullable로 변경 및 retry_quiz_set_id 추가)
ALTER TABLE attempt
MODIFY COLUMN quiz_set_id INT NULL,
ADD COLUMN retry_quiz_set_id INT NULL AFTER quiz_set_id;

-- 6. retry_quiz_set 테이블 생성 (quiz_set_id 포함)
CREATE TABLE retry_quiz_set (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_attempt_id INT NOT NULL,
    quiz_set_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_original_attempt_id (original_attempt_id),
    INDEX idx_quiz_set_id (quiz_set_id),
    FOREIGN KEY (original_attempt_id) REFERENCES attempt(id) ON DELETE CASCADE,
    FOREIGN KEY (quiz_set_id) REFERENCES quiz_set(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. retry_quiz_item 테이블 생성
CREATE TABLE retry_quiz_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    retry_quiz_set_id INT NOT NULL,
    original_quiz_id INT NOT NULL,
    `order` INT,
    INDEX idx_retry_quiz_set_id (retry_quiz_set_id),
    INDEX idx_original_quiz_id (original_quiz_id),
    FOREIGN KEY (retry_quiz_set_id) REFERENCES retry_quiz_set(id) ON DELETE CASCADE,
    FOREIGN KEY (original_quiz_id) REFERENCES quiz(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. attempt 테이블에 retry_quiz_set_id 외래키 제약조건 추가
ALTER TABLE attempt
ADD CONSTRAINT fk_attempt_retry_quiz_set
FOREIGN KEY (retry_quiz_set_id) REFERENCES retry_quiz_set(id) ON DELETE SET NULL;

-- 9. 성능 개선을 위한 인덱스 추가 (존재하지 않는 경우만)
-- quiz_result 테이블에 인덱스가 이미 있는지 확인 후 추가
ALTER TABLE quiz_result
ADD INDEX IF NOT EXISTS idx_attempt_id (attempt_id),
ADD INDEX IF NOT EXISTS idx_quiz_id (quiz_id),
ADD INDEX IF NOT EXISTS idx_is_correct (is_correct);

-- 완료
SELECT 'Migration completed successfully! retry_quiz_set now includes quiz_set_id column.' AS status;
