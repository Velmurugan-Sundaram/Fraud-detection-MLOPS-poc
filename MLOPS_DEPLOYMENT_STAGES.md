# MLOps Deployment Stages - Complete Guide

## Overview
This document describes the 9 implementation stages for complete MLOps deployment of the Fraud Detection system.

---

## Stage 1: Dockerize + Deploy v1 (✅ Complete)
**Expected Output:** Model v1 live

### Files Created
- `.github/workflows/deploy-v1.yml` - Deployment workflow

### Features
- Docker image building and push
- Model artifact validation
- Registry audit trail recording
- Deployment notifications

### Commands
```bash
# Trigger manual deployment
gh workflow run deploy-v1.yml --ref main
```

---

## Stage 2: Train Model v2 (✅ Complete)
**Expected Output:** Model v2 ready

### Files Created
- `src/models/train_v2.py` - Enhanced training script
- `.github/workflows/train-v2.yml` - Training workflow
- Models stored in `models/v2/` with metadata

### Features
- Enhanced hyperparameters
- SMOTE for class imbalance
- MLFlow experiment tracking
- Metrics saved to v2 directory

### Commands
```bash
# Run locally
python src/models/train_v2.py

# Trigger via workflow
gh workflow run train-v2.yml --ref main
```

---

## Stage 3: Canary Deployment (✅ Complete)
**Expected Output:** Traffic split live

### Files Created
- `.github/workflows/deploy-canary.yml` - Canary workflow
- `docker-compose.canary.yml` - Multi-service compose
- `canary_nginx.conf` - Nginx traffic splitting (95% v1 / 5% v2)

### Features
- 95% traffic → v1 (stable)
- 5% traffic → v2 (canary)
- Client IP-based consistent hashing
- Separate logging per version

### Deployment
```bash
# Deploy canary locally
docker-compose -f docker-compose.canary.yml up -d

# Access via nginx
curl http://localhost/api/predict  # Routes to v1 or v2 based on client IP
```

---

## Stage 4: Prometheus Metrics (✅ Complete)
**Expected Output:** Metrics exposed

### Files Created
- `src/api/metrics.py` - Prometheus metrics decorators
- `prometheus.yml` - Prometheus scrape config
- Metrics endpoint: `/metrics`

### Metrics Exposed
- `fraud_detection_predictions_total` - Prediction counter
- `fraud_detection_prediction_latency_seconds` - Latency histogram
- `fraud_detection_model_accuracy` - Model accuracy gauge
- `fraud_detection_model_f1_score` - F1 score gauge
- `fraud_detection_api_requests_total` - API request counter
- `fraud_detection_api_request_latency_seconds` - API latency histogram
- `fraud_detection_data_drift_detected` - Drift detection flag

### Access
```bash
# View metrics
curl http://localhost:8000/metrics

# Access Prometheus UI
http://localhost:9090
```

---

## Stage 5: Grafana Dashboard (✅ Complete)
**Expected Output:** Dashboard live

### Files Created
- `grafana_dashboard.json` - Complete dashboard definition
- 10 pre-configured panels

### Panels
1. Model Accuracy (by version)
2. Model F1 Score (by version)
3. Prediction Latency (p95)
4. Predictions per Minute
5. API Request Rate
6. API Error Rate
7. Data Drift Alerts
8. Deployed Model Versions
9. Active Alerts (stat)
10. System Health (stat)

### Access
```bash
# Start stack including Grafana
docker-compose -f docker-compose.canary.yml up -d

# Access dashboard
http://localhost:3000
# Login: admin / admin
```

---

## Stage 6: Drift Detection Job (✅ Complete)
**Expected Output:** Drift report

### Files Created
- `src/models/drift_detection.py` - Drift detection engine
- `.github/workflows/drift-detection.yml` - Automated job (every 6 hours)
- Drift reports in `models/drift_reports/`

### Features
- Kolmogorov-Smirnov statistical test
- Feature-level drift detection
- Prediction distribution drift
- Configurable thresholds (default 10%)

### Drift Report Contents
```json
{
  "timestamp": "2026-02-05T...",
  "drift_detected": false,
  "features_with_drift": [],
  "metrics": {
    "feature_name": {
      "mean_diff_pct": 5.2,
      "std_diff_pct": 3.1,
      "range_diff_pct": 2.8
    }
  }
}
```

---

## Stage 7: Drift Alerts (✅ Complete)
**Expected Output:** Alerts configured

### Files Created
- `alert_rules.yml` - Prometheus alert rules
- `alertmanager.yml` - Alert routing and management

### Alert Rules
1. **DataDriftDetected** - Warning when drift > threshold
2. **HighPredictionLatency** - Warning for p95 > 500ms
3. **LowModelAccuracy** - Critical if accuracy < 80%
4. **LowF1Score** - Critical if F1 < 60%
5. **HighAPIErrorRate** - Warning if error rate > 5%
6. **FraudDetectionServiceDown** - Critical if service unreachable
7. **HighMemoryUsage** - Warning if memory > 85%
8. **ModelRetrainingNeeded** - Info alert for persistent drift

### Alert Routing
- **Critical alerts** → Immediate notification
- **Warnings** → Batched every 5 minutes
- **Data quality** → Data team webhook
- **Model quality** → ML team webhook

