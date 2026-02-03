"""Configuration loader and manager"""
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ConfigManager:
    """Load and manage configuration"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def load(self, config_path: str = "src/config/config.yaml") -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if self._config is not None:
            return self._config
        
        try:
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return self._config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML: {e}")
            raise
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load() first.")
        
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        
        return value
