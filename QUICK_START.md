# 🚀 Quick Reference - ML Pipeline Commands

## Environment Setup
```bash
cd c:\Users\mangeshd\Documents\Fraud-Detection-Mlops-poc
.\venv\Scripts\Activate.ps1
```

## ONE-LINE COMMANDS

### 1️⃣ Run Complete Pipeline (Recommended)
```bash
python -c "from src.pipelines.ml_pipeline import MLTrainingPipeline; MLTrainingPipeline().run()"
```
**Expected Output:**
- ✓ Model v1 registered in MLFlow
- ✓ Best model selected
- ✓ All metrics tracked

### 2️⃣ Start Prediction API
```bash
python src/api/service.py
```
**Access:** http://localhost:8000/docs

### 3️⃣ Run All Tests
```bash
pytest tests/test_ml_pipeline.py -v
```

### 4️⃣ Start MLFlow UI
```bash
mlflow ui
```
**Access:** http://localhost:5000

---

## INTERACTIVE RUNNER

```bash
python run_pipeline.py
```
**Menu Options:**
1. Complete pipeline
2. Data ingestion only
3. Feature engineering only
4. Feature consistency checks
5. Model training
6. Model comparison
7. Start API service
8. Run tests
9. Exit

---

## STEP-BY-STEP MANUAL

### Step 1: Feature Engineering
```bash
python -c """
import pandas as pd
from src.features.engineering import FeatureEngineer
import yaml

with open('src/config/config.yaml') as f:
    config = yaml.safe_load(f)

df = pd.read_parquet(config['data']['validated_path'])
engineer = FeatureEngineer(config)
df_eng = engineer.engineer_features(df)
df_scaled = engineer.scale_features(df_eng)
X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)
print('Features ready')
"""
```

### Step 2: Consistency Checks (Parity Verified)
```bash
python -c """
import pandas as pd
from src.features.engineering import FeatureEngineer
from src.features.consistency import FeatureConsistencyChecker
import yaml

with open('src/config/config.yaml') as f:
    config = yaml.safe_load(f)

df = pd.read_parquet(config['data']['validated_path'])
engineer = FeatureEngineer(config)
df_eng = engineer.engineer_features(df)

checker = FeatureConsistencyChecker(config)
valid, report = checker.check_feature_parity(df, df_eng)
print(f'Parity verified: {valid}')
"""
```

### Step 3: Model Training + MLFlow (Model v1)
```bash
python -c """
import pandas as pd
from src.features.engineering import FeatureEngineer
from src.models.training import ModelTrainer
import yaml

with open('src/config/config.yaml') as f:
    config = yaml.safe_load(f)

df = pd.read_parquet(config['data']['validated_path'])
engineer = FeatureEngineer(config)
df_eng = engineer.engineer_features(df)
df_scaled = engineer.scale_features(df_eng)
X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)

trainer = ModelTrainer(config)
results = trainer.train_all_models(X_train, X_test, y_train, y_test)
trainer.save_models('models')
print('Model v1 trained and registered')
"""
```

### Step 4: Model Comparison & Selection (Best Model)
```bash
python -c """
import json
from src.models.comparison import ModelComparator
import yaml

with open('src/config/config.yaml') as f:
    config = yaml.safe_load(f)

with open('models/metrics.json') as f:
    metrics = json.load(f)

comparator = ModelComparator(config)
rankings = comparator.get_model_rankings(metrics)
print(f'Best model: {rankings[0]["model"]}')
"""
```

### Step 5: FastAPI Service (Prediction API)
```bash
python -m uvicorn src.api.service:create_app --host 0.0.0.0 --port 8000 --reload
```
**Features:**
- http://localhost:8000/docs - Interactive docs
- http://localhost:8000/redoc - ReDoc
- POST /predict - Single prediction
- POST /predict_batch - Batch predictions

---

## PREDICTION EXAMPLES

### Single Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "Time": 0,
    "Amount": 149.62,
    "V1": -1.3598071336738,
    "V2": -0.0727812121200,
    "V3": 2.3365864637038,
    ... (add all V1-V28 fields)
    "V28": 0.22007563606245
  }'
```

### Batch Predictions
```bash
curl -X POST "http://localhost:8000/predict_batch" \
  -H "Content-Type: application/json" \
  -d '{
    "transactions": [
      { "Time": 0, "Amount": 149.62, ... },
      { "Time": 1, "Amount": 242.00, ... }
    ]
  }'
```

---

## FILE LOCATIONS

| Component | File |
|-----------|------|
| Feature Engineering | `src/features/engineering.py` |
| Consistency Checks | `src/features/consistency.py` |
| Model Training | `src/models/training.py` |
| Model Selection | `src/models/comparison.py` |
| FastAPI Service | `src/api/service.py` |
| ML Pipeline | `src/pipelines/ml_pipeline.py` |
| Configuration | `src/config/config.yaml` |
| Tests | `tests/test_ml_pipeline.py` |

---

## OUTPUT LOCATIONS

| Output | Location |
|--------|----------|
| Validated Data | `data/validated/creditcard_validated.parquet` |
| Consistency Report | `data/validated/feature_consistency_report.json` |
| Models (PKL) | `models/*.pkl` |
| Metrics | `models/metrics.json` |
| Model Comparison | `models/model_comparison_report.json` |
| Model Info | `models/model_info.json` |
| MLFlow Artifacts | `artifacts/` |

---

## MONITORING & DEBUGGING

### Check Model Status
```bash
ls -la models/
```

### View MLFlow Experiments
```bash
# Browser: http://localhost:5000
```

### Check API Health
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# Logs printed to console during execution
# All timestamps and levels shown
```

---

## TROUBLESHOOTING

### Port 8000 in use
```bash
python -m uvicorn src.api.service:create_app --port 8001
```

### MLFlow connection failed
```bash
mlflow server --backend-store-uri sqlite:///mlflow.db
```

### Model not found
```bash
# Run model training first
python run_pipeline.py  # Select option 5
```

### Import errors
```bash
pip install -r requirements.txt
```

---

## QUICK VERIFICATION

```bash
# 1. Check config
python -c "import yaml; print(yaml.safe_load(open('src/config/config.yaml'))['model'])"

# 2. Check data
python -c "import pandas as pd; print(pd.read_parquet('data/validated/creditcard_validated.parquet').shape)"

# 3. Check models
python -c "import os; print(os.listdir('models/'))"

# 4. Check API
python -c "from src.api.service import PredictionAPI; print('API imports OK')"
```

---

## PERFORMANCE TIPS

- **Faster training:** Use fewer models in config
- **Faster predictions:** Use batch API endpoint
- **Better models:** Increase hyperparameter tuning
- **Lower memory:** Reduce dataset size in testing

---

## VERSION INFO

- **Python:** 3.8+
- **Pipeline:** v1.0
- **Model Registry:** fraud-detection-v1
- **API Version:** 1.0.0
- **MLFlow:** 2.10.2+

---

## DOCUMENTATION

- **Complete Guide:** `ML_PIPELINE_COMPLETE.md`
- **Build Summary:** `BUILD_SUMMARY.md`
- **This File:** `QUICK_START.md`

---

**Status:** READY TO USE

Enjoy your ML pipeline! 🚀
