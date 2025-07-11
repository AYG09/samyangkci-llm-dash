# DB 연결 및 초기화 함수
import sqlite3
import pandas as pd
from typing import Any, Dict, Optional
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "candidates.db")

def get_db_connection() -> sqlite3.Connection:
    """데이터베이스 커넥션을 반환합니다."""
    return sqlite3.connect(DB_PATH)

def init_db() -> None:
    """데이터베이스를 초기화하고 candidate_analysis 테이블을 생성합니다."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS candidate_analysis (
            id TEXT PRIMARY KEY,
            name TEXT,
            evaluator TEXT,
            interview_date TEXT,
            json_data TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_candidate_data(data: Dict[str, Any]) -> None:
    """후보자 분석 결과를 데이터베이스에 저장합니다."""
    conn = get_db_connection()
    c = conn.cursor()
    cid = data.get("id")
    name = data.get("name")
    evaluator = data.get("evaluator")
    interview_date = data.get("interview_date")
    json_data = data.get("json_data")

    if isinstance(json_data, (dict, list)):
        json_str = json.dumps(json_data, ensure_ascii=False)
    elif isinstance(json_data, str):
        json_str = json_data
    else:
        json_str = "{}"
    c.execute(
        "INSERT OR REPLACE INTO candidate_analysis (id, name, evaluator, interview_date, json_data) VALUES (?, ?, ?, ?, ?)",
        (cid, name, evaluator, interview_date, json_str)
    )
    conn.commit()
    conn.close()

def load_candidates() -> pd.DataFrame:
    """모든 후보자 데이터를 데이터프레임으로 불러옵니다."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query("SELECT * FROM candidate_analysis ORDER BY name ASC", conn)  # type: ignore
    except sqlite3.DatabaseError:
        df = pd.DataFrame()
    conn.close()
    return df

def delete_candidate(candidate_id: str) -> None:
    """특정 후보자를 ID로 삭제합니다."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM candidate_analysis WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()

def load_candidate_json(candidate_id: str) -> Optional[Dict[str, Any]]:
    """특정 후보자의 json_data를 dict로 반환."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT json_data FROM candidate_analysis WHERE id = ?", (candidate_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row[0])
    except Exception:
        return None
