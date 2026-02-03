# STEP 1: Data Injection & Validation - Detailed Implementation Guide

## Objective
Establish a robust data ingestion pipeline with comprehensive validation checks to ensure data quality before downstream processing.

---

## Architecture for Step 1

```
┌──────────────────┐
│  CSV Dataset     │
│ (kaggle)         │
└────────┬─────────┘
         │
         ↓
┌──────────────────────────────────┐
│  1. Load & Parse Data            │
│  (pandas, pyarrow)               │
└────────┬─────────────────────────┘
         │
         ↓
┌──────────────────────────────────┐
│  2. Schema Validation            │
│  (check columns, dtypes)         │
└────────┬─────────────────────────┘
         │
         ↓
┌──────────────────────────────────┐
│  3. Data Quality Checks          │
│  (Great Expectations)            │
│  - Completeness                  │
│  - Duplicates                    │
│  - Null values                   │
│  - Type compliance               │
│  - Value ranges                  │
│  - Distribution anomalies        │
└────────┬─────────────────────────┘
         │
         ↓
┌──────────────────────────────────┐
│  4. Data Profiling               │
│  (statistics, distributions)     │
└────────┬─────────────────────────┘
         │
         ↓
┌──────────────────────────────────┐
│  5. Data Versioning (DVC)        │
│  Track dataset versions          │
└────────┬─────────────────────────┘
         │
         ↓
┌──────────────────────────────────┐
│  6. Store in Data Lake           │
│  (Parquet format + metadata)     │
└──────────────────────────────────┘
```

---

## Components to Implement

### 1. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install pandas pyarrow great-expectations dvc dvc-s3 sqlalchemy sqlite3 pyyaml
pip install pandas-profiler evidentlyai
```

### 2. **Project Structure**

```
fraud-detection-mlops-poc/
├── data/
│   ├── raw/                    # Original dataset
│   ├── validated/              # After validation
│   └── processed/              # For modeling
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   └── config.yaml         # Configuration
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py           # Data loader
│   │   ├── validator.py        # Data validation
│   │   └── profiler.py         # Data profiling
│   └── utils/
│       ├── __init__.py
│       ├── logger.py           # Logging
│       └── constants.py        # Constants
├── tests/
│   ├── test_ingestion.py
│   └── test_validation.py
├── .dvc/                       # DVC directory (auto-created)
├── .gitignore
├── dvc.yaml                    # DVC pipeline
├── requirements.txt
└── README.md
```

---

## Implementation Details

### **Phase 1: Configuration Setup**

**File: `src/config/config.yaml`**
```yaml
# Data Configuration
data:
  raw_path: "data/raw/creditcard.csv"
  validated_path: "data/validated/creditcard_validated.parquet"
  
# Schema Definition
schema:
  columns:
    Time: int64
    V1: float64
    V2: float64
    # ... V3 to V28
    Amount: float64
    Class: int64
  
  # Validation Rules
  validation:
    Time:
      min: 0
      nullable: false
    Amount:
      min: 0
      nullable: false
    Class:
      values: [0, 1]
      nullable: false

# Quality Thresholds
quality:
  min_completeness: 0.95    # 95% non-null
  max_duplicates: 0.01      # <1% duplicates
  outlier_threshold: 3.0    # 3-sigma
```

---

### **Phase 2: Data Loader**

**File: `src/ingestion/loader.py`**
```python
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DataLoader:
    """Load and parse data from multiple sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.raw_path = config['data']['raw_path']
    
    def load_csv(self) -> pd.DataFrame:
        """Load CSV with error handling"""
        try:
            logger.info(f"Loading data from {self.raw_path}")
            df = pd.read_csv(self.raw_path)
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            return df
        except FileNotFoundError:
            logger.error(f"File not found: {self.raw_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise
    
    def load_parquet(self, path: str) -> pd.DataFrame:
        """Load Parquet file"""
        try:
            logger.info(f"Loading parquet from {path}")
            return pd.read_parquet(path)
        except Exception as e:
            logger.error(f"Error loading parquet: {e}")
            raise
    
    def save_parquet(self, df: pd.DataFrame, output_path: str) -> None:
        """Save DataFrame as Parquet"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(output_path, index=False, compression='snappy')
            logger.info(f"Saved {len(df)} rows to {output_path}")
        except Exception as e:
            logger.error(f"Error saving parquet: {e}")
            raise
