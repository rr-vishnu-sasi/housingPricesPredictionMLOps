"""
Flask API for Housing Price Prediction
Serves the trained ML model with Redis caching
"""

from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd
import json
import hashlib
import os
from pathlib import Path
import redis
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Redis connection (with fallback if Redis not available)
try:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    cache = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    cache.ping()  # Test connection
    REDIS_AVAILABLE = True
    logger.info(f"✅ Redis connected: {redis_host}:{redis_port}")
except:
    REDIS_AVAILABLE = False
    cache = None
    logger.warning("⚠️  Redis not available - caching disabled")

# Load model artifacts
MODEL_DIR = Path("models/saved_models")

def load_artifacts():
    """Load trained model and preprocessing artifacts"""
    global model, scaler, encoder, feature_names

    try:
        # Find latest model
        model_files = list(MODEL_DIR.glob("model_*.joblib"))
        if not model_files:
            raise FileNotFoundError("No model files found!")

        latest_model = max(model_files, key=lambda x: x.stat().st_mtime)

        logger.info(f"Loading model: {latest_model.name}")
        model = joblib.load(latest_model)

        # Load preprocessing artifacts
        scaler = joblib.load(MODEL_DIR / "scaler.joblib")
        encoder = joblib.load(MODEL_DIR / "encoder.joblib")
        feature_names = joblib.load(MODEL_DIR / "feature_names.joblib")

        logger.info("✅ Model artifacts loaded successfully!")
        logger.info(f"   Features: {len(feature_names)}")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to load model: {str(e)}")
        return False

# Load on startup
model, scaler, encoder, feature_names = None, None, None, None
load_artifacts()


def create_cache_key(data):
    """Create cache key from input data"""
    # Convert data to string and hash it
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()


def preprocess_input(house_data):
    """Preprocess single house data for prediction"""
    # Expected features in order
    base_features = [
        'median_income', 'housing_median_age', 'total_rooms',
        'total_bedrooms', 'population', 'households',
        'latitude', 'longitude', 'ocean_proximity'
    ]

    # Extract values in correct order
    values = [house_data.get(f) for f in base_features]

    # Create DataFrame
    df = pd.DataFrame([values], columns=base_features)

    # Create derived features (same as training!)
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']

    # Separate numerical and categorical
    numerical_features = [
        'median_income', 'housing_median_age', 'total_rooms',
        'total_bedrooms', 'population', 'households',
        'latitude', 'longitude',
        'rooms_per_household', 'bedrooms_per_room', 'population_per_household'
    ]

    categorical_features = ['ocean_proximity']

    # Scale numerical features
    df[numerical_features] = scaler.transform(df[numerical_features])

    # Encode categorical features
    encoded = encoder.transform(df[categorical_features])
    encoded_df = pd.DataFrame(
        encoded,
        columns=encoder.get_feature_names_out(categorical_features)
    )

    # Combine
    df_processed = pd.concat([
        df[numerical_features].reset_index(drop=True),
        encoded_df.reset_index(drop=True)
    ], axis=1)

    return df_processed[feature_names]


@app.route('/')
def home():
    """Health check and API info"""
    return jsonify({
        'status': 'healthy',
        'service': 'Housing Price Prediction API',
        'version': '1.0.0',
        'model_loaded': model is not None,
        'redis_available': REDIS_AVAILABLE,
        'endpoints': {
            '/': 'API info (this page)',
            '/health': 'Health check',
            '/predict': 'POST - Predict house price',
            '/predict/batch': 'POST - Batch predictions',
            '/model/info': 'GET - Model information',
            '/cache/stats': 'GET - Cache statistics'
        },
        'example_request': {
            'url': '/predict',
            'method': 'POST',
            'body': {
                'median_income': 8.3252,
                'housing_median_age': 41.0,
                'total_rooms': 880,
                'total_bedrooms': 129,
                'population': 322,
                'households': 126,
                'latitude': 37.88,
                'longitude': -122.23,
                'ocean_proximity': 'NEAR BAY'
            }
        }
    })


@app.route('/health')
def health():
    """Kubernetes-style health check"""
    if model is None:
        return jsonify({'status': 'unhealthy', 'reason': 'Model not loaded'}), 503

    return jsonify({
        'status': 'healthy',
        'model': 'loaded',
        'redis': 'connected' if REDIS_AVAILABLE else 'disabled'
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Single house price prediction with caching"""
    try:
        # Get input data
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Check cache first
        cache_key = None
        if REDIS_AVAILABLE:
            cache_key = f"pred:{create_cache_key(data)}"
            cached_result = cache.get(cache_key)

            if cached_result:
                logger.info("✅ Cache HIT!")
                result = json.loads(cached_result)
                result['cached'] = True
                return jsonify(result)

        # Preprocess
        X = preprocess_input(data)

        # Predict
        prediction = model.predict(X)[0]

        # Create response
        result = {
            'predicted_price': float(prediction),
            'predicted_price_formatted': f"${prediction:,.2f}",
            'input_data': data,
            'cached': False
        }

        # Cache result (expires in 1 hour)
        if REDIS_AVAILABLE and cache_key:
            cache.setex(cache_key, 3600, json.dumps(result))
            logger.info("💾 Cached result")

        return jsonify(result)

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Batch predictions"""
    try:
        data = request.get_json()

        if not data or 'houses' not in data:
            return jsonify({'error': 'Expected {"houses": [...]"}'}), 400

        houses = data['houses']
        predictions = []

        for house in houses:
            X = preprocess_input(house)
            pred = model.predict(X)[0]
            predictions.append({
                'input': house,
                'predicted_price': float(pred),
                'predicted_price_formatted': f"${pred:,.2f}"
            })

        return jsonify({
            'count': len(predictions),
            'predictions': predictions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/model/info')
def model_info():
    """Get model information"""
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 503

    # Find latest model file
    model_files = list(MODEL_DIR.glob("model_*.joblib"))
    latest_model = max(model_files, key=lambda x: x.stat().st_mtime)

    return jsonify({
        'model_file': latest_model.name,
        'model_type': type(model).__name__,
        'n_features': len(feature_names),
        'features': feature_names,
        'preprocessing': {
            'scaler': type(scaler).__name__,
            'encoder': type(encoder).__name__,
        }
    })


@app.route('/cache/stats')
def cache_stats():
    """Get cache statistics"""
    if not REDIS_AVAILABLE:
        return jsonify({'error': 'Redis not available'}), 503

    try:
        info = cache.info()
        return jsonify({
            'connected': True,
            'keys': cache.dbsize(),
            'memory_used': info.get('used_memory_human', 'N/A'),
            'uptime_seconds': info.get('uptime_in_seconds', 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info(f"🚀 Starting Flask API on port {port}")
    logger.info(f"   Debug mode: {debug}")
    logger.info(f"   Redis: {'enabled' if REDIS_AVAILABLE else 'disabled'}")

    app.run(host='0.0.0.0', port=port, debug=debug)
