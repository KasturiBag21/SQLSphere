import re
from difflib import SequenceMatcher
from config import db_pool
CONFIDENCE_THRESHOLD=0.82
AMBIGUITY_MARGIN=0.08
def normalize(value):
    value=str(value or "").lower().strip()
    value=re.sub(r"[^a-z0-9]+"," ",value)
    return re.sub(r"\s+"," ",value).strip()
def acronym(value):
    words=normalize(value).split()
    if not words:
        return ""
    return "".join(word[0] for word in words if word)
def similarity(a,b):
    return SequenceMatcher(None,normalize(a),normalize(b)).ratio()
def get_distinct_values(table,column):
    connection=None
    cursor=None
    try:
        connection=db_pool.get_connection()
        cursor=connection.cursor()
        safe_table=table.replace("`","")
        safe_column=column.replace("`","")
        query=f"SELECT DISTINCT `{safe_column}` FROM `{safe_table}` WHERE `{safe_column}` IS NOT NULL LIMIT 500"
        cursor.execute(query)
        return [row[0] for row in cursor.fetchall() if row[0] is not None]
    except Exception as e:
        print(f"[Grounding] Value lookup error {table}.{column}: {e}")
        return []
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
def get_relevant_columns(question):
    words=set(normalize(question).split())
    columns=[]
    if words.intersection({"department","departments","dept","branch","stream","from"}):
        columns.append(("departments","department_name",1.00))
    if words.intersection({"course","courses","subject","subjects","class"}):
        columns.append(("courses","course_name",1.00))
    if words.intersection({"student","students","name"}):
        columns.append(("students","student_name",0.85))
    if words.intersection({"faculty","teacher","teachers","professor","professors","lecturer","lecturers"}):
        columns.append(("faculty","faculty_name",1.00))
    if words.intersection({"grade","grades"}):
        columns.append(("marks","grade",1.00))
    unique={}
    for table,column,priority in columns:
        key=(table,column)
        unique[key]=max(unique.get(key,0),priority)
    return [(table,column,priority) for (table,column),priority in unique.items()]
def clean_candidate(value):
    value=value.strip(" .,:;!?")
    value=re.sub(r"\bdepartment\s*$","",value,flags=re.IGNORECASE).strip()
    value=re.sub(r"\bdept\s*$","",value,flags=re.IGNORECASE).strip()
    value=re.sub(r"\bbranch\s*$","",value,flags=re.IGNORECASE).strip()
    value=re.sub(r"\bstream\s*$","",value,flags=re.IGNORECASE).strip()
    value=re.sub(r"\b(?:with|having|whose|above|below|greater|less|more|than|and|or)\b.*$","",value,flags=re.IGNORECASE).strip()
    return value.strip(" .,:;!?")
def extract_candidate_values(question):
    candidates=[]
    quoted=re.findall(r'"([^"]+)"|\'([^\']+)\'',question)
    for first,second in quoted:
        value=first or second
        if value:
            candidates.append(value.strip())
    patterns=[
        r"\b(?:belonging|belongs|belong)\s+to\s+(?:the\s+)?([A-Za-z][A-Za-z0-9&.\- ]*)",
        r"\b(?:in|from)\s+(?:the\s+)?([A-Za-z][A-Za-z0-9&.\- ]*)",
        r"\bdepartment\s+(?:is\s+)?(?:the\s+)?([A-Za-z][A-Za-z0-9&.\- ]*)",
        r"\bbranch\s+(?:is\s+)?(?:the\s+)?([A-Za-z][A-Za-z0-9&.\- ]*)",
        r"\bstream\s+(?:is\s+)?(?:the\s+)?([A-Za-z][A-Za-z0-9&.\- ]*)",
        r"\bcourse\s+(?:is\s+)?(?:the\s+)?([A-Za-z][A-Za-z0-9&.\- ]*)"
    ]
    for pattern in patterns:
        matches=re.findall(pattern,question,flags=re.IGNORECASE)
        for match in matches:
            value=clean_candidate(match)
            if value:
                candidates.append(value)
    abbreviations=re.findall(r"\b[A-Z]{2,8}\b",question)
    candidates.extend(abbreviations)
    cleaned=[]
    ignored={"SHOW","GIVE","LIST","FIND","DISPLAY","GET","STUDENT","STUDENTS","ATTENDANCE","PERCENT","PERCENTAGE","BELOW","ABOVE","FROM","WHERE","WITH","WHOSE","ONLY","THE"}
    for value in candidates:
        value=clean_candidate(value)
        if not value or value.upper() in ignored:
            continue
        if value not in cleaned:
            cleaned.append(value)
    return cleaned
