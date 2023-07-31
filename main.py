import logging
from logging.handlers import RotatingFileHandler
from contextlib import redirect_stdout
from io import StringIO
import os
from server import server
import webview
import webview.menu as wm
from functools import partial
import configparser

# flake8: disable=E501
INSTANCE_URI = None


def go_exit():
    """
        Close the active window
    """
    active_window = webview.active_window()
    if active_window:
        active_window.destroy()


def new_window():
    """
        Create a new window
    """
    # Get window count
    window_count = len(webview.windows)
    webview.create_window(f"Demo Application {window_count}", server, min_size=(1024, 768), confirm_close=True)


def go_to(endpoint):
    """
        Load the given endpoint in the active window

        param 
        endpoint: The endpoint to load
    """
    global INSTANCE_URI
    active_window = webview.active_window()
    if active_window:
        url = f"{INSTANCE_URI}/?route={endpoint}"
        active_window.load_url(url)


def set_instance_uri(window):
    """
        Set the INSTANCE_URI global variable to the current window's URL

        param 
        window: The window to get the URL from
    """
    global INSTANCE_URI
    if INSTANCE_URI is None:
        INSTANCE_URI = window.get_current_url()
        server.logger.info("Instance URI set to {}".format(INSTANCE_URI))



# Function to read the config.ini file
def read_config():
    """
        This function reads the config.ini file and returns the config object.
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config


# Function to write changes to the config.ini file
def write_config(config_data):
    """
        This function writes the changes to the config.ini file.
        It also updates the global state variables with the new values.
    """
    # Update the config.ini file with the new values, but also global state variables
    with open('config.ini', 'w') as config_file:
        config_data.write(config_file)



def main():

    # Get the full path of this applications directory
    app_dir = os.path.dirname(__file__)

    # Get the full path of the config.ini file
    config_file = os.path.join(app_dir, 'config.ini')

    # Read the config.ini file to the server instance
    config = configparser.ConfigParser()
    config.read(config_file)
    server._config_data = config
    # Add the write function to the server instance
    server.write_config = write_config


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


    # Our Menu for the application
    app_menu = [
        wm.Menu('File', [
                wm.MenuAction('New Window', new_window),
                wm.MenuSeparator(),
                wm.MenuAction('Configuration', partial(go_to, 'config')),
                wm.MenuSeparator(),
                wm.MenuAction('Exit', go_exit),
                wm.MenuSeparator()
            ]),
        wm.Menu('Tools',[
                wm.MenuAction('Calculator', partial(go_to, 'calc')),
                wm.MenuSeparator(),
                wm.MenuAction('System Information', partial(go_to, 'system'))
            ]),
        wm.Menu('Help',[
                wm.MenuAction('About', partial(go_to, 'about')),
                wm.MenuSeparator(),
                wm.MenuAction('Documentation', partial(go_to, 'docs')),
                wm.MenuSeparator(),
                wm.MenuAction('View Logs', partial(go_to, 'logs')),
                wm.MenuSeparator(),
                wm.MenuAction('License', partial(go_to, 'license'))
            ])
    ]

    # Start the application server
    stream = StringIO()
    with redirect_stdout(stream):
        window_one = webview.create_window('Demo Application', server, min_size=(1024, 768), confirm_close=True)
        webview.start(set_instance_uri, window_one, debug=False, menu=app_menu)

if __name__ == '__main__':
    main()
