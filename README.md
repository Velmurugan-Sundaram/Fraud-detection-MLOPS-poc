# Fraud Detection MLOps Production System

## Overview

This is a production-grade MLOps platform for credit card fraud detection implementing end-to-end machine learning lifecycle with drift detection, canary deployments, and comprehensive monitoring.

### Core Components

- **Data Pipeline**: Automated ingestion, validation, profiling with quality checks
- **Model Training**: Multi-model approach (LogisticRegression, RandomForest, XGBoost, LightGBM) with SMOTE
- **Feature Engineering**: 12+ engineered features with automated consistency validation
- **Model Registry**: Version control with audit trails and rollback capability
- **Drift Detection**: K-S statistical testing with automated alerting
- **Deployment**: Canary deployment pattern with Nginx load balancing (95%/5% split)
- **Monitoring**: Prometheus metrics + Grafana dashboards + Alertmanager
- **API**: FastAPI service with batch prediction capability

## Quick Start

### 1. Setup Environment

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 2. Run Data Pipeline

```bash
python run_pipeline.py
```

This executes:
- Data ingestion from CSV
- Data validation and profiling
- Feature engineering
- Feature consistency checks
- Train/test split with stratification

### 3. Train Models

```bash
python run_pipeline.py
# Select: 2 - Train Models (XGBoost, LightGBM, etc.)
```

Models are trained with:
- Class imbalance handling (SMOTE)
- Cross-validation
- Hyperparameter tuning
- MLFlow experiment tracking

### 4. Run Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

## Project Structure

```
fraud-detection-mlops-poc/
├── src/
│   ├── api/
│   │   ├── service.py              # FastAPI application
│   │   └── metrics.py              # Prometheus instrumentation
│   ├── config/
│   │   └── config.yaml             # Configuration settings
│   ├── features/
│   │   ├── engineering.py          # Feature creation (12+ features)
│   │   └── consistency.py          # Feature validation
│   ├── ingestion/
│   │   ├── loader.py               # Data loading
│   │   ├── validator.py            # Data validation rules
│   │   ├── profiler.py             # Data profiling
│   │   └── pipeline.py             # Orchestration
│   ├── models/
│   │   ├── training.py             # Model training (v1)
│   │   ├── train_v2.py             # Enhanced training (v2)
│   │   ├── comparison.py           # Model comparison
│   │   ├── drift_detection.py      # K-S test implementation
│   │   ├── rollback.py             # Version rollback
│   │   └── registry.py             # Model registry & audit
│   ├── pipelines/
│   │   └── ml_pipeline.py          # End-to-end orchestrator
│   └── utils/
│       ├── constants.py            # Configuration constants
│       └── logger.py               # Logging setup
├── tests/
│   ├── test_ingestion.py           # Data pipeline tests
│   └── test_ml_pipeline.py         # MLOps workflow tests
├── .github/workflows/
│   ├── deploy-v1.yml               # Production deployment
│   ├── train-v2.yml                # Model training workflow
│   ├── deploy-canary.yml           # Canary deployment
│   ├── drift-detection.yml         # Drift monitoring
│   └── rollback.yml                # Emergency rollback
├── dataset/
│   └── creditcard.csv              # Training dataset
├── data/
│   ├── raw/                        # Ingested data
│   └── validated/                  # Validated data
├── models/
│   ├── v1/                         # Production models
│   └── v2/                         # Canary models
├── docker-compose.yml              # Multi-service orchestration
├── Dockerfile                      # Container image
├── requirements.txt                # Python dependencies
└── run_pipeline.py                 # Interactive pipeline runner
```

## Data Pipeline

### Stage 1: Ingestion
- Loads creditcard.csv
- Detects data types
- Generates profile report
- Output: `data/raw/creditcard.parquet`

### Stage 2: Validation
- Rule-based validation (nulls, ranges, types)
- Statistical profiling
- Quality scoring
- Output: `data/validated/creditcard_validated.parquet`

### Stage 3: Feature Engineering
Creates 12+ features:
- Statistical features (mean, std, quantiles)
- Temporal features (transaction frequency, velocity)
- Categorical encodings
- Normalization via StandardScaler

### Stage 4: Consistency Validation
- Feature parity checks between datasets
- Distribution comparison
- Correlation validation

## Model Training

### Multi-Model Approach
- LogisticRegression: Baseline, interpretable
- RandomForest: Ensemble baseline
- XGBoost: Gradient boosting (primary model)
- LightGBM: Fast gradient boosting alternative

### Key Features
- SMOTE for class imbalance handling
- Stratified k-fold cross-validation
- Hyperparameter tuning with grid search
- Comprehensive metrics: Precision, Recall, F1, ROC-AUC
- MLFlow experiment tracking

### Sample Metrics
- XGBoost F1-Score: 0.7319
- LightGBM F1-Score: 0.7298
- RandomForest F1-Score: 0.7121
- LogisticRegression F1-Score: 0.6821

## Model Registry & Versioning

### Registry Features
- Version tracking (v1, v2, v3...)
- Training timestamp and parameters
- Performance metrics
- Model artifacts storage

### Rollback Capability
- Maintains 10 model versions
- One-click rollback via GitHub Actions
- Version history with complete metadata
- Audit trail (JSON + CSV export)

## Drift Detection

### K-Kolmogorov-Smirnov Testing
- Statistic threshold: K-S > 0.1 triggers alert
- Feature-level drift analysis
- Prediction distribution drift
- Runs every 6 hours (cron schedule)

### Automated Response
- Alert on detected drift
- Triggers investigation workflow
- Recommends model retraining
- Logs comprehensive statistics

## Canary Deployment

### Traffic Split
- Stable v1.0.0: 95% traffic
- Canary v2.0.0: 5% traffic
- Nginx reverse proxy with consistent hashing
- 24-48 hour evaluation period