```

---

### **Phase 3: Schema Validator**

**File: `src/ingestion/validator.py`**
```python
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from great_expectations.core.batch import RuntimeBatchRequest
import great_expectations as ge

logger = logging.getLogger(__name__)

class SchemaValidator:
    """Validate data schema and quality"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.schema = config['schema']['columns']
        self.quality_rules = config['quality']
    
    def validate_schema(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Check column names and types"""
        errors = []
        
        # Check columns exist
        expected_cols = set(self.schema.keys())
        actual_cols = set(df.columns)
        
        missing = expected_cols - actual_cols
        extra = actual_cols - expected_cols
        
        if missing:
            errors.append(f"Missing columns: {missing}")
        if extra:
            errors.append(f"Extra columns: {extra}")
        
        # Check dtypes (with tolerance)
        for col, expected_type in self.schema.items():
            if col in df.columns:
                actual_type = df[col].dtype
                # Convert string type to numpy dtype
                try:
                    expected_np_type = np.dtype(expected_type)
                    if not np.issubdtype(actual_type, expected_np_type):
                        errors.append(
                            f"Column {col}: expected {expected_type}, "
                            f"got {actual_type}"
                        )
                except:
                    pass
        
        success = len(errors) == 0
        if success:
            logger.info("✓ Schema validation passed")
        else:
            logger.error(f"✗ Schema validation failed: {errors}")
        
        return success, errors
    
    def validate_quality(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Run quality checks"""
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'checks': {}
        }
        
        # 1. Completeness check
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        report['checks']['completeness'] = {
            'value': completeness,
            'threshold': self.quality_rules['min_completeness'],
            'passed': completeness >= self.quality_rules['min_completeness']
        }
        
        # 2. Duplicates check
        duplicate_ratio = df.duplicated().sum() / len(df)
        report['checks']['duplicates'] = {
            'value': duplicate_ratio,
            'threshold': self.quality_rules['max_duplicates'],
            'passed': duplicate_ratio <= self.quality_rules['max_duplicates']
        }
        
        # 3. Null values per column
        null_report = {}
        for col in df.columns:
            null_pct = df[col].isnull().sum() / len(df)
            null_report[col] = null_pct
        report['checks']['nulls_per_column'] = null_report
        
        # 4. Numeric columns - range & outliers
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_report = {}
        for col in numeric_cols:
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outlier_count = (z_scores > self.quality_rules['outlier_threshold']).sum()
            outlier_report[col] = {
                'count': int(outlier_count),
                'percentage': (outlier_count / len(df)) * 100
            }
        report['checks']['outliers'] = outlier_report
        
        # 5. Class distribution (for target variable)
        if 'Class' in df.columns:
            class_dist = df['Class'].value_counts(normalize=True).to_dict()
            report['checks']['class_distribution'] = class_dist
            report['checks']['class_imbalance_ratio'] = class_dist.get(1, 0) / (class_dist.get(0, 1) + 0.0001)
        
        # Overall pass/fail
        all_checks_passed = all(
            check.get('passed', True) 
            for check in report['checks'].values() 
            if isinstance(check, dict) and 'passed' in check
        )
        
        return all_checks_passed, report
```

---

### **Phase 4: Data Profiler**

**File: `src/ingestion/profiler.py`**
```python
import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DataProfiler:
    """Generate comprehensive data profile"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed data profile"""
        profile = {
            'metadata': {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024
            },
            'columns': {}
        }
        
        for col in df.columns:
            col_profile = {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': float(df[col].isnull().sum() / len(df) * 100),
                'unique_values': int(df[col].nunique()),
                'unique_percentage': float(df[col].nunique() / len(df) * 100)
            }
            
            # For numeric columns
            if np.issubdtype(df[col].dtype, np.number):
                col_profile.update({
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'std': float(df[col].std()),
                    'q25': float(df[col].quantile(0.25)),
                    'q75': float(df[col].quantile(0.75)),
                    'skewness': float(df[col].skew()),
                    'kurtosis': float(df[col].kurtosis())
                })
            
            # For categorical columns
            else:
                col_profile['top_values'] = df[col].value_counts().head(5).to_dict()
            
            profile['columns'][col] = col_profile
        
        return profile
    
    def save_profile(self, profile: Dict[str, Any], output_path: str) -> None:
        """Save profile as JSON"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(profile, f, indent=2)
        logger.info(f"Profile saved to {output_path}")
```

---

### **Phase 5: Main Ingestion Pipeline**

**File: `src/ingestion/pipeline.py`**
```python
import yaml
import logging
from pathlib import Path
from .loader import DataLoader
from .validator import SchemaValidator
from .profiler import DataProfiler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    """Main data ingestion orchestrator"""
    
    def __init__(self, config_path: str = "src/config/config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.loader = DataLoader(self.config)
        self.validator = SchemaValidator(self.config)
        self.profiler = DataProfiler(self.config)
    
    def run(self) -> None:
        """Execute full ingestion pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Data Ingestion Pipeline")
        logger.info("=" * 60)
        
        # Step 1: Load data
        logger.info("\n[1/5] Loading data...")
        df = self.loader.load_csv()
        logger.info(f"✓ Loaded {len(df)} rows")
        
        # Step 2: Validate schema
        logger.info("\n[2/5] Validating schema...")
        schema_valid, schema_errors = self.validator.validate_schema(df)
        if not schema_valid:
            logger.error("Schema validation failed!")
            raise ValueError(f"Schema errors: {schema_errors}")
        
        # Step 3: Validate quality
        logger.info("\n[3/5] Running quality checks...")
        quality_valid, quality_report = self.validator.validate_quality(df)
        self._log_quality_report(quality_report)
        
        if not quality_valid:
            logger.warning("Some quality checks failed, but continuing...")
        
        # Step 4: Profile data
        logger.info("\n[4/5] Profiling data...")
        profile = self.profiler.profile(df)
        profile_path = "data/validated/profile.json"
        self.profiler.save_profile(profile, profile_path)
        logger.info(f"✓ Profile saved to {profile_path}")
        
        # Step 5: Save validated data
        logger.info("\n[5/5] Saving validated data...")
        output_path = self.config['data']['validated_path']
        self.loader.save_parquet(df, output_path)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Data Ingestion Pipeline Completed Successfully!")
        logger.info("=" * 60)
        
        return df
    
    def _log_quality_report(self, report: dict) -> None:
        """Pretty print quality report"""
        print("\nData Quality Report:")
        print(f"  Total Rows: {report['total_rows']}")
        print(f"  Total Columns: {report['total_columns']}")
        
        checks = report['checks']
        print("\n  Checks:")
        
        if 'completeness' in checks:
            c = checks['completeness']
            status = "✓" if c['passed'] else "✗"
            print(f"    {status} Completeness: {c['value']:.2%} (threshold: {c['threshold']:.2%})")
        
        if 'duplicates' in checks:
            d = checks['duplicates']
            status = "✓" if d['passed'] else "✗"
            print(f"    {status} Duplicates: {d['value']:.2%} (threshold: {d['threshold']:.2%})")
        
        if 'class_imbalance_ratio' in checks:
            print(f"    Class Imbalance Ratio (1/0): {checks['class_imbalance_ratio']:.4f}")
        
        if 'class_distribution' in checks:
            dist = checks['class_distribution']
            print(f"    Class Distribution: {dist}")

# Main execution
if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    df = pipeline.run()
```

---

### **Phase 6: Unit Tests**

**File: `tests/test_ingestion.py`**
```python
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import yaml

from src.ingestion.loader import DataLoader
from src.ingestion.validator import SchemaValidator
from src.ingestion.profiler import DataProfiler

# Create test config
@pytest.fixture
def test_config():
    return {
        'data': {
            'raw_path': 'data/raw/creditcard.csv',
            'validated_path': 'data/validated/creditcard_validated.parquet'
        },
        'schema': {
            'columns': {
                'Time': 'int64',
                'V1': 'float64',
                'Amount': 'float64',
                'Class': 'int64'
            }
        },
        'quality': {
            'min_completeness': 0.95,
            'max_duplicates': 0.01,
            'outlier_threshold': 3.0
        }
    }

@pytest.fixture
def sample_df():
    """Create sample dataframe"""
    return pd.DataFrame({
        'Time': [0, 1, 2, 3, 4],
        'V1': [1.0, 2.0, 3.0, 4.0, 5.0],
        'Amount': [100.0, 200.0, 300.0, 400.0, 500.0],
        'Class': [0, 0, 0, 0, 1]
    })

def test_schema_validator(test_config, sample_df):
    """Test schema validation"""
    validator = SchemaValidator(test_config)
    is_valid, errors = validator.validate_schema(sample_df)
    assert is_valid
    assert len(errors) == 0

def test_quality_validation(test_config, sample_df):
    """Test quality checks"""
    validator = SchemaValidator(test_config)
    is_valid, report = validator.validate_quality(sample_df)
    assert 'completeness' in report['checks']
    assert 'duplicates' in report['checks']

def test_data_profiler(test_config, sample_df):
    """Test data profiling"""
    profiler = DataProfiler(test_config)
    profile = profiler.profile(sample_df)
    assert profile['metadata']['rows'] == 5
    assert profile['metadata']['columns'] == 4
    assert 'Time' in profile['columns']

def test_data_loader_parquet(test_config, sample_df):
    """Test parquet save/load"""
    loader = DataLoader(test_config)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = f"{tmpdir}/test.parquet"
        loader.save_parquet(sample_df, output_path)
        
        loaded_df = loader.load_parquet(output_path)
        assert len(loaded_df) == len(sample_df)
        assert list(loaded_df.columns) == list(sample_df.columns)
```

---

## DVC Configuration for Data Versioning

**File: `dvc.yaml`**
```yaml
stages:
  data_ingestion:
    cmd: python -c "from src.ingestion.pipeline import DataIngestionPipeline; pipeline = DataIngestionPipeline(); pipeline.run()"
    deps:
      - data/raw/creditcard.csv
      - src/ingestion/
    outs:
      - data/validated/creditcard_validated.parquet:
          cache: true
    metrics:
      - data/validated/profile.json:
          cache: false
```

---

## Quick Start Commands

```bash
# 1. Set up environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Initialize DVC
dvc init

# 3. Run ingestion pipeline
python -c "from src.ingestion.pipeline import DataIngestionPipeline; p = DataIngestionPipeline(); p.run()"

# 4. Run tests
pytest tests/ -v

# 5. Version data with DVC
dvc add data/validated/creditcard_validated.parquet
git add data/validated/creditcard_validated.parquet.dvc
git commit -m "Add validated dataset v1"
```

---

## Expected Outputs

After running STEP 1, you should have:

1. ✓ **Validated Dataset:** `data/validated/creditcard_validated.parquet`
2. ✓ **Data Profile:** `data/validated/profile.json`
3. ✓ **Quality Report:** Console output with validation results
4. ✓ **DVC Tracking:** `data/validated/creditcard_validated.parquet.dvc`
5. ✓ **Unit Tests:** All passing

---

## Success Criteria

- [ ] All rows successfully ingested
- [ ] Schema validation passes
- [ ] Data quality report generated
- [ ] 95%+ completeness achieved
- [ ] <1% duplicates
- [ ] Data versioned in DVC
- [ ] All unit tests pass
- [ ] No critical data quality issues

---

## Next Step

Once Step 1 is complete, proceed to **STEP 2: Data Profiling & Feature Engineering**

See `STEP2_DATA_PROFILING.md`
