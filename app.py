import logging
import requests
import json
from flask import Flask, request, render_template
from configparser import ConfigParser
from log_ingestor import search_logs  # Assuming search_logs function is available

app = Flask(__name__)

def configure_logging():
    """Configures logging."""
    log_level = logging.INFO  # Adjust log level as needed
    log_file = 'app.log'  # Adjust log file name/path as needed

    logging.basicConfig(filename=log_file, level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

def create_log_message(level, message, timestamp, source):
    """Creates a standardized log message in JSON format."""
    return json.dumps({
        'level': level,
        'log_string': message,
        'timestamp': timestamp,
        'metadata': {
            'source': source
        }
    })

def ingest_log(api_url, log_message, retry_count=3):
    """Ingests a log message to a specified API endpoint."""
    for attempt in range(retry_count):
        try:
            response = requests.post(api_url, data=log_message)
            response.raise_for_status()  # Raise an exception for non-2xx status codes
            logging.info(f"Log ingested successfully (attempt {attempt+1})")
            return
        except requests.exceptions.RequestException as e:
            logging.error(f"Error ingesting log (attempt {attempt+1}): {e}")
            if attempt == retry_count - 1:
                raise  # Raise the error on the last attempt

@app.route('/')
def search():
    return render_template('search.html')

@app.route('/results', methods=['POST'])
def search_results():
    level = request.form.get('level')
    message = request.form.get('message')
    timestamp_range = request.form.get('timestamp_range')  # Handle date range parsing
    source = request.form.get('source')
    logs = search_logs(level, message, timestamp_range, source)
    return render_template('results.html', logs=logs)

def main():
    """Main function to ingest logs from multiple APIs."""
    configure_logging()

    # Replace with actual API URLs and log file paths
    api_urls = [
        'https://api1.example.com/logs',
        'https://api2.example.com/logs',
        # ... (more API URLs)
    ]
    log_file_paths = [
        'log1.log',
        'log2.log',
        # ... (more log file paths)
    ]

    for api_url, log_file_path in zip(api_urls, log_file_paths):
        # Simulate log data generation (replace with actual logic)
        log_data = {
            'level': 'error',
            'message': 'Sample error message',
            'timestamp': '2024-05-15T00:00:00Z',  # Adjust timestamp as needed
            'source': log_file_path
        }
        log_message = create_log_message(**log_data)

        try:
            ingest_log(api_url, log_message)
        except Exception as e:
            logging.critical(f"Failed to ingest log to {api_url}: {e}")

if __name__ == '__main__':
    main()
    app.run(debug=True, port=5000)
