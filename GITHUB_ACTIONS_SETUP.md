# 🚀 GitHub Actions CI/CD Pipeline Setup

## Overview

Complete CI/CD pipeline for the Fraud Detection MLOps project using GitHub Actions. Automated testing, validation, and deployment of the ML pipeline.

---

## 📋 Workflow Files

### 1. **ML Pipeline CI** (`ml-pipeline-ci.yml`)
**Trigger:** Push or PR to `Mangesh_m1` branch, or manual trigger

**Stages:**
1. ✅ **Setup & Unit Tests**
   - Python environment setup
   - Dependencies installation
   - Code linting (Pylint)
   - Unit tests with coverage

2. ✅ **Data Ingestion & Validation**
   - Load data from source
   - Validate data schema
   - Data quality checks
   - Save validated data

3. ✅ **Feature Engineering**
   - Feature transformations
   - Feature scaling
   - Train/test splitting
   - Feature metadata

4. ✅ **Feature Consistency Checks (Parity Verified)**
   - Parity verification
   - Data leakage detection
   - Distribution analysis
   - Class balance validation
   - Generate consistency report

5. ✅ **Model Training + MLFlow (Model v1 Registration)**
   - Train 4 models (LogisticRegression, RandomForest, XGBoost, LightGBM)
   - Handle class imbalance (SMOTE)
   - MLFlow experiment tracking
   - Save metrics

6. ✅ **Model Comparison & Selection (Best Model Selected)**
   - Compare model performance
   - Calculate composite scores
   - Select best model
   - Generate comparison report

7. ✅ **FastAPI Service Validation**
   - Validate API initialization
   - Check model loading
   - Verify service readiness

8. ✅ **Integration Tests**
   - Run full test suite
   - Generate coverage reports
   - Upload test results

**Artifacts:**
- Trained models (.pkl files)
- Metrics (JSON)
- Model comparison report
- Feature consistency report
- Test results

---

### 2. **ML Pipeline CD** (`ml-pipeline-cd.yml`)
**Trigger:** Successful completion of CI workflow

**Stages:**
1. Download CI artifacts
2. Validate models
3. Generate deployment status
4. Success notification

**Purpose:** Post-CI deployment checks and readiness validation

---

### 3. **PR Validation** (`pr-validation.yml`)
**Trigger:** Pull request to `Mangesh_m1` or `main` branch

**Checks:**
- Code formatting (Black)
- Import sorting (isort)
- Linting (Pylint, Flake8)
- Unit tests with coverage
- Data pipeline validation
- Feature pipeline validation
- Model pipeline validation
- API initialization

**Artifacts:**
- Coverage reports (HTML)
- Coverage badge

---

## 🔧 Setup Instructions

### 1. Add Workflow Files to Repository

Copy the workflow files to your repository:
```
.github/
└── workflows/
    ├── ml-pipeline-ci.yml
    ├── ml-pipeline-cd.yml
    └── pr-validation.yml
```

### 2. Update Branch Configuration

The workflows are configured for the `Mangesh_m1` branch. Update if needed:

```yaml
# In each workflow file:
on:
  push:
    branches:
      - Mangesh_m1  # Change if using different branch name
```

### 3. Configure Repository Secrets (Optional)

Add these secrets in GitHub repository settings (`Settings > Secrets and variables > Actions`):

```
MLFLOW_TRACKING_URI=http://localhost:5000
# Add any API keys needed for deployment
```

### 4. Enable GitHub Actions

1. Go to `Settings > Actions`
2. Select "All workflows can run"
3. Enable by selecting "Allow all actions and reusable workflows"

---

## 📊 Workflow Execution

### CI Pipeline Flow

```
┌─────────────────────────────────────┐
│    Push to Mangesh_m1 branch        │
└────────────────┬────────────────────┘
                 │
         ┌───────▼────────┐
         │  Setup & Tests │
         └───────┬────────┘
                 │
      ┌──────────▼──────────┐
      │ Data Ingestion      │
      │ & Validation        │
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────┐
      │ Feature Engineering │
      └──────────┬──────────┘
                 │
      ┌──────────▼──────────────────────┐
      │ Feature Consistency Checks      │
      │ (Parity Verified)               │
      └──────────┬──────────────────────┘
                 │
      ┌──────────▼──────────────────────┐
      │ Model Training + MLFlow         │
      │ (Model v1 Registered)           │
      └──────────┬──────────────────────┘
                 │
      ┌──────────▼──────────────────────┐
      │ Model Comparison & Selection    │
      │ (Best Model Selected)           │
      └──────────┬──────────────────────┘
                 │
      ┌──────────▼──────────────────────┐
      │ FastAPI Service Validation      │
      └──────────┬──────────────────────┘
                 │
      ┌──────────▼──────────────────────┐
      │ Integration Tests               │
      └──────────┬──────────────────────┘
                 │
      ┌──────────▼──────────────────────┐
      │ Final Report & Artifacts        │
      └──────────┬──────────────────────┘
                 │
         ┌───────▼────────┐
         │  CD Deployment │
         │   Validation   │
         └────────────────┘
```

---

## 🎯 Key Features

### Automated Stages

1. **Code Quality**
   - Linting (Pylint, Flake8)
   - Formatting (Black)
   - Import sorting (isort)

2. **Testing**
   - Unit tests
   - Integration tests
   - Coverage reports

3. **Data Pipeline**
   - Data ingestion
   - Data validation
   - Schema checking

