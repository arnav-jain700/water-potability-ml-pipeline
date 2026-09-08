import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="AquaGuard ML: Water Potability Triage",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CACHED MODEL LOADER
@st.cache_resource
def load_pipeline():
    model_path = os.path.join(os.path.dirname(__file__), "models", "water_potability_pipeline.joblib")
    if not os.path.exists(model_path):
        model_path = "models/water_potability_pipeline.joblib"
    return joblib.load(model_path)

try:
    pipeline = load_pipeline()
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)

# 3. WHO / EPA SAFE RANGES REFERENCE
SAFE_LIMITS = {
    "ph": (6.5, 8.5, "pH units"),
    "Hardness": (150.0, 300.0, "mg/L"),
    "Solids": (0.0, 1000.0, "ppm (TDS)"),
    "Chloramines": (0.0, 4.0, "ppm"),
    "Sulfate": (0.0, 250.0, "mg/L"),
    "Conductivity": (0.0, 400.0, "uS/cm"),
    "Organic_carbon": (0.0, 4.0, "ppm (TOC)"),
    "Trihalomethanes": (0.0, 80.0, "ug/L (THMs)"),
    "Turbidity": (0.0, 5.0, "NTU")
}

# --- HEADER SECTION ---
st.title("🌊 AquaGuard ML: Municipal Water Potability Triage Engine")
st.caption("Production-Grade Machine Learning Pipeline | CSD 302 Capstone Project | Developer: Arnav Jain")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Operating Policy")
policy_mode = st.sidebar.radio(
    "Classification Policy:",
    ["Public Health Safety (tau = 0.65)", "Standard Commercial (tau = 0.50)"],
    help="Public safety policy requires 65% confidence before declaring water potable."
)
threshold = 0.65 if "0.65" in policy_mode else 0.50

st.sidebar.divider()
st.sidebar.header("Sample Telemetry Input")

station_type = st.sidebar.selectbox(
    "Station Catchment Type:",
    ["Urban_Treatment", "Agricultural_Runoff", "Industrial_Catchment", "Reservoir_Lake", "River_Basin"]
)

data_source = st.sidebar.selectbox(
    "Telemetry Provenance:",
    ["Regional_Network_B", "Global_Survey_A"]
)

st.sidebar.subheader("Biochemical Parameters")
ph_val = st.sidebar.slider("pH Equilibrium", 0.0, 14.0, 7.25, 0.05)
hardness_val = st.sidebar.slider("Hardness (Ca/Mg mg/L)", 50.0, 400.0, 196.0, 1.0)
solids_val = st.sidebar.slider("Total Dissolved Solids (ppm)", 100.0, 55000.0, 20000.0, 100.0)
chloramines_val = st.sidebar.slider("Chloramines (ppm)", 0.0, 15.0, 7.1, 0.1)
sulfate_val = st.sidebar.slider("Sulfate Minerals (mg/L)", 100.0, 500.0, 333.0, 1.0)
conductivity_val = st.sidebar.slider("Electrical Conductivity (uS/cm)", 100.0, 800.0, 420.0, 5.0)
organic_carbon_val = st.sidebar.slider("Total Organic Carbon (ppm)", 0.0, 30.0, 14.2, 0.1)
trihalomethanes_val = st.sidebar.slider("Trihalomethanes (ug/L)", 0.0, 140.0, 66.0, 1.0)
turbidity_val = st.sidebar.slider("Turbidity (NTU)", 0.0, 8.0, 3.9, 0.1)

# Assemble input DataFrame
input_df = pd.DataFrame([{
    "ph": ph_val,
    "Hardness": hardness_val,
    "Solids": solids_val,
    "Chloramines": chloramines_val,
    "Sulfate": sulfate_val,
    "Conductivity": conductivity_val,
    "Organic_carbon": organic_carbon_val,
    "Trihalomethanes": trihalomethanes_val,
    "Turbidity": turbidity_val,
    "Data_Source": data_source,
    "Station_Type": station_type
}])

# --- MAIN TABS ---
tab1, tab2, tab3 = st.tabs(["Single Sample Triage", "Batch CSV Triage", "System Metrics"])

