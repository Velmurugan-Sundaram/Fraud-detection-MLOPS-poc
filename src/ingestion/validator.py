"""Data validation module"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class SchemaValidator:
    """Validate data schema and quality"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration"""
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
        
        # Check dtypes (with numeric type flexibility)
        for col, expected_type in self.schema.items():
            if col in df.columns:
                actual_type = df[col].dtype
                # Convert string type to numpy dtype
                try:
                    expected_np_type = np.dtype(expected_type)
                    # Allow int/float interchangeability for numeric columns
                    if np.issubdtype(expected_np_type, np.integer) and np.issubdtype(actual_type, np.number):
                        # int64 expected but float64 received is OK for numeric data
                        continue
                    elif np.issubdtype(expected_np_type, np.floating) and np.issubdtype(actual_type, np.number):
                        # float64 expected and numeric received is OK
                        continue
                    elif not np.issubdtype(actual_type, expected_np_type):
                        errors.append(
                            f"Column '{col}': expected {expected_type}, "
                            f"got {actual_type}"
                        )
                except:
                    pass
        
        success = len(errors) == 0
        if success:
            logger.info("âœ“ Schema validation passed")
        else:
            logger.error(f"âœ— Schema validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
        
        return success, errors
    
    def validate_quality(self, df: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Run quality checks"""
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'checks': {}
        }
        
        # 1. Row count check
        min_rows = self.quality_rules['min_rows']
        row_check = len(df) >= min_rows
        report['checks']['minimum_rows'] = {
            'value': len(df),
            'threshold': min_rows,
            'passed': row_check
        }
        
        # 2. Completeness check
        completeness = 1 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
        report['checks']['completeness'] = {
            'value': completeness,
            'threshold': self.quality_rules['min_completeness'],
            'passed': completeness >= self.quality_rules['min_completeness']
        }
        
        # 3. Duplicates check
        duplicate_ratio = df.duplicated().sum() / len(df)
        report['checks']['duplicates'] = {
            'value': duplicate_ratio,
            'threshold': self.quality_rules['max_duplicates'],
            'passed': duplicate_ratio <= self.quality_rules['max_duplicates']
        }
        
        # 4. Null values per column
        null_report = {}
        for col in df.columns:
            null_pct = df[col].isnull().sum() / len(df)
            null_report[col] = null_pct
        report['checks']['nulls_per_column'] = null_report
        
        # 5. Numeric columns - range & outliers
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_report = {}
        for col in numeric_cols:
            if df[col].std() > 0:  # Avoid division by zero
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_count = (z_scores > self.quality_rules['outlier_threshold']).sum()
                outlier_report[col] = {
                    'count': int(outlier_count),
                    'percentage': float((outlier_count / len(df)) * 100)
                }
            else:
                outlier_report[col] = {'count': 0, 'percentage': 0.0}
        report['checks']['outliers'] = outlier_report
        
        # 6. Class distribution (for target variable)
        if 'Class' in df.columns:
            class_dist = df['Class'].value_counts(normalize=True).to_dict()
            report['checks']['class_distribution'] = {
                int(k): float(v) for k, v in class_dist.items()
            }
            
            # Calculate imbalance ratio
            fraud_ratio = class_dist.get(1, 0)
            legit_ratio = class_dist.get(0, 1)
            imbalance_ratio = fraud_ratio / (legit_ratio + 1e-10)
            report['checks']['class_imbalance_ratio'] = float(imbalance_ratio)
        
        # Overall pass/fail
        all_checks_passed = all(
            check.get('passed', True) 
            for check in report['checks'].values() 
            if isinstance(check, dict) and 'passed' in check
        )
        
        return all_checks_passed, report
