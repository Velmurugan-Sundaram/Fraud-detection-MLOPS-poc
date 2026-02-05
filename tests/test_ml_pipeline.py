"""Integration tests for ML pipeline components"""
import pytest
import pandas as pd
import numpy as np
import tempfile
import yaml
import json
from pathlib import Path
import logging

from src.features.engineering import FeatureEngineer
from src.features.consistency import FeatureConsistencyChecker
from src.models.training import ModelTrainer
from src.models.comparison import ModelComparator

logger = logging.getLogger(__name__)


@pytest.fixture
def test_config():
    """Create test configuration"""
    config = {
        'features': {
            'scaling_method': 'StandardScaler',
            'test_split_ratio': 0.2,
            'stratified_split': True,
            'random_state': 42
        },
        'model': {
            'models_to_train': ['LogisticRegression', 'RandomForest'],
            'hyperparameters': {
                'LogisticRegression': {
                    'max_iter': 100,
                    'class_weight': 'balanced',
                    'random_state': 42
                },
                'RandomForest': {
                    'n_estimators': 10,
                    'max_depth': 3,
                    'class_weight': 'balanced',
                    'random_state': 42
                }
            }
        },
        'mlflow': {
            'tracking_uri': 'http://127.0.0.1:5000',
            'experiment_name': 'test_experiment'
        }
    }
    return config


@pytest.fixture
def sample_data():
    """Create sample test data"""
    np.random.seed(42)
    n_samples = 500
    
    data = {
        'Time': np.random.randint(0, 86400, n_samples),
        'Amount': np.random.exponential(100, n_samples),
        **{f'V{i}': np.random.randn(n_samples) for i in range(1, 29)},
        'Class': np.random.binomial(1, 0.01, n_samples)  # ~1% fraud
    }
    
    return pd.DataFrame(data)


class TestFeatureEngineering:
    """Test feature engineering module"""
    
    def test_feature_engineer_initialization(self, test_config):
        """Test FeatureEngineer initialization"""
        engineer = FeatureEngineer(test_config)
        assert engineer.scaling_method == 'StandardScaler'
        logger.info("Feature engineer initialization test passed")
    
    def test_feature_engineering(self, test_config, sample_data):
        """Test feature engineering transformations"""
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        
        # Check new features were created
        assert len(df_engineered.columns) > len(sample_data.columns)
        assert 'Amount_log' in df_engineered.columns
        assert 'Time_hour' in df_engineered.columns
        assert 'V_mean' in df_engineered.columns
        
        # Check no NaN introduced
        assert df_engineered.isna().sum().sum() < len(df_engineered) * 0.01
        
        logger.info("Feature engineering test passed")
    
    def test_feature_scaling(self, test_config, sample_data):
        """Test feature scaling"""
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        df_scaled = engineer.scale_features(df_engineered, fit=True)
        
        # Check scaling applied
        assert df_scaled.shape == df_engineered.shape
        
        # Check mean and std for scaled features (should be ~0 and ~1)
        numeric_cols = df_scaled.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if col not in ['Time', 'Class']:
                mean_val = abs(df_scaled[col].mean())
                std_val = df_scaled[col].std()
                # Allow some tolerance
                assert mean_val < 1.0, f"Scaled {col} mean too large: {mean_val}"
                assert 0.5 < std_val < 1.5, f"Scaled {col} std not near 1: {std_val}"
        
        logger.info("Feature scaling test passed")
    
    def test_data_splitting(self, test_config, sample_data):
        """Test train/test splitting"""
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        df_scaled = engineer.scale_features(df_engineered, fit=True)
        
        X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)
        
        # Check split ratios
        total_samples = len(X_train) + len(X_test)
        assert total_samples == len(df_scaled)
        assert len(X_test) / len(df_scaled) == pytest.approx(0.2, abs=0.05)
        
        # Check stratification (class distribution similar)
        train_positive = y_train.sum() / len(y_train)
        test_positive = y_test.sum() / len(y_test)
        assert abs(train_positive - test_positive) < 0.05
        
        # Check no leakage
        assert len(set(X_train.index) & set(X_test.index)) == 0
        
        logger.info("Data splitting test passed")


class TestFeatureConsistency:
    """Test feature consistency checks"""
    
    def test_consistency_checker_initialization(self, test_config):
        """Test FeatureConsistencyChecker initialization"""
        checker = FeatureConsistencyChecker(test_config)
        assert checker.config is not None
        logger.info("Consistency checker initialization test passed")
    
    def test_feature_parity_check(self, test_config, sample_data):
        """Test feature parity verification"""
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        
        checker = FeatureConsistencyChecker(test_config)
        parity_valid, report = checker.check_feature_parity(sample_data, df_engineered)
        
        # Check parity passed
        assert parity_valid
        assert report['checks']['row_count_preserved']
        assert report['checks']['original_columns_intact']
        
        logger.info("Feature parity check test passed")
    
    def test_train_test_consistency(self, test_config, sample_data):
        """Test train/test consistency checks"""
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        df_scaled = engineer.scale_features(df_engineered, fit=True)
        
        X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)
        
        checker = FeatureConsistencyChecker(test_config)
        consistent, report = checker.check_train_test_consistency(
            X_train, X_test, y_train, y_test
        )
        
        # Check consistency
        assert consistent
        assert report['checks']['same_columns']
        assert report['checks']['no_data_leakage']
        
        logger.info("Train/test consistency test passed")
    
    def test_distribution_check(self, test_config, sample_data):
        """Test feature distribution checking"""
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        df_scaled = engineer.scale_features(df_engineered, fit=True)
        
        X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)
        
        checker = FeatureConsistencyChecker(test_config)
        dist_ok, report = checker.check_feature_distributions(X_train, X_test)
        
        # Check distributions (may have some shifts)
        assert 'statistics' in report
        assert len(report['statistics']) > 0
        
        logger.info("Distribution check test passed")


