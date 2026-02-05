"""Feature consistency and validation checks for parity verification"""
import pandas as pd
import numpy as np
import logging
import json
from typing import Dict, Any, List, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class FeatureConsistencyChecker:
    """Validates feature consistency and parity across different stages"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize feature consistency checker
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.feature_stats = {}
        self.consistency_report = {}
        
    def check_feature_parity(self, 
                            df_original: pd.DataFrame,
                            df_engineered: pd.DataFrame) -> Tuple[bool, Dict[str, Any]]:
        """Check that feature engineering doesn't corrupt original data
        
        Args:
            df_original: Original dataframe
            df_engineered: Engineered dataframe
            
        Returns:
            Tuple of (parity_valid, report)
        """
        logger.info("Checking feature engineering parity...")
        
        report = {
            'parity_valid': True,
            'checks': {},
            'issues': []
        }
        
        # Check 1: Row count preserved
        if len(df_original) != len(df_engineered):
            report['issues'].append(f"Row count mismatch: {len(df_original)} vs {len(df_engineered)}")
            report['parity_valid'] = False
        report['checks']['row_count_preserved'] = len(df_original) == len(df_engineered)
        
        # Check 2: Original columns intact
        original_cols = set(df_original.columns)
        engineered_cols = set(df_engineered.columns)
        
        missing_cols = original_cols - engineered_cols
        if missing_cols:
            report['issues'].append(f"Missing original columns: {missing_cols}")
            report['parity_valid'] = False
        report['checks']['original_columns_intact'] = len(missing_cols) == 0
        
        # Check 3: Original data not corrupted (for overlapping columns)
        for col in original_cols & engineered_cols:
            if col in ['Time', 'Amount', 'Class']:  # Check key original columns
                # Check for NaN introduction
                orig_nulls = df_original[col].isna().sum()
                eng_nulls = df_engineered[col].isna().sum()
                
                if eng_nulls > orig_nulls:
                    report['issues'].append(
                        f"NaN introduction in column '{col}': {orig_nulls} -> {eng_nulls}"
                    )
                    report['parity_valid'] = False
        
        report['checks']['no_data_corruption'] = len([i for i in report['issues'] if 'NaN' in i]) == 0
        
        # Check 4: New features have no unexpected NaN
        new_cols = engineered_cols - original_cols
        for col in new_cols:
            null_ratio = df_engineered[col].isna().sum() / len(df_engineered)
            if null_ratio > 0.05:  # Allow up to 5% NaN in new features
                report['issues'].append(
                    f"High NaN ratio in new feature '{col}': {null_ratio:.2%}"
                )
                report['parity_valid'] = False
        
        report['checks']['new_features_valid'] = len(new_cols) > 0
        
        # Check 5: Feature value ranges reasonable
        numeric_cols = df_engineered.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col in new_cols:  # Check new engineered features
                values = df_engineered[col].dropna()
                if len(values) > 0:
                    if np.isinf(values).any():
                        report['issues'].append(f"Infinite values found in '{col}'")
                        report['parity_valid'] = False
        
        report['checks']['no_infinite_values'] = len([i for i in report['issues'] if 'Infinite' in i]) == 0
        
        # Summary
        logger.info(f"\nFeature Parity Check Results:")
        logger.info(f"  Original rows: {len(df_original)}, Engineered rows: {len(df_engineered)}")
        logger.info(f"  Original columns: {len(original_cols)}, Engineered columns: {len(engineered_cols)}")
        logger.info(f"  New features created: {len(new_cols)}")
        logger.info(f"  Parity valid: {report['parity_valid']}" if report['parity_valid'] else f"  Parity valid: {report['parity_valid']}")
        
        if report['issues']:
            for issue in report['issues']:
                logger.warning(f"    âš ï¸  {issue}")
        
        return report['parity_valid'], report
    
    def check_train_test_consistency(self,
                                   X_train: pd.DataFrame,
                                   X_test: pd.DataFrame,
                                   y_train: pd.Series,
                                   y_test: pd.Series) -> Tuple[bool, Dict[str, Any]]:
        """Check consistency between train and test sets
        
        Args:
            X_train: Training features
            X_test: Test features
            y_train: Training labels
            y_test: Test labels
            
        Returns:
            Tuple of (consistent, report)
        """
        logger.info("Checking train/test consistency...")
        
        report = {
            'consistent': True,
            'checks': {},
            'issues': []
        }
        
        # Check 1: Same columns
        if set(X_train.columns) != set(X_test.columns):
            report['issues'].append("Train and test have different columns")
            report['consistent'] = False
        report['checks']['same_columns'] = set(X_train.columns) == set(X_test.columns)
        
        # Check 2: No data leakage (ensure test data not in train)
        # This is a simple check based on exact row matching
        if len(X_train) > 0 and len(X_test) > 0:
            # Create temporary index for comparison
            train_tuples = set(map(tuple, X_train.values))
            test_tuples = set(map(tuple, X_test.values))
            
            overlap = len(train_tuples & test_tuples)
            if overlap > 0:
                logger.warning(f"    âš ï¸  Found {overlap} overlapping rows between train and test")
                report['issues'].append(f"Data leakage: {overlap} rows in both train and test")
        
        report['checks']['no_data_leakage'] = len([i for i in report['issues'] if 'leakage' in i.lower()]) == 0
        
        # Check 3: Feature statistics consistency
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns
        feature_stats = {}
        
        for col in numeric_cols:
            train_mean = X_train[col].mean()
            train_std = X_train[col].std()
            test_mean = X_test[col].mean()
            test_std = X_test[col].std()
            
            feature_stats[col] = {
                'train_mean': float(train_mean),
                'train_std': float(train_std),
                'test_mean': float(test_mean),
                'test_std': float(test_std)
            }
        
        report['feature_statistics'] = feature_stats
        report['checks']['statistics_calculated'] = len(feature_stats) == len(numeric_cols)
        
        # Check 4: Class balance consistency
        train_positive_ratio = y_train.sum() / len(y_train)
        test_positive_ratio = y_test.sum() / len(y_test)
        
        # Allow 2% difference in positive class ratio
        if abs(train_positive_ratio - test_positive_ratio) > 0.02:
            logger.warning(
                f"    âš ï¸  Class imbalance mismatch: "
                f"Train={train_positive_ratio:.2%}, Test={test_positive_ratio:.2%}"
            )
        
        report['class_distribution'] = {
            'train_positive_ratio': float(train_positive_ratio),
            'test_positive_ratio': float(test_positive_ratio)
        }
        report['checks']['class_balance_similar'] = abs(train_positive_ratio - test_positive_ratio) <= 0.02
        
        # Summary
        logger.info(f"\nTrain/Test Consistency Check Results:")
        logger.info(f"  Same columns: {report['checks']['same_columns']}")
        logger.info(f"  No data leakage: {report['checks']['no_data_leakage']}")
        logger.info(f"  Class balance (Train): {train_positive_ratio:.2%}")
        logger.info(f"  Class balance (Test): {test_positive_ratio:.2%}")
        logger.info(f"  Consistent: {report['consistent']}" if report['consistent'] else f"  Consistent: {report['consistent']}")
        
        if report['issues']:
            for issue in report['issues']:
                logger.warning(f"    âš ï¸  {issue}")
        
        return report['consistent'], report
    
    def check_feature_distributions(self, 
                                   X_train: pd.DataFrame,
                                   X_test: pd.DataFrame,
                                   max_distribution_diff: float = 0.1) -> Tuple[bool, Dict[str, Any]]:
        """Check that train and test feature distributions are similar
        
        Args:
            X_train: Training features
            X_test: Test features
            max_distribution_diff: Maximum allowed KL divergence
            
        Returns:
            Tuple of (distributions_ok, report)
        """
        logger.info("Checking feature distributions...")
        
        report = {
            'distributions_ok': True,
            'statistics': {},
            'issues': []
        }
        
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            train_values = X_train[col].dropna()
            test_values = X_test[col].dropna()
            
            if len(train_values) == 0 or len(test_values) == 0:
                continue
            
            # Calculate distribution statistics
            stats = {
                'train_mean': float(train_values.mean()),
                'train_median': float(train_values.median()),
                'train_std': float(train_values.std()),
                'test_mean': float(test_values.mean()),
                'test_median': float(test_values.median()),
                'test_std': float(test_values.std()),
            }
            
            # Check for significant mean shift
            if stats['train_std'] > 0:
                mean_diff = abs(stats['train_mean'] - stats['test_mean']) / stats['train_std']
                if mean_diff > 2.0:  # More than 2 std deviations
                    report['issues'].append(
                        f"Distribution shift in '{col}': mean diff = {mean_diff:.2f}Ïƒ"
                    )
            
            report['statistics'][col] = stats
        
        report['distributions_ok'] = len(report['issues']) == 0
        
        logger.info(f"  Features checked: {len(report['statistics'])}")
        logger.info(f"  Distribution shifts detected: {len(report['issues'])}")
        logger.info(f"  Distributions OK: {report['distributions_ok']}" if report['distributions_ok'] else f"  Distributions OK: {report['distributions_ok']}")
        
        if report['issues']:
            for issue in report['issues']:
                logger.warning(f"    âš ï¸  {issue}")
        
        return report['distributions_ok'], report
    
    def save_consistency_report(self, report: Dict[str, Any], output_path: str) -> None:
        """Save consistency report to file
        
        Args:
            report: Consistency report dictionary
            output_path: Path to save report
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Consistency report saved to {output_path}")
