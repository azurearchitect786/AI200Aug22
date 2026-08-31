# probe-demo/app.py
from flask import Flask, render_template_string, jsonify
import time
import os

app = Flask(__name__)

# Track the application health state globally in memory
APP_START_TIME = time.time()
IS_READY = False          # Controlled by Startup/Readiness rules
IS_ALIVE = True           # Controlled by Liveness rule
SIMULATED_DELAY = 0       # Simulates server lag / database timeout

# HTML UI Dashboard for browser demo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Azure Container Apps Health Probe Demo</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; line-height: 1.6; }
        .card { border: 1px solid #ccc; padding: 20px; border-radius: 8px; margin-bottom: 20px; background: #f9f9f9; }
        .status { font-weight: bold; padding: 5px 10px; border-radius: 4px; color: white; display: inline-block; }
        .healthy { background-color: #28a745; }
        .unhealthy { background-color: #dc3545; }
        .btn { display: inline-block; padding: 10px 15px; color: white; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; margin-right: 10px; font-weight: bold; }
        .btn-kill { background-color: #dc3545; }
        .btn-lag { background-color: #ffc107; color: black; }
        .btn-recover { background-color: #007bff; }
    </style>
</head>
<body>
    <h2>🚀 Azure Container Apps Probe Control Panel</h2>
    <p>Container Hostname: <strong>{{ hostname }}</strong></p>
    <p>Uptime: <strong>{{ uptime }} seconds</strong></p>

    <div class="card">
        <h3>Live Application Health State</h3>
        <p>Liveness State: <span class="status {% if alive %}healthy{% else %}unhealthy{% endif %}">{% if alive %}ALIVE (200 OK){% else %}DEAD (500 ERROR){% endif %}</span></p>
        <p>Readiness State: <span class="status {% if ready %}healthy{% else %}unhealthy{% endif %}">{% if ready %}READY (200 OK){% else %}NOT READY (503 SERVICE UNAVAILABLE){% endif %}</span></p>
        <p>Simulated Request Lag: <strong>{{ delay }} seconds</strong></p>
    </div>

    <div class="card">
        <h3>Simulate Infrastructure Failure Actions</h3>
        <p>Click these buttons to alter the live behavior of the container and watch ACA react:</p>
        <a href="/fail-liveness" class="btn btn-kill">Trigger Liveness Failure (Crash App)</a>
        <a href="/fail-readiness" class="btn btn-lag">Trigger Readiness Lag (5s Delay)</a>
        <a href="/recover" class="btn btn-recover">Reset App Status</a>
    </div>

    <script>
        // Auto-refresh the page every 3 seconds to keep track of live state updates
        setInterval(() => { location.reload(); }, 3000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    global IS_READY
    # Simulate a slow startup sequence (Ready only after running for 15 seconds)
    uptime = int(time.time() - APP_START_TIME)
    if uptime >= 15 and SIMULATED_DELAY == 0:
        IS_READY = True
        
    return render_template_string(
        HTML_TEMPLATE, 
        hostname=os.getenv('CONTAINER_APP_REVISION', 'Local-Host'),
        uptime=uptime,
        alive=IS_ALIVE,
        ready=IS_READY,
        delay=SIMULATED_DELAY
    )

# --- PROBE ENDPOINTS ---

@app.route('/startup')
def startup_probe():
    """Startup Probe: Ensures heavy setup tasks (like loading AI model files) are complete."""
    uptime = time.time() - APP_START_TIME
    if uptime < 12:
        return jsonify(status="Booting up services..."), 503
    return jsonify(status="Application kernel loaded!"), 200

@app.route('/liveness')
def liveness_probe():
    """Liveness Probe: Determines if the container needs a hard hardware reboot."""
    if not IS_ALIVE:
        return jsonify(status="Deadlocked!"), 500
    return jsonify(status="Alive"), 200

@app.route('/readiness')
def readiness_probe():
    """Readiness Probe: Determines if traffic can be routed safely."""
    global IS_READY
    
    # Calculate uptime directly during the probe request
    uptime = int(time.time() - APP_START_TIME)
    if uptime >= 15 and SIMULATED_DELAY == 0:
        IS_READY = True

    if SIMULATED_DELAY > 0:
        time.sleep(SIMULATED_DELAY)
        
    if not IS_READY:
        return jsonify(status="Not ready for traffic"), 503
        
    return jsonify(status="Ready"), 200

# --- SIMULATION TRIGGERS ---

@app.route('/fail-liveness')
def fail_liveness():
    global IS_ALIVE
    IS_ALIVE = False
    return "Liveness failure triggered! This container will fail health checks and restart shortly. Go back and watch."

@app.route('/fail-readiness')
def fail_readiness():
    global SIMULATED_DELAY, IS_READY
    SIMULATED_DELAY = 6  # Exceeds the probe timeout configuration boundary limit
    IS_READY = False
    return "Readiness lag triggered! The app will stop serving public ingress requests. Go back and watch."

@app.route('/recover')
def recover():
    global IS_ALIVE, IS_READY, SIMULATED_DELAY
    IS_ALIVE = True
    IS_READY = True
    SIMULATED_DELAY = 0
    return "Application state restored to healthy parameters. Go back."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
