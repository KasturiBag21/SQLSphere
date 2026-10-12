import React,{useEffect,useMemo,useState} from "react";
import {Chart as ChartJS,CategoryScale,LinearScale,BarElement,PointElement,LineElement,ArcElement,Tooltip,Legend} from "chart.js";
import {Bar,Line,Pie,Doughnut} from "react-chartjs-2";
ChartJS.register(CategoryScale,LinearScale,BarElement,PointElement,LineElement,ArcElement,Tooltip,Legend);
const CHART_COLORS=["#60A5FA","#A78BFA","#F472B6","#FB923C","#34D399","#22D3EE","#FACC15","#F87171","#818CF8","#2DD4BF"];
function AutoChart({chart}){
  const [chartType,setChartType]=useState("bar");
  useEffect(()=>{
    if(chart?.type)setChartType(chart.type);
  },[chart]);
  const chartData=useMemo(()=>{
    if(!chart)return null;
    const labels=chart.labels||[];
    const values=(chart.values||[]).map(value=>Number(value));
    const backgroundColors=labels.map((_,index)=>CHART_COLORS[index%CHART_COLORS.length]);
    const isCircular=chartType==="pie"||chartType==="doughnut";
    return {
      labels,
      datasets:[{
        label:chart.title||"Results",
        data:values,
        backgroundColor:backgroundColors,
        borderColor:isCircular?"#ffffff":"#73787f",
        borderWidth:isCircular?3:2,
        borderRadius:chartType==="bar"?8:0,
        borderSkipped:false,
        tension:0.35,
        pointBackgroundColor:"#8B5CF6",
        pointBorderColor:"#ffffff",
        pointBorderWidth:2,
        pointRadius:chartType==="line"?5:0,
        pointHoverRadius:chartType==="line"?7:0,
        hoverBorderWidth:3,
        hoverOffset:isCircular?8:0
      }]
    };
  },[chart,chartType]);
  if(!chart||!chartData)return null;
  const isCircular=chartType==="pie"||chartType==="doughnut";
  const options={
    responsive:true,
    maintainAspectRatio:false,
    animation:{duration:1000},
    plugins:{
      legend:{
        display:isCircular,
        position:"bottom",
        labels:{padding:16,usePointStyle:true,boxWidth:10,font:{size:12}},
        maxHeight:80
      },
      tooltip:{
        enabled:true,
        callbacks:{label:function(context){return ` ${context.raw}`;}}
      }
    },
    scales:isCircular?{}:{
      x:{grid:{display:true},ticks:{maxRotation:45,minRotation:0}},
      y:{beginAtZero:true,grid:{display:true}}
    }
  };
  return (
    <div className="auto-chart-container">
      <div className="chart-heading">
        <span>📊 {chart.title||"Data Visualization"}</span>
        <span className="chart-badge">AI Suggested</span>
      </div>
      <div className="chart-controls">
        <button type="button" className={chartType==="bar"?"active-chart":""} onClick={()=>setChartType("bar")}>📊 Bar</button>
        <button type="button" className={chartType==="line"?"active-chart":""} onClick={()=>setChartType("line")}>📈 Line</button>
        <button type="button" className={chartType==="pie"?"active-chart":""} onClick={()=>setChartType("pie")}>🥧 Pie</button>
        <button type="button" className={chartType==="doughnut"?"active-chart":""} onClick={()=>setChartType("doughnut")}>🍩 Doughnut</button>
      </div>
      <div className="chart-wrapper">
        {chartType==="bar"&&<Bar data={chartData} options={options}/>}
        {chartType==="line"&&<Line data={chartData} options={options}/>}
        {chartType==="pie"&&<Pie data={chartData} options={options}/>}
        {chartType==="doughnut"&&<Doughnut data={chartData} options={options}/>}
      </div>
    </div>
  );
}
export default AutoChart;