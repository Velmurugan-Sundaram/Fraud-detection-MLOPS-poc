# GitHub Actions - Quick Reference Guide

## 🚀 Workflows Overview

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **CI Pipeline** | `ml-pipeline-ci.yml` | Push/PR to `Mangesh_m1` | Complete ML pipeline execution |
| **CD Pipeline** | `ml-pipeline-cd.yml` | Successful CI completion | Deployment validation |
| **PR Validation** | `pr-validation.yml` | PR to `Mangesh_m1`/`main` | Code quality & tests |

---

## 🔄 Pipeline Stages

### CI Pipeline - 8 Stages

```
1. Setup & Unit Tests
   ├─ Python environment
   ├─ Dependencies
   ├─ Linting
   └─ Unit tests + coverage

2. Data Ingestion & Validation
   ├─ Load data
   ├─ Schema validation
   └─ Quality checks

3. Feature Engineering
   ├─ Feature transformations
   ├─ Scaling
   └─ Data splitting

4. Feature Consistency Checks
   ├─ Parity verification
   ├─ Leakage detection
   └─ Distribution analysis

5. Model Training + MLFlow
   ├─ Train 4 models
   ├─ SMOTE resampling
   ├─ MLFlow tracking
   └─ Model registration (v1)

6. Model Comparison & Selection
   ├─ Compare metrics
   ├─ Calculate scores
   ├─ Select best model
   └─ Generate report

7. FastAPI Service Validation
   ├─ API initialization
   ├─ Model loading
   └─ Service readiness

8. Integration Tests
   ├─ Full test suite
   ├─ Coverage reports
   └─ Result upload
```

---

## 📊 Artifacts Generated

### After Successful CI Run

```
Trained Models:
  └─ trained-models/
     ├─ LogisticRegression_model.pkl
     ├─ RandomForest_model.pkl
     ├─ XGBoost_model.pkl
     └─ LightGBM_model.pkl

Reports:
  └─ models/
     ├─ metrics.json
     ├─ model_info.json
     └─ model_comparison_report.json

Tests:
  └─ test-results/
     └─ coverage.xml

CI Report:
  └─ ci-report/
     └─ ci_report.txt
```

---

## 🔧 How to Use

### 1. Initial Setup

```bash
# Clone repository
git clone https://github.com/mangesh-deshmane/Fraud-Detection-Mlops-poc.git
cd Fraud-Detection-Mlops-poc

# Ensure workflows are in place
ls -la .github/workflows/

# Should show:
# - ml-pipeline-ci.yml
# - ml-pipeline-cd.yml
# - pr-validation.yml
```

### 2. Create/Push to Mangesh_m1 Branch

```bash
# Create branch if it doesn't exist
git checkout -b Mangesh_m1

# Make changes
git add .
git commit -m "Add ML pipeline implementation"

# Push to trigger CI
git push origin Mangesh_m1
```

### 3. Monitor Workflow Execution

**Option A: GitHub Web UI**
1. Go to repository
2. Click `Actions` tab
3. Select workflow
4. Watch real-time execution

**Option B: GitHub CLI**
```bash
# List workflows
gh workflow list

# Watch workflow run
gh run watch <run-id>

# View workflow status
gh run list --branch Mangesh_m1

# Download artifacts
gh run download <run-id>
```

---

## 📥 Download Artifacts

### Via GitHub Web UI

1. Go to Actions tab
2. Click completed workflow run
3. Scroll to "Artifacts" section
4. Download desired artifact

### Via GitHub CLI

```bash
# List artifacts from specific run
gh run view <run-id>

# Download all artifacts
gh run download <run-id>

# Download specific artifact
gh run download <run-id> -n trained-models
```

---

## 🔍 View Logs

### Web UI

```
Actions > Workflow > Run > Step Name > View Log
```

### GitHub CLI

```bash
# View all logs
gh run view <run-id> --log

# View specific job logs
gh run view <run-id> --log --job <job-id>

# Follow running workflow
gh run watch <run-id> --log
```

