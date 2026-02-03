#!/bin/bash
set -e

echo "Starting Fraud Detection Pipeline..."

echo "-----------------------------------"
echo "Step 1: Data Ingestion"
echo "-----------------------------------"
python src/data_ingestion.py

echo "-----------------------------------"
echo "Step 2: Data Validation"
echo "-----------------------------------"
python src/data_validation.py

echo "-----------------------------------"
echo "Pipeline Completed Successfully!"
echo "-----------------------------------"
