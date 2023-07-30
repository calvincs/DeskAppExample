import logging
from logging.handlers import RotatingFileHandler
from contextlib import redirect_stdout
from io import StringIO
import os
from server import server
import webview

# flake8: disable=E501

if __name__ == '__main__':
    # Logs Path
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    server.logger.setLevel(logging.INFO) # Set the minimum log level of interest
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)  # create the directory if it does not exist
    log_file = os.path.join(logs_dir, "application.log")
    handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=5)  # 10 KB file size, keep 10 backup logs
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    server.log_file_name = log_file
    server.logger.setLevel(logging.INFO)
    server.logger.addHandler(handler)
    server.logger.info("Application started")

    # Start the application server
    stream = StringIO()
    with redirect_stdout(stream):
        window = webview.create_window('Demo Application', server, min_size=(1024, 768), confirm_close=True)
        webview.start(debug=False)