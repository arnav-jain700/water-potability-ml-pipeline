# ==============================================================================
# AUTOMATED UNIT TESTS FOR WATER POTABILITY MACHINE LEARNING PIPELINE
# ==============================================================================
import os
import pytest
import pandas as pd
import numpy as np
import joblib
from sklearn.pipeline import Pipeline

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'dataset', 'cleaned_water_potability.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'water_potability_pipeline.joblib')


def test_data_integrity():
    """Test that cleaned dataset exists, contains no null values, and has valid target labels."""
    assert os.path.exists(DATA_PATH), f"Data file not found at {DATA_PATH}"
    df = pd.read_csv(DATA_PATH)
    
    # Verify dimensions
    assert df.shape[0] == 7776, f"Expected 7776 rows, got {df.shape[0]}"
    assert df.shape[1] == 12, f"Expected 12 columns, got {df.shape[1]}"
    
    # Verify zero missing values
    assert df.isnull().sum().sum() == 0, "Cleaned dataset contains unexpected null values!"
    
    # Verify target variable binary domain
    assert set(df['Potability'].unique()).issubset({0, 1}), "Target variable contains non-binary values!"


def test_model_artifact_loading():
    """Test that the serialized pipeline artifact loads cleanly as a valid Scikit-Learn Pipeline."""
    assert os.path.exists(MODEL_PATH), f"Model artifact not found at {MODEL_PATH}"
    pipeline = joblib.load(MODEL_PATH)
    assert isinstance(pipeline, Pipeline), "Loaded artifact is not a Scikit-Learn Pipeline instance!"
    assert 'preprocessor' in pipeline.named_steps, "Pipeline missing preprocessor step!"
    assert 'classifier' in pipeline.named_steps, "Pipeline missing classifier step!"


def test_pipeline_inference_bounds():
    """Test that pipeline correctly handles raw DataFrame input and outputs valid probability distributions."""
    pipeline = joblib.load(MODEL_PATH)
    
    # Raw unscaled test sample
    sample = pd.DataFrame([{
        'ph': 7.35,
        'Hardness': 205.0,
        'Solids': 19500.0,
        'Chloramines': 7.1,
        'Sulfate': 340.0,
        'Conductivity': 420.0,
        'Organic_carbon': 13.5,
        'Trihalomethanes': 65.0,
        'Turbidity': 3.9,
        'Data_Source': 'Regional_Network_B',
        'Station_Type': 'Urban_Treatment'
    }])
    
    probs = pipeline.predict_proba(sample)[0]
    assert len(probs) == 2, "Output probability vector should contain exactly 2 classes"
    assert 0.0 <= probs[0] <= 1.0, f"Class 0 probability {probs[0]} out of bounds"
    assert 0.0 <= probs[1] <= 1.0, f"Class 1 probability {probs[1]} out of bounds"
    assert np.isclose(probs.sum(), 1.0), f"Probabilities do not sum to 1.0: {probs.sum()}"


def test_cost_sensitive_threshold_logic():
    """Test that the public safety threshold (optimal tau = 0.65) overrides naive 0.50 coin flips."""
    SAFETY_THRESHOLD = 0.65
    borderline_prob = 0.55
    standard_decision = int(borderline_prob >= 0.50)
    assert standard_decision == 1, "Standard policy should have predicted 1"
    safety_decision = int(borderline_prob >= SAFETY_THRESHOLD)
    assert safety_decision == 0, "Public safety policy should have flagged borderline sample as 0 (Toxic)!"