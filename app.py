import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
import plotly.express as px
import streamlit.components.v1 as components

# ==============================================================================
# 1. PAGE SETUP & CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="AquaGuard ML | Water Potability Triage",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. REACTBITS-INSPIRED DESIGN SYSTEM & MODERN CSS
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Typography & Palette */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #F8FAFC;
    }
    
    code, pre, .mono-val {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Aurora Fluid Hero Container */
    .aurora-hero {
        position: relative;
        background: radial-gradient(circle at 12% 18%, rgba(0, 229, 190, 0.18) 0%, transparent 45%),
                    radial-gradient(circle at 88% 82%, rgba(59, 130, 246, 0.18) 0%, transparent 45%),
                    radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.10) 0%, transparent 55%),
                    rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 20px;
        padding: 26px 30px;
        margin-bottom: 24px;
        overflow: hidden;
        box-shadow: 0 20px 45px -15px rgba(0, 0, 0, 0.6);
    }
    
    .hero-top-bar {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }

    /* ReactBits Live Telemetry Pulsing Pill */
    .live-status-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(0, 229, 190, 0.10);
        border: 1px solid rgba(0, 229, 190, 0.35);
        border-radius: 9999px;
        padding: 5px 14px;
        font-size: 0.76rem;
        font-weight: 700;
        color: #00E5BE;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    .pulse-radar-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #00E5BE;
        margin-right: 9px;
        box-shadow: 0 0 0 0 rgba(0, 229, 190, 0.7);
        animation: pulse-ring 2.2s infinite cubic-bezier(0.66, 0, 0, 1);
    }

    @keyframes pulse-ring {
        0% { box-shadow: 0 0 0 0 rgba(0, 229, 190, 0.7); }
        70% { box-shadow: 0 0 0 9px rgba(0, 229, 190, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 229, 190, 0); }
    }

    .hero-chips-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .spec-chip {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 9999px;
        padding: 4px 12px;
        font-size: 0.75rem;
        font-weight: 500;
        color: #94A3B8;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ReactBits Shiny Text Shimmer */
    .shiny-title {
        background: linear-gradient(110deg, #FFFFFF 15%, #00E5BE 40%, #60A5FA 65%, #FFFFFF 85%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textShine 6s linear infinite;
        font-weight: 800;
        font-size: 2.3rem;
        letter-spacing: -0.025em;
        margin: 0;
        line-height: 1.2;
    }

    @keyframes textShine {
        to {
            background-position: 200% center;
        }
    }

    .hero-subtitle {
        color: #94A3B8;
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 6px;
        margin-bottom: 0;
    }

    /* ReactBits Spotlight Glassmorphic Verdict Cards */
    .verdict-card-safe {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.14) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1.5px solid rgba(16, 185, 129, 0.45);
        box-shadow: 0 12px 35px -10px rgba(16, 185, 129, 0.25);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
    }
    
    .verdict-card-danger {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(15, 23, 42, 0.85) 100%);
        border: 1.5px solid rgba(239, 68, 68, 0.45);
        box-shadow: 0 12px 35px -10px rgba(239, 68, 68, 0.25);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        position: relative;
    }

    .verdict-header-badge-safe {
        display: inline-flex;
        align-items: center;
        background: rgba(16, 185, 129, 0.22);
        color: #34D399;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 5px 12px;
        border-radius: 6px;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        border: 1px solid rgba(16, 185, 129, 0.35);
        font-family: 'JetBrains Mono', monospace;
    }

    .verdict-header-badge-danger {
        display: inline-flex;
        align-items: center;
        background: rgba(239, 68, 68, 0.22);
        color: #F87171;
        font-weight: 700;
        font-size: 0.78rem;
        padding: 5px 12px;
        border-radius: 6px;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        border: 1px solid rgba(239, 68, 68, 0.35);
        font-family: 'JetBrains Mono', monospace;
    }

    .verdict-title {
        font-size: 1.55rem;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 6px;
        color: #FFFFFF;
        letter-spacing: -0.015em;
    }

    .verdict-desc {
        font-size: 0.94rem;
        color: #CBD5E1;
        line-height: 1.55;
        margin-bottom: 18px;
    }

    /* KPI Row inside Verdict Card */
    .kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        padding-top: 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    .kpi-box {
        background: rgba(8, 13, 26, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 10px 12px;
    }

    .kpi-box-label {
        font-size: 0.70rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94A3B8;
        margin-bottom: 4px;
    }

    .kpi-box-val {
        font-size: 1.15rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        color: #FFFFFF;
    }

    /* Culprit Diagnostic Cards */
    .spotlight-culprit-card {
        background: rgba(15, 23, 42, 0.85);
        border-left: 4px solid #EF4444;
        border-top: 1px solid rgba(239, 68, 68, 0.22);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .spotlight-culprit-card:hover {
        transform: translateY(-2px);
        border-top-color: rgba(239, 68, 68, 0.45);
    }

    .safe-profile-badge-card {
        background: rgba(16, 185, 129, 0.10);
        border: 1.5px solid rgba(16, 185, 129, 0.35);
        border-radius: 12px;
        padding: 16px 20px;
        color: #86EFAC;
        font-size: 0.92rem;
        margin-bottom: 18px;
    }

    /* Chart Card Enclosure */
    .glass-chart-container {
        background: rgba(15, 23, 42, 0.70);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 22px 16px 22px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    }

    .chart-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        padding-bottom: 10px;
    }

    .chart-card-title {
        font-size: 1.02rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .chart-card-pill {
        font-size: 0.72rem;
        font-weight: 600;
        color: #00E5BE;
        background: rgba(0, 229, 190, 0.10);
        border: 1px solid rgba(0, 229, 190, 0.25);
        border-radius: 6px;
        padding: 3px 8px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ReactBits Segmented Tab Bar */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        padding: 6px 8px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 22px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #94A3B8 !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #F8FAFC !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(0, 229, 190, 0.12) !important;
        color: #00E5BE !important;
        border: 1px solid rgba(0, 229, 190, 0.35) !important;
        box-shadow: 0 4px 14px -2px rgba(0, 229, 190, 0.25);
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Clean, High-Contrast Slider Formatting (Fixing tooltip readability) */
    div[data-testid="stSlider"] label {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }
    div[data-testid="stSlider"] [data-testid="stThumbValue"] {
        color: #FFFFFF !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700 !important;
    }
    div[data-testid="stSlider"] [data-baseweb="slider"] {
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }

    /* Custom Streamlit Buttons */
    div[data-testid="stButton"] > button {
        background: rgba(15, 23, 42, 0.80);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #F8FAFC;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.25s ease;
    }
    div[data-testid="stButton"] > button:hover {
        border-color: #00E5BE;
        color: #00E5BE;
        box-shadow: 0 0 12px rgba(0, 229, 190, 0.25);
        transform: translateY(-1px);
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
# 3. WHO / EPA REGULATORY BENCHMARKS
# ==============================================================================
REGULATORY_LIMITS = {
    'ph': {'min': 6.5, 'max': 8.5, 'unit': 'pH', 'desc': 'Acid-Base Equilibrium', 'icon': '🧪'},
    'Hardness': {'min': 150.0, 'max': 300.0, 'unit': 'mg/L', 'desc': 'Calcium & Magnesium Hardness', 'icon': '🪨'},
    'Solids': {'min': 0.0, 'max': 1000.0, 'unit': 'ppm', 'desc': 'Total Dissolved Solids (TDS)', 'icon': '🧂'},
    'Chloramines': {'min': 0.0, 'max': 4.0, 'unit': 'ppm', 'desc': 'Disinfection Chloramines', 'icon': '🫧'},
    'Sulfate': {'min': 0.0, 'max': 250.0, 'unit': 'mg/L', 'desc': 'Dissolved Sulfate Minerals', 'icon': '🌋'},
    'Conductivity': {'min': 0.0, 'max': 400.0, 'unit': 'μS/cm', 'desc': 'Electrical Conductivity', 'icon': '⚡'},
    'Organic_carbon': {'min': 0.0, 'max': 4.0, 'unit': 'ppm', 'desc': 'Total Organic Carbon (TOC)', 'icon': '🌿'},
    'Trihalomethanes': {'min': 0.0, 'max': 80.0, 'unit': 'μg/L', 'desc': 'Trihalomethanes (THMs)', 'icon': '☣️'},
    'Turbidity': {'min': 0.0, 'max': 5.0, 'unit': 'NTU', 'desc': 'Particulate Turbidity', 'icon': '🌫️'}
}


# ==============================================================================
# 4. PRESET SCENARIO HANDLER
# ==============================================================================
PRESETS = {
    "Pristine Tap (Safe)": {
        'ph': 7.35, 'Hardness': 195.0, 'Solids': 16500.0, 'Chloramines': 6.8,
        'Sulfate': 315.0, 'Conductivity': 390.0, 'Organic_carbon': 11.0,
        'Trihalomethanes': 58.0, 'Turbidity': 3.1, 'Station_Type': 'Urban_Treatment'
    },
    "Industrial Spill (Hazardous)": {
        'ph': 3.90, 'Hardness': 110.0, 'Solids': 46000.0, 'Chloramines': 12.5,
        'Sulfate': 490.0, 'Conductivity': 720.0, 'Organic_carbon': 25.5,
        'Trihalomethanes': 118.0, 'Turbidity': 6.8, 'Station_Type': 'Industrial_Catchment'
    },
    "Borderline Infiltration (Edge Case)": {
        'ph': 6.30, 'Hardness': 145.0, 'Solids': 24000.0, 'Chloramines': 8.2,
        'Sulfate': 365.0, 'Conductivity': 460.0, 'Organic_carbon': 16.5,
        'Trihalomethanes': 78.0, 'Turbidity': 4.8, 'Station_Type': 'Agricultural_Runoff'
    }
}

# Initialize session state for inputs if not present
for param in ['ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate', 'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity']:
    if param not in st.session_state:
        st.session_state[param] = PRESETS["Pristine Tap (Safe)"][param]

if 'Station_Type' not in st.session_state:
    st.session_state['Station_Type'] = 'Urban_Treatment'

def apply_preset(preset_name):
    cfg = PRESETS[preset_name]
    for key, val in cfg.items():
        st.session_state[key] = val


# ==============================================================================
# 5. AURORA HERO BANNER (REACTBITS SHINY TEXT & PULSING TELEMETRY)
# ==============================================================================
st.markdown("""
<div class="aurora-hero">
    <div class="hero-top-bar">
        <div class="live-status-pill">
            <span class="pulse-radar-dot"></span>
            <span>TELEMETRY STREAM ACTIVE &bull; MODEL v2.4</span>
        </div>
        <div class="hero-chips-container">
            <span class="spec-chip">🌲 Tuned Random Forest (400 Trees)</span>
            <span class="spec-chip">🎯 Cost-Sensitive τ* = 0.65</span>
            <span class="spec-chip">⚡ 9 Telemetry Sensors</span>
        </div>
    </div>
    <h1 class="shiny-title">AquaGuard ML</h1>
    <p class="hero-subtitle">Production Environmental Telemetry Engine & Early-Warning Water Potability Classifier &bull; CSD 302 Capstone</p>
</div>
""", unsafe_allow_html=True)


# ==============================================================================
# 6. SIDEBAR: OPERATING POLICIES & SENSOR TELEMETRY CONTROLS
# ==============================================================================
st.sidebar.markdown("### ⚙️ Operating Decision Policy")
policy_choice = st.sidebar.radio(
    "Decision Policy:",
    ["Public Health Safety (Threshold = 0.65)", "Standard Commercial (Threshold = 0.50)"],
    help="Public safety policy requires 65% confidence before clearing water for human consumption, minimizing dangerous false potables."
)
policy_threshold = 0.65 if "0.65" in policy_choice else 0.50

st.sidebar.divider()
st.sidebar.markdown("### 📍 Catchment Environment")
station_type = st.sidebar.selectbox(
    "Monitoring Station Type:",
    ["Urban_Treatment", "Agricultural_Runoff", "Industrial_Catchment", "Reservoir_Lake", "River_Basin"],
    index=["Urban_Treatment", "Agricultural_Runoff", "Industrial_Catchment", "Reservoir_Lake", "River_Basin"].index(st.session_state['Station_Type'])
)
data_source = st.sidebar.selectbox(
    "Data Stream Provenance:",
    ["Regional_Network_B", "Global_Survey_A"]
)

st.sidebar.divider()
st.sidebar.markdown("### 🧪 Sensor Telemetry Controls")

st.sidebar.markdown("#### 🧪 Physicochemical Baseline")
ph_input = st.sidebar.slider("pH Level", 0.0, 14.0, float(st.session_state['ph']), 0.05, format="%.2f")
hardness_input = st.sidebar.slider("Hardness (mg/L)", 50.0, 400.0, float(st.session_state['Hardness']), 1.0, format="%.0f mg/L")
conductivity_input = st.sidebar.slider("Conductivity (μS/cm)", 100.0, 800.0, float(st.session_state['Conductivity']), 5.0, format="%.0f μS/cm")
turbidity_input = st.sidebar.slider("Turbidity (NTU)", 0.0, 8.0, float(st.session_state['Turbidity']), 0.1, format="%.1f NTU")

st.sidebar.markdown("#### 🧂 Minerals & Dissolved Solids")
solids_input = st.sidebar.slider("Total Dissolved Solids (ppm)", 100.0, 50000.0, float(st.session_state['Solids']), 250.0, format="%.0f ppm")
sulfate_input = st.sidebar.slider("Sulfate Minerals (mg/L)", 100.0, 500.0, float(st.session_state['Sulfate']), 1.0, format="%.0f mg/L")

st.sidebar.markdown("#### ☣️ Disinfectants & Organics")
chloramines_input = st.sidebar.slider("Chloramines (ppm)", 0.0, 15.0, float(st.session_state['Chloramines']), 0.1, format="%.1f ppm")
organic_carbon_input = st.sidebar.slider("Total Organic Carbon (ppm)", 0.0, 30.0, float(st.session_state['Organic_carbon']), 0.1, format="%.1f ppm")
trihalomethanes_input = st.sidebar.slider("Trihalomethanes (μg/L)", 0.0, 140.0, float(st.session_state['Trihalomethanes']), 1.0, format="%.0f μg/L")

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
# 7. APPLICATION TABS
# ==============================================================================
tab_single, tab_batch, tab_analytics = st.tabs([
    "🔬 Real-Time Telemetry Triage",
    "📁 Batch Ingestion Engine",
    "📊 Pipeline Metrics & Architecture"
])


# ------------------------------------------------------------------------------
# TAB 1: REAL-TIME TELEMETRY TRIAGE & COMMAND CENTER
# ------------------------------------------------------------------------------
with tab_single:
    if not model_loaded:
        st.error(f"Model pipeline failed to load: {load_error}")
    else:
        # --- QUICK SCENARIO SIMULATION BAR ---
        st.markdown("##### ⚡ Quick Scenario Simulation")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            if st.button("🏙️ Safe Municipal Tap", use_container_width=True, help="Load clean municipal drinking water baseline"):
                apply_preset("Pristine Tap (Safe)")
                st.rerun()
        with col_p2:
            if st.button("🏭 Toxic Industrial Spill", use_container_width=True, help="Load severe chemical contamination with high TDS & Sulfate"):
                apply_preset("Industrial Spill (Hazardous)")
                st.rerun()
        with col_p3:
            if st.button("🌾 Borderline Agricultural Runoff", use_container_width=True, help="Load borderline agricultural infiltration edge case"):
                apply_preset("Borderline Infiltration (Edge Case)")
                st.rerun()

        st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

        # Run inference
        probs = pipeline.predict_proba(current_sample_df)[0]
        prob_potable = probs[1]
        is_potable = prob_potable >= policy_threshold

        # Detect regulatory violations
        violations = []
        for param, info in REGULATORY_LIMITS.items():
            val = current_sample_df[param].iloc[0]
            if val < info['min']:
                violations.append({
                    'name': info['desc'],
                    'icon': info['icon'],
                    'reading': f"{val:.2f} {info['unit']}",
                    'boundary': f"Below safe floor of {info['min']} {info['unit']}"
                })
            elif val > info['max']:
                violations.append({
                    'name': info['desc'],
                    'icon': info['icon'],
                    'reading': f"{val:.2f} {info['unit']}",
                    'boundary': f"Exceeds safe ceiling of {info['max']} {info['unit']}"
                })

        # --- 2-COLUMN COMMAND CENTER REPOSITIONED LAYOUT ---
        col_left, col_right = st.columns([1.15, 1.0], gap="medium")

        with col_left:
            # --- REAL REACTBITS SPOTLIGHT VERDICT COMPONENT ---
            border_color = "rgba(16, 185, 129, 0.45)" if is_potable else "rgba(239, 68, 68, 0.45)"
            glow_shadow = "0 12px 35px -10px rgba(16, 185, 129, 0.25)" if is_potable else "0 12px 35px -10px rgba(239, 68, 68, 0.25)"
            spotlight_color = "rgba(16, 185, 129, 0.22)" if is_potable else "rgba(239, 68, 68, 0.22)"
            badge_bg = "rgba(16, 185, 129, 0.2)" if is_potable else "rgba(239, 68, 68, 0.2)"
            badge_color = "#34D399" if is_potable else "#F87171"
            badge_border = "rgba(16, 185, 129, 0.35)" if is_potable else "rgba(239, 68, 68, 0.35)"
            badge_text = "✓ WHO GUIDELINE COMPLIANT" if is_potable else "⚠ PUBLIC HEALTH HAZARD DETECTED"
            title_text = "POTABLE / SAFE DRINKING WATER" if is_potable else "HAZARDOUS / CONTAMINATION ALERT"
            score_color = "#34D399" if is_potable else "#F87171"
            policy_label = policy_choice.split('(')[0].strip()
            advisory_text = (
                f"Physicochemical sensor readings satisfy drinking water safety thresholds under the active <b>{policy_label}</b> protocol. Cleared for distribution into municipal supply."
                if is_potable else
                f"Sample fails safety thresholds under the active <b>{policy_label}</b> protocol. Immediate intake pipeline isolation and chemical neutralization mandated."
            )
            delta_val = (prob_potable - policy_threshold) * 100
            delta_str = f"{delta_val:+.1f}%"
            delta_label = "Safety Margin" if is_potable else "Safety Deficit"
            target_pct = prob_potable * 100
            thresh_pct = policy_threshold * 100
            violations_n = len(violations)

            react_code = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; font-family: 'Inter', -apple-system, sans-serif; color: #F8FAFC; overflow: hidden; }}
  .spotlight-card {{
    position: relative;
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.88);
    border: 1.5px solid {border_color};
    box-shadow: {glow_shadow};
    padding: 20px 22px;
    overflow: hidden;
    cursor: default;
    transition: border-color 0.25s ease;
  }}
  .spotlight-overlay {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
    z-index: 1;
  }}
  .card-content {{ position: relative; z-index: 2; }}
  .badge-row {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }}
  .status-badge {{
    display: inline-flex;
    align-items: center;
    background: {badge_bg};
    color: {badge_color};
    border: 1px solid {badge_border};
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
  }}
  .pulse-dot {{
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background-color: {badge_color};
    margin-right: 7px;
    box-shadow: 0 0 0 0 {badge_color};
    animation: pulse-ring 2s infinite cubic-bezier(0.66, 0, 0, 1);
  }}
  @keyframes pulse-ring {{
    0% {{ box-shadow: 0 0 0 0 {badge_color}; }}
    70% {{ box-shadow: 0 0 0 8px transparent; }}
    100% {{ box-shadow: 0 0 0 0 transparent; }}
  }}
  .react-tag {{
    font-size: 0.68rem;
    font-weight: 600;
    color: #00E5BE;
    font-family: 'JetBrains Mono', monospace;
    background: rgba(0, 229, 190, 0.08);
    padding: 3px 8px;
    border-radius: 6px;
    border: 1px solid rgba(0, 229, 190, 0.25);
  }}
  .verdict-title {{
    font-size: 1.40rem;
    font-weight: 800;
    color: #FFFFFF;
    letter-spacing: -0.015em;
    margin-bottom: 5px;
  }}
  .verdict-desc {{
    font-size: 0.86rem;
    color: #CBD5E1;
    line-height: 1.45;
    margin-bottom: 12px;
  }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
  }}
  .kpi-cell {{
    background: rgba(8, 13, 26, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 7px 10px;
    transition: transform 0.2s ease, border-color 0.2s ease;
  }}
  .kpi-cell:hover {{
    transform: translateY(-2px);
    border-color: rgba(255, 255, 255, 0.18);
  }}
  .kpi-lbl {{
    font-size: 0.66rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #94A3B8;
    margin-bottom: 2px;
  }}
  .kpi-val {{
    font-size: 1.10rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: #FFFFFF;
  }}
</style>
</head>
<body>
<div id="react-root"></div>
<script>
  const e = React.createElement;

  function CountUp({{ to, decimals = 1, suffix = '%' }}) {{
    const [val, setVal] = React.useState(0);
    React.useEffect(() => {{
      let startTime = null;
      const duration = 900;
      function animate(now) {{
        if (!startTime) startTime = now;
        const progress = Math.min((now - startTime) / duration, 1);
        const easeOut = 1 - Math.pow(1 - progress, 3);
        setVal((to * easeOut).toFixed(decimals));
        if (progress < 1) {{
          requestAnimationFrame(animate);
        }}
      }}
      requestAnimationFrame(animate);
    }}, [to]);
    return e('span', null, val + suffix);
  }}

  function ReactBitsSpotlightVerdict() {{
    const [pos, setPos] = React.useState({{ x: -500, y: -500 }});
    const [opacity, setOpacity] = React.useState(0);
    const cardRef = React.useRef(null);

    const onMouseMove = (evt) => {{
      if (!cardRef.current) return;
      const rect = cardRef.current.getBoundingClientRect();
      setPos({{ x: evt.clientX - rect.left, y: evt.clientY - rect.top }});
      setOpacity(1);
    }};

    const onMouseLeave = () => {{
      setOpacity(0);
    }};

    return e('div', {{
      ref: cardRef,
      onMouseMove: onMouseMove,
      onMouseLeave: onMouseLeave,
      className: 'spotlight-card'
    }}, [
      e('div', {{
        key: 'spotlight',
        className: 'spotlight-overlay',
        style: {{
          opacity: opacity,
          background: 'radial-gradient(420px circle at ' + pos.x + 'px ' + pos.y + 'px, {spotlight_color}, transparent 65%)'
        }}
      }}),
      e('div', {{ key: 'content', className: 'card-content' }}, [
        e('div', {{ key: 'badge-row', className: 'badge-row' }}, [
          e('div', {{ key: 'badge', className: 'status-badge' }}, [
            e('span', {{ key: 'dot', className: 'pulse-dot' }}),
            '{badge_text}'
          ]),
          e('span', {{ key: 'tag', className: 'react-tag' }}, '⚛️ ReactBits SpotlightCard')
        ]),
        e('h2', {{ key: 'title', className: 'verdict-title' }}, '{title_text}'),
        e('p', {{
          key: 'desc',
          className: 'verdict-desc',
          dangerouslySetInnerHTML: {{ __html: `{advisory_text}` }}
        }}),
        e('div', {{ key: 'kpis', className: 'kpi-grid' }}, [
          e('div', {{ key: 'kpi1', className: 'kpi-cell' }}, [
            e('div', {{ className: 'kpi-lbl' }}, 'Potability Score'),
            e('div', {{ className: 'kpi-val', style: {{ color: '{score_color}' }} }}, [
              e(CountUp, {{ to: {target_pct:.1f}, decimals: 1, suffix: '%' }})
            ])
          ]),
          e('div', {{ key: 'kpi2', className: 'kpi-cell' }}, [
            e('div', {{ className: 'kpi-lbl' }}, 'Policy Bar'),
            e('div', {{ className: 'kpi-val' }}, '{thresh_pct:.0f}%')
          ]),
          e('div', {{ key: 'kpi3', className: 'kpi-cell' }}, [
            e('div', {{ className: 'kpi-lbl' }}, '{delta_label}'),
            e('div', {{ className: 'kpi-val', style: {{ color: '{score_color}' }} }}, '{delta_str}')
          ]),
          e('div', {{ key: 'kpi4', className: 'kpi-cell' }}, [
            e('div', {{ className: 'kpi-lbl' }}, 'WHO Breaches'),
            e('div', {{ className: 'kpi-val', style: {{ color: '{score_color}' }} }}, '{violations_n}')
          ])
        ])
      ])
    ]);
  }}

  ReactDOM.render(e(ReactBitsSpotlightVerdict), document.getElementById('react-root'));
</script>
</body>
</html>"""
            components.html(react_code, height=245, scrolling=False)

            # --- CHEMICAL CULPRIT DIAGNOSTIC PANEL ---
            if violations:
                st.markdown(f"##### 🚨 Detected Chemical Culprits ({len(violations)} Critical Breaches)")
                v_cols = st.columns(min(len(violations), 2))
                for idx, v in enumerate(violations):
                    with v_cols[idx % 2]:
                        st.markdown(f"""
                        <div class="spotlight-culprit-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                <span style="font-weight: 700; color: #FCA5A5; font-size: 0.90rem;">{v['icon']} {v['name']}</span>
                                <span style="font-size: 0.68rem; font-weight: 700; background: rgba(239, 68, 68, 0.25); color: #FCA5A5; padding: 2px 7px; border-radius: 4px; font-family: 'JetBrains Mono', monospace;">BREACH</span>
                            </div>
                            <div style="font-family: 'JetBrains Mono', monospace; font-size: 1.12rem; font-weight: 700; color: #FFFFFF; margin-bottom: 2px;">
                                {v['reading']}
                            </div>
                            <div style="font-size: 0.78rem; color: #CBD5E1;">
                                {v['boundary']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="safe-profile-badge-card">
                    <b>🟢 Optimal Physicochemical Profile:</b> All 9 sensor parameters strictly conform to standard EPA & WHO drinking water envelopes. Zero contaminants detected.
                </div>
                """, unsafe_allow_html=True)

            # --- PHYSICOCHEMICAL REGULATORY AUDIT TABLE ---
            st.markdown("##### 📋 Physicochemical Regulatory Audit")
            audit_records = []
            for key, info in REGULATORY_LIMITS.items():
                val = current_sample_df[key].iloc[0]
                in_bounds = info['min'] <= val <= info['max']
                status_str = "✅ Within Guideline" if in_bounds else "⚠️ Guideline Breach"
                
                audit_records.append({
                    "Parameter": f"{info['icon']} {info['desc']}",
                    "Reading": f"{val:.2f} {info['unit']}",
                    "WHO Guideline": f"{info['min']} - {info['max']} {info['unit']}",
                    "Status": status_str
                })
            st.dataframe(pd.DataFrame(audit_records), use_container_width=True, hide_index=True)

        with col_right:
            # --- HIGH-CONTRAST GAUGE CHART ---
            st.markdown("""
            <div class="glass-chart-container">
                <div class="chart-card-header">
                    <div class="chart-card-title">🧭 Potability Confidence Gauge</div>
                    <div class="chart-card-pill">INFERENCE ENGINE</div>
                </div>
            """, unsafe_allow_html=True)

            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=prob_potable * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                delta={
                    'reference': policy_threshold * 100,
                    'increasing': {'color': "#10B981"},
                    'decreasing': {'color': "#EF4444"},
                    'font': {'size': 18}
                },
                number={
                    'suffix': "%",
                    'font': {'size': 44, 'color': "#FFFFFF", 'family': "sans-serif"}
                },
                gauge={
                    'axis': {
                        'range': [0, 100],
                        'tickwidth': 2,
                        'tickcolor': "#FFFFFF",
                        'tickfont': {'color': '#FFFFFF', 'size': 13, 'family': "sans-serif"}
                    },
                    'bar': {'color': "#00E5BE", 'thickness': 0.32},
                    'bgcolor': "rgba(255, 255, 255, 0.05)",
                    'borderwidth': 1.5,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.35)'},
                        {'range': [50, policy_threshold * 100], 'color': 'rgba(245, 158, 11, 0.35)'},
                        {'range': [policy_threshold * 100, 100], 'color': 'rgba(16, 185, 129, 0.35)'}
                    ],
                    'threshold': {
                        'line': {'color': "#EF4444", 'width': 4},
                        'thickness': 0.85,
                        'value': policy_threshold * 100
                    }
                }
            ))
            fig_gauge.update_layout(
                height=290,
                margin=dict(l=20, r=20, t=25, b=15),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font={'color': '#FFFFFF', 'family': 'sans-serif'}
            )
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.markdown("""
                <div style="font-size: 0.76rem; color: #94A3B8; text-align: center; margin-top: -10px;">
                    Red needle marks your active policy decision threshold (τ* = 0.65).
                </div>
            </div>
            """, unsafe_allow_html=True)

            # --- 9-POINT WHO RADAR CHART ---
            st.markdown("""
            <div class="glass-chart-container">
                <div class="chart-card-header">
                    <div class="chart-card-title">🕸️ Physicochemical Fingerprint</div>
                    <div class="chart-card-pill">WHO ENVELOPE</div>
                </div>
            """, unsafe_allow_html=True)

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
                name='WHO Safe Limit (100%)',
                line=dict(color='#10B981', width=2.2),
                fillcolor='rgba(16, 185, 129, 0.20)'
            ))
            
            # Current Water Sample Trace
            sample_line_color = '#00E5BE' if is_potable else '#EF4444'
            sample_fill_color = 'rgba(0, 229, 190, 0.28)' if is_potable else 'rgba(239, 68, 68, 0.28)'
            
            fig_radar.add_trace(go.Scatterpolar(
                r=sample_ratios,
                theta=radar_categories,
                fill='toself',
                name='Current Water Sample',
                line=dict(color=sample_line_color, width=2.5),
                fillcolor=sample_fill_color
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 180],
                        ticksuffix="%",
                        color="#CBD5E1",
                        tickfont={'color': '#CBD5E1', 'size': 10}
                    ),
                    angularaxis=dict(
                        tickfont={'color': '#FFFFFF', 'size': 12, 'family': 'sans-serif'},
                        linecolor='#475569'
                    ),
                    bgcolor='rgba(255, 255, 255, 0.02)'
                ),
                height=300,
                margin=dict(l=30, r=30, t=20, b=20),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.25,
                    xanchor="center",
                    x=0.5,
                    font={'color': '#FFFFFF', 'size': 11}
                ),
                font={'color': '#FFFFFF', 'family': 'sans-serif'}
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            st.markdown("""
                <div style="font-size: 0.76rem; color: #94A3B8; text-align: center; margin-top: 2px;">
                    Points breaching outside the green perimeter violate WHO maximum safety ceilings.
                </div>
            </div>
            """, unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# TAB 2: BATCH TELEMETRY INGESTION & SCORING
# ------------------------------------------------------------------------------
with tab_batch:
    st.markdown("### 📁 High-Throughput Batch Telemetry Ingestion")
    st.write("Upload municipal sensor telemetry CSV files to score hundreds of water sources simultaneously through the production pipeline.")
    
    col_u1, col_u2 = st.columns([2, 1])
    with col_u1:
        uploaded_batch = st.file_uploader("Upload Telemetry CSV Stream", type=["csv"])
    
    with col_u2:
        st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)
        sample_download_df = pd.DataFrame([
            {'ph': 7.1, 'Hardness': 210, 'Solids': 18000, 'Chloramines': 6.5, 'Sulfate': 320, 'Conductivity': 410, 'Organic_carbon': 11.2, 'Trihalomethanes': 62, 'Turbidity': 3.4, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Urban_Treatment'},
            {'ph': 4.3, 'Hardness': 120, 'Solids': 45000, 'Chloramines': 11.0, 'Sulfate': 480, 'Conductivity': 650, 'Organic_carbon': 23.0, 'Trihalomethanes': 110, 'Turbidity': 6.5, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Industrial_Catchment'},
            {'ph': 8.2, 'Hardness': 180, 'Solids': 16000, 'Chloramines': 7.2, 'Sulfate': 290, 'Conductivity': 390, 'Organic_carbon': 9.8, 'Trihalomethanes': 54, 'Turbidity': 2.9, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Reservoir_Lake'}
        ])
        st.download_button(
            "📄 Download CSV Template",
            sample_download_df.to_csv(index=False).encode('utf-8'),
            "water_telemetry_batch_template.csv",
            "text/csv",
            use_container_width=True
        )
    
    if uploaded_batch is not None:
        batch_df = pd.read_csv(uploaded_batch)
        st.success(f"✓ Ingested {len(batch_df)} samples into memory.")
        
        if 'Data_Source' not in batch_df.columns:
            batch_df['Data_Source'] = 'Regional_Network_B'
        if 'Station_Type' not in batch_df.columns:
            batch_df['Station_Type'] = 'Urban_Treatment'
            
        if st.button("🚀 Execute Batch Triage Inference", use_container_width=True):
            with st.spinner("Executing pipeline inference across batch..."):
                probs_batch = pipeline.predict_proba(batch_df)[:, 1]
                batch_df['Potability_Probability'] = probs_batch
                batch_df['Triage_Verdict'] = np.where(probs_batch >= policy_threshold, 'Potable / Safe', 'Toxic / Unsafe')
                
                safe_n = (batch_df['Triage_Verdict'] == 'Potable / Safe').sum()
                toxic_n = len(batch_df) - safe_n
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Total Ingested Volume", f"{len(batch_df)} samples")
                m2.metric("Potable Sources Cleared", f"{safe_n} ({safe_n/len(batch_df)*100:.1f}%)")
                m3.metric("Contaminated Sources Flagged", f"{toxic_n} ({toxic_n/len(batch_df)*100:.1f}%)")
                
                c1, c2 = st.columns([1, 1.5])
                with c1:
                    fig_pie = px.pie(
                        values=[safe_n, toxic_n],
                        names=['Potable / Safe', 'Toxic / Unsafe'],
                        color=['Potable / Safe', 'Toxic / Unsafe'],
                        color_discrete_map={'Potable / Safe': '#10B981', 'Toxic / Unsafe': '#EF4444'},
                        hole=0.55,
                        title="Batch Safety Ratio",
                        template="plotly_dark"
                    )
                    fig_pie.update_layout(
                        height=290,
                        margin=dict(l=10, r=10, t=35, b=10),
                        paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': '#FFFFFF'}
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with c2:
                    fig_sc = px.scatter(
                        batch_df,
                        x='ph',
                        y='Sulfate',
                        color='Triage_Verdict',
                        color_discrete_map={'Potable / Safe': '#10B981', 'Toxic / Unsafe': '#EF4444'},
                        hover_data=['Solids', 'Chloramines', 'Potability_Probability'],
                        title="Cluster Distribution: pH vs. Sulfate Minerals",
                        template="plotly_dark"
                    )
                    fig_sc.update_layout(
                        height=290,
                        margin=dict(l=10, r=10, t=35, b=10),
                        paper_bgcolor='rgba(0,0,0,0)',
                        font={'color': '#FFFFFF'}
                    )
                    st.plotly_chart(fig_sc, use_container_width=True)
                
                st.dataframe(batch_df, use_container_width=True)
                
                st.download_button(
                    "📥 Export Scored Telemetry Results (CSV)",
                    batch_df.to_csv(index=False).encode('utf-8'),
                    "triaged_batch_output.csv",
                    "text/csv"
                )


# ------------------------------------------------------------------------------
# TAB 3: SYSTEM METRICS & PIPELINE ARCHITECTURE
# ------------------------------------------------------------------------------
with tab_analytics:
    st.markdown("### 🏗️ Production Architecture & Mathematical Rigor")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="glass-chart-container">
            <h4 style="color: #00E5BE; margin-top: 0;">🛠️ End-to-End Pipeline Workflow</h4>
            <ul style="color: #CBD5E1; line-height: 1.8; font-size: 0.92rem;">
                <li><b>Ingestion:</b> Dual-source master dataset (<code>7,776</code> telemetry samples).</li>
                <li><b>Winsorization:</b> Outlier capping via Tukey's IQR fences ([Q1 - 1.5 IQR, Q3 + 1.5 IQR]) with physical zero-floor clipping.</li>
                <li><b>Imputation:</b> 5-Nearest Neighbors (<code>KNNImputer</code>) preserving covariance without mean distortion.</li>
                <li><b>Transformation:</b> Atomic <code>ColumnTransformer</code> (StandardScaler on 9 numerical features + OneHotEncoder on provenance).</li>
                <li><b>Ensemble Classifier:</b> Tuned Random Forest (400 estimators, <code>min_samples_leaf=4</code>, <code>class_weight='balanced_subsample'</code>).</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="glass-chart-container">
            <h4 style="color: #00E5BE; margin-top: 0;">⚖️ Asymmetric Cost-Sensitive Thresholding</h4>
            <p style="color: #CBD5E1; font-size: 0.92rem; line-height: 1.6;">
                In municipal public health, false negative errors (classifying poisonous water as safe) 
                carry catastrophic human costs compared to benign false alarms:
            </p>
            <div style="background: rgba(8, 13, 26, 0.6); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #38BDF8; margin-bottom: 10px;">
                C(FN) = 10 &times; C(FP) &rarr; Optimal Threshold &tau;* = 0.65
            </div>
            <p style="color: #94A3B8; font-size: 0.85rem;">
                Operating at &tau;* = 0.65 eliminates over <b>60% of false potable poisonings</b> while preserving 0.779 ROC-AUC on untouched test data.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🏆 Algorithm Benchmark & Validation Matrix")
    
    bench_table = pd.DataFrame([
        {'Model': 'Logistic Regression (Linear Baseline)', '5-Fold CV ROC-AUC': '0.618', 'Test ROC-AUC': '0.615', 'Macro F1': '0.562', 'Limitation': 'Linear hyperplane fails on bounded safety intervals (e.g. 6.5 <= pH <= 8.5)'},
        {'Model': 'XGBoost Classifier', '5-Fold CV ROC-AUC': '0.745', 'Test ROC-AUC': '0.741', 'Macro F1': '0.675', 'Limitation': 'Slight variance sensitivity on noisy chemical telemetry'},
        {'Model': 'Baseline Random Forest', '5-Fold CV ROC-AUC': '0.772', 'Test ROC-AUC': '0.768', 'Macro F1': '0.696', 'Limitation': 'Unconstrained tree depth allowed mild variance overfitting'},
        {'Model': 'Tuned Champion Random Forest 🏆', '5-Fold CV ROC-AUC': '0.779', 'Test ROC-AUC': '0.779', 'Macro F1': '0.702', 'Limitation': 'Production Champion: 400 trees with leaf regularization and balanced weights'}
    ])
    st.dataframe(bench_table, use_container_width=True, hide_index=True)

