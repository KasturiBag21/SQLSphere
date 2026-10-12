from flask import Flask,request,jsonify
from flask_cors import CORS
from config import db_pool
from gemini_service import generate_sql,repair_sql
from value_grounding import ground_values
from query_history import add_history,get_history,clear_history
from sql_explainer import explain_sql
from conversation_context import add_context,get_context,get_latest_context,clear_context
from sql_security import validate_sql
from evaluation import save_evaluation,create_evaluation,get_evaluations,clear_evaluations
from numbers import Number
import re
import time
app=Flask(__name__)
CORS(app)
MAX_REPAIR_ATTEMPTS=2
EVALUATION_MODE=True
def detect_chart(results):
    if not results or not isinstance(results[0],dict):
        return None
    columns=list(results[0].keys())
    if len(columns)!=2:
        return None
    col1,col2=columns
    value1=results[0][col1]
    value2=results[0][col2]
    if isinstance(value1,Number) and not isinstance(value2,Number):
        value_col=col1
        label_col=col2
    elif isinstance(value2,Number) and not isinstance(value1,Number):
        value_col=col2
        label_col=col1
    else:
        return None
    labels=[str(row[label_col]) for row in results]
    values=[]
    for row in results:
        try:
            values.append(float(row[value_col]))
        except(TypeError,ValueError):
            return None
    label=label_col.lower()
    value=value_col.lower()
    time_words=["date","day","month","year","week","time"]
    if any(word in label for word in time_words):
        chart_type="line"
    elif any(word in label for word in ["gender","grade","category","status"]):
        chart_type="pie"
    elif any(word in value for word in ["percent","percentage","share"]):
        chart_type="doughnut"
    else:
        chart_type="bar"
    return {"type":chart_type,"title":f"{value_col.replace('_',' ').title()} by {label_col.replace('_',' ').title()}","labels":labels,"values":values}
def validate_input(question):
    if not question:
        return False,"Question is required."
    text=question.strip()
    if "\x00" in text:
        return False,"Invalid input detected."
    if re.search(r"--|/\*|\*/|#",text,re.IGNORECASE):
        return False,"SQL comments are not allowed."
    dangerous_statements=["INSERT","UPDATE","DELETE","DROP","ALTER","CREATE","TRUNCATE","REPLACE","GRANT","REVOKE","CALL","LOAD","HANDLER","LOCK","UNLOCK","SET","USE","RENAME"]
    for keyword in dangerous_statements:
        if re.search(rf"^\s*{keyword}\b",text,re.IGNORECASE):
            return False,"This action is not allowed. SQLSphere only permits read-only queries."
    if ";" in text:
        return False,"Multiple SQL statements are not allowed."
    if re.match(r"^\s*(SELECT|WITH)\b",text,re.IGNORECASE):
        if re.search(r"\b(?:INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|REPLACE|GRANT|REVOKE|CALL|LOAD|HANDLER|LOCK|UNLOCK|SET|USE|RENAME)\b",text,re.IGNORECASE):
            return False,"This action is not allowed. SQLSphere only permits read-only queries."
    if re.search(r"\bINTO\s+(?:OUTFILE|DUMPFILE)\b",text,re.IGNORECASE):
        return False,"This action is not allowed. SQLSphere only permits read-only queries."
    return True,text
def execute_sql(sql):
    connection=None
    cursor=None
    try:
        connection=db_pool.get_connection()
        cursor=connection.cursor(dictionary=True)
        cursor.execute(sql)
        results=cursor.fetchall()
        return True,results,None
    except Exception as e:
        return False,[],str(e)
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if connection:
            try:
                connection.close()
            except:
                pass
@app.route("/")
def home():
    return "AI-Powered Conversational Database Assistant Backend is Running!"
@app.route("/students")
def students():
    success,results,error=execute_sql("SELECT * FROM students")
    if not success:
        return jsonify({"error":error}),500
    return jsonify(results)
