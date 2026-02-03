"""Constants and configurations"""

# Dataset constants
FRAUD_LABEL = "Class"
LEGITIMATE_CLASS = 0
FRAUD_CLASS = 1

# Model constants
RANDOM_STATE = 42
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Performance thresholds
MIN_PRECISION = 0.90
MIN_RECALL = 0.80
MIN_F1 = 0.85

# Data quality thresholds
MIN_COMPLETENESS = 0.95
MAX_DUPLICATES = 0.01
OUTLIER_THRESHOLD = 3.0
