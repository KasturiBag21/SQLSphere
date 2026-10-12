import re
FORBIDDEN_KEYWORDS=["INSERT","UPDATE","DELETE","DROP","ALTER","CREATE","TRUNCATE","REPLACE","GRANT","REVOKE","CALL","LOAD","HANDLER","LOCK","UNLOCK","SET","USE","RENAME"]
def remove_strings_and_comments(sql):
    sql=re.sub(r"/\*[\s\S]*?\*/"," ",sql)
    sql=re.sub(r"--[^\r\n]*"," ",sql)
    sql=re.sub(r"#[^\r\n]*"," ",sql)
    sql=re.sub(r"'(?:''|[^'])*'","''",sql)
    sql=re.sub(r'"(?:""|[^"])*"','""',sql)
    sql=re.sub(r"`(?:``|[^`])*`","``",sql)
    return sql
def validate_sql(sql):
    if not sql:
        return False,"Empty SQL query."
    sql=sql.strip()
    sql=re.sub(r"^```(?:sql)?\s*","",sql,flags=re.IGNORECASE)
    sql=re.sub(r"\s*```$","",sql).strip()
    if not sql:
        return False,"Empty SQL query."
    if "\x00" in sql:
        return False,"Invalid SQL query."
    if ";" in sql:
        return False,"Multiple SQL statements are not allowed."
    if re.search(r"--|/\*|\*/|#",sql):
        return False,"SQL comments are not allowed."
    if not re.match(r"^(SELECT|WITH)\b",sql,re.IGNORECASE):
        return False,"This action is not allowed. SQLSphere only permits read-only queries."
    cleaned=remove_strings_and_comments(sql)
    if re.search(r"\bINTO\s+(?:OUTFILE|DUMPFILE)\b",cleaned,re.IGNORECASE):
        return False,"This action is not allowed. SQLSphere only permits read-only queries."
    for keyword in FORBIDDEN_KEYWORDS:
        if re.search(rf"\b{keyword}\b",cleaned,re.IGNORECASE):
            return False,"This action is not allowed. SQLSphere only permits read-only queries."
    if not re.match(r"^\s*(SELECT|WITH)\b",cleaned,re.IGNORECASE):
        return False,"This action is not allowed. SQLSphere only permits read-only queries."
    return True,sql