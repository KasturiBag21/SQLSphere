import re


def explain_sql(sql):
    sql=sql.strip().rstrip(";")

    select_match=re.search(
        r"\bSELECT\b(.*?)(?:\bFROM\b)",
        sql,
        re.IGNORECASE|re.DOTALL
    )

    from_match=re.search(
        r"\bFROM\b\s+([a-zA-Z_][a-zA-Z0-9_]*)(?:\s+(?:AS\s+)?[a-zA-Z_][a-zA-Z0-9_]*)?",
        sql,
        re.IGNORECASE
    )

    where_match=re.search(
        r"\bWHERE\b(.*?)(?=\bGROUP\s+BY\b|\bHAVING\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
        sql,
        re.IGNORECASE|re.DOTALL
    )

    group_match=re.search(
        r"\bGROUP\s+BY\b(.*?)(?=\bHAVING\b|\bORDER\s+BY\b|\bLIMIT\b|$)",
        sql,
        re.IGNORECASE|re.DOTALL
    )

    order_match=re.search(
        r"\bORDER\s+BY\b(.*?)(?=\bLIMIT\b|$)",
        sql,
        re.IGNORECASE|re.DOTALL
    )

    limit_match=re.search(
        r"\bLIMIT\b\s+(\d+)",
        sql,
        re.IGNORECASE
    )

    parts=[]

    if select_match:
        selected=re.sub(r"\s+"," ",select_match.group(1)).strip()

        if selected=="*":
            parts.append("retrieves all columns")
        elif re.search(r"\bCOUNT\s*\(",selected,re.IGNORECASE):
            parts.append("retrieves a count or number of records")
        elif re.search(r"\bAVG\s*\(",selected,re.IGNORECASE):
            parts.append("calculates an average")
        elif re.search(r"\bSUM\s*\(",selected,re.IGNORECASE):
            parts.append("calculates a total")
        elif re.search(r"\bMAX\s*\(",selected,re.IGNORECASE):
            parts.append("finds the maximum value")
        elif re.search(r"\bMIN\s*\(",selected,re.IGNORECASE):
            parts.append("finds the minimum value")
        else:
            parts.append("retrieves the requested columns")

    if from_match:
        table=from_match.group(1)
        parts.append(f"from the {table} table")

    if re.search(r"\bJOIN\b",sql,re.IGNORECASE):
        join_count=len(re.findall(r"\b(?:INNER|LEFT|RIGHT|FULL|CROSS)?\s*JOIN\b",sql,re.IGNORECASE))
        if join_count==1:
            parts.append("using a table join")
        else:
            parts.append(f"using {join_count} table joins")

    if where_match:
        condition=re.sub(r"\s+"," ",where_match.group(1)).strip()
        parts.append(f"filters the results using the condition: {condition}")

    if group_match:
        grouping=re.sub(r"\s+"," ",group_match.group(1)).strip()
        parts.append(f"groups the results by {grouping}")

    if re.search(r"\bHAVING\b",sql,re.IGNORECASE):
        parts.append("applies a condition to the grouped results")

    if order_match:
        ordering=re.sub(r"\s+"," ",order_match.group(1)).strip()
        parts.append(f"sorts the results by {ordering}")

    if limit_match:
        parts.append(f"limits the output to {limit_match.group(1)} rows")

    if not parts:
        return "This SQL query retrieves data from the database."

    return "This query "+", ".join(parts)+"."
