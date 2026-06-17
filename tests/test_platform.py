import pytest
import numpy as np
import pandas as pd
import torch
from fastapi.testclient import TestClient
from backend.app.main import app
from ai_service.app.pipelines.urdu_preprocessing import preprocess_text, normalize_urdu_characters
from ai_service.app.pipelines.validation import validate_dataframe_schema, run_quality_checks
from ai_service.app.model.classifier import HierarchicalViolenceClassifier
from backend.app.core.security import create_access_token, verify_password, get_password_hash

# 1. Text Preprocessing Tests
def test_urdu_character_normalization():
    # Arabic kaf character should map to Urdu keheh character
    raw_text = "كتاب" # Arabic Kaf
    normalized = normalize_urdu_characters(raw_text)
    assert "ک" in normalized # Urdu Keheh
    assert "ك" not in normalized

def test_noise_removal():
    raw_text = "Check this out https://google.com and @user #violence!"
    cleaned = preprocess_text(raw_text)
    assert "https" not in cleaned
    assert "@user" not in cleaned
    assert "#" not in cleaned
    assert "violence" in cleaned

# 2. Data Validation Schema Tests
def test_validation_schema_correct():
    data = {
        "text": ["یہ ایک پرامن بیان ہے۔", "اسے مار ڈالو!"],
        "level1": ["Non-Violence", "Violence"],
        "level2": ["None", "Political"]
    }
    df = pd.DataFrame(data)
    valid, msg = validate_dataframe_schema(df)
    assert valid is True
    
    report = run_quality_checks(df)
    assert report["success"] is True
    assert report["empty_text_count"] == 0

def test_validation_schema_invalid():
    # Missing required 'level1' column
    data = {
        "text": ["یہ ایک پرامن بیان ہے۔"],
        "level2": ["None"]
    }
    df = pd.DataFrame(data)
    valid, msg = validate_dataframe_schema(df)
    assert valid is False

# 3. Model Structure Shapes Tests
def test_model_initialization():
    model = HierarchicalViolenceClassifier(num_heads=2)
    # Validate layer configurations
    assert model.bilstm is not None
    assert model.attention is not None
    assert model.level1_head is not None
    assert model.level2_head is not None

# 4. Security & Cryptography Tests
def test_password_hashing():
    pwd = "super-secret-password-123"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong-password", hashed) is False

def test_jwt_generation():
    token = create_access_token(subject="admin_user", role="Admin")
    assert token is not None
    assert isinstance(token, str)

# 5. API Router Tests (using FastAPI TestClient)
client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics_endpoint():
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    assert "system" in response.json()
    assert "performance" in response.json()

def test_security_headers():
    response = client.get("/api/v1/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert "Content-Security-Policy" in response.headers