@app.route("/schema",methods=["GET"])
def schema():
    connection=None
    cursor=None
    try:
        connection=db_pool.get_connection()
        cursor=connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.TABLE_NAME,c.COLUMN_NAME,c.DATA_TYPE,c.COLUMN_KEY,c.IS_NULLABLE
            FROM information_schema.COLUMNS c
            WHERE c.TABLE_SCHEMA=%s
            ORDER BY c.TABLE_NAME,c.ORDINAL_POSITION
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
        tables={}
        for column in columns:
            table_name=column["TABLE_NAME"]
            if table_name not in tables:
                tables[table_name]={"table_name":table_name,"columns":[],"foreign_keys":[]}
            tables[table_name]["columns"].append({"name":column["COLUMN_NAME"],"type":column["DATA_TYPE"],"primary_key":column["COLUMN_KEY"]=="PRI","nullable":column["IS_NULLABLE"]=="YES"})
        for fk in foreign_keys:
            table_name=fk["TABLE_NAME"]
            if table_name in tables:
                tables[table_name]["foreign_keys"].append({"column":fk["COLUMN_NAME"],"referenced_table":fk["REFERENCED_TABLE_NAME"],"referenced_column":fk["REFERENCED_COLUMN_NAME"]})
        return jsonify({"database":connection.database,"tables":list(tables.values())})
    except Exception as e:
        print("[SQLSphere] Schema ERROR:",str(e))
        return jsonify({"error":str(e)}),500
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if connection:
            try:
                connection.close()
            except:
                pass
@app.route("/context/clear",methods=["POST"])
def clear_conversation_context():
    clear_context()
    return jsonify({"success":True,"message":"Conversation context cleared."})
@app.route("/context",methods=["GET"])
def conversation_context():
    return jsonify({"history":get_context()})
