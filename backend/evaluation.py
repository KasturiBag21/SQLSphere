from datetime import datetime
evaluation_history=[]
MAX_EVALUATIONS=100
def save_evaluation(data):
    evaluation_history.append(data)
    if len(evaluation_history)>MAX_EVALUATIONS:
        del evaluation_history[0]
def get_evaluations():
    return list(reversed(evaluation_history))
def clear_evaluations():
    evaluation_history.clear()
def get_confidence(grounding):
    if not grounding:
        return None
    scores=[item.get("confidence") for item in grounding if isinstance(item,dict) and isinstance(item.get("confidence"),(int,float))]
    if not scores:
        return None
    return round(sum(scores)/len(scores),4)
def create_evaluation(question,generated_sql,grounding,validation_result,execution_success,row_count,repair_attempted,repair_success,final_sql,response_time,context_used,error=None):
    return {
        "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question":question,
        "generated_sql":generated_sql,
        "grounded_values":grounding,
        "confidence_score":get_confidence(grounding),
        "validation_result":validation_result,
        "execution_success":execution_success,
        "row_count":row_count,
        "repair_attempted":repair_attempted,
        "repair_success":repair_success,
        "final_sql":final_sql,
        "response_time_ms":round(response_time*1000,2),
        "context_used":context_used,
        "error":error,
        "mode":"development_evaluation"
    }