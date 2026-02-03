# MLOps POC for Fraud Detection - Quick Start Guide

## 📋 Overview

This project implements a complete MLOps pipeline for credit card fraud detection with the following principles:
- **End-to-End MLOps Lifecycle** - Full pipeline from data to production
- **Production-Grade Concerns** - Drift detection, rollback, canary deployments, observability
- **Open-Source Stack** - Cost-effective tools (no expensive cloud services)
- **Hybrid ML Approach** - Classical ML + anomaly detection + streaming capability

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or: source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Data Ingestion Pipeline (STEP 1)

```bash
# Run the complete data ingestion and validation pipeline
python -c "from src.ingestion.pipeline import DataIngestionPipeline; p = DataIngestionPipeline(); p.run()"
```

**Expected Output:**
- ✓ Validated dataset: `data/validated/creditcard_validated.parquet`
- ✓ Data profile: `data/validated/profile.json`
- ✓ Quality report with statistics

### 3. Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src --cov-report=html
```

## 📁 Project Structure

```
fraud-detection-mlops-poc/
├── dataset/                       # Original Kaggle dataset
│   └── creditcard.csv
├── data/
│   ├── raw/                      # Raw data (before processing)
│   └── validated/                # Validated data (after Step 1)
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.yaml           # Configuration file
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py             # Data loading
│   │   ├── validator.py          # Data validation
│   │   ├── profiler.py           # Data profiling
│   │   └── pipeline.py           # Main pipeline
│   └── utils/
│       ├── __init__.py
│       ├── logger.py             # Logging setup
│       └── constants.py          # Constants
├── tests/
│   └── test_ingestion.py         # Unit tests
├── .dvc/                         # DVC configuration
├── .dvcignore                    # DVC ignore rules
├── .gitignore                    # Git ignore rules
├── dvc.yaml                      # DVC pipeline definition
├── requirements.txt              # Python dependencies
├── MLOPS_APPROACH.md            # Full MLOps strategy document
├── STEP1_DATA_INJECTION.md      # Step 1 detailed guide
└── README.md                     # This file
```

## 📊 Dataset Information

**Kaggle Credit Card Fraud Detection Dataset**

```
Rows:      284,807 transactions
Columns:   31 features
Features:  Time (seconds), V1-V28 (PCA-transformed), Amount, Class
Target:    Class (0=legitimate, 1=fraud)
Imbalance: ~0.17% fraud rate (highly imbalanced)
```

### Schema
- `Time` (int): Seconds elapsed since first transaction
- `V1-V28` (float): PCA-transformed features (for privacy)
- `Amount` (float): Transaction amount in dollars
- `Class` (int): 0 (legitimate) or 1 (fraud)

## 🔄 MLOps Pipeline Stages

### ✅ STEP 1: Data Injection & Validation (CURRENT)
**Status:** Implementation files ready

**Components:**
- CSV data loading
- Schema validation (30 features, dtypes check)
- Data quality checks (completeness, duplicates, outliers)
- Data profiling (statistics, distributions)
- DVC versioning

**Outputs:**
- Validated Parquet file
- Data quality report
- Statistical profile

**See:** [STEP1_DATA_INJECTION.md](STEP1_DATA_INJECTION.md)

---

### ⏳ STEP 2: Data Profiling & Feature Engineering
**Features:** EDA, statistical analysis, feature selection, class imbalance handling

### ⏳ STEP 3: Governance & Lineage Tracking
**Features:** Data lineage, model registry, audit trails, compliance

### ⏳ STEP 4: Model Training & Experimentation
**Models:** Logistic Regression, Random Forest, XGBoost, Isolation Forest

### ⏳ STEP 5: Model Evaluation & Registry
**Features:** Metrics comparison, threshold tuning, model versioning

### ⏳ STEP 6: Deployment & Orchestration
**Features:** Canary deployment, A/B testing, automatic rollback

### ⏳ STEP 7: Inference & Serving
**Features:** Real-time API, batch scoring, low-latency inference

### ⏳ STEP 8: Monitoring & Observability
**Features:** Drift detection, alerts, auto-retraining, self-healing

---

## 🛠️ Tools & Technologies

| Layer | Tools |
|-------|-------|
| **Data Processing** | pandas, pyarrow, NumPy |
| **Data Quality** | Great Expectations, Pandas Profiler, Evidentlyai |
| **Data Versioning** | DVC |
| **Experiment Tracking** | MLflow |
| **Model Training** | scikit-learn, XGBoost, LightGBM |
| **Hyperparameter Tuning** | Optuna |
| **API Serving** | FastAPI |
| **Containerization** | Docker |
| **Orchestration** | Airflow / Prefect |
| **Monitoring** | Prometheus, Grafana |
| **Stream Processing** | Apache Kafka, Spark (optional) |

---

## 📈 Configuration

Edit `src/config/config.yaml` to customize:

```yaml
data:
  raw_path: "dataset/creditcard.csv"
  validated_path: "data/validated/creditcard_validated.parquet"

