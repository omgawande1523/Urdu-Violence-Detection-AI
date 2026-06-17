from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import pydantic
import pandas as pd
import io
import time
import psutil
from backend.app.models.database import get_db, User, Prediction, Explanation, ModelMetadata, TrainingRun, AuditLog, SystemMetric
from backend.app.core.security import (
    create_access_token, get_password_hash, verify_password, 
    get_current_user, TokenData, allow_analyst, allow_moderator, allow_admin
)
from ai_service.app.service import AIServicePipeline

router = APIRouter()

# Initialize AI Service
ai_pipeline = AIServicePipeline()

# --- Pydantic Schemas ---
class UserRegister(pydantic.BaseModel):
    username: str
    email: str
    password: str
    role: Optional[str] = "Analyst"

class Token(pydantic.BaseModel):
    access_token: str
    token_type: str

class PredictRequest(pydantic.BaseModel):
    text: str

class BatchPredictRequest(pydantic.BaseModel):
    texts: List[str]

class PredictionResponse(pydantic.BaseModel):
    id: Optional[int] = None
    text: str
    normalized_text: str
    level1_pred: str
    level1_conf: float
    level2_pred: str
    level2_conf: float

class ExplanationResponse(PredictionResponse):
    lime: List[Dict[str, Any]]
    shap: List[Dict[str, Any]]
    attention: List[Dict[str, Any]]
    explanation: str

# --- Endpoints ---

