# DB 연결 및 초기화 함수
import sqlite3
import pandas as pd
from typing import Any, Dict

DB_PATH = "candidates.db"

def get_db_connection() -> sqlite3.Connection:
    """데이터베이스 커넥션을 반환합니다."""
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    """데이터베이스를 초기화하고 candidates 테이블을 생성합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            raw_result TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # 컬럼이 없으면 추가 (마이그레이션)
    columns_to_add = [
        ("name", "TEXT"),
        ("evaluator", "TEXT"),
        ("overall_score", "REAL"),
        ("growth_potential_digital_literacy", "REAL"),
        ("growth_potential_wb_personal_growth", "REAL"),
        ("teamwork", "REAL"),
        ("problem_solving", "REAL"),
        ("communication", "REAL"),
        ("general_report", "TEXT"),
        ("reliability", "REAL")
    ]
    for col, typ in columns_to_add:
        try:
            c.execute(f"ALTER TABLE candidates ADD COLUMN {col} {typ}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

def load_candidates() -> pd.DataFrame:
    """모든 후보자 데이터를 데이터프레임으로 불러옵니다."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM candidates ORDER BY created_at DESC", conn)  # type: ignore
    except sqlite3.DatabaseError:
        df = pd.DataFrame()
    conn.close()
    return df

def delete_candidate(candidate_id: int) -> None:
    """특정 후보자를 ID로 삭제합니다."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()

def save_candidate_data(data: Dict[str, Any]) -> None:
    """LLM 분석 결과(개조식 전체 텍스트)를 데이터베이스에 저장합니다."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO candidates (
            name, raw_result, evaluator, created_at,
            overall_score, growth_potential_digital_literacy, growth_potential_wb_personal_growth,
            teamwork, problem_solving, communication, general_report, reliability
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("name"),
            data.get("raw_result"),
            data.get("evaluator"),
            data.get("created_at"),
            data.get("overall_score"),
            data.get("growth_potential_digital_literacy"),
            data.get("growth_potential_wb_personal_growth"),
            data.get("teamwork"),
            data.get("problem_solving"),
            data.get("communication"),
            data.get("general_report"),
            data.get("reliability")
        )
    )
    conn.commit()
    conn.close()
