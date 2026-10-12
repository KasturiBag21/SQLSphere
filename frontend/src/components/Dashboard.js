import React,{useEffect,useState} from "react";
import axios from "axios";
import {useNavigate} from "react-router-dom";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import "../App.css";
import Earth3D from "./Earth3D";
import AutoChart from "./AutoChart";
import SchemaExplorer from "./SchemaExplorer";

const highlightSQL=(sql)=>{
  if(!sql)return null;
  const tokens=sql.split(/(\b(?:SELECT|FROM|JOIN|LEFT|RIGHT|INNER|OUTER|FULL|CROSS|ON|WHERE|GROUP|BY|ORDER|ASC|DESC|HAVING|LIMIT|OFFSET|AS|AND|OR|NOT|IN|IS|NULL|LIKE|BETWEEN|UNION|ALL|DISTINCT|WITH|CASE|WHEN|THEN|ELSE|END)\b|\b(?:COUNT|SUM|AVG|MIN|MAX|ROUND|COALESCE|CONCAT)\b|\b\d+(?:\.\d+)?\b|'[^']*'|"[^"]*"|[=<>!]+|[(),;])/gi);
  return tokens.map((token,index)=>{
    if(!token)return null;
    const upper=token.toUpperCase();
    if(["SELECT","FROM","JOIN","LEFT","RIGHT","INNER","OUTER","FULL","CROSS","ON","WHERE","GROUP","BY","ORDER","ASC","DESC","HAVING","LIMIT","OFFSET","AS","AND","OR","NOT","IN","IS","NULL","LIKE","BETWEEN","UNION","ALL","DISTINCT","WITH","CASE","WHEN","THEN","ELSE","END"].includes(upper))return <span className="sql-keyword" key={index}>{token}</span>;
    if(["COUNT","SUM","AVG","MIN","MAX","ROUND","COALESCE","CONCAT"].includes(upper))return <span className="sql-function" key={index}>{token}</span>;
    if(/^\d+(?:\.\d+)?$/.test(token))return <span className="sql-number" key={index}>{token}</span>;
    if((token.startsWith("'")&&token.endsWith("'"))||(token.startsWith('"')&&token.endsWith('"')))return <span className="sql-string" key={index}>{token}</span>;
    if(/^[=<>!]+$/.test(token))return <span className="sql-operator" key={index}>{token}</span>;
    if(/^[(),;]$/.test(token))return <span className="sql-punctuation" key={index}>{token}</span>;
    if(/^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*$/.test(token)){
      const [alias,column]=token.split(".");
      return <span className="sql-column" key={index}><span className="sql-alias">{alias}</span><span className="sql-dot">.</span>{column}</span>;
    }
    return <span className="sql-normal" key={index}>{token}</span>;
  });
};

function Dashboard(){
  const navigate=useNavigate();
  const [question,setQuestion]=useState("");
  const [sql,setSql]=useState("");
  const [results,setResults]=useState([]);
  const [chart,setChart]=useState(null);
  const [loading,setLoading]=useState(false);
  const [clarification,setClarification]=useState(null);
  const [explanation,setExplanation]=useState("");
  const [queryHistory,setQueryHistory]=useState([]);
  const [historyLoading,setHistoryLoading]=useState(false);
  const [activeView,setActiveView]=useState("dashboard");
  const [sidebarOpen,setSidebarOpen]=useState(false);
  const [darkMode,setDarkMode]=useState(()=>localStorage.getItem("sqlsphereDarkMode")==="true");
  const [showSQL,setShowSQL]=useState(()=>localStorage.getItem("sqlsphereShowSQL")!=="false");
  const [showExplanation,setShowExplanation]=useState(()=>localStorage.getItem("sqlsphereShowExplanation")!=="false");
  const [visualization,setVisualization]=useState(()=>localStorage.getItem("sqlsphereVisualization")||"Auto");
  const [repairInfo,setRepairInfo]=useState(null);
  const [loadingText,setLoadingText]=useState("🤖 Analysing your question...");

  const loadingMessages=[
    "🤖 Analysing your question...",
    "🧠 Understanding database schema...",
    "🔗 Finding table relationships...",
    "⚡ Generating optimized SQL...",
    "📊 Executing SQL query..."
  ];

  useEffect(()=>{
    document.body.classList.toggle("sqlsphere-dark",darkMode);
    localStorage.setItem("sqlsphereDarkMode",String(darkMode));
  },[darkMode]);

  useEffect(()=>{
    if(!loading)return;
    let index=0;
    const interval=setInterval(()=>{
      index=(index+1)%loadingMessages.length;
      setLoadingText(loadingMessages[index]);
    },900);
    return()=>clearInterval(interval);
  },[loading]);

  useEffect(()=>{loadHistory();},[]);

  const loadHistory=async()=>{
    try{
      setHistoryLoading(true);
      const response=await axios.get("http://127.0.0.1:5000/history");
      setQueryHistory(response.data.history||[]);
    }catch(error){
      console.error("History loading error:",error);
    }finally{
      setHistoryLoading(false);
    }
  };

  const handleLogout=()=>{
    localStorage.removeItem("isLoggedIn");
    navigate("/");
  };

  const clearQueryHistory=async()=>{
    try{
      await axios.post("http://127.0.0.1:5000/history/clear");
      setQueryHistory([]);
    }catch(error){
      console.error("History clear error:",error);
      alert("Unable to clear query history.");
    }
  };

  const clearContext=async()=>{
    try{
      await axios.post("http://127.0.0.1:5000/context/clear");
      alert("Conversation context cleared.");
    }catch(error){
      alert("Unable to clear conversation context.");
    }
  };

  const clearEvaluation=async()=>{
    try{
      await axios.post("http://127.0.0.1:5000/evaluation/clear");
      alert("Evaluation data cleared.");
    }catch(error){
      alert("Unable to clear evaluation data.");
    }
  };

  const changeView=(view)=>{
  setActiveView(view);
  if(view==="history")loadHistory();
  };

  const runHistoryQuery=(historyQuestion)=>{
  setQuestion(historyQuestion);
  setActiveView("dashboard");
  askQuestion(historyQuestion);
  window.scrollTo({top:0,behavior:"smooth"});
  };

  const exportCSV=()=>{
    if(!results||results.length===0){
      alert("There are no results to export.");
      return;
    }
    const headers=Object.keys(results[0]);
    const csvRows=[headers.join(","),...results.map(row=>headers.map(header=>{
      const value=row[header]??"";
      return `"${String(value).replace(/"/g,'""')}"`;
    }).join(","))];
    const blob=new Blob([csvRows.join("\n")],{type:"text/csv;charset=utf-8;"});
    const url=URL.createObjectURL(blob);
    const link=document.createElement("a");
    link.href=url;
    link.download="sqlsphere_results.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  const exportExcel=()=>{
    if(!results||results.length===0){
      alert("There are no results to export.");
      return;
    }
    const worksheet=XLSX.utils.json_to_sheet(results);
    const workbook=XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook,worksheet,"SQLSphere Results");
    XLSX.writeFile(workbook,"sqlsphere_results.xlsx");
  };

  const exportPDF=()=>{
    if(!results||results.length===0){
      alert("There are no results to export.");
      return;
    }
    const doc=new jsPDF({orientation:"landscape",unit:"mm",format:"a4"});
    doc.setFontSize(18);
    doc.text("SQLSphere - Query Results",14,15);
    doc.setFontSize(10);
    doc.text(`Question: ${question}`,14,23);
    const headers=Object.keys(results[0]);
    const rows=results.map(row=>headers.map(header=>row[header]===null||row[header]===undefined?"":String(row[header])));
    autoTable(doc,{head:[headers],body:rows,startY:30,styles:{fontSize:8,cellPadding:3},headStyles:{fontSize:8,fontStyle:"bold"},alternateRowStyles:{fillColor:[245,247,250]},margin:{left:10,right:10}});
    doc.save("sqlsphere_results.pdf");
  };

  const askQuestion=async(customQuestion=null)=>{
    const query=customQuestion??question;
    if(!query.trim()||loading)return;
    setLoading(true);
    setSql("");
    setResults([]);
    setChart(null);
    setClarification(null);
    setExplanation("");
    setRepairInfo(null);
    try{
      const response=await axios.post("http://127.0.0.1:5000/query",{question:query});
      console.log("Backend Response:",response.data);
      if(response.data.clarification_required){
        setClarification(response.data);
        return;
      }
      if(response.data.error){
        alert(response.data.error);
        setSql(response.data.generated_sql||"");
        setResults([]);
        setChart(null);
        setExplanation("");
      }else{
        setSql(response.data.generated_sql||"");
        setResults(response.data.results||[]);
        setChart(response.data.chart||null);
        setExplanation(response.data.explanation||"");
        if(response.data.repair_success){
          setRepairInfo({
            attempts:response.data.repair_attempts||1,
            finalSql:response.data.final_sql||response.data.generated_sql||""
          });
        }
        await loadHistory();
      }
    }catch(err){
      console.error("Request error:",err);
      const backendError=err.response?.data?.error||err.response?.data?.message||err.message||"An unexpected error occurred.";
      alert(backendError);
      if(err.response?.data?.generated_sql)setSql(err.response.data.generated_sql);
    }finally{
      setLoading(false);
    }
  };

  const selectClarification=(originalValue,selectedValue)=>{
    const updatedQuestion=question.replace(new RegExp(originalValue.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"),"i"),selectedValue);
    setQuestion(updatedQuestion);
    setClarification(null);
    askQuestion(updatedQuestion);
  };

  const Toggle=({checked,onChange})=><button type="button" className={`settings-toggle ${checked?"active":""}`} onClick={()=>onChange(!checked)} aria-label="Toggle setting"><span></span></button>;

  const Sidebar=()=>(
    <>
      <button
  type="button"
  className={`hamburger-button ${sidebarOpen?"open":""}`}
  onClick={()=>setSidebarOpen(prev=>!prev)}
  aria-label={sidebarOpen?"Close menu":"Open menu"}
  aria-expanded={sidebarOpen}
>
  <span></span>
  <span></span>
  <span></span>
</button>
    {sidebarOpen&&<div className="sidebar-backdrop"></div>}
      <aside className={`app-sidebar ${sidebarOpen?"sidebar-open":""}`}>
        <div className="sidebar-brand">
          <span className="sidebar-brand-icon">🌐</span>
          <span>SQLSphere</span>
        </div>
        <nav className="sidebar-nav">
          <button className={activeView==="dashboard"?"active":""} onClick={()=>changeView("dashboard")}><span>🏠</span>Dashboard</button>
          <button className={activeView==="history"?"active":""} onClick={()=>changeView("history")}><span>🕘</span>Query History</button>
          <button className={activeView==="schema"?"active":""} onClick={()=>changeView("schema")}><span>🗄️</span>Database Schema</button>
          <button className={activeView==="settings"?"active":""} onClick={()=>changeView("settings")}><span>⚙️</span>Settings</button>
        </nav>
        <div className="sidebar-bottom">
          <button className="sidebar-logout" onClick={handleLogout}><span>🚪</span>Logout</button>
        </div>
      </aside>
    </>
  );

  const DashboardView=()=>(
    <>
      <div className="page-header dashboard-header">
        <div>
          <h1>SQLSphere</h1>
          <p>AI-Powered Conversational Database Assistant</p>
        </div>
      </div>
      <div className="logo-container dashboard-logo">
        <div className="earth-wrapper">
          <div className="earth-ring"></div>
          <div className="earth-ring earth-ring2"></div>
          <Earth3D/>
        </div>
      </div>
      <div className="search-box">
        <input type="text" placeholder="Ask your database in plain English..." value={question} onChange={e=>setQuestion(e.target.value)} onKeyDown={e=>{if(e.key==="Enter"&&!loading)askQuestion();}}/>
        <button onClick={()=>askQuestion()} disabled={loading}>{loading?"Generating...":"Generate SQL"}</button>
      </div>
      {clarification&&(
        <div className="card clarification-card">
          <h2>🔎 Please clarify</h2>
          <p>{clarification.message||"Multiple database values match your request."}</p>
          {clarification.grounding?.map((item,index)=>(
            <div className="clarification-item" key={`${item.table}-${item.column}-${index}`}>
              <p><strong>"{item.original_value}"</strong></p>
              <p className="muted-text">Possible values from <strong>{item.table}.{item.column}</strong></p>
              {item.alternatives?.map((option,optionIndex)=>(
                <button className="clarification-option" key={`${option.value}-${optionIndex}`} onClick={()=>selectClarification(item.original_value,option.value)}>
                  {optionIndex+1}. {option.value}
                </button>
              ))}
            </div>
          ))}
        </div>
      )}
      {showSQL&&(
        <div className="card">
          <h2>Generated SQL</h2>
          {loading?(
            <div className="ai-loading">
              <div className="ai-brain">🤖</div>
              <h3 className="typing-text">{loadingText}</h3>
              <p className="loading-subtitle">Gemini AI is processing your request...</p>
              <div className="progress-bar"><div className="progress-fill"></div></div>
              <div className="loading-dots"><span></span><span></span><span></span></div>
            </div>
          ):(
            <pre className="sql-code">{sql?highlightSQL(sql):"Your generated SQL will appear here..."}</pre>
          )}
        </div>
      )}
      {showExplanation&&explanation&&(
        <div className="card">
          <h2>SQL Explanation</h2>
          <p className="explanation-text">{explanation}</p>
        </div>
      )}
      {repairInfo&&(
        <div className="card repair-card">
          <h2>🔧 Query Automatically Repaired</h2>
          <p>SQLSphere detected an SQL execution error and automatically repaired the query using Gemini AI.</p>
          <p>Repair attempts: <strong>{repairInfo.attempts}</strong></p>
          {repairInfo.finalSql&&<details><summary>View Corrected SQL</summary><pre className="sql-code repair-sql">{highlightSQL(repairInfo.finalSql)}</pre></details>}
        </div>
      )}
      <div className="card">
        <div className="section-heading-row">
          <div>
            <h2>Results</h2>
            <p className="muted-text">Database query results</p>
          </div>
          {!loading&&results.length>0&&<div className="export-controls">
            <button onClick={exportCSV}>📄 Export CSV</button>
            <button onClick={exportExcel}>📊 Export Excel</button>
            <button onClick={exportPDF}>📕 Export PDF</button>
          </div>}
        </div>
        {loading?<p className="empty-message">Waiting for AI to execute the SQL query...</p>:results.length===0?<p className="empty-message">No records found.</p>:(
          <>
            <div className="table-wrapper">
              <table>
                <thead><tr>{Object.keys(results[0]).map(key=><th key={key}>{key}</th>)}</tr></thead>
                <tbody>{results.map((row,index)=><tr key={index}>{Object.values(row).map((value,i)=><td key={i}>{String(value)}</td>)}</tr>)}</tbody>
              </table>
            </div>
            {chart&&<div className="visualization-section"><h3>📊 Data Visualization</h3><AutoChart chart={chart}/></div>}
          </>
        )}
      </div>
    </>
  );

  const HistoryView=()=>(
    <div className="content-view">
      <div className="page-header">
        <div>
          <h1>🕘 Query History</h1>
          <p>Your recent successful database queries</p>
        </div>
        {queryHistory.length>0&&<button className="danger-button clear-history-button" onClick={clearQueryHistory}>🗑 Clear History</button>}
      </div>
      <div className="history-list">
        {historyLoading?<div className="card empty-message">Loading query history...</div>:queryHistory.length===0?(
          <div className="card empty-message"><div className="empty-icon">🕘</div><p>No query history yet.</p><span>Successful queries will appear here.</span></div>
        ):queryHistory.map((item,index)=>(
          <div className="history-card" key={`${item.timestamp}-${index}`}>
            <div className="history-main">
              <div className="history-question">{item.question}</div>
              <div className="history-meta">🕒 {item.timestamp} <span>•</span> 📊 {item.row_count} rows</div>
            </div>
            <div className="history-actions">
              <button className="danger-button history-action-button" onClick={()=>runHistoryQuery(item.question)}>▶ Run Again</button>
              {item.sql&&<details className="history-sql-details">
                <summary className="danger-button history-action-button">▾ View SQL</summary>
                <pre className="history-sql-code">{item.sql}</pre>
              </details>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const SettingsView=()=>(
    <div className="content-view settings-view">
      <div className="page-header">
        <div>
          <h1>⚙️ Settings</h1>
          <p>Customize your SQLSphere experience</p>
        </div>
      </div>
      <div className="settings-card">
        <div className="settings-card-title"><span>🎨</span><div><h2>Appearance</h2><p>Choose how SQLSphere should look and feel.</p></div></div>
        <div className="setting-row">
          <div><h3>Dark Mode</h3><p>Use the dark interface for a comfortable viewing experience.</p></div>
          <Toggle checked={darkMode} onChange={setDarkMode}/>
        </div>
      </div>
      <div className="settings-card">
        <div className="settings-card-title"><span>🎛️</span><div><h2>Query Preferences</h2><p>Control how SQLSphere presents and processes your queries.</p></div></div>
        <div className="setting-row">
          <div><h3>Default Visualization</h3><p>Choose the preferred chart type for compatible query results.</p></div>
          <select value={visualization} onChange={e=>{setVisualization(e.target.value);localStorage.setItem("sqlsphereVisualization",e.target.value);}}>
            <option>Auto</option><option>Bar</option><option>Line</option><option>Pie</option><option>Doughnut</option>
          </select>
        </div>
        <div className="setting-row">
          <div><h3>Show Generated SQL</h3><p>Display the SQL statement generated by Gemini AI.</p></div>
          <Toggle checked={showSQL} onChange={value=>{setShowSQL(value);localStorage.setItem("sqlsphereShowSQL",String(value));}}/>
        </div>
        <div className="setting-row">
          <div><h3>Show SQL Explanation</h3><p>Display a simple explanation of the generated SQL query.</p></div>
          <Toggle checked={showExplanation} onChange={value=>{setShowExplanation(value);localStorage.setItem("sqlsphereShowExplanation",String(value));}}/>
        </div>
      </div>
      <div className="settings-card">
        <div className="settings-card-title"><span>🧹</span><div><h2>Application</h2><p>Manage temporary SQLSphere application data.</p></div></div>
        <div className="setting-row">
          <div><h3>Conversation Context</h3><p>Clear the current conversation context used for follow-up queries.</p></div>
          <button className="danger-button settings-action" onClick={clearContext}>Clear Context</button>
        </div>
        <div className="setting-row">
          <div><h3>Query History</h3><p>Remove saved successful queries from the current session.</p></div>
          <button className="danger-button settings-action" onClick={clearQueryHistory}>Clear History</button>
        </div>
        <div className="setting-row">
          <div><h3>Evaluation Data</h3><p>Clear development evaluation records generated during testing.</p></div>
          <button className="danger-button settings-action" onClick={clearEvaluation}>Clear Evaluation</button>
        </div>
      </div>
      <div className="settings-card account-card">
        <div className="settings-card-title"><span>👤</span><div><h2>Account</h2><p>Manage your SQLSphere session.</p></div></div>
        <div className="setting-row">
          <div><h3>Logout</h3><p>Sign out of the current SQLSphere session.</p></div>
          <button className="danger-button logout-settings-button" onClick={handleLogout}>🚪 Logout</button>
        </div>
      </div>
    </div>
  );

  return(
    <div className={`dashboard-page ${darkMode?"dark-mode":""}`}>
      {Sidebar()}
      <div className="dashboard-overlay">
        <main className="main-content">
          {activeView==="dashboard"&&DashboardView()}
{activeView==="history"&&HistoryView()}
{activeView==="schema"&&<div className="content-view"><div className="page-header"><div><h1>🗄️ Database Schema</h1><p>Explore the SQLSphere database structure and relationships.</p></div></div><SchemaExplorer/></div>}
{activeView==="settings"&&SettingsView()}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;