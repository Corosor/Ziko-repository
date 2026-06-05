from flask import Flask, jsonify
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import time

app = Flask(__name__)

REQUEST_COUNT = Counter(
    'app_requests_total',
    'Nombre total de requêtes',
    ['endpoint']
)

@app.route('/')
def home():
    REQUEST_COUNT.labels(endpoint='/').inc()
    return jsonify({
        #"message": "Hello DevOps",
        "message": "Version 12 - DevOps Project ",
        "status": "running"
    })
    
@app.route('/health')
def health():
    REQUEST_COUNT.labels(endpoint='/health').inc()
    return jsonify({
        "status": "healthy",
        "timestamp": time.time()
    })

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)