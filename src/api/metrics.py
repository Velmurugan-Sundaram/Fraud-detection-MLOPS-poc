"""Prometheus metrics instrumentation for FastAPI service"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
from functools import wraps

# Define metrics
prediction_counter = Counter(
    'fraud_detection_predictions_total',
    'Total number of fraud detection predictions',
    ['model_name', 'prediction_label']
)

prediction_latency = Histogram(
    'fraud_detection_prediction_latency_seconds',
    'Fraud detection prediction latency',
    ['model_name'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0)
)

model_accuracy = Gauge(
    'fraud_detection_model_accuracy',
    'Model accuracy on validation set',
    ['model_name', 'version']
)

model_f1_score = Gauge(
    'fraud_detection_model_f1_score',
    'Model F1 score on validation set',
    ['model_name', 'version']
)

data_drift_detected = Gauge(
    'fraud_detection_data_drift_detected',
    'Data drift detection flag',
    ['feature']
)

model_versions_deployed = Gauge(
    'fraud_detection_model_versions_deployed',
    'Number of model versions deployed',
    ['version']
)

api_requests_total = Counter(
    'fraud_detection_api_requests_total',
    'Total API requests',
    ['endpoint', 'method', 'status']
)

api_request_latency = Histogram(
    'fraud_detection_api_request_latency_seconds',
    'API request latency',
    ['endpoint', 'method'],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)
)


def track_prediction(model_name: str):
    """Decorator to track prediction metrics
    
    Args:
        model_name: Name of the model making the prediction
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                
                # Track prediction
                prediction_label = str(result.get('prediction', 'unknown'))
                prediction_counter.labels(
                    model_name=model_name,
                    prediction_label=prediction_label
                ).inc()
                
                # Track latency
                latency = time.time() - start_time
                prediction_latency.labels(model_name=model_name).observe(latency)
                
                return result
            except Exception as e:
                prediction_counter.labels(
                    model_name=model_name,
                    prediction_label='error'
                ).inc()
                raise
        
        return wrapper
    return decorator


def track_api_request(endpoint: str, method: str):
    """Decorator to track API request metrics
    
    Args:
        endpoint: API endpoint path
        method: HTTP method
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = 'unknown'
            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                # Track metrics
                api_requests_total.labels(
                    endpoint=endpoint,
                    method=method,
                    status=status
                ).inc()
                
                latency = time.time() - start_time
                api_request_latency.labels(
                    endpoint=endpoint,
                    method=method
                ).observe(latency)
        
        return wrapper
    return decorator


def get_metrics():
    """Generate Prometheus metrics in text format"""
    return generate_latest(REGISTRY)
