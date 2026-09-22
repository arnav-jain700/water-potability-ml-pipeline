import os
import io
import joblib
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
from pydantic import BaseModel, Field

# ==============================================================================
# 1. CONSTANTS & REGULATORY BENCHMARKS (WHO / EPA)
# ==============================================================================
REGULATORY_LIMITS: Dict[str, Dict[str, Any]] = {
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

PRESETS: Dict[str, Dict[str, Any]] = {
    "Pristine Tap (Safe)": {
        'ph': 7.35, 'Hardness': 195.0, 'Solids': 16500.0, 'Chloramines': 6.8,
        'Sulfate': 315.0, 'Conductivity': 390.0, 'Organic_carbon': 11.0,
        'Trihalomethanes': 58.0, 'Turbidity': 3.1,
        'Station_Type': 'Urban_Treatment', 'Data_Source': 'Regional_Network_B',
        'description': 'Municipal treated tap water baseline meeting safety specifications.'
    },
    "Industrial Spill (Hazardous)": {
        'ph': 3.90, 'Hardness': 110.0, 'Solids': 46000.0, 'Chloramines': 12.5,
        'Sulfate': 490.0, 'Conductivity': 720.0, 'Organic_carbon': 25.5,
        'Trihalomethanes': 118.0, 'Turbidity': 6.8,
        'Station_Type': 'Industrial_Catchment', 'Data_Source': 'Regional_Network_B',
        'description': 'Severe chemical contamination with high solids, chloramines, and sulfate.'
    },
    "Borderline Infiltration (Edge Case)": {
        'ph': 6.30, 'Hardness': 145.0, 'Solids': 24000.0, 'Chloramines': 8.2,
        'Sulfate': 365.0, 'Conductivity': 460.0, 'Organic_carbon': 16.5,
        'Trihalomethanes': 78.0, 'Turbidity': 4.8,
        'Station_Type': 'Agricultural_Runoff', 'Data_Source': 'Regional_Network_B',
        'description': 'Borderline agricultural infiltration testing public safety threshold.'
    }
}

# ==============================================================================
# 2. MODEL LOADER
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'water_potability_pipeline.joblib')

pipeline = None
model_error = None

def get_pipeline():
    global pipeline, model_error
    if pipeline is None and model_error is None:
        try:
            if not os.path.exists(MODEL_PATH):
                raise FileNotFoundError(f"Model artifact missing at {MODEL_PATH}")
            pipeline = joblib.load(MODEL_PATH)
        except Exception as e:
            model_error = str(e)
            raise HTTPException(status_code=500, detail=f"Failed to load ML pipeline: {model_error}")
    if model_error:
        raise HTTPException(status_code=500, detail=f"Pipeline unavailable: {model_error}")
    return pipeline

