"""Data loader module"""
import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class DataLoader:
    """Load and parse data from multiple sources"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration"""
        self.config = config
        self.raw_path = config['data']['raw_path']
    
    def load_csv(self) -> pd.DataFrame:
        """Load CSV with error handling"""
        try:
            logger.info(f"Loading data from {self.raw_path}")
            df = pd.read_csv(self.raw_path)
            logger.info(f"✓ Loaded {len(df):,} rows, {len(df.columns)} columns")
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
            df = pd.read_parquet(path)
            logger.info(f"✓ Loaded {len(df):,} rows from parquet")
            return df
        except Exception as e:
            logger.error(f"Error loading parquet: {e}")
            raise
    
    def save_parquet(self, df: pd.DataFrame, output_path: str) -> None:
        """Save DataFrame as Parquet"""
        try:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(output_path, index=False, compression='snappy')
            logger.info(f"✓ Saved {len(df):,} rows to {output_path}")
        except Exception as e:
            logger.error(f"Error saving parquet: {e}")
            raise
