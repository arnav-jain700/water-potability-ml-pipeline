import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# 1. PAGE SETUP & WATER POTABILITY THEME CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="AquaGuard AI | Municipal Water Potability & Early Warning",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Hydrological Clean-Tech CSS Theme
st.markdown("""
<style>
    /* Global Typography & Background Adjustments */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, #0A2540 0%, #0F3B5F 50%, #0284C7 100%);
        border-radius: 16px;
        padding: 28px 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(2, 132, 199, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #FFFFFF, #67E8F9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #BAE6FD;
        margin-top: 6px;
        font-weight: 400;
    }
    
    /* Triage Decision Cards */
    .card-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.16) 100%);
        border: 1.5px solid #10B981;
        border-radius: 14px;
        padding: 20px 24px;
        color: #065F46;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.1);
    }
    
    .card-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(220, 38, 38, 0.16) 100%);
        border: 1.5px solid #EF4444;
        border-radius: 14px;
        padding: 20px 24px;
        color: #991B1B;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.1);
    }
    
    .metric-chip {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .chip-safe { background: #D1FAE5; color: #065F46; border: 1px solid #10B981; }
    .chip-danger { background: #FEE2E2; color: #991B1B; border: 1px solid #EF4444; }
    
    /* Sidebar Polish */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. CACHED MODEL ARTIFACT LOADER
# ==============================================================================
@st.cache_resource
def load_production_pipeline():
    model_path = os.path.join(os.path.dirname(__file__), "models", "water_potability_pipeline.joblib")
    if not os.path.exists(model_path):
        model_path = "models/water_potability_pipeline.joblib"
    return joblib.load(model_path)

try:
    pipeline = load_production_pipeline()
    model_loaded = True
except Exception as e:
    model_loaded = False
    load_error = str(e)


# ==============================================================================
# 3. WHO & EPA REGULATORY COMPLIANCE BENCHMARKS
# ==============================================================================
REGULATORY_LIMITS = {
    'ph': {'min': 6.5, 'max': 8.5, 'unit': 'pH', 'norm_max': 14.0, 'desc': 'Acid-Base Equilibrium'},
    'Hardness': {'min': 150.0, 'max': 300.0, 'unit': 'mg/L', 'norm_max': 400.0, 'desc': 'Ca / Mg Mineral Content'},
    'Solids': {'min': 0.0, 'max': 1000.0, 'unit': 'ppm', 'norm_max': 35000.0, 'desc': 'Total Dissolved Solids (TDS)'},
    'Chloramines': {'min': 0.0, 'max': 4.0, 'unit': 'ppm', 'norm_max': 12.0, 'desc': 'Disinfection Residuals'},
    'Sulfate': {'min': 0.0, 'max': 250.0, 'unit': 'mg/L', 'norm_max': 500.0, 'desc': 'Dissolved Sulfate Minerals'},
    'Conductivity': {'min': 0.0, 'max': 400.0, 'unit': 'μS/cm', 'norm_max': 800.0, 'desc': 'Electrical Charge Mobility'},
    'Organic_carbon': {'min': 0.0, 'max': 4.0, 'unit': 'ppm', 'norm_max': 25.0, 'desc': 'Total Organic Carbon (TOC)'},
    'Trihalomethanes': {'min': 0.0, 'max': 80.0, 'unit': 'μg/L', 'norm_max': 130.0, 'desc': 'Chlorination Byproducts (THMs)'},
    'Turbidity': {'min': 0.0, 'max': 5.0, 'unit': 'NTU', 'norm_max': 8.0, 'desc': 'Suspended Particulate Clarity'}
}


# ==============================================================================
# 4. TOP HERO BANNER
# ==============================================================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🌊 AquaGuard AI — Water Potability & Triage System</div>
    <div class="hero-subtitle">
        Production-Grade Environmental Telemetry Inference Engine &bull; Cost-Sensitive Public Health Decision Support
    </div>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 5. SIDEBAR: TELEMETRY CONTROLS & POLICY SELECTION
# ==============================================================================
st.sidebar.markdown("### ⚙️ Operational Triage Policy")
policy_choice = st.sidebar.radio(
    "Select Operating Threshold:",
    ["🛡️ Public Safety Policy (τ = 0.65)", "⚖️ Standard Policy (τ = 0.50)"],
    help="Public Safety Policy imposes a 10x penalty on false potables, requiring 65% probability before clearing water for human consumption."
)
policy_threshold = 0.65 if "0.65" in policy_choice else 0.50

st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Station Metadata")
station_type = st.sidebar.selectbox(
    "Monitoring Station Catchment:",
    ["Urban_Treatment", "Agricultural_Runoff", "Industrial_Catchment", "Reservoir_Lake", "River_Basin"]
)
data_source = st.sidebar.selectbox(
    "Telemetry Provenance:",
    ["Regional_Network_B", "Global_Survey_A"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧪 Chemical Sensor Telemetry")
ph_input = st.sidebar.slider("pH Level", 0.0, 14.0, 7.25, 0.05, help="WHO safe range: 6.5 - 8.5")
hardness_input = st.sidebar.slider("Hardness (mg/L)", 50.0, 400.0, 205.0, 1.0)
solids_input = st.sidebar.slider("Total Dissolved Solids (ppm)", 100.0, 50000.0, 18500.0, 250.0)
chloramines_input = st.sidebar.slider("Chloramines (ppm)", 0.0, 15.0, 7.1, 0.1)
sulfate_input = st.sidebar.slider("Sulfate Minerals (mg/L)", 100.0, 500.0, 333.0, 1.0)
conductivity_input = st.sidebar.slider("Conductivity (μS/cm)", 100.0, 800.0, 420.0, 5.0)
organic_carbon_input = st.sidebar.slider("Total Organic Carbon (ppm)", 0.0, 30.0, 13.5, 0.1)
trihalomethanes_input = st.sidebar.slider("Trihalomethanes (μg/L)", 0.0, 140.0, 66.0, 1.0)
turbidity_input = st.sidebar.slider("Turbidity (NTU)", 0.0, 8.0, 3.9, 0.1)

# Assemble DataFrame
current_sample_df = pd.DataFrame([{
    'ph': ph_input,
    'Hardness': hardness_input,
    'Solids': solids_input,
    'Chloramines': chloramines_input,
    'Sulfate': sulfate_input,
    'Conductivity': conductivity_input,
    'Organic_carbon': organic_carbon_input,
    'Trihalomethanes': trihalomethanes_input,
    'Turbidity': turbidity_input,
    'Data_Source': data_source,
    'Station_Type': station_type
}])


# ==============================================================================
# 6. MAIN APPLICATION TABS
# ==============================================================================
tab_single, tab_batch, tab_analytics = st.tabs([
    "🔬 Real-Time Sample Triage",
    "📁 Batch Municipal Surveillance",
    "📊 Model Architecture & XAI"
])


# ------------------------------------------------------------------------------
# TAB 1: REAL-TIME SAMPLE TRIAGE & INTERACTIVE CHARTS
# ------------------------------------------------------------------------------
with tab_single:
    if not model_loaded:
        st.error(f"⚠️ Model pipeline failed to load: {load_error}")
    else:
        # Run inference
        probs = pipeline.predict_proba(current_sample_df)[0]
        prob_potable = probs[1]
        is_potable = prob_potable >= policy_threshold

        # --- ROW 1: TRIAGE BANNER & KEY METRICS ---
        col_banner, col_metric1, col_metric2 = st.columns([2, 1, 1])

        with col_banner:
            if is_potable:
                st.markdown(f"""
                <div class="card-safe">
                    <span class="metric-chip chip-safe">✓ Approved for Distribution</span>
                    <h2 style="margin: 8px 0 4px 0; color: #065F46;">SAFE / POTABLE DRINKING WATER</h2>
                    <p style="margin: 0; font-size: 0.95rem;">
                        Water parameters meet health thresholds under the <b>{policy_choice}</b>.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="card-danger">
                    <span class="metric-chip chip-danger">⚠ Contamination Alert</span>
                    <h2 style="margin: 8px 0 4px 0; color: #991B1B;">HAZARDOUS / NON-POTABLE ALERT</h2>
                    <p style="margin: 0; font-size: 0.95rem;">
                        Sample poses waterborne illness risks. Do not route to public municipal mains.
                    </p>
                </div>
                """, unsafe_allow_html=True)

        with col_metric1:
            st.metric(
                label="Potability Probability",
                value=f"{prob_potable*100:.1f}%",
                delta=f"{(prob_potable - policy_threshold)*100:+.1f}% vs Policy τ"
            )

        with col_metric2:
            st.metric(
                label="Operating Policy Threshold",
                value=f"{policy_threshold*100:.0f}%",
                help="Minimum confidence required to classify water as safe."
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # --- ROW 2: INTERACTIVE PLOTLY VISUALIZATIONS ---
        col_gauge, col_radar = st.columns([1, 1.2])

        with col_gauge:
            st.markdown("#### 🧭 Potability Confidence Gauge")
            
            # Interactive Plotly Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=prob_potable * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                delta={'reference': policy_threshold * 100, 'increasing': {'color': "#10B981"}, 'decreasing': {'color': "#EF4444"}},
                number={'suffix': "%", 'font': {'size': 38, 'color': "#0F172A"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#94A3B8"},
                    'bar': {'color': "#0284C7", 'thickness': 0.28},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#E2E8F0",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.22)'},
                        {'range': [50, policy_threshold * 100], 'color': 'rgba(245, 158, 11, 0.25)'},
                        {'range': [policy_threshold * 100, 100], 'color': 'rgba(16, 185, 129, 0.25)'}
                    ],
                    'threshold': {
                        'line': {'color': "#DC2626", 'width': 4},
                        'thickness': 0.8,
                        'value': policy_threshold * 100
                    }
                }
            ))
            fig_gauge.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=30, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'family': 'Plus Jakarta Sans'}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.caption("Red needle indicates the active policy decision boundary.")

        with col_radar:
            st.markdown("#### 🕸️ Chemical Fingerprint vs. WHO Envelope")
            
            # Normalize parameters to percentage of safe upper bound for radar display
            radar_categories = ['pH', 'Hardness', 'Solids', 'Chloramines', 'Sulfate', 'Conductivity', 'TOC', 'THMs', 'Turbidity']
            param_keys = ['ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate', 'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity']
            
            sample_ratios = []
            who_benchmark = [100.0] * len(radar_categories)
            
            for key in param_keys:
                val = current_sample_df[key].iloc[0]
                safe_max = REGULATORY_LIMITS[key]['max']
                # Ratio: 100% means right at WHO upper limit
                sample_ratios.append(min((val / safe_max) * 100.0, 200.0))
            
            fig_radar = go.Figure()
            
            # WHO Safe Envelope
            fig_radar.add_trace(go.Scatterpolar(
                r=who_benchmark,
                theta=radar_categories,
                fill='toself',
                name='WHO Safe Envelope (100% Cap)',
                line_color='#10B981',
                fillcolor='rgba(16, 185, 129, 0.15)'
            ))
            
            # Current Sample Trace
            sample_color = '#0284C7' if is_potable else '#EF4444'
            sample_fill = 'rgba(2, 132, 199, 0.25)' if is_potable else 'rgba(239, 68, 68, 0.25)'
            
            fig_radar.add_trace(go.Scatterpolar(
                r=sample_ratios,
                theta=radar_categories,
                fill='toself',
                name='Current Water Sample',
                line_color=sample_color,
                fillcolor=sample_fill
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 180], ticksuffix="%")
                ),
                height=300,
                margin=dict(l=30, r=30, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                font={'family': 'Plus Jakarta Sans'}
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption("Spikes breaching outside the green perimeter indicate chemical threshold violations.")

        st.markdown("---")

        # --- ROW 3: COMPREHENSIVE COMPLIANCE AUDIT TABLE ---
        st.markdown("#### 📋 Detailed Physicochemical Regulatory Audit")
        
        audit_records = []
        for key, info in REGULATORY_LIMITS.items():
            val = current_sample_df[key].iloc[0]
            in_bounds = info['min'] <= val <= info['max']
            status_str = "✅ Within Guideline" if in_bounds else "⚠️ Guideline Breach"
            
            audit_records.append({
                "Parameter": info['desc'],
                "Sensor Measurement": f"{val:.2f} {info['unit']}",
                "WHO / EPA Standard": f"{info['min']} - {info['max']} {info['unit']}",
                "Compliance Verdict": status_str
            })
            
        audit_table = pd.DataFrame(audit_records)
        st.dataframe(audit_table, use_container_width=True, hide_index=True)


# ------------------------------------------------------------------------------
# TAB 2: BATCH MUNICIPAL SURVEILLANCE
# ------------------------------------------------------------------------------
with tab_batch:
    st.markdown("### 📁 Batch Telemetry Ingestion & Scoring Engine")
    st.write("Upload municipal sensor streams (CSV format) to score hundreds of regional water bodies simultaneously.")
    
    uploaded_batch = st.file_uploader("Upload Telemetry Batch CSV", type=["csv"])
    
    # Provide sample download button if no file is uploaded yet
    sample_download_df = pd.DataFrame([
        {'ph': 7.1, 'Hardness': 210, 'Solids': 18000, 'Chloramines': 6.5, 'Sulfate': 320, 'Conductivity': 410, 'Organic_carbon': 11.2, 'Trihalomethanes': 62, 'Turbidity': 3.4, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Urban_Treatment'},
        {'ph': 4.3, 'Hardness': 120, 'Solids': 45000, 'Chloramines': 11.0, 'Sulfate': 480, 'Conductivity': 650, 'Organic_carbon': 23.0, 'Trihalomethanes': 110, 'Turbidity': 6.5, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Industrial_Catchment'},
        {'ph': 8.2, 'Hardness': 180, 'Solids': 16000, 'Chloramines': 7.2, 'Sulfate': 290, 'Conductivity': 390, 'Organic_carbon': 9.8, 'Trihalomethanes': 54, 'Turbidity': 2.9, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Reservoir_Lake'}
    ])
    
    st.download_button(
        "📄 Download Sample Batch Template (CSV)",
        sample_download_df.to_csv(index=False).encode('utf-8'),
        "sample_water_telemetry_batch.csv",
        "text/csv"
    )
    
    if uploaded_batch is not None:
        batch_input_df = pd.read_csv(uploaded_batch)
        st.success(f"✓ Successfully ingested {len(batch_input_df)} observations from file.")
        
        # Ensure metadata columns exist
        if 'Data_Source' not in batch_input_df.columns:
            batch_input_df['Data_Source'] = 'Regional_Network_B'
        if 'Station_Type' not in batch_input_df.columns:
            batch_input_df['Station_Type'] = 'Urban_Treatment'
            
        if st.button("🚀 Execute Batch Triage Pipeline"):
            with st.spinner("Executing inference across production pipeline..."):
                batch_probabilities = pipeline.predict_proba(batch_input_df)[:, 1]
                batch_input_df['Potability_Probability'] = batch_probabilities
                batch_input_df['Triage_Decision'] = np.where(batch_probabilities >= policy_threshold, 'Potable / Safe', 'Toxic / Unsafe')
                
                safe_n = (batch_input_df['Triage_Decision'] == 'Potable / Safe').sum()
                toxic_n = len(batch_input_df) - safe_n
                
                # Metric Summary Chips
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Batch Volume", f"{len(batch_input_df)} samples")
                m2.metric("Safe Water Streams", f"{safe_n} ({safe_n/len(batch_input_df)*100:.1f}%)")
                m3.metric("Contamination Flags", f"{toxic_n} ({toxic_n/len(batch_input_df)*100:.1f}%)")
                
                # Interactive Batch Charts
                c_pie, c_scatter = st.columns([1, 1.5])
                
                with c_pie:
                    fig_donut = px.pie(
                        values=[safe_n, toxic_n],
                        names=['Safe / Potable', 'Toxic / Unsafe'],
                        color=['Safe / Potable', 'Toxic / Unsafe'],
                        color_discrete_map={'Safe / Potable': '#10B981', 'Toxic / Unsafe': '#EF4444'},
                        hole=0.55,
                        title="Cohort Safety Distribution"
                    )
                    fig_donut.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig_donut, use_container_width=True)
                    
                with c_scatter:
                    fig_scat = px.scatter(
                        batch_input_df,
                        x='ph',
                        y='Sulfate',
                        color='Triage_Decision',
                        color_discrete_map={'Potable / Safe': '#10B981', 'Toxic / Unsafe': '#EF4444'},
                        hover_data=['Solids', 'Chloramines', 'Potability_Probability'],
                        title="Batch Distribution: pH vs. Sulfate"
                    )
                    fig_scat.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10))
                    st.plotly_chart(fig_scat, use_container_width=True)
                
                st.dataframe(batch_input_df, use_container_width=True)
                
                # Export Button
                scored_csv = batch_input_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Export Scored Telemetry CSV",
                    scored_csv,
                    "aquaguard_triaged_output.csv",
                    "text/csv"
                )


# ------------------------------------------------------------------------------
# TAB 3: SYSTEM ARCHITECTURE & EXPLAINABLE AI
# ------------------------------------------------------------------------------
with tab_analytics:
    st.markdown("### 🏗️ Production System Architecture")
    
    col_arch1, col_arch2 = st.columns(2)
    
    with col_arch1:
        st.markdown("""
        #### 📦 End-to-End Pipeline Composition
        * **1. Ingestion Layer**: Multi-source harmonization ($7,776$ records) combining historical surveys and live sensor networks.
        * **2. Cleaning & Imputation**: Outlier Winsorization via Tukey's IQR Fences and 5-Nearest Neighbors (`KNNImputer`) preserving multivariate KDE distributions.
        * **3. Feature Engine**: Strict zero-leakage `ColumnTransformer` (StandardScaler on continuous chemistry + OneHotEncoder on metadata).
        * **4. Model Architecture**: Tuned Random Forest Classifier ($400$ estimators, `min_samples_leaf=4`, `class_weight='balanced_subsample'`).
        """)
        
    with col_arch2:
        st.markdown("""
        #### ⚖️ Asymmetric Cost-Sensitive Optimization
        * **The Flaw of Accuracy**: Standard $0.50$ thresholds treat a catastrophic poisoning equally with a $15 laboratory re-test.
        * **Cost Matrix**: Penalizes False Negatives (Type II) by $10\times$ relative to False Positives (Type I).
        * **Optimal Operating Point**: $\tau^* = 0.65$ eliminates over $60\%$ of hazardous false-potable events on held-out test data.
        """)

    st.markdown("---")
    st.markdown("#### 🏆 Cross-Validation Benchmark Comparison")
    
    benchmark_data = pd.DataFrame([
        {'Algorithm': 'Logistic Regression (Linear Baseline)', '5-Fold CV ROC-AUC': '0.618', 'Macro F1': '0.562', 'Architectural Limitation': 'Linear hyperplane cannot isolate bounded chemical ranges (e.g. 6.5 <= pH <= 8.5)'},
        {'Algorithm': 'XGBoost Classifier', '5-Fold CV ROC-AUC': '0.745', 'Macro F1': '0.675', 'Architectural Limitation': 'Gradient boosting slightly sensitive to local sensor noise'},
        {'Algorithm': 'Baseline Random Forest', '5-Fold CV ROC-AUC': '0.772', 'Macro F1': '0.696', 'Architectural Limitation': 'Un-regularized leaf depths allowed slight variance'},
        {'Algorithm': 'Tuned Random Forest (Champion) 🏆', '5-Fold CV ROC-AUC': '0.779', 'Macro F1': '0.702', 'Architectural Limitation': 'Optimal bagging ensemble regularized against noise'}
    ])
    st.dataframe(benchmark_data, use_container_width=True, hide_index=True)
