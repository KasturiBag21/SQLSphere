from google import genai
from config import GEMINI_API_KEY,db_pool
import time
MODEL_NAME="gemini-3.1-flash-lite"
MAX_RETRIES=3
RETRY_DELAY=2
client=genai.Client(api_key=GEMINI_API_KEY)
def get_database_schema():
    connection=None
    cursor=None
    try:
        connection=db_pool.get_connection()
        cursor=connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT TABLE_NAME,COLUMN_NAME,DATA_TYPE,COLUMN_KEY
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s
            ORDER BY TABLE_NAME,ORDINAL_POSITION
        """,(connection.database,))
        columns=cursor.fetchall()
        cursor.execute("""
            SELECT TABLE_NAME,COLUMN_NAME,REFERENCED_TABLE_NAME,REFERENCED_COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA=%s
            AND REFERENCED_TABLE_NAME IS NOT NULL
            ORDER BY TABLE_NAME,COLUMN_NAME
        """,(connection.database,))
        foreign_keys=cursor.fetchall()
        schema={}
        for column in columns:
            table_name=column["TABLE_NAME"]
            if table_name not in schema:
                schema[table_name]=[]
            key=""
            if column["COLUMN_KEY"]=="PRI":
                key=" PRIMARY KEY"
            schema[table_name].append(f'{column["COLUMN_NAME"]} {column["DATA_TYPE"]}{key}')
        schema_text=""
        for table_name,table_columns in schema.items():
            schema_text+=f"TABLE {table_name}:\n"
            for column in table_columns:
                schema_text+=f"  - {column}\n"
            schema_text+="\n"
        if foreign_keys:
            schema_text+="RELATIONSHIPS:\n"
            for fk in foreign_keys:
                schema_text+=f'  - {fk["TABLE_NAME"]}.{fk["COLUMN_NAME"]} -> {fk["REFERENCED_TABLE_NAME"]}.{fk["REFERENCED_COLUMN_NAME"]}\n'
        return schema_text
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if connection:
            try:
                connection.close()
            except Exception:
                pass
def clean_sql(sql):
    if not sql:
        return ""
    sql=sql.strip()
    if sql.startswith("```sql"):
        sql=sql[6:]
    elif sql.startswith("```SQL"):
        sql=sql[6:]
    elif sql.startswith("```"):
        sql=sql[3:]
    if sql.endswith("```"):
        sql=sql[:-3]
    return sql.strip().rstrip(";").strip()
def build_grounding_text(grounding):
    if not grounding:
        return "No grounded values found."
    grounded_items=[]
    for item in grounding:
        if item.get("status")!="matched":
            continue
        grounded_items.append(f'- User value "{item["original_value"]}" matched to "{item["matched_value"]}" in {item["table"]}.{item["column"]} (confidence {item["confidence"]})')
    if not grounded_items:
        return "No grounded values found."
    return "\n".join(grounded_items)
def build_context_text(context):
    if not context:
        return "No previous conversation context."
    latest=context[-1]
    return f"""
PREVIOUS USER QUESTION
======================
{latest["question"]}
PREVIOUS GENERATED SQL
======================
{latest["sql"]}
PREVIOUS RESULT ROW COUNT
=========================
{latest["row_count"]}
"""
def is_temporary_gemini_error(error):
    error_text=str(error).upper()
    temporary_errors=["503","UNAVAILABLE","HIGH DEMAND","429","RESOURCE EXHAUSTED","500","502","504","INTERNAL","DEADLINE EXCEEDED","TIMEOUT","SERVER DISCONNECTED","CONNECTION RESET","CONNECTION ERROR","REMOTE DISCONNECTED"]
    return any(value in error_text for value in temporary_errors)
def generate_gemini_content(prompt,operation="generation"):
    last_error=None
    for attempt in range(1,MAX_RETRIES+1):
        try:
            print(f"[Gemini] {operation} attempt {attempt}/{MAX_RETRIES}")
            response=client.models.generate_content(model=MODEL_NAME,contents=prompt)
            return response
        except Exception as error:
            last_error=error
            print(f"[Gemini] Attempt {attempt} failed:")
            print(f"[Gemini] {error}")
            if not is_temporary_gemini_error(error):
                print("[Gemini] Non-temporary error. No retry.")
                raise
            if attempt<MAX_RETRIES:
                print(f"[Gemini] Temporary error. Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
    print("[Gemini] All retry attempts failed.")
    raise RuntimeError("Gemini service is temporarily unavailable. Please try again in a moment.") from last_error
def generate_sql(question,grounding=None,context=None):
    schema=get_database_schema()
    grounding_text=build_grounding_text(grounding)
    context_text=build_context_text(context)
    prompt=f"""
