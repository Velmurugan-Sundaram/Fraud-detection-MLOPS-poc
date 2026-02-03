# 🐳 Docker & AWS EC2 Deployment Guide

## Overview

This guide covers complete Docker containerization and deployment on AWS EC2 for the Fraud Detection MLOps POC.

---

## 📋 Prerequisites

### Local Machine (Build Docker Image)
- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- 4GB+ RAM for Docker
- Git (for version control)

### AWS (Deploy on EC2)
- AWS Account with EC2 access
- IAM role with EC2, ECR permissions
- EC2 instance: t3.medium or larger
- Security group configured
- Key pair for SSH access

---

## 🚀 Quick Start

### Local Development (Docker Compose)

```bash
# 1. Navigate to project
cd Fraud-Detection-Mlops-poc

# 2. Build image
docker build -t fraud-detection-mlops:latest .

# 3. Run with monitoring stack
docker-compose up -d

# 4. Check status
docker ps
docker logs -f fraud-detection-pipeline

# 5. Stop services
docker-compose down
```

**Total Time: ~10 minutes**

---

## 🛠️ Docker Files Included

### 1. **Dockerfile**
Multi-stage build optimized for production:
- Stage 1: Builder (with build tools)
- Stage 2: Runtime (slim, minimal)
- Non-root user for security
- Health checks enabled
- ~600MB final image size

### 2. **docker-compose.yml**
Complete stack with:
- Fraud detection pipeline container
- Prometheus for metrics
- Grafana for dashboards
- Volume mounts for data/logs
- Network configuration
- Resource limits

### 3. **.dockerignore**
Optimizes build context:
- Excludes unnecessary files
- Reduces build time
- Keeps image lean

### 4. **deploy-docker.ps1**
PowerShell automation script:
- Build images
- Run containers
- Stop/cleanup
- Test setup
- Push to registry

### 5. **setup-ec2.sh**
EC2 instance initialization:
- Install Docker & Docker Compose
- Create directories
- AWS CLI configuration
- ECR login setup

### 6. **ecs-task-definition.json**
AWS ECS deployment config:
- Task definition for ECS
- CloudWatch logging
- Port mappings
- Environment variables

---

## 📦 Docker Image Details

### Specification
```
Base Image:     python:3.11-slim
Image Size:     ~600-800 MB
Build Time:     ~5 minutes (first build)
User:           appuser (non-root)
Workdir:        /app
Health Check:   30s interval, 3 retries
```

### Installed Packages (30+)
- Data: pandas, pyarrow, numpy
- Quality: great-expectations, pandas-profiler, evidentlyai
- ML: scikit-learn, xgboost, lightgbm
- Testing: pytest
- API: fastapi, uvicorn
- Monitoring: prometheus-client
- And more...

---

## 🏗️ Local Testing with Docker

### Build Image

```bash
# Option 1: Using PowerShell script (Windows)
.\deploy-docker.ps1 -Action build

# Option 2: Manual build
docker build -t fraud-detection-mlops:latest .

# With custom tag
docker build -t fraud-detection-mlops:v1.0 .

# View image info
docker images fraud-detection-mlops
```

### Run Container (Standalone)

```bash
# Simple run
docker run fraud-detection-mlops:latest

# With volume mounts
docker run \
  --name fraud-detection \
  -v $(pwd)/dataset:/app/dataset:ro \
  -v $(pwd)/data:/app/data:rw \
  -v $(pwd)/logs:/app/logs:rw \
  fraud-detection-mlops:latest

# Interactive shell
docker run -it --rm fraud-detection-mlops:latest /bin/bash

# Run specific command
docker run fraud-detection-mlops:latest \
  python -c "import pandas; print(pandas.__version__)"
```

### Run with Docker Compose (Recommended)

```bash
# Start all services
docker-compose up

# Detached mode (background)
docker-compose up -d

# View specific logs
docker-compose logs -f fraud-detection-pipeline

# View all logs
docker-compose logs -f

# Stop services
docker-compose down

# Remove volumes too
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild image
docker-compose up --build
```

### Monitor Running Container