# ==============================================================================
# 3. FASTAPI APP & MIDDLEWARE
# ==============================================================================
app = FastAPI(
    title="AquaGuard ML | Water Potability Triage API",
    description="High-performance async REST API for real-time water potability classification and batch environmental triage.",
    version="2.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# 4. SCHEMAS
# ==============================================================================
class WaterSampleInput(BaseModel):
    ph: float = Field(7.35, ge=0.0, le=14.0, description="pH Level (0-14)")
    Hardness: float = Field(195.0, ge=0.0, description="Hardness (mg/L)")
    Solids: float = Field(16500.0, ge=0.0, description="Total Dissolved Solids (ppm)")
    Chloramines: float = Field(6.8, ge=0.0, description="Chloramines (ppm)")
    Sulfate: float = Field(315.0, ge=0.0, description="Sulfate minerals (mg/L)")
    Conductivity: float = Field(390.0, ge=0.0, description="Electrical Conductivity (μS/cm)")
    Organic_carbon: float = Field(11.0, ge=0.0, description="Total Organic Carbon (ppm)")
    Trihalomethanes: float = Field(58.0, ge=0.0, description="Trihalomethanes (μg/L)")
    Turbidity: float = Field(3.1, ge=0.0, description="Turbidity (NTU)")
    Data_Source: str = Field("Regional_Network_B", description="Data Stream Provenance")
    Station_Type: str = Field("Urban_Treatment", description="Monitoring Station Environment")
    threshold: float = Field(0.65, ge=0.0, le=1.0, description="Decision threshold policy (default: 0.65)")

class ViolationItem(BaseModel):
    parameter: str
    name: str
    icon: str
    reading: float
    formatted_reading: str
    unit: str
    min: float
    max: float
    boundary: str
    severity: str

class RadarPoint(BaseModel):
    subject: str
    current: float
    benchmark: float

class AuditItem(BaseModel):
    parameter: str
    reading: str
    guideline: str
    status: str
    in_bounds: bool

class PredictionResponse(BaseModel):
    potability_probability: float
    confidence_pct: float
    threshold: float
    is_potable: bool
    status: str
    badge_color: str
    advisory: str
    delta_pct: float
    violations_count: int
    violations: List[ViolationItem]
    radar_data: List[RadarPoint]
    audit_table: List[AuditItem]

class BatchSummary(BaseModel):
    total_samples: int
    safe_count: int
    toxic_count: int
    safe_percentage: float
    toxic_percentage: float
    threshold_applied: float

# ==============================================================================
# 5. ENDPOINTS
# ==============================================================================
@app.get("/api/health")
def health_check():
    """Returns the operational status of the ML pipeline and runtime."""
    pipe = get_pipeline()
    steps = [name for name, _ in pipe.named_steps.items()] if hasattr(pipe, 'named_steps') else []
    return {
        "status": "healthy",
        "service": "AquaGuard ML REST Engine",
        "model_loaded": True,
        "version": "2.4.0",
        "pipeline_steps": steps,
        "champion_model": "Tuned Random Forest (400 Trees)",
        "cv_roc_auc": 0.779,
        "default_threshold": 0.65
    }

@app.get("/api/presets")
def get_presets():
    """Returns curated test presets for instant simulation."""
    return PRESETS

@app.get("/api/limits")
def get_limits():
    """Returns WHO and EPA maximum and minimum regulatory envelopes."""
    return REGULATORY_LIMITS

@app.post("/api/predict", response_model=PredictionResponse)
def predict_sample(sample: WaterSampleInput):
    """Executes single-sample water potability inference against the calibrated pipeline."""
    pipe = get_pipeline()

    input_dict = {
        'ph': sample.ph,
        'Hardness': sample.Hardness,
        'Solids': sample.Solids,
        'Chloramines': sample.Chloramines,
        'Sulfate': sample.Sulfate,
        'Conductivity': sample.Conductivity,
        'Organic_carbon': sample.Organic_carbon,
        'Trihalomethanes': sample.Trihalomethanes,
        'Turbidity': sample.Turbidity,
        'Data_Source': sample.Data_Source,
        'Station_Type': sample.Station_Type
    }
    df = pd.DataFrame([input_dict])

    try:
        probs = pipe.predict_proba(df)[0]
        prob_potable = float(probs[1])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference execution failed: {str(e)}")

    is_potable = bool(prob_potable >= sample.threshold)
    confidence_pct = round(prob_potable * 100.0, 2)
    threshold_pct = round(sample.threshold * 100.0, 2)
    delta_pct = round(confidence_pct - threshold_pct, 2)

    # Detect WHO breaches
    violations: List[ViolationItem] = []
    audit_table: List[AuditItem] = []
    radar_data: List[RadarPoint] = []

    radar_name_map = {
        'ph': 'pH',
        'Hardness': 'Hardness',
        'Solids': 'Solids',
        'Chloramines': 'Chloramines',
        'Sulfate': 'Sulfate',
        'Conductivity': 'Conductivity',
        'Organic_carbon': 'TOC',
        'Trihalomethanes': 'THMs',
        'Turbidity': 'Turbidity'
    }

    for param, info in REGULATORY_LIMITS.items():
        val = float(input_dict[param])
        in_bounds = (val >= info['min']) and (val <= info['max'])
        status_text = "Within Guideline" if in_bounds else "Guideline Breach"

        audit_table.append(AuditItem(
            parameter=f"{info['icon']} {info['desc']}",
            reading=f"{val:.2f} {info['unit']}",
            guideline=f"{info['min']} - {info['max']} {info['unit']}",
            status=status_text,
            in_bounds=in_bounds
        ))

        # Radar calculation (ratio capped at 200% for legible plotting)
        safe_max = float(info['max'])
        ratio = round(min((val / safe_max) * 100.0 if safe_max > 0 else 0.0, 200.0), 1)
        radar_data.append(RadarPoint(
            subject=radar_name_map.get(param, param),
            current=ratio,
            benchmark=100.0
        ))

        if not in_bounds:
            if val < info['min']:
                bound_desc = f"Below safe floor of {info['min']} {info['unit']}"
            else:
                bound_desc = f"Exceeds safe ceiling of {info['max']} {info['unit']}"
            violations.append(ViolationItem(
                parameter=param,
                name=info['desc'],
                icon=info['icon'],
                reading=val,
                formatted_reading=f"{val:.2f} {info['unit']}",
                unit=info['unit'],
                min=float(info['min']),
                max=float(info['max']),
                boundary=bound_desc,
                severity="CRITICAL"
            ))

    if is_potable:
        status = "POTABLE / CLEARED FOR CONSUMPTION"
        badge_color = "#10B981"
        advisory = (
            f"Water sample cleared under <strong>τ = {sample.threshold:.2f}</strong> public safety policy. "
            f"Physical parameter safety envelope conformed across required standards."
        )
    else:
        status = "CONTAMINATED / UNFIT FOR DRINKING"
        badge_color = "#EF4444"
        advisory = (
            f"Water sample flagged as hazardous. Potability probability of <strong>{confidence_pct}%</strong> "
            f"falls below the required <strong>{threshold_pct}%</strong> safety clearance bar."
        )

    return PredictionResponse(
        potability_probability=prob_potable,
        confidence_pct=confidence_pct,
        threshold=sample.threshold,
        is_potable=is_potable,
        status=status,
        badge_color=badge_color,
        advisory=advisory,
        delta_pct=delta_pct,
        violations_count=len(violations),
        violations=violations,
        radar_data=radar_data,
        audit_table=audit_table
    )

@app.post("/api/batch-predict")
async def batch_predict(
    file: UploadFile = File(...),
    threshold: float = Form(0.65)
):
    """Parses uploaded CSV stream, runs batch classification, and returns enriched telemetry and distribution stats."""
    pipe = get_pipeline()

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file format: {str(e)}")

    # Check minimum required numerical features
    required_numerical = ['ph', 'Hardness', 'Solids', 'Chloramines', 'Sulfate', 'Conductivity', 'Organic_carbon', 'Trihalomethanes', 'Turbidity']
    missing = [c for c in required_numerical if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"CSV missing mandatory parameter columns: {', '.join(missing)}")

    # Fill defaults for categorical if missing
    if 'Data_Source' not in df.columns:
        df['Data_Source'] = 'Regional_Network_B'
    if 'Station_Type' not in df.columns:
        df['Station_Type'] = 'Urban_Treatment'

    try:
        probs = pipe.predict_proba(df)[:, 1]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch model prediction failed: {str(e)}")

    df['Potability_Probability'] = np.round(probs, 4)
    df['Confidence_Pct'] = np.round(probs * 100.0, 2)
    df['Is_Potable'] = probs >= threshold
    df['Triage_Verdict'] = np.where(probs >= threshold, 'Potable / Safe', 'Toxic / Unsafe')

    total = len(df)
    safe_count = int((df['Is_Potable']).sum())
    toxic_count = total - safe_count
    safe_pct = round((safe_count / total) * 100.0, 2) if total > 0 else 0.0
    toxic_pct = round((toxic_count / total) * 100.0, 2) if total > 0 else 0.0

    # Scatter plot sample points (limit to 300 points for quick frontend rendering)
    sample_size = min(total, 300)
    sampled_df = df.sample(n=sample_size, random_state=42) if total > sample_size else df
    scatter_points = []
    for _, row in sampled_df.iterrows():
        scatter_points.append({
            'ph': round(float(row['ph']), 2),
            'Sulfate': round(float(row['Sulfate']), 2),
            'Solids': round(float(row['Solids']), 1),
            'Chloramines': round(float(row['Chloramines']), 2),
            'probability': round(float(row['Potability_Probability']), 3),
            'verdict': str(row['Triage_Verdict']),
            'is_potable': bool(row['Is_Potable'])
        })

    # Convert results preview table (top 50 rows)
    preview_rows = df.head(50).to_dict(orient='records')
    # Generate CSV output string for direct download
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_string = csv_buffer.getvalue()

    return {
        "summary": {
            "total_samples": total,
            "safe_count": safe_count,
            "toxic_count": toxic_count,
            "safe_percentage": safe_pct,
            "toxic_percentage": toxic_pct,
            "threshold_applied": threshold
        },
        "scatter_points": scatter_points,
        "preview_rows": preview_rows,
        "csv_data": csv_string
    }

@app.get("/api/batch-template")
def download_batch_template():
    """Provides a sample CSV template for batch scoring."""
    sample_df = pd.DataFrame([
        {'ph': 7.1, 'Hardness': 210, 'Solids': 18000, 'Chloramines': 6.5, 'Sulfate': 320, 'Conductivity': 410, 'Organic_carbon': 11.2, 'Trihalomethanes': 62, 'Turbidity': 3.4, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Urban_Treatment'},
        {'ph': 4.3, 'Hardness': 120, 'Solids': 45000, 'Chloramines': 11.0, 'Sulfate': 480, 'Conductivity': 650, 'Organic_carbon': 23.0, 'Trihalomethanes': 110, 'Turbidity': 6.5, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Industrial_Catchment'},
        {'ph': 8.2, 'Hardness': 180, 'Solids': 16000, 'Chloramines': 7.2, 'Sulfate': 290, 'Conductivity': 390, 'Organic_carbon': 9.8, 'Trihalomethanes': 54, 'Turbidity': 2.9, 'Data_Source': 'Regional_Network_B', 'Station_Type': 'Reservoir_Lake'}
    ])
    csv_content = sample_df.to_csv(index=False)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=water_telemetry_batch_template.csv"}
    )

# ==============================================================================
# 6. STATIC FRONTEND SPA SERVING (PRODUCTION MODE)
# ==============================================================================
FRONTEND_DIST = os.path.join(BASE_DIR, 'frontend', 'dist')
if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