4. **Feature Pipeline**
   - Feature engineering
   - Feature scaling
   - Data splitting
   - Parity verification
   - Consistency checks

5. **Model Pipeline**
   - Model training (4 models)
   - MLFlow tracking
   - Automatic model registration (v1)
   - Model comparison
   - Best model selection

6. **API Validation**
   - FastAPI service initialization
   - Model loading verification
   - Service readiness check

---

## 📊 Artifact Management

### Generated Artifacts

```
Trained Models:
├── LogisticRegression_model.pkl
├── RandomForest_model.pkl
├── XGBoost_model.pkl
└── LightGBM_model.pkl

Reports:
├── metrics.json
├── model_info.json
├── model_comparison_report.json
├── feature_consistency_report.json
└── ci_report.txt

Tests:
├── coverage.xml
└── test_results.txt
```

### Artifact Retention

- **Default:** 30 days
- **Configurable:** Edit retention-days in workflow files

### Download Artifacts

1. Go to Actions tab
2. Select completed workflow run
3. Scroll to "Artifacts" section
4. Download desired artifacts

---

## 🔔 Notifications

### GitHub Notifications

- Workflow completion emails
- Check failures (can be configured)
- PR comments with coverage reports

### Custom Notifications (Optional)

Add to workflow for Slack/email notifications:

```yaml
- name: Slack Notification
  uses: slackapi/slack-github-action@v1.24.0
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "ML Pipeline CI Completed",
        "blocks": [...]
      }
```

---

## 🐛 Troubleshooting

### Workflow Failures

1. **Check logs:** Go to Actions > Run > Step details
2. **Common issues:**
   - Missing dependencies: Check `requirements.txt`
   - Data path issues: Verify config paths
   - Memory issues: Check runner resource limits

### Re-running Workflows

```bash
# Re-run failed job from GitHub UI
# or use GitHub CLI:
gh run rerun <run-id>
```

### Debugging

Enable debug logging:

```yaml
env:
  ACTIONS_STEP_DEBUG: true
  RUNNER_DEBUG: true
```

---

## 📈 Monitoring & Analytics

### View Workflow Status

1. Go to `Actions` tab
2. Select workflow
3. View run history
4. Click on run for details

### Check Coverage Trends

1. Visit Codecov integration
2. View coverage history
3. Track improvements

### Performance Metrics

Monitor in Actions tab:
- Total execution time
- Time per stage
- Resource usage

---

## 🔐 Security Best Practices

### Secrets Management

1. Never commit secrets
2. Use GitHub Secrets for sensitive data
3. Reference as `${{ secrets.SECRET_NAME }}`

### Branch Protection

Configure in Settings > Branches:
```
- Require status checks to pass
- Require code reviews
- Dismiss stale reviews
- Require branches up to date
```

### Dependency Security

- Keep dependencies updated
- Use `pip-audit` for vulnerabilities
- Review dependabot alerts

---

## 📝 Customization

### Add New Workflow

Create new file in `.github/workflows/`:

```yaml
name: Custom Workflow
on:
  push:
    branches: [Mangesh_m1]
jobs:
  custom-job:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # Add your steps
```

### Modify Triggers

Change workflow triggers:

```yaml
# Options:
on:
  push:
    branches: [branch-name]
  pull_request:
    branches: [branch-name]
  schedule:
    - cron: '0 2 * * *'  # Daily 2 AM UTC
  workflow_dispatch:     # Manual trigger
```

### Add Environment Variables

```yaml
env:
  PYTHON_VERSION: '3.10'
  MODEL_REGISTRY: 'mlflow'
```

---

## 🚀 Next Steps

### 1. Push to Branch

```bash
git checkout Mangesh_m1
git push origin Mangesh_m1
```

### 2. Monitor Execution

- Go to GitHub repository
- Click `Actions` tab
- Watch workflow execution

### 3. Review Artifacts

- After workflow completes
- Download artifacts
- Review reports

### 4. Configure Deployment

```yaml
# Optional: Add deployment step
- name: Deploy to Staging
  run: |
    # Your deployment commands
```

---

## 📚 References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Artifacts](https://docs.github.com/en/actions/using-workflows/storing-workflow-data-as-artifacts)

---

## ✅ Verification Checklist

Before deploying workflows:

- [ ] Workflow files in `.github/workflows/` directory
- [ ] Branch name correct (Mangesh_m1)
- [ ] Dependencies in `requirements.txt`
- [ ] Configuration in `src/config/config.yaml`
- [ ] Tests in `tests/` directory
- [ ] All modules importable
- [ ] Secrets configured (if needed)
- [ ] Branch protection rules set

---

## 📊 Status Badge

Add to your README:

```markdown
[![ML Pipeline CI](https://github.com/mangesh-deshmane/Fraud-Detection-Mlops-poc/actions/workflows/ml-pipeline-ci.yml/badge.svg?branch=Mangesh_m1)](https://github.com/mangesh-deshmane/Fraud-Detection-Mlops-poc/actions/workflows/ml-pipeline-ci.yml)

[![PR Validation](https://github.com/mangesh-deshmane/Fraud-Detection-Mlops-poc/actions/workflows/pr-validation.yml/badge.svg)](https://github.com/mangesh-deshmane/Fraud-Detection-Mlops-poc/actions/workflows/pr-validation.yml)
```

---

**Last Updated:** February 4, 2026
**Status:** ✅ Ready for Use

For support or issues, check the Actions logs or the project documentation.