### Success Criteria
- No critical alerts from Prometheus
- Accuracy within 2% of stable model
- Latency within +100ms
- Error rate < 1% increase

### Automatic Promotion
- Manual review after monitoring period
- Roll back on critical alerts
- Full production deployment on success

## Monitoring & Observability

### Prometheus Metrics
- Request count, duration, errors
- Model predictions (fraud/legitimate)
- Feature statistics
- Data quality scores

### Grafana Dashboard
- 10+ visualization panels
- Real-time model performance
- Data distribution monitoring
- Alert status display

### Alertmanager Rules
- High error rate (>1% for 5 min)
- Latency spike (+200ms)
- Drift detection (K-S > 0.1)
- No predictions (model offline)

## API Endpoints

### Service Interface

```
GET  /health                    # Health check
POST /predict                   # Single prediction
POST /predict_batch            # Batch predictions
GET  /model_info               # Model metadata
GET  /metrics                  # Prometheus metrics
```

### Prediction Response

```json
{
  "prediction": 1,
  "probability": 0.87,
  "model_version": "v2.1.0",
  "timestamp": "2024-01-15T10:30:45Z"
}
```

## Docker Deployment

### Build & Run

```bash
docker build -t fraud-detection:latest .
docker run -p 8000:8000 fraud-detection:latest
```

### Docker Compose (Full Stack)

```bash
docker-compose up -d
```

Services:
- FastAPI (port 8000)
- Prometheus (port 9090)
- Grafana (port 3000)
- Nginx (port 80/443)

## GitHub Actions Workflows

### 1. deploy-v1.yml
Triggers on: Manual dispatch
- Deploys stable production model
- Updates Docker image
- Registers in model registry
- Verifies API health

### 2. train-v2.yml
Triggers on: Manual dispatch
- Trains v2 models
- Compares with baseline
- Archives if improved
- Runs automated tests

### 3. deploy-canary.yml
Triggers on: Manual dispatch
- Deploys v2 as canary (5%)
- Configures Nginx split
- Activates monitoring
- Sets up alerting

### 4. drift-detection.yml
Triggers on: Scheduled (every 6 hours)
- Analyzes feature distributions
- Compares model outputs
- Reports drift statistics
- Triggers alerts if K-S > 0.1

### 5. rollback.yml
Triggers on: Manual dispatch
- Reverts to previous model version
- Stops current canary
- Records event in audit trail
- Validates health checks

## Configuration

### config.yaml

```yaml
data:
  path: dataset/creditcard.csv
  test_size: 0.2
  random_state: 42

models:
  xgboost:
    max_depth: 6
    learning_rate: 0.1
    n_estimators: 100
  
  lightgbm:
    num_leaves: 31
    learning_rate: 0.05
    n_estimators: 100

drift_detection:
  ks_threshold: 0.1
  check_frequency_hours: 6
```

## Performance Benchmarks

### Training Time
- Data Pipeline: 15-20 seconds
- Model Training (4 models): 2-3 minutes
- Full Pipeline: ~5 minutes

### Model Performance
- Dataset: 284,807 transactions, 0.17% fraud rate
- Test set: 71,202 transactions
- Best Model: XGBoost F1 = 0.7319

### Inference
- Single prediction: <5ms
- Batch (100): <50ms
- API response: <100ms (p95)

## Troubleshooting

### Model Training Fails

```bash
# Check if models directory exists
mkdir -p models/v1 models/v2

# Verify Python version
python --version  # Should be 3.10+

# Check dependencies
pip list | grep -E "xgboost|lightgbm|scikit"
```

### Drift Detection Issues

```bash
# Verify validated data exists
ls -la data/validated/

# Check drift thresholds
cat src/utils/constants.py | grep KS_THRESHOLD
```

### API Not Responding

```bash
# Check if FastAPI is running
curl http://localhost:8000/health

# View logs
docker logs fraud-detection-api
```

## Development Guidelines

### Code Organization
- Modular design with clear separation of concerns
- Type hints for better IDE support
- Comprehensive logging with proper levels
- Error handling with meaningful messages

### Testing Requirements
- Unit tests for data validation
- Integration tests for ML pipeline
- Minimum 80% code coverage
- Automated tests in CI/CD

### Deployment Checklist
- All tests passing
- No unresolved alerts
- Model performance baseline verified
- Rollback plan documented

## Production Deployment Steps

1. **Prepare Model**
   - Train and validate v2 models
   - Compare metrics with v1
   - Archive if F1 score improved

2. **Canary Deployment**
   - Deploy v2 to 5% traffic
   - Monitor for 24-48 hours
   - Track drift, latency, errors

3. **Full Rollout**
   - Promote to 100% traffic
   - Update documentation
   - Archive old model version

4. **Ongoing Monitoring**
   - Daily drift detection checks
   - Alert on performance degradation
   - Quarterly model retraining

## Key Technologies

- **Python 3.10+**: Core language
- **XGBoost & LightGBM**: Model training
- **Scikit-learn**: ML utilities
- **Pandas & NumPy**: Data processing
- **FastAPI**: API framework
- **Prometheus**: Metrics collection
- **Grafana**: Dashboard visualization
- **Docker**: Containerization
- **GitHub Actions**: CI/CD automation

## Maintenance

### Regular Tasks
- Monitor drift detection alerts
- Review model performance metrics
- Update dependencies monthly
- Analyze API latency trends
- Audit model registry

### Annual Review
- Retrain on latest data
- Evaluate new model architectures
- Update feature engineering
- Review alert thresholds
- Capacity planning

## License

This project is provided as-is for educational and commercial use.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Enable debug logging in config.yaml
4. Consult model registry audit trail
