"""Drift detection module - detect data and prediction drift"""
import logging
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detect data drift and prediction drift in production"""
    
    def __init__(self, baseline_stats_path: str = "models/baseline_stats.json"):
        """
        Initialize drift detector
        
        Args:
            baseline_stats_path: Path to baseline statistics from training data
        """
        self.baseline_stats_path = baseline_stats_path
        self.baseline_stats = self._load_baseline_stats()
    
    def _load_baseline_stats(self) -> Dict:
        """Load baseline statistics from training phase"""
        if Path(self.baseline_stats_path).exists():
            with open(self.baseline_stats_path, 'r') as f:
                return json.load(f)
        return {}
    
    def calculate_feature_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate statistical summaries for features"""
        stats = {}
        for col in df.select_dtypes(include=[np.number]).columns:
            stats[col] = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'median': float(df[col].median()),
                'q25': float(df[col].quantile(0.25)),
                'q75': float(df[col].quantile(0.75))
            }
        return stats
    
    def detect_drift(self, current_df: pd.DataFrame, threshold: float = 0.1) -> Tuple[bool, Dict]:
        """
        Detect drift between baseline and current data using Kolmogorov-Smirnov test
        
        Args:
            current_df: Current production data
            threshold: Maximum allowed divergence (default 10%)
            
        Returns:
            Tuple of (drift_detected, drift_report)
        """
        from scipy.stats import ks_2samp
        
        logger.info("Detecting data drift...")
        drift_detected = False
        drift_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'drift_detected': False,
            'features_with_drift': [],
            'metrics': {}
        }
        
        if not self.baseline_stats:
            logger.warning("No baseline stats available - skipping drift detection")
            return False, drift_report
        
        current_stats = self.calculate_feature_stats(current_df)
        
        for feature in current_stats.keys():
            if feature not in self.baseline_stats:
                continue
            
            baseline = self.baseline_stats[feature]
            current = current_stats[feature]
            
            # Check for significant changes in distribution
            mean_diff = abs(current['mean'] - baseline['mean']) / (abs(baseline['mean']) + 1e-6)
            std_diff = abs(current['std'] - baseline['std']) / (abs(baseline['std']) + 1e-6)
            range_diff = abs(current['max'] - baseline['max']) / (abs(baseline['max']) + 1e-6)
            
            max_diff = max(mean_diff, std_diff, range_diff)
            
            drift_report['metrics'][feature] = {
                'mean_diff_pct': mean_diff * 100,
                'std_diff_pct': std_diff * 100,
                'range_diff_pct': range_diff * 100,
                'max_diff_pct': max_diff * 100
            }
            
            if max_diff > threshold:
                drift_detected = True
                drift_report['features_with_drift'].append({
                    'feature': feature,
                    'severity': max_diff * 100
                })
                logger.warning(f"  âš ï¸  Drift detected in {feature}: {max_diff*100:.2f}%")
        
        drift_report['drift_detected'] = drift_detected
        logger.info(f"  {'âœ… No drift' if not drift_detected else 'âš ï¸  Drift detected'}")
        
        return drift_detected, drift_report
    
    def detect_prediction_drift(self, predictions: np.ndarray, 
                               baseline_pred_dist: Dict) -> Tuple[bool, Dict]:
        """
        Detect drift in prediction distribution
        
        Args:
            predictions: Current model predictions
            baseline_pred_dist: Baseline prediction distribution
            
        Returns:
            Tuple of (drift_detected, drift_report)
        """
        logger.info("Detecting prediction drift...")
        
        drift_report = {
            'timestamp': datetime.utcnow().isoformat(),
            'prediction_drift_detected': False,
            'current_dist': {}
        }
        
        # Calculate current prediction distribution
        unique, counts = np.unique(predictions, return_counts=True)
        current_dist = {str(int(u)): int(c) for u, c in zip(unique, counts)}
        drift_report['current_dist'] = current_dist
        
        if not baseline_pred_dist:
            logger.warning("No baseline prediction distribution - skipping")
            return False, drift_report
        
        # Compare distributions
        baseline_total = sum(baseline_pred_dist.values())
        current_total = sum(current_dist.values())
        
        max_class_diff = 0
        for class_label in baseline_pred_dist.keys():
            baseline_ratio = baseline_pred_dist.get(class_label, 0) / baseline_total
            current_ratio = current_dist.get(class_label, 0) / current_total
            class_diff = abs(current_ratio - baseline_ratio)
            max_class_diff = max(max_class_diff, class_diff)
        
        drift_report['prediction_drift_detected'] = max_class_diff > 0.1
        logger.info(f"  {'âœ… Stable' if not drift_report['prediction_drift_detected'] else 'âš ï¸  Drift'}")
        
        return drift_report['prediction_drift_detected'], drift_report


def save_drift_report(report: Dict, output_path: str = "models/drift_report.json"):
    """Save drift detection report"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    logger.info(f"âœ… Drift report saved to {output_path}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage
    detector = DriftDetector()
    logger.info("Drift detector initialized")
