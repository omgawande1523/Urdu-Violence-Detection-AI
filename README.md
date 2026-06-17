# Explainable Violence Incitation Detection Platform (AVIP)

AVIP is an enterprise-grade hierarchical machine learning platform designed to identify and explain violence incitation in Urdu social media text.

---

## System Architecture

AVIP follows a microservices clean architecture separating presentation, data ingestion, business logic, model inference, and audit logging.

```
explainable_violence_detection/
├── backend/                  # FastAPI Application Gateway & Security Manager
│   ├── app/
│   │   ├── api/              # Routers (predict, auth, explain, etc.)
│   │   ├── core/             # Configuration, RBAC Security, Database setup
│   │   └── models/           # SQLAlchemy models matching Postgres schema
│   └── Dockerfile
├── ai_service/               # AI Model Service
│   ├── app/
│   │   ├── model/            # PyTorch Hierarchical Model Architecture
│   │   ├── pipelines/        # Urdu Pre-processing & PyArrow validation
│   │   ├── explainability/   # LIME & SHAP word importance attribution
│   │   ├── evaluation/       # Statistical tests, significance & reports
│   │   └── service.py        # Independent FastAPI inference web API
│   └── Dockerfile
├── frontend/                 # Next.js & Tailwind CSS Presentation Layer
│   ├── src/app/
│   │   ├── login/            # Authentication Interface
│   │   └── dashboard/        # Operator Command Centers (Live/Batch prediction, registry)
│   └── Dockerfile
├── database/
│   └── schema.sql            # Core PostgreSQL schema
├── prometheus/
│   └── prometheus.yml        # Metrics collector configurations
├── nginx.conf                # API Gateway Reverse Proxy & Rate Limiter
├── docker-compose.yml        # Multi-container local production compose
└── README.md
```

---

## Setup & Execution

### 1. Prerequisite Packages
Ensure you have Docker and Docker Compose installed.

### 2. Startup via Docker Compose
To build and spin up the complete microservice stack:
```bash
docker-compose up --build
```
This boots:
* **PostgreSQL** on port `5432` (Auto-initializes schema)
* **Redis** on port `6379`
* **AI Service** on port `8001`
* **FastAPI Gateway** on port `8000`
* **Next.js Frontend** on port `3000`
* **Prometheus Scraper** on port `9090`
* **Grafana Dashboards** on port `3001` (Mapping localhost:3000 internally)

---

## Core ML Model Design

AVIP utilizes a deep hierarchical classification network:
1. **Input text** -> tokenized using XLM-RoBERTa base tokenizer.
2. **XLM-RoBERTa Embeddings** -> maps tokens to contextual embedding spaces.
3. **BiLSTM layer** -> extracts forward and backward sequence order features.
4. **Multi-Head Self-Attention** -> extracts relative token activation weights.
5. **Class Heads**:
   * **Level 1**: Threat State (Violence / Non-Violence)
   * **Level 2**: Violence Category (Gender, Economic, Ethnic, Political, Religious, General)
   
*Note: If Level 1 predicts Non-Violence, Level 2 classification is bypassed entirely to reduce inference cost.*

---

## API Endpoints Reference

### Authentication
* `POST /api/v1/auth/register` - Registers a new system operator.
* `POST /api/v1/auth/login` - Authenticates and issues JWT token credentials.

### Machine Learning
* `POST /api/v1/predict` - Standard single post classification.
* `POST /api/v1/batch-predict` - Ingests lists of posts for high-throughput prediction.
* `POST /api/v1/explain` - Computes LIME and SHAP word attribution values and outputs attention mappings.
* `POST /api/v1/retrain` - Manually triggers model training and publishes metrics to MLflow.

### Health & Metrics
* `GET /api/v1/health` - Check health status.
* `GET /api/v1/metrics` - Fetch real-time memory, cpu, request latency, and data drift values.
* `GET /api/v1/model-info` - Fetch accuracy, F1 score, and versioning hashes of active models.

---

## Explainability Engines

AVIP implements multiple layers of Explainable AI (XAI):
* **LIME (Local Interpretable Model-agnostic Explanations)**: Perturbs input strings by randomly masking token arrays, fitting a weighted local linear model to calculate feature importance coefficients.
* **SHAP (SHapley Additive exPlanations)**: Uses a Leave-One-Out marginal contribution approximation for fast, scalable calculation of Shapley values.
* **Attention Activation Weights**: Extracts self-attention matrices from the attention layer, averaging across heads to render word activation intensities.
* **Natural Explanations**: Generates a bilingual summary (Urdu/English) detailing the primary trigger tokens influencing classification.