quality:
  min_completeness: 0.95      # 95% non-null requirement
  max_duplicates: 0.01        # <1% duplicates
  outlier_threshold: 3.0      # 3-sigma
```

---

## 🧪 Testing

Run the test suite:

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/test_ingestion.py::test_schema_validator -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

---

## 🗂️ Data Versioning with DVC

```bash
# Initialize DVC (one-time)
dvc init

# Track validated data
dvc add data/validated/creditcard_validated.parquet

# Commit to git
git add data/validated/creditcard_validated.parquet.dvc
git commit -m "Add validated dataset v1.0"

# View data history
dvc dag
```

---

## 📝 Configuration Files

### `src/config/config.yaml`
Main configuration file defining:
- Data paths
- Schema definition
- Quality thresholds
- Validation rules

### `.gitignore`
Excludes:
- Virtual environments
- Cached data
- Model artifacts
- IDE files

### `.dvcignore`
Prevents DVC from tracking:
- Processed data folders
- Temporary files

---

## 🎯 Success Metrics (STEP 1)

- [ ] All rows successfully ingested
- [ ] Schema validation passes (all 30 columns with correct types)
- [ ] Data quality report generated
- [ ] ≥95% completeness achieved
- [ ] <1% duplicates detected
- [ ] Data versioned in DVC
- [ ] All unit tests pass (6/6)
- [ ] No null values in Class column
- [ ] Class imbalance ratio documented (~0.17%)

---

## 🚨 Troubleshooting

### Issue: "File not found" error
```bash
# Make sure dataset is in the right location
ls dataset/creditcard.csv
```

### Issue: Import errors
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Issue: YAML parsing error
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('src/config/config.yaml'))"
```

---

## 📚 Next Steps

1. ✅ Complete STEP 1: Data Injection & Validation
2. → Proceed to STEP 2: Data Profiling & Feature Engineering
3. → STEP 3: Governance & Lineage Tracking
4. → STEP 4: Model Training & Experimentation
5. → STEP 5: Model Evaluation & Registry
6. → STEP 6: Deployment & Orchestration
7. → STEP 7: Inference & Serving
8. → STEP 8: Monitoring & Observability

---

## 📖 Documentation

- [MLOPS_APPROACH.md](MLOPS_APPROACH.md) - Complete MLOps strategy and architecture
- [STEP1_DATA_INJECTION.md](STEP1_DATA_INJECTION.md) - Step 1 detailed implementation
- [README.md](README.md) - This file

---

## 📞 Support

For issues or questions:
1. Check the documentation files
2. Review the test cases in `tests/`
3. Check the configuration in `src/config/config.yaml`
4. Review logs for detailed error messages

---

## 📄 License

MLOps POC - Educational & Research Purpose

---

**Created:** 2024  
**Purpose:** Credit Card Fraud Detection with Production-Grade MLOps  
**Dataset:** Kaggle - Credit Card Fraud Detection