```bash
# View running containers
docker ps
docker ps -a  # Include stopped containers

# View logs
docker logs fraud-detection-pipeline
docker logs -f fraud-detection-pipeline  # Follow logs
docker logs --tail 50 fraud-detection-pipeline  # Last 50 lines
docker logs --timestamps fraud-detection-pipeline

# Check resource usage
docker stats fraud-detection-pipeline

# Inspect container
docker inspect fraud-detection-pipeline

# View processes
docker top fraud-detection-pipeline

# Execute command in running container
docker exec -it fraud-detection-pipeline bash
```

---

## 🌐 AWS EC2 Deployment

### Step 1: Launch EC2 Instance

**Using AWS Console:**
1. Go to EC2 Dashboard
2. Click "Launch Instance"
3. Select **Amazon Linux 2 AMI** (Free Tier eligible)
4. Instance type: **t3.medium** (2 vCPU, 4GB RAM)
5. Add storage: 50GB (gp2)
6. Add security group:
   - Allow SSH (22) from your IP
   - Allow HTTP (8000) from anywhere
   - Allow Prometheus (9090) from your IP
7. Review and launch
8. Select existing key pair or create new

**Using AWS CLI:**
```bash
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups fraud-detection-sg \
  --user-data file://setup-ec2.sh
```

### Step 2: Connect to Instance

```bash
# Get instance IP
INSTANCE_IP=$(aws ec2 describe-instances \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# SSH into instance
ssh -i your-key.pem ec2-user@$INSTANCE_IP

# Copy files to instance
scp -i your-key.pem -r . ec2-user@$INSTANCE_IP:/home/ec2-user/fraud-detection/
```

### Step 3: Setup Docker on EC2

```bash
# On EC2 instance:
cd /home/ec2-user/fraud-detection

# Make scripts executable
chmod +x setup-ec2.sh

# Run setup (installs Docker, Docker Compose, etc.)
./setup-ec2.sh

# Verify Docker installation
docker --version
docker-compose --version

# Test Docker
docker run hello-world
```

### Step 4: Build and Run on EC2

```bash
# On EC2 instance:
cd /home/ec2-user/fraud-detection

# Build image (takes ~5-10 minutes)
docker build -t fraud-detection-mlops:latest .

# Run with Docker Compose
docker-compose up -d

# Check status
docker ps
docker logs -f fraud-detection-pipeline
```

### Step 5: Access Results

```bash
# SSH into instance
ssh -i your-key.pem ec2-user@$INSTANCE_IP

# View output files
ls -lh /data/fraud-detection/validated/

# Download results to local machine
scp -i your-key.pem -r ec2-user@$INSTANCE_IP:/data/fraud-detection/validated/* ./data/validated/

# View logs
cat /logs/fraud-detection/pipeline.log
```

---

## 🔧 AWS ECR (Elastic Container Registry)

### Create ECR Repository

```bash
# Set variables
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
REPO=fraud-detection-mlops

# Create repository
aws ecr create-repository \
  --repository-name $REPO \
  --region $REGION

# Enable image scanning
aws ecr put-image-scanning-configuration \
  --repository-name $REPO \
  --image-scanning-configuration scanOnPush=true \
  --region $REGION
```

### Build and Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build image
docker build -t $REPO:latest .

# Tag for ECR
docker tag $REPO:latest \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:latest

# Push to ECR
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:latest

# Verify push
aws ecr list-images --repository-name $REPO --region $REGION
```

### Pull from ECR

```bash
# On EC2 instance:
# Login
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Pull image
docker pull $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:latest

# Run image
docker run $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$REPO:latest
```

---

## 📊 Monitoring

### Local Monitoring (Docker Compose)

```bash
# Prometheus
# http://localhost:9090
# Query: up{job="fraud-detection"}

# Grafana
# http://localhost:3000
# Credentials: admin / admin
```

### AWS CloudWatch Monitoring

```bash
# View logs
aws logs tail /ecs/fraud-detection-mlops --follow

# Create metric alarm
aws cloudwatch put-metric-alarm \
  --alarm-name fraud-detection-cpu \
  --alarm-description "Alert if CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# View metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --start-time 2024-02-01T00:00:00Z \
  --end-time 2024-02-02T00:00:00Z \
  --period 3600 \
  --statistics Average
