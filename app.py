import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import plotly.express as px

# ==============================================================================
# 1. PAGE SETUP
# ==============================================================================
st.set_page_config(
    page_title="AquaGuard ML | Water Potability Triage",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-contrast, clean card styling (explicit text and background colors)
st.markdown("""
<style>
    .safe-banner {
        background-color: #ECFDF5 !important;
        border: 2px solid #10B981 !important;
        border-radius: 12px;
        padding: 20px 24px;
        color: #065F46 !important;
        margin-bottom: 20px;
    }
    .safe-banner h2 {
        color: #065F46 !important;
        margin-top: 0;
        margin-bottom: 8px;
    }
    .safe-banner p {
        color: #047857 !important;
        margin-bottom: 0;
    }

    .danger-banner {
        background-color: #FEF2F2 !important;
        border: 2px solid #EF4444 !important;
        border-radius: 12px;
        padding: 20px 24px;
        color: #991B1B !important;
        margin-bottom: 20px;
    }
    .danger-banner h2 {
        color: #991B1B !important;
        margin-top: 0;
        margin-bottom: 8px;
    }
    .danger-banner p {
        color: #B91C1C !important;
        margin-bottom: 0;
    }

    .metric-container {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# 2. CACHED MODEL LOADER
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
# 3. WHO / EPA REGULATORY SAFE BENCHMARKS
# ==============================================================================
REGULATORY_LIMITS = {
    'ph': {'min': 6.5, 'max': 8.5, 'unit': 'pH', 'desc': 'Acid-Base Equilibrium'},
    'Hardness': {'min': 150.0, 'max': 300.0, 'unit': 'mg/L', 'desc': 'Calcium & Magnesium Content'},
    'Solids': {'min': 0.0, 'max': 1000.0, 'unit': 'ppm', 'desc': 'Total Dissolved Solids (TDS)'},
    'Chloramines': {'min': 0.0, 'max': 4.0, 'unit': 'ppm', 'desc': 'Disinfection Residuals'},
    'Sulfate': {'min': 0.0, 'max': 250.0, 'unit': 'mg/L', 'desc': 'Dissolved Sulfate Minerals'},
    'Conductivity': {'min': 0.0, 'max': 400.0, 'unit': 'μS/cm', 'desc': 'Electrical Conductivity'},
    'Organic_carbon': {'min': 0.0, 'max': 4.0, 'unit': 'ppm', 'desc': 'Total Organic Carbon (TOC)'},
    'Trihalomethanes': {'min': 0.0, 'max': 80.0, 'unit': 'μg/L', 'desc': 'Chlorination Byproducts (THMs)'},
    'Turbidity': {'min': 0.0, 'max': 5.0, 'unit': 'NTU', 'desc': 'Particulate Clarity'}
}


# ==============================================================================
# 4. HEADER SECTION
# ==============================================================================
st.title("🌊 AquaGuard ML: Municipal Water Potability Triage")
st.markdown("**Production Environmental Telemetry Engine** &bull; CSD 302 Capstone Project &bull; Developer: Arnav Jain")
st.divider()


# ==============================================================================
# 5. SIDEBAR CONTROLS
# ==============================================================================
st.sidebar.header("⚙️ Triage Policy")
policy_choice = st.sidebar.radio(
    "Decision Policy:",
    ["Public Health Safety (Threshold = 0.65)", "Standard Commercial (Threshold = 0.50)"],
    help="Public safety policy requires 65% confidence before clearing water for human consumption, minimizing dangerous false potables."
)
policy_threshold = 0.65 if "0.65" in policy_choice else 0.50

st.sidebar.divider()
st.sidebar.header("📍 Station Catchment")
station_type = st.sidebar.selectbox(
    "Monitoring Station Type:",
    ["Urban_Treatment", "Agricultural_Runoff", "Industrial_Catchment", "Reservoir_Lake", "River_Basin"]
)
data_source = st.sidebar.selectbox(
    "Data Stream Provenance:",
    ["Regional_Network_B", "Global_Survey_A"]
)

st.sidebar.divider()
st.sidebar.header("🧪 Sensor Measurements")
ph_input = st.sidebar.slider("pH Level", 0.0, 14.0, 7.25, 0.05)
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
# 6. APPLICATION TABS
# ==============================================================================
tab_single, tab_batch, tab_analytics = st.tabs([
    "🔬 Real-Time Sample Triage",
    "📁 Batch Telemetry Analysis",
    "📊 System Metrics & Architecture"
])


# ------------------------------------------------------------------------------
# TAB 1: REAL-TIME SAMPLE TRIAGE & INTERACTIVE CHARTS
# ------------------------------------------------------------------------------
with tab_single:
    if not model_loaded:
        st.error(f"Model pipeline failed to load: {load_error}")
    else:
        # Run inference
        probs = pipeline.predict_proba(current_sample_df)[0]
        prob_potable = probs[1]
        is_potable = prob_potable >= policy_threshold

        # --- ROW 1: STATUS BANNER & METRICS ---
        col_banner, col_m1, col_m2 = st.columns([2, 1, 1])

        with col_banner:
            if is_potable:
                st.markdown("""
                <div class="safe-banner">
                    <h2>✅ POTABLE / SAFE DRINKING WATER</h2>
                    <p>Water parameters conform to safety thresholds under the selected operating policy.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="danger-banner">
                    <h2>⚠️ HAZARDOUS / CONTAMINATION ALERT</h2>
                    <p>Sample exceeds safe risk thresholds. Do not release into municipal drinking supply.</p>
                </div>
                """, unsafe_allow_html=True)

        with col_m1:
            st.metric(
                label="Potability Probability",
                value=f"{prob_potable*100:.1f}%",
                delta=f"{(prob_potable - policy_threshold)*100:+.1f}% vs Policy Threshold"
            )

        with col_m2:
            st.metric(
                label="Operating Policy Threshold",
                value=f"{policy_threshold*100:.0f}%",
                help="Minimum confidence required to classify water as safe."
            )

        # --- ROW 2: INTERACTIVE PLOTLY VISUALIZATIONS ---
        col_gauge, col_radar = st.columns([1, 1.2])

        with col_gauge:
            st.subheader("🧭 Potability Confidence Gauge")
            
            # Interactive Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=prob_potable * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                delta={'reference': policy_threshold * 100, 'increasing': {'color': "#059669"}, 'decreasing': {'color': "#DC2626"}},
                number={'suffix': "%", 'font': {'size': 36, 'color': "#0F172A"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                    'bar': {'color': "#0284C7", 'thickness': 0.28},
                    'bgcolor': "#FFFFFF",
                    'borderwidth': 1.5,
                    'bordercolor': "#CBD5E1",
                    'steps': [
                        {'range': [0, 50], 'color': '#FEE2E2'},
                        {'range': [50, policy_threshold * 100], 'color': '#FEF3C7'},
                        {'range': [policy_threshold * 100, 100], 'color': '#D1FAE5'}
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
                margin=dict(l=20, r=20, t=30, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                font={'color': '#0F172A'}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.caption("Red needle indicates the active policy decision threshold.")

        with col_radar:
            st.subheader("🕸️ Chemical Fingerprint vs. WHO Envelope")
            
            radar_categories = ['pH', 'Hardness', 'Solids', 'Chloramines', 'Sulfate', 'Conductivity', 'TOC', 'THMs', 'Turbidity']
            param_keys = ['ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate', 'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity']
            
            sample_ratios = []
            who_benchmark = [100.0] * len(radar_categories)
            
            for key in param_keys:
                val = current_sample_df[key].iloc[0]
                safe_max = REGULATORY_LIMITS[key]['max']
                sample_ratios.append(min((val / safe_max) * 100.0, 200.0))
            
            fig_radar = go.Figure()
            
            # WHO Safe Envelope
            fig_radar.add_trace(go.Scatterpolar(
                r=who_benchmark,
                theta=radar_categories,
                fill='toself',
                name='WHO Safe Envelope (100% Limit)',
                line_color='#059669',
                fillcolor='rgba(16, 185, 129, 0.20)'
            ))
            
            # Current Sample Trace
            sample_line_color = '#0284C7' if is_potable else '#DC2626'
            sample_fill_color = 'rgba(2, 132, 199, 0.25)' if is_potable else 'rgba(220, 38, 38, 0.25)'
            
            fig_radar.add_trace(go.Scatterpolar(
                r=sample_ratios,
                theta=radar_categories,
                fill='toself',
                name='Current Water Sample',
                line_color=sample_line_color,
                fillcolor=sample_fill_color
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 180], ticksuffix="%", color="#475569")
                ),
                height=300,
                margin=dict(l=30, r=30, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                font={'color': '#0F172A'}
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.caption("Points breaching outside the green perimeter violate WHO safety limits.")

        st.divider()

        # --- ROW 3: COMPLIANCE AUDIT TABLE ---
        st.subheader("📋 Physicochemical Regulatory Audit")
        
        audit_records = []
        for key, info in REGULATORY_LIMITS.items():
            val = current_sample_df[key].iloc[0]
            in_bounds = info['min'] <= val <= info['max']
            status_str = "✅ Within Guideline" if in_bounds else "⚠️ Guideline Breach"
            
            audit_records.append({
                "Parameter": info['desc'],
                "Sensor Measurement": f"{val:.2f} {info['unit']}",
                "WHO / EPA Guideline": f"{info['min']} - {info['max']} {info['unit']}",
                "Compliance Status": status_str
            })
            
        st.dataframe(pd.DataFrame(audit_records), use_container_width=True, hide_index=True)


# ------------------------------------------------------------------------------
# TAB 2: BATCH TELEMETRY INGESTION & SCORING
# ------------------------------------------------------------------------------
with tab_batch:
    st.subheader("📁 Batch Ingestion Engine")
    st.write("Upload municipal sensor telemetry CSV files to score hundreds of water sources simultaneously.")
    
    uploaded_batch = st.file_uploader("Upload CSV File", type=["csv"])
    
    # Template download
    sample_download_df = pd.DataFrame([
        {'ph': 7.1, 'Hardness': 210, 'Solids': 18000, 'Chloramines': 6.5, 'Sulfate': 320, 'Conductivity': 410, 'Organic_carbon': 11.2, 'Trihalomethanes': 62, 'Turbidity': 3.4, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Urban_Treatment'},
        {'ph': 4.3, 'Hardness': 120, 'Solids': 45000, 'Chloramines': 11.0, 'Sulfate': 480, 'Conductivity': 650, 'Organic_carbon': 23.0, 'Trihalomethanes': 110, 'Turbidity': 6.5, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Industrial_Catchment'},
        {'ph': 8.2, 'Hardness': 180, 'Solids': 16000, 'Chloramines': 7.2, 'Sulfate': 290, 'Conductivity': 390, 'Organic_carbon': 9.8, 'Trihalomethanes': 54, 'Turbidity': 2.9, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Reservoir_Lake'}
    ])
    
    st.download_button(
        "📄 Download Batch CSV Template",
        sample_download_df.to_csv(index=False).encode('utf-8'),
        "water_telemetry_batch_template.csv",
        "text/csv"
    )
    
    if uploaded_batch is not None:
        batch_df = pd.read_csv(uploaded_batch)
        st.success(f"✓ Loaded {len(batch_df)} samples from file.")
        
        if 'Data_Source' not in batch_df.columns:
            batch_df['Data_Source'] = 'Regional_Network_B'
        if 'Station_Type' not in batch_df.columns:
            batch_df['Station_Type'] = 'Urban_Treatment'
            
        if st.button("🚀 Score Entire Batch"):
            with st.spinner("Scoring batch through ML pipeline..."):
                probs_batch = pipeline.predict_proba(batch_df)[:, 1]
                batch_df['Potability_Probability'] = probs_batch
                batch_df['Triage_Verdict'] = np.where(probs_batch >= policy_threshold, 'Potable / Safe', 'Toxic / Unsafe')
                
                safe_n = (batch_df['Triage_Verdict'] == 'Potable / Safe').sum()
                toxic_n = len(batch_df) - safe_n
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Batch Volume", f"{len(batch_df)} samples")
                m2.metric("Potable Sources", f"{safe_n} ({safe_n/len(batch_df)*100:.1f}%)")
                m3.metric("Contaminated Sources", f"{toxic_n} ({toxic_n/len(batch_df)*100:.1f}%)")
                
                c1, c2 = st.columns([1, 1.5])
                with c1:
                    fig_pie = px.pie(
                        values=[safe_n, toxic_n],
                        names=['Potable / Safe', 'Toxic / Unsafe'],
                        color=['Potable / Safe', 'Toxic / Unsafe'],
                        color_discrete_map={'Potable / Safe': '#10B981', 'Toxic / Unsafe': '#EF4444'},
                        hole=0.50,
                        title="Cohort Safety Ratio"
                    )
                    fig_pie.update_layout(height=280, margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with c2:
                    fig_sc = px.scatter(
                        batch_df,
                        x='ph',
                        y='Sulfate',
                        color='Triage_Verdict',
                        color_discrete_map={'Potable / Safe': '#10B981', 'Toxic / Unsafe': '#EF4444'},
                        hover_data=['Solids', 'Chloramines', 'Potability_Probability'],
                        title="Distribution: pH vs. Sulfate"
                    )
                    fig_sc.update_layout(height=280, margin=dict(l=10, r=10, t=35, b=10))
                    st.plotly_chart(fig_sc, use_container_width=True)
                
                st.dataframe(batch_df, use_container_width=True)
                
                st.download_button(
                    "📥 Download Scored Results (CSV)",
                    batch_df.to_csv(index=False).encode('utf-8'),
                    "triaged_batch_output.csv",
                    "text/csv"
                )


# ------------------------------------------------------------------------------
# TAB 3: SYSTEM METRICS & ARCHITECTURE
# ------------------------------------------------------------------------------
with tab_analytics:
    st.subheader("🏗️ Pipeline Architecture & Validation")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        **Pipeline Design**:
        * **Ingestion**: Multi-source data pipeline ($7,776$ records).
        * **Cleaning**: Tukey's IQR fences with non-negative Winsorization clipping.
        * **Imputation**: 5-Nearest Neighbors (`KNNImputer`) preserving multivariate KDE distributions.
        * **Preprocessing**: Strict `ColumnTransformer` (StandardScaler on 9 numeric + OneHotEncoder on metadata).
        * **Model**: Tuned Random Forest ($400$ estimators, `min_samples_leaf=4`, `class_weight='balanced_subsample'`).
        """)
    with col_b:
        st.markdown("""
        **Asymmetric Cost Matrix**:
        * **Public Health Priority**: Cost of False Negative (distributing contaminated water) is $10\times$ higher than a secondary lab re-test.
        * **Optimal Operating Point**: $\tau^* = 0.65$ eliminates $>60%$ of dangerous false-potable poisonings.
        * **Held-Out Test Score**: ROC-AUC **0.779** on $1,556$ unseen samples (zero overfitting).
        """)

    st.divider()
    st.subheader("Cross-Validation Leaderboard")
    
    bench_table = pd.DataFrame([
        {'Algorithm': 'Logistic Regression (Linear Baseline)', '5-Fold CV ROC-AUC': '0.618', 'Macro F1': '0.562', 'Limitation': 'Linear boundary cannot separate bounded safe intervals (6.5 <= pH <= 8.5)'},
        {'Algorithm': 'XGBoost Classifier', '5-Fold CV ROC-AUC': '0.745', 'Macro F1': '0.675', 'Limitation': 'Boosting slightly sensitive to noisy field telemetry'},
        {'Algorithm': 'Baseline Random Forest', '5-Fold CV ROC-AUC': '0.772', 'Macro F1': '0.696', 'Limitation': 'Unconstrained leaf depth allowed minor variance'},
        {'Algorithm': 'Tuned Champion Random Forest 🏆', '5-Fold CV ROC-AUC': '0.779', 'Macro F1': '0.702', 'Limitation': 'Production Champion: 400 trees with leaf regularization'}
    ])
    st.dataframe(bench_table, use_container_width=True, hide_index=True)
