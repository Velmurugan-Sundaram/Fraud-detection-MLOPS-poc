# Docker Deployment Guide - Fraud Detection MLOps POC

## Quick Start (Local Testing with Docker)

### 1. Build Docker Image
```bash
cd c:\Users\mangeshd\Documents\Fraud-Detection-Mlops-poc
docker build -t fraud-detection-mlops:latest .
```

### 2. Run with Docker Compose (Recommended)
```bash
# Start all services (pipeline + monitoring)
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f fraud-detection-pipeline

# Stop services
docker-compose down
```

### 3. Run Standalone Container
```bash
docker run \
  --name fraud-detection \
  -v $(pwd)/dataset:/app/dataset:ro \
  -v $(pwd)/data:/app/data:rw \
  -v $(pwd)/logs:/app/logs:rw \
  fraud-detection-mlops:latest
```

---

## AWS EC2 Deployment

### Prerequisites
- AWS Account with EC2 access
- IAM permissions for ECR, EC2
- EC2 instance (t3.medium or larger)
- Security group with ports: 22 (SSH), 8000 (API), 9090 (Prometheus)

### Step 1: Launch EC2 Instance

```bash
# AWS CLI command to launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups fraud-detection-sg \
  --region us-east-1 \
  --user-data file://setup-ec2.sh
```

Or use AWS Console:
1. Go to EC2 Dashboard
2. Launch new instance
3. Choose Amazon Linux 2 AMI
4. Instance type: t3.medium or larger
5. Assign security group (allow 22, 8000, 9090)
6. User data script: Copy content from `setup-ec2.sh`

### Step 2: Connect to EC2 Instance

```bash
# Get public IP
INSTANCE_IP=$(aws ec2 describe-instances \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text)

# SSH into instance
ssh -i your-key.pem ec2-user@$INSTANCE_IP
```

### Step 3: Setup & Deploy on EC2

```bash
# SSH into the instance, then run:

# Clone or upload project
# Option A: Use git (if repo exists)
git clone https://github.com/YOUR_ORG/fraud-detection-mlops-poc.git
cd fraud-detection-mlops-poc

# Option B: Upload files (from local machine)
scp -i your-key.pem -r . ec2-user@$INSTANCE_IP:/home/ec2-user/fraud-detection-mlops/

# On EC2 instance:
cd ~/fraud-detection-mlops

# Make setup script executable
chmod +x setup-ec2.sh

# Run setup (only first time)
./setup-ec2.sh

# Build Docker image
docker build -t fraud-detection-mlops:latest .

# Run with Docker Compose
docker-compose up -d
```

### Step 4: Monitor Pipeline

```bash
# Check running containers
docker ps

# View pipeline logs
docker logs -f fraud-detection-pipeline

# Access monitoring (if enabled)
# Prometheus: http://EC2_IP:9090
# Grafana: http://EC2_IP:3000
```

---

## AWS ECR (Elastic Container Registry) Deployment

### Step 1: Create ECR Repository

```bash
# Set variables
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
REPO_NAME=fraud-detection-mlops

# Create repository
aws ecr create-repository \
  --repository-name $REPO_NAME \
  --region $REGION
```

### Step 2: Build & Push Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region $REGION | \
  docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com

# Build image
docker build -t fraud-detection-mlops:latest .

# Tag image for ECR
docker tag fraud-detection-mlops:latest \
  $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/fraud-detection-mlops:latest

# Push to ECR
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/fraud-detection-mlops:latest
```

### Step 3: Deploy with ECS (Optional)

```bash
# Register task definition
aws ecs register-task-definition \
  --cli-input-json file://ecs-task-definition.json \
  --region $REGION

# Create cluster
aws ecs create-cluster --cluster-name fraud-detection-cluster --region $REGION

# Run task
aws ecs run-task \
  --cluster fraud-detection-cluster \
  --task-definition fraud-detection-mlops \
  --region $REGION
```

---

## Data Handling

### Option 1: Volume Mounts
```bash
# Dataset stored locally on EC2
docker-compose up
```

### Option 2: S3 Integration
```bash
# Download dataset from S3
aws s3 cp s3://YOUR_BUCKET/creditcard.csv data/raw/

# Run pipeline
docker-compose up
```

### Option 3: Download from Kaggle
```bash
# Inside container, download from Kaggle API
pip install kaggle
kaggle datasets download -d mlg-ulb/creditcardfraud
unzip creditcardfraud.zip -d data/raw/
```

---

## Environment Variables

### Local (docker-compose.yml)
```yaml
environment:
  - PYTHONUNBUFFERED=1
  - LOG_LEVEL=INFO
  - ENV=development
```

### EC2 Production (.env file)
```bash
# Create .env file
cat > .env << EOF
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO
ENV=production
AWS_REGION=us-east-1
AWS_BUCKET=your-bucket-name
DATABASE_URL=postgres://user:pass@host:5432/db
MLFLOW_TRACKING_URI=http://your-mlflow-server
EOF

