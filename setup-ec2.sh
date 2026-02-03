#!/bin/bash
# AWS EC2 Instance Setup Script for Fraud Detection MLOps POC
# Usage: bash setup-ec2.sh
# This script sets up Docker and pulls/runs the fraud detection container on EC2

set -e

echo "=========================================="
echo "Fraud Detection MLOps - EC2 Setup Script"
echo "=========================================="

# Update system
echo "[1/8] Updating system packages..."
sudo yum update -y

# Install Docker
echo "[2/8] Installing Docker..."
sudo yum install -y docker
sudo usermod -aG docker ec2-user
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
echo "[3/8] Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version

# Install AWS CLI (if not present)
echo "[4/8] Installing AWS CLI..."
sudo yum install -y aws-cli

# Create data directories
echo "[5/8] Creating data directories..."
sudo mkdir -p /data/fraud-detection/dataset
sudo mkdir -p /data/fraud-detection/validated
sudo mkdir -p /logs/fraud-detection
sudo chown -R ec2-user:ec2-user /data /logs

# Download dataset from S3 (if configured)
echo "[6/8] Attempting to download dataset from S3..."
# Uncomment and modify if you have S3 bucket configured
# aws s3 cp s3://YOUR_BUCKET/creditcard.csv /data/fraud-detection/dataset/

echo "[7/8] Logging in to ECR..."
# Get AWS account ID (modify region if needed)
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}
echo "AWS Account: $AWS_ACCOUNT_ID, Region: $AWS_REGION"

# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "[8/8] Setup complete!"
echo ""
echo "Next steps:"
echo "1. Build image: docker build -t fraud-detection-mlops:latest ."
echo "2. Tag image: docker tag fraud-detection-mlops:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/fraud-detection-mlops:latest"
echo "3. Push to ECR: docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/fraud-detection-mlops:latest"
echo "4. Run locally: docker-compose up"
echo ""
echo "=========================================="
