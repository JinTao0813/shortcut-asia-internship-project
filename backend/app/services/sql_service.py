import re
import sqlite3
from fastapi import HTTPException

class SQLService:
    def __init__(self, llm, db_path: str):
        self.llm = llm
        self.db_path = db_path

    def _is_safe_select(self, sql_text: str) -> bool:
        clean_sql = sql_text.strip().lower()
        return bool(re.match(r"^select\b", clean_sql))

    def process_natural_language_query(self, user_query: str, max_rows: int = 50):
        try:
            # 1. Constructing the prompt
            # We provide the schema explicitly to help the LLM
            prompt = (
                "You are a SQL expert. Convert the user's question into a SQLite query.\n"
                "Table: outlets\n"
                "Columns: id, name, category, address, maps_url\n\n"
                "Rules:\n"
                "1. Return ONLY the raw SQL query. No markdown, no explanations.\n"
                "2. If the user asks for a location (like 'Ampang', 'PJ', 'KL'), you MUST check both 'name' AND 'address' columns.\n"
                "3. Use the LIKE operator with % wildcards for searching (e.g., address LIKE '%Ampang%').\n"
                "4. Example: SELECT * FROM outlets WHERE name LIKE '%Ampang%' OR address LIKE '%Ampang%';\n"
                f"5. LIMIT the results to {max_rows}.\n\n"
                f"Question: {user_query}\n"
                "SQL:"
            )

            # 2. Generate SQL using LLM
            response = self.llm.invoke(prompt)
            raw_text = response.content

            # Debugging output
            print(f"\n[DEBUG] Generated SQL: {raw_text}\n")

            # 3. Clean SQL (Remove markdown ```sql ... ``` if LLM disobeyed)
            clean_sql = re.sub(r"```sql|```", "", raw_text, flags=re.IGNORECASE).strip()
            
            # 4. Security check to prevent harmful queries
            if not self._is_safe_select(clean_sql):
                raise HTTPException(
                    status_code=400, 
                    detail="I can only perform search queries (SELECT), not modifications."
                )

            # 5. Execution
            # We connect per-request to ensure thread safety with SQLite
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(clean_sql)
                rows = [dict(row) for row in cursor.fetchall()]

            return {
                "generated_sql": clean_sql,
                "results": rows,
                "count": len(rows)
            }

        except sqlite3.Error as e:
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
        except Exception as e:
            # In production, log the full error
            raise HTTPException(status_code=500, detail="Failed to process outlet search.")