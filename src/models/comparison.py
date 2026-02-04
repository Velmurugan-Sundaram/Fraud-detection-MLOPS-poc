"""Model comparison and selection for best model registration"""
import pandas as pd
import numpy as np
import logging
import json
from typing import Dict, Any, List, Tuple
from pathlib import Path
import pickle

import mlflow
import mlflow.sklearn
import mlflow.xgboost

logger = logging.getLogger(__name__)


class ModelComparator:
    """Compare models and select the best one"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize model comparator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.mlflow_config = config.get('mlflow', {})
        self.comparison_results = None
        
    def compare_models(self, metrics: Dict[str, Dict[str, float]]) -> pd.DataFrame:
        """Compare models based on multiple metrics
        
        Args:
            metrics: Dictionary of model metrics {model_name: {metric: value}}
            
        Returns:
            DataFrame with comparison results
        """
        logger.info("=" * 70)
        logger.info("MODEL COMPARISON")
        logger.info("=" * 70)
        
        # Convert to dataframe for easier comparison
        comparison_df = pd.DataFrame(metrics).T
        
        # Rank models on each metric
        ranking_df = comparison_df.copy()
        for col in comparison_df.columns:
            ranking_df[f"{col}_rank"] = comparison_df[col].rank(ascending=False)
        
        # Calculate average rank
        rank_cols = [col for col in ranking_df.columns if col.endswith('_rank')]
        ranking_df['avg_rank'] = ranking_df[rank_cols].mean(axis=1)
        ranking_df = ranking_df.sort_values('avg_rank')
        
        logger.info("\n📊 METRICS COMPARISON:")
        logger.info(comparison_df.to_string())
        
        logger.info("\n🏆 MODEL RANKINGS (by average rank):")
        logger.info(ranking_df[['avg_rank']].to_string())
        
        self.comparison_results = {
            'metrics_df': comparison_df,
            'ranking_df': ranking_df
        }
        
        return comparison_df
    
    def select_best_model(self, 
                         metrics: Dict[str, Dict[str, float]],
                         selection_criteria: str = "f1_score") -> Tuple[str, float]:
        """Select best model based on criteria
        
        Args:
            metrics: Dictionary of model metrics
            selection_criteria: Metric to use for selection (default: f1_score)
            
        Returns:
            Tuple of (best_model_name, best_score)
        """
        logger.info(f"\nSelecting best model based on: {selection_criteria}")
        
        best_model = None
        best_score = -np.inf
        
        for model_name, model_metrics in metrics.items():
            if selection_criteria in model_metrics:
                score = model_metrics[selection_criteria]
                if score > best_score:
                    best_score = score
                    best_model = model_name
        
        if best_model is None:
            raise ValueError(f"No models have metric: {selection_criteria}")
        
        logger.info(f"✅ BEST MODEL: {best_model}")
        logger.info(f"   {selection_criteria}: {best_score:.4f}")
        
        return best_model, best_score
    
    def get_model_rankings(self, metrics: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Get detailed model rankings
        
        Args:
            metrics: Dictionary of model metrics
            
        Returns:
            List of ranked models with details
        """
        rankings = []
        
        # Calculate composite score (weighted average)
        weights = {
            'f1_score': 0.35,
            'roc_auc': 0.25,
            'pr_auc': 0.20,
            'recall': 0.15,
            'precision': 0.05
        }
        
        for model_name, model_metrics in metrics.items():
            composite_score = 0
            for metric, weight in weights.items():
                if metric in model_metrics:
                    composite_score += model_metrics[metric] * weight
            
            rankings.append({
                'model': model_name,
                'composite_score': composite_score,
                'metrics': model_metrics
            })
        
        # Sort by composite score
        rankings = sorted(rankings, key=lambda x: x['composite_score'], reverse=True)
        
        logger.info("\n📊 COMPOSITE MODEL RANKINGS:")
        logger.info("(Weights: F1=35%, ROC-AUC=25%, PR-AUC=20%, Recall=15%, Precision=5%)\n")
        
        for rank, model_info in enumerate(rankings, 1):
            logger.info(f"{rank}. {model_info['model']:<20} - Composite Score: {model_info['composite_score']:.4f}")
            for metric, value in model_info['metrics'].items():
                logger.info(f"   {metric:<15}: {value:.4f}")
            logger.info("")
        
        return rankings
    
    def register_best_model(self,
                           best_model_name: str,
                           model: Any,
                           metrics: Dict[str, float],
                           version: str = "v1") -> str:
        """Register best model in MLFlow model registry
        
        Args:
            best_model_name: Name of the best model
            model: Trained model object
            metrics: Model metrics
            version: Model version string
            
        Returns:
            Model URI
        """
        logger.info("\n" + "=" * 70)
        logger.info("REGISTERING BEST MODEL IN MLFLOW MODEL REGISTRY")
        logger.info("=" * 70)
        
        model_registry_name = f"fraud-detection-{version}"
        
        try:
            # Get current run
            with mlflow.start_run() as run:
                run_id = run.info.run_id
                
                # Log metrics for this registration run
                for metric_name, metric_value in metrics.items():
                    mlflow.log_metric(metric_name, metric_value)
                
                # Log parameters
                mlflow.log_param("selected_model", best_model_name)
                mlflow.log_param("model_version", version)
                
                # Register model
                if best_model_name == "XGBoost":
                    model_uri = mlflow.xgboost.log_model(
                        model, 
                        artifact_path="fraud_detection_model"
                    )
                else:
                    model_uri = mlflow.sklearn.log_model(
                        model,
                        artifact_path="fraud_detection_model"
                    )
                
                # Register in model registry
                model_info = mlflow.register_model(
                    f"runs:/{run_id}/fraud_detection_model",
                    model_registry_name
                )
                
                logger.info(f"✅ MODEL REGISTERED SUCCESSFULLY")
                logger.info(f"   Registry Name: {model_registry_name}")
                logger.info(f"   Version: {model_info.version}")
                logger.info(f"   Best Model Algorithm: {best_model_name}")
                logger.info(f"   Run ID: {run_id}")
                
                # Save registration details
                registration_details = {
                    'registry_name': model_registry_name,
                    'version': model_info.version,
                    'best_model_algorithm': best_model_name,
                    'run_id': run_id,
                    'metrics': metrics,
                    'model_uri': str(model_info)
                }
                
                return model_registry_name
        
        except Exception as e:
            logger.error(f"❌ Failed to register model: {e}")
            raise
    
    def save_comparison_report(self, output_path: str) -> None:
        """Save comparison report to file
        
        Args:
            output_path: Path to save report
        """
        if self.comparison_results is None:
            logger.warning("No comparison results to save")
            return
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        report = {
            'metrics': self.comparison_results['metrics_df'].to_dict(),
            'rankings': self.comparison_results['ranking_df'].to_dict()
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"✅ Comparison report saved to {output_path}")
    
    def get_best_model_info(self, rankings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get information about the best ranked model
        
        Args:
            rankings: List of ranked models
            
        Returns:
            Dictionary with best model information
        """
        if not rankings:
            raise ValueError("No rankings provided")
        
        best_model = rankings[0]
        
        return {
            'name': best_model['model'],
            'composite_score': best_model['composite_score'],
            'metrics': best_model['metrics']
        }