---

## Stage 8: Rollback Automation (✅ Complete)
**Expected Output:** Auto rollback

### Files Created
- `src/models/rollback.py` - Rollback management
- `.github/workflows/rollback.yml` - Manual rollback trigger

### Features
- Version history tracking
- Automatic backup before rollback
- Version comparison (metrics delta)
- Audit trail recording

### Usage
```bash
# Trigger rollback
gh workflow run rollback.yml \
  -f target_version=v1.0.0 \
  -f reason="Critical accuracy drop detected"
```

### Rollback Process
1. Backup current version
2. Restore target version models
3. Update current_version.json
4. Record event in audit trail
5. Verify health checks

---

## Stage 9: Registry Audit Trail (✅ Complete)
**Expected Output:** Version history

### Files Created
- `registry_audit_trail.json` - JSON audit log
- `registry_audit_trail.csv` - CSV format for spreadsheet tools
- `src/models/registry.py` - Audit trail management

### Audit Trail Contents
```json
{
  "timestamp": "2026-02-05T...",
  "event_type": "deployment|training|rollback|canary_deployment",
  "version": "v1.0.0",
  "status": "success|failed|pending",
  "environment": "production|staging|development",
  "models": ["LogisticRegression", "RandomForest", ...],
  "triggered_by": "github-actions|user@domain.com",
  "commit": "abc123...",
  "details": {}
}
```

### Registry Queries
```python
from src.models.registry import RegistryAuditTrail

registry = RegistryAuditTrail()

# Get deployment history
deployments = registry.get_deployment_history()

# Get active versions
active = registry.get_active_versions()

# Get version info
info = registry.get_version_info('v1.0.0')

# Generate report
report = registry.generate_report(
  start_date='2026-01-01T00:00:00',
  end_date='2026-02-05T23:59:59'
)
```

---

## Complete Deployment Stack

### Local Testing
```bash
# Start all services (v1 + v2 + monitoring)
docker-compose -f docker-compose.canary.yml up -d

# Verify services
curl http://localhost/health           # Nginx health
curl http://localhost:8000/metrics     # API metrics
curl http://localhost:9090             # Prometheus UI
curl http://localhost:3000             # Grafana UI
curl http://localhost:9093             # Alertmanager UI
```

### GitHub Actions Workflows
1. **deploy-v1.yml** - Deploy v1 to production
2. **train-v2.yml** - Train new models (weekly)
3. **deploy-canary.yml** - Deploy canary (triggered after train-v2)
4. **drift-detection.yml** - Monitor drift (every 6 hours)
5. **rollback.yml** - Manual emergency rollback

### Directory Structure
```
models/
├── v1/                          # v1 models and metadata
├── v2/                          # v2 models and metadata
├── drift_reports/               # Drift detection reports
├── baseline_stats.json          # Training data baseline
├── metrics.json                 # Current metrics
├── current_version.json         # Active version info
├── version_history.json         # MLOps version tracking
└── rollback_backups/            # Backup versions for rollback
```

---

## Monitoring Dashboards

### Grafana (http://localhost:3000)
- Model accuracy trends
- Prediction latency distribution
- API error rates
- Data drift detection
- Alert status

### Prometheus (http://localhost:9090)
- Raw metrics queries
- Alert status
- Service discovery
- Recording rules

### Alertmanager (http://localhost:9093)
- Active alerts
- Alert routing rules
- Alert grouping
- Inhibition rules

---

## Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| Model Accuracy | < 80% | Alert - Consider retraining |
| F1 Score | < 60% | Alert - Model quality issue |
| Prediction Latency (p95) | > 500ms | Warning - Performance degradation |
| Data Drift | > 10% | Info - Monitor and consider retrain |
| API Error Rate | > 5% | Warning - Service health check |
| Service Uptime | < 99.9% | Alert - Investigate downtime |

---

## Troubleshooting

### Canary Not Splitting Traffic
```bash
# Check nginx logs
docker logs fraud-detection-nginx

# Verify routing config
docker exec fraud-detection-nginx nginx -T
```

### Prometheus Not Scraping Metrics
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets

# Verify FastAPI metrics endpoint
curl http://localhost:8000/metrics
```

### Rollback Failed
```bash
# Check version history
python -c "from src.models.rollback import ModelRollback; rm = ModelRollback(); print(rm.list_available_versions())"

# Verify backup exists
ls -la models/backup_*
```

---

## Next Steps

1. **Monitor canary** - Run for 24-48 hours
2. **Verify metrics** - Check accuracy delta is < 2%
3. **Promote to production** - If canary metrics are good
4. **Continue drift monitoring** - Schedule ongoing checks
5. **Scale infrastructure** - Add more replicas if needed

---

## Summary

✅ All 9 MLOps stages implemented:
- Stage 1: Dockerize v1 ✅
- Stage 2: Train v2 ✅
- Stage 3: Canary deployment ✅
- Stage 4: Prometheus metrics ✅
- Stage 5: Grafana dashboard ✅
- Stage 6: Drift detection ✅
- Stage 7: Drift alerts ✅
- Stage 8: Rollback automation ✅
- Stage 9: Registry audit trail ✅

System ready for production MLOps!
