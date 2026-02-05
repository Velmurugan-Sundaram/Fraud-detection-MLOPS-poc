"""Data profiling module"""
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
        """Initialize with configuration"""
        self.config = config
    
    def profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate detailed data profile"""
        profile = {
            'metadata': {
                'rows': int(len(df)),
                'columns': int(len(df.columns)),
                'memory_mb': float(df.memory_usage(deep=True).sum() / 1024 / 1024)
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
                top_values = df[col].value_counts().head(5).to_dict()
                col_profile['top_values'] = {str(k): int(v) for k, v in top_values.items()}
            
            profile['columns'][col] = col_profile
        
        return profile
    
    def save_profile(self, profile: Dict[str, Any], output_path: str) -> None:
        """Save profile as JSON"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(profile, f, indent=2)
            logger.info(f"âœ“ Profile saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving profile: {e}")
            raise
