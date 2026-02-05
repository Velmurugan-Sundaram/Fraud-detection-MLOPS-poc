"""Rollback automation - quickly revert to previous model version"""
import logging
import json
import shutil
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class ModelRollback:
    """Manage model versioning and automated rollback"""
    
    def __init__(self, models_dir: str = "models"):
        """Initialize rollback manager
        
        Args:
            models_dir: Root models directory
        """
        self.models_dir = Path(models_dir)
        self.version_history_path = self.models_dir / "version_history.json"
        self.current_version_path = self.models_dir / "current_version.json"
    
    def get_version_history(self) -> list:
        """Get complete version history"""
        if self.version_history_path.exists():
            with open(self.version_history_path, 'r') as f:
                return json.load(f)
        return []
    
    def get_current_version(self) -> dict:
        """Get currently deployed version"""
        if self.current_version_path.exists():
            with open(self.current_version_path, 'r') as f:
                return json.load(f)
        return {}
    
    def record_deployment(self, version: str, models: list, metrics: dict = None) -> None:
        """Record a model deployment in version history
        
        Args:
            version: Version identifier (e.g., 'v1.0.0')
            models: List of trained models
            metrics: Model performance metrics
        """
        logger.info(f"Recording deployment: {version}")
        
        # Load existing history
        history = self.get_version_history()
        
        # Create entry
        entry = {
            'version': version,
            'timestamp': datetime.utcnow().isoformat(),
            'models': models,
            'metrics': metrics or {},
            'status': 'active'
        }
        
        history.append(entry)
        
        # Save history
        with open(self.version_history_path, 'w') as f:
            json.dump(history, f, indent=2)
        
        # Update current version
        with open(self.current_version_path, 'w') as f:
            json.dump(entry, f, indent=2)
        
        logger.info(f"✅ Deployment recorded: {version}")
    
    def rollback_to_version(self, target_version: str) -> bool:
        """Rollback to a previous model version
        
        Args:
            target_version: Version to rollback to
            
        Returns:
            True if rollback successful, False otherwise
        """
        logger.info(f"Rolling back to version: {target_version}")
        
        history = self.get_version_history()
        
        # Find target version
        target_entry = None
        for entry in reversed(history):
            if entry['version'] == target_version:
                target_entry = entry
                break
        
        if not target_entry:
            logger.error(f"❌ Version {target_version} not found in history")
            return False
        
        try:
            # Backup current version
            current = self.get_current_version()
            if current:
                backup_dir = self.models_dir / f"backup_{current['version']}_{datetime.utcnow().timestamp()}"
                if (self.models_dir / f"{current['version']}").exists():
                    shutil.copytree(
                        self.models_dir / f"{current['version']}",
                        backup_dir
                    )
                    logger.info(f"✅ Backed up current version to {backup_dir}")
            
            # Restore target version
            target_dir = self.models_dir / target_version
            if target_dir.exists():
                # Copy target version models to main models directory
                for model_file in target_dir.glob("*.pkl"):
                    shutil.copy2(model_file, self.models_dir / model_file.name)
                
                # Update current version
                target_entry['status'] = 'active'
                target_entry['restored_at'] = datetime.utcnow().isoformat()
                
                with open(self.current_version_path, 'w') as f:
                    json.dump(target_entry, f, indent=2)
                
                logger.info(f"✅ Successfully rolled back to {target_version}")
                return True
            else:
                logger.error(f"❌ Target version directory not found: {target_dir}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            return False
    
    def list_available_versions(self) -> list:
        """List all available versions with their metadata
        
        Returns:
            List of version entries
        """
        return self.get_version_history()
    
    def get_version_info(self, version: str) -> dict:
        """Get detailed information about a specific version
        
        Args:
            version: Version identifier
            
        Returns:
            Version entry with metadata
        """
        history = self.get_version_history()
        for entry in history:
            if entry['version'] == version:
                return entry
        return {}
    
    def compare_versions(self, version1: str, version2: str) -> dict:
        """Compare metrics between two versions
        
        Args:
            version1: First version
            version2: Second version
            
        Returns:
            Comparison report
        """
        info1 = self.get_version_info(version1)
        info2 = self.get_version_info(version2)
        
        if not info1 or not info2:
            logger.error("One or both versions not found")
            return {}
        
        comparison = {
            'version1': version1,
            'version2': version2,
            'metrics_v1': info1.get('metrics', {}),
            'metrics_v2': info2.get('metrics', {}),
            'improvement': {}
        }
        
        # Calculate metric differences
        for metric in info1.get('metrics', {}).keys():
            if metric in info2.get('metrics', {}):
                v1_val = info1['metrics'][metric]
                v2_val = info2['metrics'][metric]
                if isinstance(v1_val, (int, float)) and isinstance(v2_val, (int, float)):
                    improvement = ((v2_val - v1_val) / abs(v1_val)) * 100 if v1_val != 0 else 0
                    comparison['improvement'][metric] = improvement
        
        return comparison


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    rm = ModelRollback()
    versions = rm.list_available_versions()
    print(f"Available versions: {len(versions)}")
    for v in versions:
        print(f"  - {v['version']} ({v['status']})")
