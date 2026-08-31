import os
from flask import Flask

app = Flask(__name__)

# --- NEW HEALTH CHECK ENDPOINT ---
@app.route('/health')
def health_check():
    # Return JSON payload with explicit 200 HTTP status code
    return {'status': 'healthy'}, 200


@app.route('/')
def home():
    # Fetch configurations from App Settings and Connection Strings
    app_env = os.environ.get("APP_ENVIRONMENT", "Production")
    db_conn = os.environ.get("CUSTOMCONNSTR_DB_CONNECTION", "Not Found")
    
    # Read/Write verify persistent file mount
    mount_path = "/mnt/storage/data.txt"
    file_status = "Storage mount missing."
    if os.path.exists("/mnt/storage"):
        with open(mount_path, "a+") as f:
            f.write("App hit logged successfully!\n")
            f.seek(0)
            lines = len(f.readlines())
        file_status = f"Persistent storage is verified active! File has {lines} log entries."

    return f"""
    <h1>Azure App Service Custom Container Demo</h1>
    <p><b>Environment Setting:</b> {app_env}</p>
    <p><b>Database Connection String:</b> {db_conn}</p>
    <p><b>Persistent Storage Status:</b> {file_status}</p>
    """

if __name__ == '__main__':
    # Listen to custom environment port dynamically
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
