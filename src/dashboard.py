import streamlit as st
import requests
import pandas as pd
import json
import os
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Set page config
st.set_page_config(
    page_title="Fraud Detection MLOps Command Center",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
API_URL = "http://fraud-detection-pipeline:8000"
METRICS_PATH = "artifacts/models/metrics.json"
DRIFT_REPORT_PATH = "artifacts/drift_report.html"

# Styles
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stCard {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🛡️ Sentinel MLOps")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🚀 Pipeline Overview",
        "📊 Model Performance",
        "⚡ Real-time Inference",
        "📉 Data Drift Analysis",
        "🏥 System Health"
    ])
    st.markdown("---")
    st.markdown("### System Info")
    st.info(f"Last Refreshed: {datetime.now().strftime('%H:%M:%S')}")
    if st.button("Refresh Data"):
        st.rerun()

def get_pipeline_status():
    # In a real scenario, this would check a database or file locks
    # Here we check file mtimes through the shared volume (mounted in docker-compose)
    steps = {
        "1. Data Ingestion": "artifacts/raw.csv",
        "2. Data Validation": "artifacts/raw.csv", 
        "3. Feature Engineering": "artifacts/scaler.pkl",
        "4. Data Splitting": "artifacts/train.csv",
        "5. Model Training": "artifacts/models/metrics.json",
        "6. Model Monitoring": "artifacts/drift_report.html"
    }
    status_data = []
    for step, path in steps.items():
        status = "Pending"
        timestamp = "-"
        if os.path.exists(path):
            status = "Completed"
            timestamp = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
        status_data.append({"Step": step, "Status": status, "Last Updated": timestamp})
    return pd.DataFrame(status_data)

# --- Pages ---

if page == "🚀 Pipeline Overview":
    st.title("🚀 End-to-End MLOps Pipeline")
    st.markdown("Visualizing the complete lifecycle of the Fraud Detection System.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Pipeline Architecture")
        st.graphviz_chart("""
            digraph G {
                rankdir=LR;
                node [shape=box, style=filled, fillcolor="#E8F4F9", fontname="Helvetica"];
                edge [fontname="Helvetica"];
                
                Source [label="Dataset\n(creditcard.csv)", shape=ellipse, fillcolor="#FFE0B2"];
                Ingestion [label="Data Ingestion\n(Pandas Load)"];
                Validation [label="Data Validation\n(Great Expectations)"];
                FeatureEng [label="Feature Engineering\n(Scaling Amount)"];
                Splitting [label="Data Splitting\n(Train/Test)"];
                Training [label="Model Training\n(XGBoost/LGBM/LogReg)"];
                Registration [label="Model Registration\n(MLflow)"];
                Inference [label="Inference API\n(FastAPI)"];
                Monitoring [label="Monitoring\n(Evidently/Prometheus)"];
                
                Source -> Ingestion;
                Ingestion -> Validation;
                Validation -> FeatureEng;
                FeatureEng -> Splitting;
                Splitting -> Training;
                Training -> Registration;
                Registration -> Inference;
                Inference -> Monitoring;
                Training -> Monitoring [style=dashed, label="Ref Data"];
            }
        """)
        
    with col2:
        st.subheader("Step Status")
        status_df = get_pipeline_status()
        
        for index, row in status_df.iterrows():
            color = "green" if row['Status'] == "Completed" else "gray"
            with st.container():
                st.markdown(f"""
                <div style="border-left: 5px solid {color}; padding-left: 10px; margin-bottom: 10px; background-color: white; padding: 10px; border-radius: 5px;">
                    <strong>{row['Step']}</strong><br>
                    <span style="color: {color}">{row['Status']}</span> | <small>{row['Last Updated']}</small>
                </div>
                """, unsafe_allow_html=True)