@app.route("/query",methods=["POST"])
def query():
    start_time=time.perf_counter()
    data=request.get_json(silent=True) or {}
    question=data.get("question","").strip()
    if not question:
        return jsonify({"error":"Question is required."}),400
    input_valid,input_result=validate_input(question)
    if not input_valid:
        print("[SQLSphere] Input blocked:",input_result)
        if EVALUATION_MODE:
            save_evaluation(create_evaluation(question,"",[],f"blocked: {input_result}",False,0,False,False,"",time.perf_counter()-start_time,False,input_result))
        return jsonify({"question":question,"error":input_result,"blocked":True}),400
    question=input_result
    print("\n"+"="*70)
    print("[SQLSphere] Question:",question)
    context=get_context()
    if context:
        latest=get_latest_context()
        print("[Context] Previous question:",latest["question"])
        print("[Context] Previous SQL:",latest["sql"])
    else:
        print("[Context] No previous conversation.")
    repair_attempts=0
    repair_history=[]
    original_sql=""
    final_sql=""
    try:
        grounding=ground_values(question)
        print("[Grounding] Results:",grounding)
        ambiguous=[item for item in grounding if item["status"] in ("ambiguous","low_confidence")]
        print("[Grounding] Ambiguous:",ambiguous)
        if ambiguous:
            if EVALUATION_MODE:
                save_evaluation(create_evaluation(question,"",grounding,"not executed - clarification required",False,0,False,False,"",time.perf_counter()-start_time,bool(context),"Clarification required"))
            return jsonify({"question":question,"clarification_required":True,"message":"Please clarify the value.","grounding":ambiguous}),200
        sql=generate_sql(question,grounding,context)
        original_sql=sql
        final_sql=sql
        print("[SQLSphere] Generated SQL:")
        print(sql)
        valid,result=validate_sql(sql)
        if not valid:
            print("[SQLSphere] Validation error:",result)
            if EVALUATION_MODE:
                save_evaluation(create_evaluation(question,sql,grounding,f"failed: {result}",False,0,False,False,sql,time.perf_counter()-start_time,bool(context),result))
            return jsonify({"question":question,"generated_sql":sql,"error":result,"blocked":True,"repair_attempted":False}),400
        sql=result
        final_sql=sql
        success,results,error=execute_sql(sql)
        if success:
            print("[SQLSphere] Rows returned:",len(results))
            add_context(question,sql,results)
            add_history(question,sql,len(results))
            chart=detect_chart(results)
            if EVALUATION_MODE:
                save_evaluation(create_evaluation(question,original_sql,grounding,"passed",True,len(results),False,False,sql,time.perf_counter()-start_time,bool(context)))
            print("[Context] Saved current query.")
            print("[History] Saved current query.")
            print("[SQLSphere] Success.")
            print("="*70)
            return jsonify({"question":question,"generated_sql":sql,"results":results,"chart":chart,"grounding":grounding,"repair_attempted":False,"repair_success":False,"repair_attempts":0,"final_sql":sql,"repair_history":[],"context_used":bool(context),"explanation":explain_sql(sql)})
        print("[SQLSphere] SQL execution error:",error)
        repair_error=error
        while repair_attempts<MAX_REPAIR_ATTEMPTS:
            repair_attempts+=1
            print(f"[Repair] Attempt {repair_attempts}/{MAX_REPAIR_ATTEMPTS}")
            repaired_sql=repair_sql(question,final_sql,repair_error,grounding)
            repair_record={"attempt":repair_attempts,"original_sql":final_sql,"error":repair_error,"repaired_sql":repaired_sql,"success":False}
            valid,repaired_result=validate_sql(repaired_sql)
            if not valid:
                repair_record["validation_error"]=repaired_result
                repair_history.append(repair_record)
                repair_error=repaired_result
                continue
            repaired_sql=repaired_result
            success,results,error=execute_sql(repaired_sql)
            if success:
                repair_record["success"]=True
                repair_history.append(repair_record)
                final_sql=repaired_sql
                add_context(question,final_sql,results)
                add_history(question,final_sql,len(results))
                if EVALUATION_MODE:
                    save_evaluation(create_evaluation(question,original_sql,grounding,"passed after repair",True,len(results),True,True,final_sql,time.perf_counter()-start_time,bool(context),None))
                print("[Repair] Repair successful.")
                chart=detect_chart(results)
                print("[SQLSphere] Rows returned:",len(results))
                print("[Context] Saved repaired query.")
                print("[History] Saved repaired query.")
                print("[SQLSphere] Success after repair.")
                print("="*70)
                return jsonify({"question":question,"generated_sql":original_sql,"results":results,"chart":chart,"grounding":grounding,"repair_attempted":True,"repair_success":True,"repair_attempts":repair_attempts,"final_sql":final_sql,"repair_history":repair_history,"context_used":bool(context),"explanation":explain_sql(final_sql)})
            repair_record["error_after_repair"]=error
            repair_history.append(repair_record)
            final_sql=repaired_sql
            repair_error=error
        print("[Repair] All repair attempts failed.")
        if EVALUATION_MODE:
            save_evaluation(create_evaluation(question,original_sql,grounding,"passed validation; execution failed",False,0,True,False,final_sql,time.perf_counter()-start_time,bool(context),repair_error))
        return jsonify({"question":question,"generated_sql":original_sql,"results":[],"chart":None,"grounding":grounding,"repair_attempted":True,"repair_success":False,"repair_attempts":repair_attempts,"final_sql":final_sql,"repair_history":repair_history,"context_used":bool(context),"error":repair_error}),500
    except Exception as e:
        error=str(e)
        error_lower=error.lower()
        print("[SQLSphere] ERROR:",error)
        print("="*70)
        if EVALUATION_MODE:
            save_evaluation(create_evaluation(question,original_sql,[], "error",False,0,repair_attempts>0,False,final_sql,time.perf_counter()-start_time,False,error))
        if "temporarily unavailable" in error_lower or "503" in error or "unavailable" in error_lower or "high demand" in error_lower:
            return jsonify({"question":question,"error":"The AI service is temporarily unavailable. Please try again in a moment.","error_type":"gemini_unavailable"}),503
        if "quota" in error_lower or "429" in error or "resource exhausted" in error_lower:
            return jsonify({"question":question,"error":"The AI service is temporarily busy. Please try again in a moment.","error_type":"gemini_rate_limit"}),429
        if "deadline" in error_lower or "timeout" in error_lower:
            return jsonify({"question":question,"error":"The AI service took too long to respond. Please try again.","error_type":"gemini_timeout"}),504
        return jsonify({"question":question,"error":error}),500
@app.route("/history",methods=["GET"])
def query_history():
    return jsonify({"history":get_history()})
@app.route("/history/clear",methods=["POST"])
def clear_query_history():
    clear_history()
    return jsonify({"success":True,"message":"Query history cleared."})
@app.route("/evaluation",methods=["GET"])
def evaluation():
    if not EVALUATION_MODE:
        return jsonify({"error":"Not found"}),404
    return jsonify({"mode":"development_evaluation","evaluations":get_evaluations()})
@app.route("/evaluation/clear",methods=["POST"])
def clear_evaluation():
    if not EVALUATION_MODE:
        return jsonify({"error":"Not found"}),404
    clear_evaluations()
    return jsonify({"success":True,"message":"Evaluation data cleared."})
if __name__=="__main__":
    app.run(host="127.0.0.1",port=5000,debug=False,use_reloader=False)