# Load with docker-compose
docker-compose --env-file .env up
```

---

## Monitoring & Logs

### View Container Logs
```bash
# Real-time logs
docker logs -f fraud-detection-pipeline

# Last 100 lines
docker logs --tail 100 fraud-detection-pipeline

# Timestamps
docker logs -f --timestamps fraud-detection-pipeline
```

### AWS CloudWatch Logs
```bash
# View logs in CloudWatch
aws logs tail /ecs/fraud-detection-mlops --follow --region us-east-1
```

### Prometheus Metrics
```bash
# Access at http://EC2_IP:9090
# Query examples:
# - up{job="fraud-detection"}
# - process_resident_memory_bytes
```

### Grafana Dashboard
```bash
# Access at http://EC2_IP:3000
# Default credentials: admin / admin
# Create dashboards from Prometheus metrics
```

---

## Troubleshooting

### Docker Build Issues
```bash
# Clear build cache
docker builder prune

# Rebuild with verbose output
docker build --progress=plain -t fraud-detection-mlops:latest .

# Check image size
docker images fraud-detection-mlops
```

### Container Won't Start
```bash
# Check logs
docker logs fraud-detection-pipeline

# Inspect container
docker inspect fraud-detection-pipeline

# Run interactive shell
docker run -it --rm fraud-detection-mlops:latest /bin/bash
```

### Permission Issues
```bash
# Fix permission issues
sudo chown -R ec2-user:ec2-user /data /logs
sudo chmod -R 755 /data /logs
```

### Out of Memory
```bash
# Increase memory in docker-compose.yml
services:
  fraud-detection-pipeline:
    deploy:
      resources:
        limits:
          memory: 8G

# Restart services
docker-compose restart
```

---

## Performance Optimization

### Image Size Optimization
Current size: ~600-800 MB (multi-stage build)

```bash
# View layer sizes
docker history fraud-detection-mlops:latest

# Further optimization:
# 1. Use slim Python image (already done)
# 2. Remove build dependencies in Stage 2
# 3. Compress with UPX (optional, risky)
```

### Runtime Performance
```bash
# Monitor resource usage
docker stats fraud-detection-pipeline

# Adjust limits in docker-compose.yml based on EC2 instance type
```

---

## Security Best Practices

### Image Security
- ✅ Non-root user (appuser)
- ✅ Read-only volume for code
- ✅ Health checks enabled
- ✅ Environment variables for secrets

### EC2 Security
- ✅ Security group restrictions
- ✅ SSH key-pair authentication
- ✅ CloudWatch logging
- ✅ IAM role for EC2 instance

### Additional Steps
```bash
# Use AWS Secrets Manager
docker run \
  -e AWS_REGION=us-east-1 \
  -v ~/.aws/credentials:/home/appuser/.aws/credentials:ro \
  fraud-detection-mlops:latest

# Scan image for vulnerabilities
docker scan fraud-detection-mlops:latest

# Use private ECR repository
aws ecr put-image-scanning-configuration \
  --repository-name fraud-detection-mlops \
  --image-scanning-configuration scanOnPush=true
```

---

## Cost Estimation (AWS)

### EC2 Instance
- t3.medium: ~$0.0416/hour (~$30/month)
- t3.large: ~$0.0832/hour (~$60/month)

### Data Transfer
- S3 to EC2: Free (same region)
- ECR bandwidth: ~$0.02/GB

### Storage
- EBS volume (100GB): ~$10/month
- S3 (dataset): ~$0.023/GB

### Monitoring
- CloudWatch: ~$0.50-2/month
- CloudWatch Logs: ~$0.50/GB

**Estimated Monthly Cost: $30-80** (for t3.medium instance)

---

## Cleanup

### Remove Containers
```bash
docker-compose down -v  # Remove volumes too
docker container prune
```

### Remove Images
```bash
docker rmi fraud-detection-mlops:latest
docker image prune
```

### Stop EC2 Instance
```bash
aws ec2 stop-instances --instance-ids i-0123456789abcdef0
aws ec2 terminate-instances --instance-ids i-0123456789abcdef0
```

---

## Next Steps

1. ✅ Build Docker image
2. ✅ Test locally with docker-compose
3. ✅ Push to ECR
4. ✅ Deploy on EC2
5. → Monitor with CloudWatch/Prometheus
6. → Scale with ECS/Fargate
7. → Setup CI/CD pipeline

---

## Support

For issues:
1. Check Docker logs: `docker logs fraud-detection-pipeline`
2. Review setup script: `setup-ec2.sh`
3. Check AWS documentation
4. Review project documentation: [README.md](README.md)

---

**Created:** 2024  
**Purpose:** Docker deployment for AWS EC2  
**Status:** Ready to deploy
