import os
import datetime
import random
import time
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- HEALTH CHECK ENDPOINT ---
@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'healthy'}, 200



# --- NEW: MOCK AI INFERENCE ENDPOINT ---
@app.route('/predict', methods=['POST'])
def predict():
    """
    Accepts a JSON payload with a 'text' or 'data' field,
    simulates model latency, and returns structured inference results.
    """
    start_time = time.time()
    payload = request.get_json(silent=True) or {}
    input_text = payload.get("text", "Default prompt context")

    # Hardcoded list of sentiment classifications for mock inference
    labels = ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    chosen_label = random.choice(labels)
    confidence_score = round(random.uniform(0.78, 0.99), 4)
    
    # Simulate realistic AI model forward-pass computational delay (150ms - 400ms)
    time.sleep(random.uniform(0.15, 0.40))
    inference_duration_ms = round((time.time() - start_time) * 1000, 2)

    response_data = {
        "model_metadata": {
            "model_name": "MockLLM-Sentiment-v1.2",
            "framework": "PyTorch-2.4-Mocked",
            "compute_time_ms": inference_duration_ms
        },
        "input_processed": input_text,
        "predictions": [
            {
                "label": chosen_label,
                "confidence": confidence_score
            }
        ]
    }

    # Optional: Log the inference transaction to your mounted Azure File Share
    output_dir = "/mnt/storage"
    if os.path.exists(output_dir):
        try:
            log_path = os.path.join(output_dir, "ai-inference-audit.log")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_path, "a+") as f:
                f.write(f"[{timestamp}] Model: {response_data['model_metadata']['model_name']} | Input: '{input_text}' | Out: {chosen_label} ({confidence_score}) | Time: {inference_duration_ms}ms\n")
        except Exception:
            pass # Prevent inference crashes if the storage share goes momentarily offline

    return jsonify(response_data), 200

# --- MAIN HOME WEB INTERFACE ---
@app.route('/')
def home():
    app_env = os.environ.get("APP_ENVIRONMENT", "Production")
    db_conn = os.environ.get("CUSTOMCONNSTR_DB_CONNECTION", "Not Found")
    
    output_dir = "/mnt/storage"
    file_path = os.path.join(output_dir, "app-output.txt")
    file_status = "Azure File Share mount missing or misconfigured."
    
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, "a+") as f:
            f.write(f"Logged hit to external Azure File Share at {timestamp}\n")
            f.seek(0)
            lines = len(f.readlines())
            
        file_status = f"Success! Written directly to Azure File Share. File has {lines} logs."
    except Exception as e:
        file_status = f"Error writing to Azure File Share: {str(e)}"

    return f"""
    <h1>Azure App Service Custom Container Demo (AI-Enabled)</h1>
    <p><b>Environment Setting:</b> {app_env}</p>
    <p><b>Database Connection String:</b> {db_conn}</p>
    <p><b>Storage Mount Status:</b> {file_status}</p>
    <hr>
    <h3>AI Testing Sandbox:</h3>
    <p>Send a POST request to <code>/predict</code> with JSON data: <code>{{"text": "Azure is awesome!"}}</code> to receive mock model analysis.</p>
    """

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
