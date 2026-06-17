from sqlalchemy import create_engine, Column, Integer, BigInteger, String, Boolean, Float, Text, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime
from backend.app.core.config import settings

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="Analyst") # Admin, Moderator, Analyst
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    versions = relationship("DatasetVersion", back_populates="dataset", cascade="all, delete-orphan")

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    version_tag = Column(String(50), nullable=False)
    dvc_hash = Column(String(255))
    file_path = Column(String(512), nullable=False)
    record_count = Column(Integer, default=0)
    metadata_json = Column(JSONB, name="metadata")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    dataset = relationship("Dataset", back_populates="versions")

class ModelMetadata(Base):
    __tablename__ = "models"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    version_tag = Column(String(50), nullable=False)
    mlflow_run_id = Column(String(255))
    is_active = Column(Boolean, default=False)
    accuracy = Column(Float)
    f1_score = Column(Float)
    metadata_json = Column(JSONB, name="metadata")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TrainingRun(Base):
    __tablename__ = "training_runs"
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"))
    dataset_version_id = Column(Integer, ForeignKey("dataset_versions.id", ondelete="SET NULL"))
    status = Column(String(50), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED
    mlflow_run_id = Column(String(255))
    metrics = Column(JSONB)
    logs = Column(Text)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(BigInteger, primary_key=True, index=True)
    text_content = Column(Text, nullable=False)
    normalized_content = Column(Text)
    level1_pred = Column(String(50), nullable=False, index=True) # Violence, Non-Violence
    level1_conf = Column(Float, nullable=False)
    level2_pred = Column(String(50), default="None")
    level2_conf = Column(Float)
    model_id = Column(Integer, ForeignKey("models.id", ondelete="SET NULL"))
    moderator_override = Column(String(50))
    moderator_override_level2 = Column(String(50))
    overridden_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    explanation = relationship("Explanation", back_populates="prediction", uselist=False, cascade="all, delete-orphan")

class Explanation(Base):
    __tablename__ = "explanations"
    id = Column(BigInteger, primary_key=True, index=True)
    prediction_id = Column(BigInteger, ForeignKey("predictions.id", ondelete="CASCADE"), unique=True, nullable=False)
    lime_explanation = Column(JSONB)
    shap_explanation = Column(JSONB)
    attention_weights = Column(JSONB)
    human_explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    prediction = relationship("Prediction", back_populates="explanation")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(255), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255))
    details = Column(JSONB)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class SystemMetric(Base):
    __tablename__ = "system_metrics"
    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    cpu_utilization = Column(Float, nullable=False)
    memory_utilization = Column(Float, nullable=False)
    gpu_utilization = Column(Float)
    gpu_memory_utilization = Column(Float)
    request_latency_ms = Column(Float, nullable=False)
    error_count = Column(Integer, default=0)
    drift_score = Column(Float)

# DB setup session logic
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
