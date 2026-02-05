"""Model v2 training script - enhanced models with hyperparameter tuning"""
import logging
import json
import pickle
from pathlib import Path
from datetime import datetime
import yaml
import pandas as pd

from src.features.engineering import FeatureEngineer
from src.models.training import ModelTrainer

logger = logging.getLogger(__name__)


def train_model_v2():
    """Train Model v2 with advanced hyperparameter tuning and enhanced feature engineering"""
    
    logger.info("=" * 70)
    logger.info("TRAINING MODEL V2 - ENHANCED")
    logger.info("=" * 70)
    
    # Load config
    with open('src/config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Update config for v2 (enhanced hyperparameters)
    config['model']['hyperparameters'] = {
        'LogisticRegression': {
            'max_iter': 200,
            'solver': 'lbfgs',
            'random_state': 42,
            'class_weight': 'balanced'
        },
        'RandomForest': {
            'n_estimators': 150,
            'max_depth': 15,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'class_weight': 'balanced'
        },
        'XGBoost': {
            'n_estimators': 150,
            'max_depth': 6,
            'learning_rate': 0.05,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'scale_pos_weight': 1.0,
            'random_state': 42
        },
        'LightGBM': {
            'n_estimators': 150,
            'max_depth': 7,
            'learning_rate': 0.05,
            'num_leaves': 31,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'class_weight': 'balanced'
        }
    }
    
    # Load and process data
    logger.info("Loading validated data...")
    df = pd.read_parquet(config['data']['validated_path'])
    
    # Feature engineering
    logger.info("Engineering features for v2...")
    engineer = FeatureEngineer(config)
    df_eng = engineer.engineer_features(df)
    df_scaled = engineer.scale_features(df_eng)
    X_train, X_test, y_train, y_test = engineer.split_data(df_scaled)
    
    # Train models with MLFlow
    logger.info("Training v2 models with enhanced hyperparameters...")
    trainer = ModelTrainer(config)
    results = trainer.train_all_models(X_train, X_test, y_train, y_test, apply_smote=True)
    
    # Save models to v2 directory
    v2_models_dir = 'models/v2'
    Path(v2_models_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving v2 models to {v2_models_dir}...")
    for model_name, model in results['models'].items():
        model_path = Path(v2_models_dir) / f"{model_name}_model_v2.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        logger.info(f"  ✅ Saved {model_name} v2 model")
    
    # Save v2 metrics
    v2_metrics_path = f"{v2_models_dir}/metrics_v2.json"
    with open(v2_metrics_path, 'w') as f:
        json.dump(results['metrics'], f, indent=2)
    logger.info(f"✅ Saved v2 metrics to {v2_metrics_path}")
    
    # Create v2 metadata
    v2_metadata = {
        'version': 'v2.0.0',
        'created_at': datetime.utcnow().isoformat(),
        'models': list(results['models'].keys()),
        'metrics': results['metrics'],
        'hyperparameters': config['model']['hyperparameters'],
        'mlflow_runs': results['run_ids']
    }
    
    v2_metadata_path = f"{v2_models_dir}/metadata.json"
    with open(v2_metadata_path, 'w') as f:
        json.dump(v2_metadata, f, indent=2)
    
    logger.info("=" * 70)
    logger.info("✅ MODEL V2 TRAINING COMPLETED")
    logger.info("=" * 70)
    logger.info(f"Location: {v2_models_dir}")
    logger.info(f"Models: {list(results['models'].keys())}")
    
    return v2_metadata


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    train_model_v2()
