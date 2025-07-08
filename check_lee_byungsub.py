import sqlite3
import pandas as pd

def get_candidate_by_name(db_path, name):
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query(f"SELECT * FROM candidates WHERE name = ? ORDER BY created_at DESC", conn, params=(name,))
    except Exception as e:
        print(f"DB Error: {e}")
        df = pd.DataFrame()
    conn.close()
    return df

if __name__ == "__main__":
    db_path = "candidates.db"
    name = "이병섭"
    df = get_candidate_by_name(db_path, name)
    print(df)