elif page == "📊 Model Performance":
    st.title("📊 Model Evaluation Metrics")
    
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r") as f:
                metrics = json.load(f)
                
            st.markdown("### Competitive Analysis")
            
            # Prepare data for plotting
            models = list(metrics.keys())
            aucs = [m['AUC'] for m in metrics.values()]
            precisions = [m['Precision_Fraud'] for m in metrics.values()]
            recalls = [m['Recall_Fraud'] for m in metrics.values()]
            f1s = [m['F1_Fraud'] for m in metrics.values()]
            
            metric_df = pd.DataFrame({
                "Model": models,
                "AUC": aucs,
                "Precision (Fraud)": precisions,
                "Recall (Fraud)": recalls,
                "F1 (Fraud)": f1s
            })
            
            # Interactive Bar Chart
            fig = px.bar(metric_df.melt(id_vars="Model"), x="variable", y="value", color="Model", barmode="group",
                         title="Model Metric Comparison", height=500)
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed Table
            st.markdown("### Detailed Metrics")
            st.dataframe(metric_df.style.highlight_max(axis=0, color='lightgreen'), use_container_width=True)
            
        except Exception as e:
            st.error(f"Error loading metrics: {e}")
    else:
        st.warning("Metrics file not found. Please run the pipeline first.")

elif page == "⚡ Real-time Inference":
    st.title("⚡ Real-time Fraud Detection")
    st.markdown("Test the deployed model with transaction data.")
    
    col1, col2 = st.columns([1, 2])
    
    def predict_request(data):
        try:
            response = requests.post(f"{API_URL}/predict", json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    with col1:
        st.subheader("Transaction Details")
        with st.form("inference_form"):
            amount = st.number_input("Transaction Amount ($)", value=100.0, step=10.0)
            time_val = st.number_input("Time (Sec)", value=0.0, step=1.0)
            
            st.markdown("#### Anonymized Features (V1-V28)")
            # Simplify inputs for demo - mostly sliders or small randoms for V features
            v_input = {}
            expanded = st.expander("Configure V1-V28", expanded=False)
            with expanded:
                for i in range(1, 29):
                    v_input[f"V{i}"] = st.number_input(f"V{i}", value=0.0, step=0.1, key=f"V{i}")
            
            submit_button = st.form_submit_button("Analyze Transaction")
            
    with col2:
        st.subheader("Analysis Result")
        if submit_button:
            payload = {"Time": time_val, "Amount": amount}
            payload.update(v_input)
            
            with st.spinner("Analyzing transaction patterns..."):
                result = predict_request(payload)
                
            if "error" in result:
                st.error(f"Prediction Failed: {result['error']}")
            else:
                prob = result['probability']
                is_fraud = result['is_fraud']
                
                # Gauge Chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = prob * 100,
                    title = {'text': "Fraud Probability (%)"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "red" if is_fraud else "green"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgreen"},
                            {'range': [50, 100], 'color': "lightpink"}],
                    }
                ))
                st.plotly_chart(fig)
                
                if is_fraud:
                    st.error(f"🚨 FRAUD DETECTED! (Probability: {prob:.4f})")
                else:
                    st.success(f"✅ Legitimate Transaction (Probability: {prob:.4f})")

elif page == "📉 Data Drift Analysis":
    st.title("📉 Data Drift & Quality Report")
    st.markdown("Monitoring data distribution changes over time using **Evidently**.")
    
    if os.path.exists(DRIFT_REPORT_PATH):
        with open(DRIFT_REPORT_PATH, 'r', encoding='utf-8') as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=1000, scrolling=True)
    else:
        st.warning("Drift report not found. Please run the model monitoring step.")

elif page == "🏥 System Health":
    st.title("🏥 System Observability")
    
    col1, col2, col3 = st.columns(3)
    
    def check_health(url, name):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return "✅ Online"
            else:
                return f"⚠️ Status {response.status_code}"
        except:
            return "❌ Offline"

    with col1:
        st.metric("FastAPI Backend", check_health(f"{API_URL}/api/health", "API"))
    with col2:
        st.metric("MLflow Tracking", check_health("http://mlflow-ui:5000/health", "MLflow"))
    with col3:
        st.metric("Prometheus", check_health("http://prometheus:9090/-/healthy", "Prometheus"))
        
    st.markdown("### External Dashboards")
    st.markdown("""
    - [**MLflow UI**](http://localhost:5000) - Experiment Tracking & Model Registry
    - [**Grafana**](http://localhost:3000) - System Metrics & Alerting
    - [**Prometheus**](http://localhost:9090) - Raw Metric Queries
    """)
    
    st.markdown("### Prometheus Metrics Preview")
    try:
        metrics_res = requests.get(f"{API_URL}/metrics")
        st.code(metrics_res.text, language="text", line_numbers=True)
    except:
        st.error("Could not fetch raw metrics.")