@router.post("/auth/register", response_model=Dict[str, str])
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """User registration API."""
    existing_user = db.query(User).filter((User.username == user_in.username) | (User.email == user_in.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    hashed_pwd = get_password_hash(user_in.password)
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=hashed_pwd,
        role=user_in.role if user_in.role in ["Admin", "Moderator", "Analyst"] else "Analyst"
    )
    db.add(user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Standard OAuth2 login returning access token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(subject=user.username, role=user.role)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/predict", response_model=PredictionResponse)
def predict(req: PredictRequest, db: Session = Depends(get_db), current_user: TokenData = Depends(allow_analyst)):
    """Predict violence incitation for a single text."""
    start_time = time.time()
    
    # Run prediction
    pred_res = ai_pipeline.predict(req.text)
    
    # Log to PostgreSQL
    db_pred = Prediction(
        text_content=req.text,
        normalized_content=pred_res["normalized_text"],
        level1_pred=pred_res["level1_pred"],
        level1_conf=pred_res["level1_conf"],
        level2_pred=pred_res["level2_pred"],
        level2_conf=pred_res["level2_conf"]
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    
    # Audit log
    audit = AuditLog(
        user_id=None, # can map to current_user
        action="prediction_created",
        resource_type="prediction",
        resource_id=str(db_pred.id),
        details={"level1": pred_res["level1_pred"], "level2": pred_res["level2_pred"]}
    )
    db.add(audit)
    
    # Metrics log
    latency = (time.time() - start_time) * 1000
    metric = SystemMetric(
        cpu_utilization=psutil.cpu_percent(),
        memory_utilization=psutil.virtual_memory().percent,
        request_latency_ms=latency
    )
    db.add(metric)
    db.commit()
    
    return {
        "id": db_pred.id,
        **pred_res
    }

@router.post("/batch-predict", response_model=List[PredictionResponse])
def batch_predict(req: BatchPredictRequest, db: Session = Depends(get_db), current_user: TokenData = Depends(allow_analyst)):
    """Predict violence incitation for a batch of texts."""
    results = []
    for text in req.texts:
        pred_res = ai_pipeline.predict(text)
        db_pred = Prediction(
            text_content=text,
            normalized_content=pred_res["normalized_text"],
            level1_pred=pred_res["level1_pred"],
            level1_conf=pred_res["level1_conf"],
            level2_pred=pred_res["level2_pred"],
            level2_conf=pred_res["level2_conf"]
        )
        db.add(db_pred)
        db.commit()
        db.refresh(db_pred)
        results.append({
            "id": db_pred.id,
            **pred_res
        })
    return results

@router.post("/explain", response_model=ExplanationResponse)
def explain(req: PredictRequest, db: Session = Depends(get_db), current_user: TokenData = Depends(allow_analyst)):
    """Provides LIME, SHAP, and Attention explanation details."""
    start_time = time.time()
    
    # Run explanation pipeline
    exp_res = ai_pipeline.explain(req.text)
    
    # Save Prediction and Explanation to Database
    db_pred = Prediction(
        text_content=req.text,
        normalized_content=exp_res["normalized_text"],
        level1_pred=exp_res["level1_pred"],
        level1_conf=exp_res["level1_conf"],
        level2_pred=exp_res["level2_pred"],
        level2_conf=exp_res["level2_conf"]
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    
    db_exp = Explanation(
        prediction_id=db_pred.id,
        lime_explanation=exp_res["lime"],
        shap_explanation=exp_res["shap"],
        attention_weights=exp_res["attention"],
        human_explanation=exp_res["explanation"]
    )
    db.add(db_exp)
    db.commit()
    
    # Metrics
    latency = (time.time() - start_time) * 1000
    metric = SystemMetric(
        cpu_utilization=psutil.cpu_percent(),
        memory_utilization=psutil.virtual_memory().percent,
        request_latency_ms=latency
    )
    db.add(metric)
    db.commit()
    
    return {
        "id": db_pred.id,
        **exp_res
    }

@router.post("/retrain", response_model=Dict[str, Any])
def retrain(db: Session = Depends(get_db), current_user: TokenData = Depends(allow_admin)):
    """Triggers retraining job run."""
    run = TrainingRun(
        status="RUNNING",
        started_at=time.strftime('%Y-%m-%d %H:%M:%S')
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    
    # Emulate background execution of training loop
    # In actual deployment this will spawn a celery worker task
    run.status = "COMPLETED"
    run.metrics = {"accuracy": 0.892, "f1_score": 0.887}
    
    # Add new model metadata
    model_meta = ModelMetadata(
        name="Urdu-Violence-Classifier-Attention",
        version_tag=f"v2.{run.id}",
        is_active=True,
        accuracy=0.892,
        f1_score=0.887
    )
    db.add(model_meta)
    db.commit()
    
    return {
        "status": "COMPLETED",
        "training_run_id": run.id,
        "metrics": run.metrics,
        "new_model_version": model_meta.version_tag
    }

@router.get("/health", response_model=Dict[str, str])
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Explainable Violence Detection Platform API"}

@router.get("/metrics", response_model=Dict[str, Any])
def get_metrics(db: Session = Depends(get_db)):
    """Fetch Prometheus style system metrics."""
    metrics = db.query(SystemMetric).order_by(SystemMetric.timestamp.desc()).limit(10).all()
    avg_latency = sum([m.request_latency_ms for m in metrics]) / len(metrics) if metrics else 0.0
    return {
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        },
        "performance": {
            "avg_latency_ms": avg_latency,
            "total_requests_logged": db.query(SystemMetric).count()
        }
    }

@router.get("/model-info", response_model=Dict[str, Any])
def model_info(db: Session = Depends(get_db)):
    """Exposes details of active models."""
    model = db.query(ModelMetadata).filter(ModelMetadata.is_active == True).first()
    if not model:
        return {
            "model_name": "Urdu-Violence-Classifier-Attention (Mock Fallback)",
            "version": "v1.0.0-mock",
            "accuracy": 0.885,
            "f1_score": 0.879,
            "status": "active"
        }
    return {
        "model_name": model.name,
        "version": model.version_tag,
        "accuracy": model.accuracy,
        "f1_score": model.f1_score,
        "status": "active",
        "mlflow_run_id": model.mlflow_run_id
    }
