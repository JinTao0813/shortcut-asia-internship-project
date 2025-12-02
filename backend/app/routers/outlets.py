import re
import sqlite3
from fastapi import APIRouter, HTTPException, Depends
from langchain_community.utilities import SQLDatabase
from app.schemas import NLQuery
from dependencies import llm, get_db_path, DB_PATH

router = APIRouter()

def is_safe_select(sql_text: str) -> bool:
    s = sql_text.strip().lower()
    return bool(re.match(r"^select\b", s))

@router.post("/")
# Generate SQL from natural language and execute against outlets DB
def outlets_text_to_sql(payload: NLQuery):
    user_query = payload.query

    if not user_query or not user_query.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    try:
        # 1. Construct Prompt for SQL Generation
        prompt = (
            "Translate the following natural language question into a single SQL SELECT statement "
            "that can run against a sqlite database with a table named 'outlets' "
            "with columns (id, name, category, address, maps_url). "
            "Return only the SQL query (no explanation, no markdown formatting like ```sql).\n"
            f"Max rows: {payload.max_rows}.\n\n"
            f"Question: {user_query}"
        )

        # 2. Generate SQL
        generated_sql = llm.invoke(prompt)
        text = generated_sql.content

        # 3. Extract and Clean SQL
        # Remove markdown code blocks if present
        clean_text = re.sub(r"```sql|```", "", text, flags=re.IGNORECASE).strip()
        
        # Extract first SELECT statement
        match = re.search(r"(select[\s\S]*?)(?:;|$)", clean_text, re.IGNORECASE)
        if match:
            sql_text = match.group(1).strip()
            if sql_text.endswith(";"):
                sql_text = sql_text[:-1]
        else:
            sql_text = clean_text

        # 4. Safety & Limit Checks
        if not is_safe_select(sql_text):
            raise HTTPException(status_code=400, detail="Generated SQL is not a SELECT statement. Aborting.")

        if not re.search(r"\blimit\b", sql_text, re.IGNORECASE):
            sql_text = f"{sql_text} LIMIT {int(payload.max_rows)}"

        # 5. Execute (Using direct sqlite3 for granular control, or use db.run(sql_text))
        # Using raw connection to ensure we get dict-like rows easily
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(sql_text)
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()

        return {"sql": sql_text, "results": rows}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating/executing SQL: {str(e)}")