conversation_history=[]
MAX_HISTORY=3
def add_context(question,sql,results):
    conversation_history.append({
        "question":question,
        "sql":sql,
        "row_count":len(results)
    })

    if len(conversation_history)>MAX_HISTORY:
        del conversation_history[0]
def get_context():
    return list(conversation_history)
def get_latest_context():
    if not conversation_history:
        return None
    return conversation_history[-1]
def clear_context():
    conversation_history.clear()