with tab1:
    if not model_loaded:
        st.error(f"Model pipeline artifact could not be loaded: {load_error}")
    else:
        probs = pipeline.predict_proba(input_df)[0]
        prob_potable = probs[1]
        is_safe = prob_potable >= threshold

        st.subheader("Automated Decision Verdict")
        col1, col2, col3 = st.columns([1.5, 1, 1])

        with col1:
            if is_safe:
                st.success("### POTABLE / SAFE FOR HUMAN CONSUMPTION")
                st.write("Water conforms to safety standards under the selected operating policy.")
            else:
                st.error("### TOXIC / HAZARDOUS CONTAMINATION ALERT")
                st.write("Water fails safety thresholds. High risk of waterborne illness or toxicity.")

        with col2:
            st.metric(
                label="Potability Confidence",
                value=f"{prob_potable*100:.1f}%",
                delta=f"{(prob_potable - threshold)*100:+.1f}% vs Threshold"
            )

        with col3:
            st.metric(
                label="Policy Safety Threshold",
                value=f"{threshold*100:.0f}%",
                help="Required confidence level before declaring potable."
            )

        st.progress(float(prob_potable))

        st.divider()
        st.subheader("Physicochemical Compliance Audit")
        
        audit_rows = []
        for param, (low, high, unit) in SAFE_LIMITS.items():
            val = input_df[param].iloc[0]
            in_range = low <= val <= high
            status = "Safe" if in_range else "Breach"
            guideline = f"{low} - {high} {unit}"
            audit_rows.append({
                "Chemical Parameter": param,
                "Current Reading": f"{val:.2f} {unit}",
                "WHO / EPA Benchmark": guideline,
                "Compliance Status": status
            })

        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True)

with tab2:
    st.subheader("Upload Municipal Telemetry CSV")
    st.write("Upload a CSV containing chemical features to score samples simultaneously.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        batch_df = pd.read_csv(uploaded_file)
        st.write(f"Loaded {len(batch_df)} samples from file.")
        
        if "Data_Source" not in batch_df.columns:
            batch_df["Data_Source"] = "Regional_Network_B"
        if "Station_Type" not in batch_df.columns:
            batch_df["Station_Type"] = "Urban_Treatment"
            
        if st.button("Execute Batch Triage"):
            with st.spinner("Scoring batch samples through pipeline..."):
                batch_probs = pipeline.predict_proba(batch_df)[:, 1]
                batch_df["Potability_Probability"] = batch_probs
                batch_df["Predicted_Verdict"] = np.where(batch_probs >= threshold, "Safe / Potable", "Toxic / Unsafe")
                
                safe_count = (batch_df["Predicted_Verdict"] == "Safe / Potable").sum()
                toxic_count = len(batch_df) - safe_count
                
                col_a, col_b = st.columns(2)
                col_a.metric("Safe Samples", f"{safe_count} ({safe_count/len(batch_df)*100:.1f}%)")
                col_b.metric("Contaminated Flagged", f"{toxic_count} ({toxic_count/len(batch_df)*100:.1f}%)")
                
                st.dataframe(batch_df, use_container_width=True)
                
                csv_data = batch_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "Download Triaged Results (CSV)",
                    csv_data,
                    "triaged_water_results.csv",
                    "text/csv"
                )

with tab3:
    st.subheader("System Architecture & Benchmark Summary")
    st.markdown("""
    * **Champion Algorithm**: Tuned Random Forest (400 trees, min_samples_leaf=4, balanced_subsample weights).
    * **Cross-Validation Performance**: 5-Fold Stratified CV ROC-AUC: **0.7789** | Held-Out Test ROC-AUC: **0.779**.
    * **Zero Data Leakage**: All preprocessing (StandardScaler + OneHotEncoder) strictly fitted on training splits.
    * **Asymmetric Risk Optimization**: Shifting decision threshold from default 0.50 to 0.65 eliminates over 60% of dangerous false-potable events.
    """)
    
    st.table(pd.DataFrame([
        {"Algorithm": "Logistic Regression (Linear Baseline)", "ROC-AUC": "0.618", "Macro F1": "0.562", "Verdict": "Fails on non-linear chemical ranges"},
        {"Algorithm": "XGBoost Classifier", "ROC-AUC": "0.745", "Macro F1": "0.675", "Verdict": "Strong runner-up"},
        {"Algorithm": "Baseline Random Forest", "ROC-AUC": "0.772", "Macro F1": "0.696", "Verdict": "Strong bagging ensemble"},
        {"Algorithm": "Tuned Champion Random Forest", "ROC-AUC": "0.779", "Macro F1": "0.702", "Verdict": "Optimal production champion"}
    ]))