---

## ✅ Status Checks

### PR Status Checks

Before merging PR, ensure all checks pass:
- ✅ Code Quality
- ✅ Test Coverage
- ✅ Data Validation
- ✅ Feature Pipeline
- ✅ Model Pipeline

### Bypass Checks (if needed)

```bash
# Force push (use with caution)
git push --force-with-lease origin Mangesh_m1
```

---

## 🐛 Troubleshooting

### Workflow Failed

1. **Check logs:**
   - Actions > Failed Run > Failed Step > View Log

2. **Common issues:**
   - Missing dependencies → Check `requirements.txt`
   - Data not found → Verify paths in `config.yaml`
   - Import errors → Check file structure

3. **Fix and retry:**
   ```bash
   git add .
   git commit -m "Fix: [issue description]"
   git push origin Mangesh_m1
   ```

### Re-run Failed Workflow

**Via Web UI:**
- Actions > Failed Run > Re-run Jobs

**Via CLI:**
```bash
gh run rerun <run-id>
```

### Debug Mode

Enable debug logging:

```bash
# Set environment variable
export RUNNER_DEBUG=true
export ACTIONS_STEP_DEBUG=true

# Push changes
git push origin Mangesh_m1
```

---

## 🚀 Deployment Checklist

Before production deployment:

- [ ] All CI checks passing
- [ ] Coverage reports reviewed
- [ ] Models downloaded and validated
- [ ] Metrics verified
- [ ] FastAPI service tested
- [ ] No data quality issues
- [ ] Feature consistency verified
- [ ] Model comparison report reviewed

---

## 📋 Common Commands

### GitHub CLI Installation

```bash
# macOS
brew install gh

# Windows (Chocolatey)
choco install gh

# Linux
# Download from https://github.com/cli/cli/releases
```

### Essential Commands

```bash
# Login to GitHub
gh auth login

# List all workflows
gh workflow list

# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id> -n <artifact-name>

# Re-run workflow
gh run rerun <run-id>

# View logs
gh run view <run-id> --log

# Create pull request
gh pr create --base main --head Mangesh_m1

# View PR status
gh pr view
```

---

## 📊 Monitoring

### Track Workflow Performance

1. Go to Actions tab
2. Click workflow name
3. View run history
4. Analyze execution times

### Check Coverage Trends

1. Actions > PR Validation > Coverage Report
2. Download HTML coverage report
3. Review coverage.html locally

---

## 🔐 Security

### Secrets Setup

1. Go to Settings > Secrets and Variables > Actions
2. Click "New repository secret"
3. Add secret (e.g., MLFLOW_TRACKING_URI)
4. Reference in workflow: `${{ secrets.SECRET_NAME }}`

### Branch Protection

1. Settings > Branches
2. Add rule for `Mangesh_m1`
3. Enable:
   - ✅ Require status checks
   - ✅ Require code reviews
   - ✅ Dismiss stale reviews

---

## 📈 Success Indicators

✅ Workflow succeeds when:
- All stages complete without error
- All tests pass
- Coverage reports generated
- Artifacts uploaded successfully
- Final report available

---

## 🎯 Next Steps

### 1. Verify Setup
```bash
git push origin Mangesh_m1
# Wait 2-5 minutes
# Check Actions tab
```

### 2. Download Results
```bash
gh run download <run-id>
ls -la
```

### 3. Review Artifacts
- Check metrics.json
- Review model comparison report
- Analyze feature consistency report

### 4. Ready for Production
- All checks passed ✅
- Models trained and registered
- API validated
- Tests passing

---

## 📞 Support

**Issues?**
1. Check workflow logs: Actions > Failed Run
2. Review `GITHUB_ACTIONS_SETUP.md`
3. Check GitHub Actions documentation

**Useful Links:**
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Action Marketplace](https://github.com/marketplace?type=actions)

---

**Last Updated:** February 4, 2026
**Status:** ✅ Ready to Use