You are an expert MySQL SQL generator for SQLSphere.
Your job is to convert the user's natural-language question into ONE valid MySQL SELECT query.
DATABASE SCHEMA
===============
{schema}
VALUE GROUNDING
===============
{grounding_text}
CONVERSATION CONTEXT
====================
{context_text}
CONVERSATION RULES
==================
1. The current question has priority.
2. Use previous context only when the current question clearly refers to it.
3. Resolve words such as:
   - their
   - them
   - those
   - these
   - same
   - above
   - below
   - now
   - only
   using the previous query when appropriate.
4. Preserve filters and conditions from the previous query when the user asks for a modification or follow-up.
5. If the user says "only show their names", return only the name column while preserving the previous filtering.
6. Do not carry unrelated conditions from an old query.
7. If the current question is independent, ignore the previous context.
SQL RULES
=========
1. Use only tables and columns from the schema.
2. Never invent columns.
3. Use grounded database values when provided.
4. Never replace a grounded database value with the user's abbreviation.
5. Use actual foreign-key relationships.
6. Generate exactly one read-only MySQL query.
7. Use SELECT or WITH only.
8. Do not use INSERT,UPDATE,DELETE,DROP,ALTER,CREATE,TRUNCATE,REPLACE,GRANT,REVOKE,CALL,LOAD,SET,USE or RENAME.
9. Return only SQL.
10. Do not use markdown.
11. Use GROUP BY,HAVING,COUNT,SUM,AVG,MIN or MAX when required.
CURRENT USER QUESTION
=====================
{question}
Return only the MySQL SQL query.
"""
    print("[Gemini] Model:",MODEL_NAME)
    print("[Gemini] Generating SQL for:",question)
    if context:
        print("[Context] Previous question:",context[-1]["question"])
    response=generate_gemini_content(prompt,"SQL generation")
    sql=clean_sql(response.text)
    print("[Gemini] SQL generated:",sql)
    return sql
def repair_sql(question,original_sql,error,grounding=None):
    schema=get_database_schema()
    grounding_text=build_grounding_text(grounding)
    prompt=f"""
You are repairing a failed MySQL SELECT query for SQLSphere.
DATABASE SCHEMA
===============
{schema}
VALUE GROUNDING
===============
{grounding_text}
USER QUESTION
=============
{question}
ORIGINAL SQL
============
{original_sql}
DATABASE ERROR
==============
{error}
TASK
====
Create a corrected version of the SQL query.
STRICT RULES
============
1. Use only tables and columns from the schema.
2. Fix the actual SQL error.
3. Preserve the user's intended question.
4. Preserve valid parts of the original SQL.
5. Use grounded database values when provided.
6. Generate exactly one read-only MySQL query.
7. Use SELECT or WITH only.
8. Never use INSERT,UPDATE,DELETE,DROP,ALTER,CREATE,TRUNCATE,REPLACE,GRANT,REVOKE,CALL,LOAD,SET,USE or RENAME.
9. Return only SQL.
10. Do not use markdown.
11. Do not explain anything.
Return only the corrected MySQL SQL query.
"""
    print("[Repair] Attempting SQL repair...")
    response=generate_gemini_content(prompt,"SQL repair")
    repaired=clean_sql(response.text)
    print("[Repair] Repaired SQL:",repaired)
    return repaired
    