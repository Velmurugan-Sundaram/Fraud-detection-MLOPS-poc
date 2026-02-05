"""Registry Audit Trail Management - Version history and deployment tracking"""
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class RegistryAuditTrail:
    """Manage registry audit trail for model deployments and version history"""
    
    def __init__(self, json_path: str = "registry_audit_trail.json", csv_path: str = "registry_audit_trail.csv"):
        """Initialize audit trail manager
        
        Args:
            json_path: Path to JSON audit trail file
            csv_path: Path to CSV audit trail file
        """
        self.json_path = Path(json_path)
        self.csv_path = Path(csv_path)
        self.ensure_files_exist()
    
    def ensure_files_exist(self):
        """Ensure audit trail files exist"""
        if not self.json_path.exists():
            with open(self.json_path, 'w') as f:
                json.dump([], f, indent=2)
        
        if not self.csv_path.exists():
            with open(self.csv_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'event_type', 'version', 'status', 'environment',
                    'models', 'reason', 'triggered_by', 'commit', 'details'
                ])
    
    def add_entry(self, event_type: str, version: str, status: str = 'success', 
                 environment: str = 'production', models: List[str] = None,
                 reason: str = '', triggered_by: str = 'system', commit: str = '', 
                 details: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add a new entry to the audit trail
        
        Args:
            event_type: Type of event (deployment, rollback, training, etc.)
            version: Model version identifier
            status: Status of the event (success, failed, pending)
            environment: Deployment environment (production, staging, dev)
            models: List of model names
            reason: Reason for the event
            triggered_by: User/system that triggered the event
            commit: Git commit hash
            details: Additional details dictionary
            
        Returns:
            The created audit entry
        """
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'version': version,
            'status': status,
            'environment': environment,
            'models': models or [],
            'reason': reason,
            'triggered_by': triggered_by,
            'commit': commit,
            'details': details or {}
        }
        
        # Add to JSON
        with open(self.json_path, 'r') as f:
            trail = json.load(f)
        trail.append(entry)
        with open(self.json_path, 'w') as f:
            json.dump(trail, f, indent=2)
        
        # Add to CSV
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                entry['timestamp'],
                entry['event_type'],
                entry['version'],
                entry['status'],
                entry['environment'],
                ';'.join(entry['models']),
                entry['reason'],
                entry['triggered_by'],
                entry['commit'],
                json.dumps(entry['details'])
            ])
        
        return entry
    
    def get_deployment_history(self, version: str = None) -> List[Dict]:
        """Get deployment history, optionally filtered by version
        
        Args:
            version: Optional version to filter by
            
        Returns:
            List of deployment entries
        """
        with open(self.json_path, 'r') as f:
            trail = json.load(f)
        
        deployments = [e for e in trail if e['event_type'] in ['deployment', 'canary_deployment']]
        
        if version:
            deployments = [e for e in deployments if e['version'] == version]
        
        return sorted(deployments, key=lambda x: x['timestamp'], reverse=True)
    
    def get_rollback_history(self) -> List[Dict]:
        """Get all rollback events"""
        with open(self.json_path, 'r') as f:
            trail = json.load(f)
        
        rollbacks = [e for e in trail if e['event_type'] == 'rollback']
        return sorted(rollbacks, key=lambda x: x['timestamp'], reverse=True)
    
    def get_training_history(self) -> List[Dict]:
        """Get model training history"""
        with open(self.json_path, 'r') as f:
            trail = json.load(f)
        
        trainings = [e for e in trail if e['event_type'] == 'training']
        return sorted(trainings, key=lambda x: x['timestamp'], reverse=True)
    
    def get_active_versions(self) -> List[str]:
        """Get currently active model versions"""
        with open(self.json_path, 'r') as f:
            trail = json.load(f)
        
        deployments = [e for e in trail if e['event_type'] in ['deployment', 'canary_deployment'] and e['status'] == 'success']
        
        # Get latest deployment per environment
        active_by_env = {}
        for deploy in sorted(deployments, key=lambda x: x['timestamp'], reverse=True):
            env = deploy['environment']
            if env not in active_by_env:
                active_by_env[env] = deploy['version']
        
        return list(active_by_env.values())
    
    def get_version_info(self, version: str) -> Dict:
        """Get complete information for a specific version
        
        Args:
            version: Version identifier
            
        Returns:
            Compiled version information
        """
        with open(self.json_path, 'r') as f:
            trail = json.load(f)
        
        entries = [e for e in trail if e['version'] == version]
        
        return {
            'version': version,
            'total_events': len(entries),
            'deployments': len([e for e in entries if 'deployment' in e['event_type']]),
            'rollbacks': len([e for e in entries if e['event_type'] == 'rollback']),
            'trainings': len([e for e in entries if e['event_type'] == 'training']),
            'current_status': entries[-1]['status'] if entries else 'unknown',
            'environments': list(set([e['environment'] for e in entries])),
            'timeline': entries
        }
    
    def generate_report(self, start_date: str = None, end_date: str = None) -> Dict:
        """Generate audit trail report for a date range
        
        Args:
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            
        Returns:
            Audit report dictionary
        """
        with open(self.json_path, 'r') as f:
            trail = json.load(f)
        
        if start_date:
            trail = [e for e in trail if e['timestamp'] >= start_date]
        if end_date:
            trail = [e for e in trail if e['timestamp'] <= end_date]
        
        report = {
            'generated_at': datetime.utcnow().isoformat(),
            'period': {'start': start_date, 'end': end_date},
            'summary': {
                'total_events': len(trail),
                'deployments': len([e for e in trail if 'deployment' in e['event_type']]),
                'rollbacks': len([e for e in trail if e['event_type'] == 'rollback']),
                'trainings': len([e for e in trail if e['event_type'] == 'training']),
                'successful_events': len([e for e in trail if e['status'] == 'success']),
                'failed_events': len([e for e in trail if e['status'] == 'failed']),
            },
            'by_version': {},
            'by_environment': {}
        }
        
        # Group by version
        for version in set([e['version'] for e in trail]):
            version_events = [e for e in trail if e['version'] == version]
            report['by_version'][version] = {
                'total': len(version_events),
                'last_event': version_events[-1]['timestamp'] if version_events else None,
                'status': version_events[-1]['status'] if version_events else 'unknown'
            }
        
        # Group by environment
        for env in set([e['environment'] for e in trail]):
            env_events = [e for e in trail if e['environment'] == env]
            report['by_environment'][env] = {
                'total': len(env_events),
                'active_version': env_events[-1]['version'] if env_events else None,
                'deployments': len([e for e in env_events if 'deployment' in e['event_type']])
            }
        
        return report


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Example usage
    trail = RegistryAuditTrail()
    
    # Add sample entries
    trail.add_entry(
        event_type='training',
        version='v1.0.0',
        status='success',
        environment='production',
        models=['LogisticRegression', 'RandomForest', 'XGBoost', 'LightGBM'],
        triggered_by='ci-pipeline'
    )
    
    trail.add_entry(
        event_type='deployment',
        version='v1.0.0',
        status='success',
        environment='production',
        models=['LightGBM'],
        triggered_by='ci-pipeline'
    )
    
    # Print history
    logger.info("Recent deployments:")
    for deploy in trail.get_deployment_history()[:3]:
        logger.info(f"  {deploy['version']} → {deploy['status']}")
    
    # Print report
    report = trail.generate_report()
    logger.info(f"Total events: {report['summary']['total_events']}")
