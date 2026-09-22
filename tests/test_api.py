# ==============================================================================
# AUTOMATED UNIT TESTS FOR AQUAGUARD ML FASTAPI REST SERVICE
# ==============================================================================
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_health_check_endpoint():
    """Verify that the health check endpoint returns 200 and indicates model is loaded."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "pipeline_steps" in data
    assert data["champion_model"] == "Tuned Random Forest (400 Trees)"
    assert data["default_threshold"] == 0.65

def test_presets_endpoint():
    """Verify that predefined simulation scenarios are available."""
    response = client.get("/api/presets")
    assert response.status_code == 200
    presets = response.json()
    assert "Pristine Tap (Safe)" in presets
    assert "Industrial Spill (Hazardous)" in presets
    assert "Borderline Infiltration (Edge Case)" in presets
    assert presets["Pristine Tap (Safe)"]["ph"] == 7.35

def test_limits_endpoint():
    """Verify that WHO regulatory parameter envelopes are returned."""
    response = client.get("/api/limits")
    assert response.status_code == 200
    limits = response.json()
    assert "ph" in limits
    assert limits["ph"]["min"] == 6.5
    assert limits["ph"]["max"] == 8.5
    assert len(limits) == 9

def test_predict_safe_sample():
    """Verify prediction response structure and safe sample inference."""
    payload = {
        "ph": 7.35,
        "Hardness": 195.0,
        "Solids": 16500.0,
        "Chloramines": 6.8,
        "Sulfate": 315.0,
        "Conductivity": 390.0,
        "Organic_carbon": 11.0,
        "Trihalomethanes": 58.0,
        "Turbidity": 3.1,
        "Data_Source": "Regional_Network_B",
        "Station_Type": "Urban_Treatment",
        "threshold": 0.65
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "potability_probability" in data
    assert 0.0 <= data["potability_probability"] <= 1.0
    assert "is_potable" in data
    assert "violations" in data
    assert "radar_data" in data
    assert len(data["radar_data"]) == 9
    assert "audit_table" in data
    assert len(data["audit_table"]) == 9

def test_predict_toxic_sample_and_violations():
    """Verify that a contaminated sample correctly surfaces WHO parameter breaches."""
    payload = {
        "ph": 3.90,
        "Hardness": 110.0,
        "Solids": 46000.0,
        "Chloramines": 12.5,
        "Sulfate": 490.0,
        "Conductivity": 720.0,
        "Organic_carbon": 25.5,
        "Trihalomethanes": 118.0,
        "Turbidity": 6.8,
        "Data_Source": "Regional_Network_B",
        "Station_Type": "Industrial_Catchment",
        "threshold": 0.65
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_potable"] is False
    assert data["violations_count"] > 0
    culprit_names = [v["parameter"] for v in data["violations"]]
    assert "ph" in culprit_names or "Solids" in culprit_names

def test_batch_template_download():
    """Verify batch CSV template is downloadable and correctly structured."""
    response = client.get("/api/batch-template")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    content = response.text
    assert "ph" in content
    assert "Turbidity" in content

def test_batch_predict_csv_upload():
    """Verify multi-sample CSV batch scoring and cohort statistics generation."""
    csv_content = (
        "ph,Hardness,Solids,Chloramines,Sulfate,Conductivity,Organic_carbon,Trihalomethanes,Turbidity,Data_Source,Station_Type\n"
        "7.35,195.0,16500.0,6.8,315.0,390.0,11.0,58.0,3.1,Regional_Network_B,Urban_Treatment\n"
        "3.90,110.0,46000.0,12.5,490.0,720.0,25.5,118.0,6.8,Regional_Network_B,Industrial_Catchment\n"
    )
    files = {"file": ("test_batch.csv", csv_content, "text/csv")}
    response = client.post("/api/batch-predict", files=files, data={"threshold": 0.65})
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert data["summary"]["total_samples"] == 2
    assert "scatter_points" in data
    assert len(data["scatter_points"]) == 2
    assert "preview_rows" in data
    assert "csv_data" in data

def test_frontend_spa_serving():
    """Verify that root URL serves the built React SPA."""
    import importlib
    import api.main
    importlib.reload(api.main)
    spa_client = TestClient(api.main.app)
    response = spa_client.get("/")
    assert response.status_code == 200
    assert "AquaGuard ML" in response.text or "<div id=\"root\">" in response.text