```

---

## 🔒 Security Best Practices

### Image Security
- ✅ Non-root user (appuser)
- ✅ Read-only volumes for code
- ✅ Health checks enabled
- ✅ Minimal base image (slim)

### Container Security
```bash
# Run as read-only
docker run --read-only fraud-detection-mlops:latest

# Drop capabilities
docker run --cap-drop ALL fraud-detection-mlops:latest

# Resource limits
docker run -m 2g --cpus 1 fraud-detection-mlops:latest
```

### EC2 Security
```bash
# Use IAM role (not keys)
aws ec2 associate-iam-instance-profile \
  --instance-id i-0123456789abcdef0 \
  --iam-instance-profile Name=fraud-detection-ec2-role

# Enable VPC encryption
# Restrict security groups
# Use Systems Manager Session Manager (no SSH)
```

---

## 🧹 Cleanup

### Local Cleanup

```bash
# Stop and remove containers
docker-compose down -v

# Remove images
docker rmi fraud-detection-mlops:latest

# Remove dangling images
docker image prune

# Remove all unused
docker system prune -a
```

### AWS Cleanup

```bash
# Stop EC2 instance
aws ec2 stop-instances --instance-ids i-0123456789abcdef0

# Terminate instance (careful!)
aws ec2 terminate-instances --instance-ids i-0123456789abcdef0

# Delete ECR repository
aws ecr delete-repository --repository-name fraud-detection-mlops --force

# Delete CloudWatch logs
aws logs delete-log-group --log-group-name /ecs/fraud-detection-mlops
```

---

## 💰 Cost Estimation

### EC2 (On-Demand, us-east-1)
```
t3.medium:      $0.0416/hour  ≈ $30/month
t3.large:       $0.0832/hour  ≈ $60/month
t3.xlarge:      $0.1664/hour  ≈ $120/month
```

### Data Transfer
```
S3 → EC2 (same region):  Free
ECR bandwidth:           $0.02/GB
Data out to internet:    $0.09/GB
```

### Storage
```
EBS (gp2):  $0.10/GB-month
S3:         $0.023/GB-month
```

### Monitoring
```
CloudWatch logs:  $0.50/GB
CloudWatch metrics: Included (first 10,000)
```

**Estimated Monthly Cost: $35-100**

---

## 🚨 Troubleshooting

### Build Fails
```bash
# Clear build cache
docker builder prune

# Rebuild with verbose output
docker build --progress=plain -t fraud-detection-mlops .

# Check Dockerfile syntax
docker run --rm -i hadolint/hadolint < Dockerfile
```

### Container Won't Start
```bash
# Check logs
docker logs fraud-detection-pipeline

# Inspect configuration
docker inspect fraud-detection-pipeline

# Run with interactive shell
docker run -it --rm fraud-detection-mlops /bin/bash

# Check health
docker ps --filter "name=fraud-detection"
```

### Permission Issues
```bash
# On EC2, fix permissions
sudo chown -R ec2-user:ec2-user /data /logs
sudo chmod -R 755 /data /logs

# Docker daemon issues
sudo usermod -aG docker ec2-user
newgrp docker
```

### Out of Memory
```bash
# Increase swap
sudo dd if=/dev/zero of=/swapfile bs=1G count=4
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Check memory
free -h
docker stats
```

---

## 📚 Additional Resources

- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Docker Compose Spec](https://github.com/compose-spec/compose-spec)
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)

---

## ✅ Deployment Checklist

- [ ] Docker installed locally
- [ ] Dockerfile reviewed and tested
- [ ] docker-compose.yml verified
- [ ] Local test with `docker-compose up`
- [ ] AWS account configured
- [ ] EC2 instance launched
- [ ] Security groups configured
- [ ] Key pair created
- [ ] SSH connection tested
- [ ] Docker installed on EC2
- [ ] Image built on EC2
- [ ] Container running successfully
- [ ] Output files verified
- [ ] Monitoring configured
- [ ] Logs reviewed

---

## 🎯 Next Steps

1. ✅ Build Docker image locally
2. ✅ Test with docker-compose
3. ✅ Launch EC2 instance
4. ✅ Deploy container
5. → Monitor with CloudWatch
6. → Setup CI/CD pipeline
7. → Scale with ECS/Fargate

---

**Created:** 2024  
**Purpose:** Complete Docker & AWS deployment guide  
**Status:** Production-ready