class TestModelTraining:
    """Test model training module"""
    
    def test_model_trainer_initialization(self, test_config):
        """Test ModelTrainer initialization"""
        trainer = ModelTrainer(test_config)
        assert trainer.model_config is not None
        assert trainer.mlflow_config is not None
        logger.info("Model trainer initialization test passed")
    
    def test_class_imbalance_handling(self, test_config, sample_data):
        """Test SMOTE for class imbalance"""
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        df_scaled = engineer.scale_features(df_engineered, fit=True)
        X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)
        
        trainer = ModelTrainer(test_config)
        X_resampled, y_resampled = trainer.handle_class_imbalance(X_train, y_train)
        
        # Check resampling
        assert len(X_resampled) >= len(X_train)
        assert y_resampled.sum() > y_train.sum()  # More fraud samples after SMOTE
        
        logger.info("Class imbalance handling test passed")


class TestModelComparison:
    """Test model comparison module"""
    
    def test_model_comparator_initialization(self, test_config):
        """Test ModelComparator initialization"""
        comparator = ModelComparator(test_config)
        assert comparator.config is not None
        logger.info("Model comparator initialization test passed")
    
    def test_model_comparison(self, test_config):
        """Test model comparison"""
        metrics = {
            'LogisticRegression': {
                'accuracy': 0.98,
                'precision': 0.80,
                'recall': 0.60,
                'f1_score': 0.68,
                'roc_auc': 0.85,
                'pr_auc': 0.75
            },
            'RandomForest': {
                'accuracy': 0.99,
                'precision': 0.90,
                'recall': 0.75,
                'f1_score': 0.82,
                'roc_auc': 0.92,
                'pr_auc': 0.85
            }
        }
        
        comparator = ModelComparator(test_config)
        comparison_df = comparator.compare_models(metrics)
        
        # Check comparison dataframe
        assert comparison_df.shape[0] == 2
        assert comparison_df.shape[1] == 6
        
        logger.info("Model comparison test passed")
    
    def test_best_model_selection(self, test_config):
        """Test best model selection"""
        metrics = {
            'LogisticRegression': {
                'f1_score': 0.68,
                'roc_auc': 0.85
            },
            'RandomForest': {
                'f1_score': 0.82,
                'roc_auc': 0.92
            }
        }
        
        comparator = ModelComparator(test_config)
        best_model, best_score = comparator.select_best_model(metrics)
        
        assert best_model == 'RandomForest'
        assert best_score == 0.82
        
        logger.info("Best model selection test passed")
    
    def test_model_rankings(self, test_config):
        """Test model ranking calculation"""
        metrics = {
            'Model1': {
                'f1_score': 0.70,
                'roc_auc': 0.80,
                'pr_auc': 0.75,
                'recall': 0.65,
                'precision': 0.75
            },
            'Model2': {
                'f1_score': 0.80,
                'roc_auc': 0.85,
                'pr_auc': 0.80,
                'recall': 0.75,
                'precision': 0.85
            }
        }
        
        comparator = ModelComparator(test_config)
        rankings = comparator.get_model_rankings(metrics)
        
        # Check rankings
        assert len(rankings) == 2
        assert rankings[0]['model'] == 'Model2'  # Model2 should rank higher
        assert rankings[0]['composite_score'] > rankings[1]['composite_score']
        
        logger.info("Model ranking test passed")


class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_end_to_end_pipeline(self, test_config, sample_data):
        """Test complete pipeline flow"""
        # Step 1: Feature Engineering
        engineer = FeatureEngineer(test_config)
        df_engineered = engineer.engineer_features(sample_data)
        df_scaled = engineer.scale_features(df_engineered, fit=True)
        X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)
        
        # Step 2: Consistency Checks
        checker = FeatureConsistencyChecker(test_config)
        parity_valid, _ = checker.check_feature_parity(sample_data, df_engineered)
        consistency_valid, _ = checker.check_train_test_consistency(
            X_train, X_test, y_train, y_test
        )
        
        # Step 3: Model Training (only LogisticRegression for speed)
        trainer = ModelTrainer(test_config)
        
        # Train simple model
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(max_iter=100, random_state=42)
        X_train_resampled, y_train_resampled = trainer.handle_class_imbalance(X_train, y_train)
        model.fit(X_train_resampled, y_train_resampled)
        
        metrics = trainer.evaluate_model(model, X_test, y_test, 'LogisticRegression')
        
        # Step 4: Model Comparison
        comparator = ModelComparator(test_config)
        best_model_name, best_score = comparator.select_best_model({
            'LogisticRegression': metrics
        })
        
        # Verify end-to-end
        assert parity_valid
        assert consistency_valid
        assert best_model_name == 'LogisticRegression'
        assert best_score > 0.5  # Should have reasonable performance
        
        logger.info("End-to-end pipeline integration test passed")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v', '-s'])
