from datetime import datetime

query_history=[]
MAX_HISTORY=20
def add_history(question,sql,row_count):
    query_history.append({
        "question":question,
        "sql":sql,
        "row_count":row_count,
        "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    if len(query_history)>MAX_HISTORY:
        del query_history[0]
def get_history():
    return list(reversed(query_history))
def clear_history():
    query_history.clear()