def abbreviation_match(candidate,db_value):
    candidate_clean=re.sub(r"[^A-Za-z]","",candidate).upper()
    if len(candidate_clean)<2:
        return False
    db_acronym=acronym(db_value).upper()
    if not db_acronym:
        return False
    if candidate_clean==db_acronym:
        return True
    if db_acronym.startswith(candidate_clean):
        return True
    meaningful_words=[word for word in normalize(db_value).split() if word not in {"and","of","the","in"}]
    meaningful_acronym="".join(word[0] for word in meaningful_words if word).upper()
    if meaningful_acronym.startswith(candidate_clean):
        return True
    candidate_letters=list(candidate_clean)
    index=0
    for word in normalize(db_value).split():
        if word in {"and","of","the","in"}:
            continue
        if index>=len(candidate_letters):
            break
        if word[0].upper()==candidate_letters[index]:
            index+=1
    return index==len(candidate_letters)
def phrase_match(candidate,db_value):
    candidate_words=normalize(candidate).split()
    db_words=normalize(db_value).split()
    if len(candidate_words)<2 or len(candidate_words)>len(db_words):
        return False
    if candidate_words==db_words[:len(candidate_words)]:
        return True
    for index in range(len(db_words)-len(candidate_words)+1):
        if db_words[index:index+len(candidate_words)]==candidate_words:
            return True
    candidate_meaningful=[word for word in candidate_words if word not in {"and","of","the","in"}]
    db_meaningful=[word for word in db_words if word not in {"and","of","the","in"}]
    if len(candidate_meaningful)>=2 and candidate_meaningful==db_meaningful[:len(candidate_meaningful)]:
        return True
    return False
def contained_word_match(candidate,db_value):
    candidate_words=normalize(candidate).split()
    db_words=normalize(db_value).split()
    if len(candidate_words)!=1:
        return False
    return candidate_words[0] in db_words
def match_value(candidate,db_values,table,column):
    candidate_normalized=normalize(candidate)
    if not candidate_normalized:
        return None
    results=[]
    for db_value in db_values:
        db_normalized=normalize(db_value)
        if not db_normalized:
            continue
        if candidate_normalized==db_normalized:
            results.append({"value":db_value,"confidence":1.00,"match_type":"exact"})
            continue
        if abbreviation_match(candidate,db_value):
            results.append({"value":db_value,"confidence":0.98,"match_type":"abbreviation"})
            continue
        if phrase_match(candidate,db_value):
            results.append({"value":db_value,"confidence":0.96,"match_type":"phrase"})
            continue
        if contained_word_match(candidate,db_value):
            results.append({"value":db_value,"confidence":0.93,"match_type":"contained_word"})
            continue
        score=similarity(candidate_normalized,db_normalized)
        if score>=0.82:
            results.append({"value":db_value,"confidence":round(score,2),"match_type":"fuzzy"})
    results.sort(key=lambda item:item["confidence"],reverse=True)
    if not results:
        return None
    best=results[0]
    alternatives=[item for item in results[1:] if best["confidence"]-item["confidence"]<=AMBIGUITY_MARGIN]
    if alternatives:
        return {
            "status":"ambiguous",
            "original_value":candidate,
            "matched_value":best["value"],
            "confidence":best["confidence"],
            "alternatives":[{"value":item["value"],"confidence":item["confidence"]} for item in [best]+alternatives[:4]],
            "table":table,
            "column":column
        }
    if best["match_type"] in {"exact","abbreviation","phrase","contained_word"}:
        return {
            "status":"matched",
            "original_value":candidate,
            "matched_value":best["value"],
            "confidence":best["confidence"],
            "table":table,
            "column":column,
            "match_type":best["match_type"]
        }
    if best["confidence"]<CONFIDENCE_THRESHOLD:
        return None
    return {
        "status":"matched",
        "original_value":candidate,
        "matched_value":best["value"],
        "confidence":best["confidence"],
        "table":table,
        "column":column,
        "match_type":best["match_type"]
    }
def ground_values(question):
    candidates=extract_candidate_values(question)
    print("[Grounding] Candidate values:",candidates)
    if not candidates:
        return []
    relevant_columns=get_relevant_columns(question)
    print("[Grounding] Relevant columns:",relevant_columns)
    if not relevant_columns:
        return []
    grounded=[]
    for table,column,priority in relevant_columns:
        values=get_distinct_values(table,column)
        print(f"[Grounding] {table}.{column} values checked:",len(values))
        if not values:
            continue
        for candidate in candidates:
            result=match_value(candidate,values,table,column)
            if not result:
                continue
            result["_priority"]=priority
            grounded.append(result)
    grounded.sort(key=lambda item:(item.get("_priority",0),item.get("confidence",0)),reverse=True)
    final=[]
    seen=set()
    for item in grounded:
        key=(item["original_value"].lower(),item["table"],item["column"])
        if key in seen:
            continue
        seen.add(key)
        if item["status"] in {"matched","ambiguous"}:
            final.append(item)
    for item in final:
        item.pop("_priority",None)
    print("[Grounding] Final matches:",final)
    return final