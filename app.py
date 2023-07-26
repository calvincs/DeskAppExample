#!/venv/bin/python


from flask import Flask, render_template, request
import webbrowser
from threading import Timer, Thread
import time
import os
import signal
import psutil
import configparser
import random
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
LAST_PING = time.time()

app.logger.setLevel(logging.INFO) # Set the minimum log level of interest
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # create the directory if it does not exist

log_file = os.path.join(log_dir, "app.log")
handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=5)  # 10 KB file size, keep 10 backup logs
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

REDIRECT_URL = "http://localhost:5000/home"


# No Caching Allowed
@app.after_request
def add_header(response):
    """
        Add headers to both force latest IE rendering engine or Chrome Frame,
        and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Web Routes
@app.route('/')
def index():
    """
        This function renders the index.html template when you visit the root URL.
    """
    global REDIRECT_URL

    app.logger.info("Index page visited")
    return render_template('index.html', on_exit=REDIRECT_URL)


@app.route("/home")
def home():
    """
        This function renders the home.html template when you visit the /home URL.
    """
    config = read_config()

    data = {
        "redirect_url": config['APP'].get('on_exit'),
        "app_name": config['APP'].get('name'),
        "owner": config['APP'].get('owner'),
        "version": config['APP'].get('version'),
        "created": config['APP'].get('created'),
    }
    return render_template("welcome.html", data=data)


@app.route('/calc', methods=['GET', 'POST'])
def calculate():
    """
        This function renders the calculator.html template when you visit the /calc URL.
    """
    if request.method == 'POST':
        try:
            num1 = int(request.form.get('num1'))
            num2 = int(request.form.get('num2'))
            operation = request.form.get('operation')

            if operation == 'add':
                result = num1 + num2
            elif operation == 'subtract':
                result = num1 - num2
            elif operation == 'multiply':
                result = num1 * num2
            elif operation == 'divide':
                result = num1 / num2

            app.logger.info("Calculation performed: {} {} {} = {}".format(num1, operation, num2, result))

            return render_template('calculator.html', result=str(result))
        except Exception as e:
            app.logger.error("Error occured: {}".format(str(e)))

            if str(e) == "division by zero":
                return "You can't divide by zero", 400
            else:
                return "Error occured, see logs for details", 400

    return render_template('calculator.html')


@app.route("/system")
def system_info():
    """
        This function renders the system_info.html template when you visit the /system URL.
    """
    # Get running processes info
    processes = []
    for process in psutil.process_iter(['username', 'pid', 'name', 'memory_info', 'cpu_percent', 'status']):
        processes.append(process.info)

    # Sort processes by memory usage (descending) and then by CPU usage (descending)
    processes = sorted(processes, key=lambda x: (x['memory_info'].rss, x['cpu_percent']), reverse=True)

    # Get memory info
    memory_info = psutil.virtual_memory()

    # Get CPU info
    cpu_info = psutil.cpu_percent(interval=None)

    # Get Disk info
    disk_info = psutil.disk_usage('/')

    app.logger.info("System info page visited")

    return render_template('system_info.html', processes=processes, memory_info=memory_info, cpu_info=cpu_info, disk_info=disk_info)


# Route to display system configuration using the configuration.html template
@app.route("/system_configuration", methods=["GET", "POST"])
def system_configuration():
    """
        This function renders the configuration.html template when you visit the /system_configuration URL.

        It also handles the form submission and updates the config.ini file with the submitted data.
    """
    # Read the config.ini file
    config = read_config()
    
    if request.method == "GET":
        # Access values from the config.ini file
        app_name = config.get('APP', 'name')
        on_exit = config.get('APP', 'on_exit')
        owner = config.get('APP', 'owner')
        version = config.get('APP', 'version')
        created = config.get('APP', 'created')
        return render_template('configuration.html', **{
            'app_name': config['APP']['name'],
            'on_exit': config['APP']['on_exit'],
            'owner': config['APP']['owner'],
            'version': config['APP']['version'],
            'created': config['APP']['created'],
        })    
    
    elif request.method == "POST":
        # Update the config values with the submitted form data
        config['APP']['name'] = request.form['name']
        config['APP']['on_exit'] = request.form['on_exit']
        config['APP']['owner'] = request.form['owner']
        config['APP']['version'] = request.form['version']
        config['APP']['created'] = request.form['created']


        #Simulate delay to show off loader, and simulate a failed update.
        random_delay = random.randint(1, 5)
        time.sleep(random_delay)

        # Determine if this was a successful update or not, randomly 50/50 chance
        if random.randint(0, 1) == 0:
            update_status = "Config update failed!"

            app.logger.warning("Config update failed!")

            return render_template('configuration.html', **{
                'app_name': config['APP']['name'],
                'on_exit': config['APP']['on_exit'],
                'owner': config['APP']['owner'],
                'version': config['APP']['version'],
                'created': config['APP']['created'],
                'update_error': update_status,
            })
        
        else:
            # Write the changes back to the config.ini file
            write_config(config)

            app.logger.info("Config updated successfully!")

            # Prepare the update status message
            update_status = "Config updated successfully!"
            return render_template('configuration.html', **{
                'app_name': config['APP']['name'],
                'on_exit': config['APP']['on_exit'],
                'owner': config['APP']['owner'],
                'version': config['APP']['version'],
                'created': config['APP']['created'],
                'update_success': update_status,
            })

    else:
        return "Method not allowed", 405


@app.route("/logs")
def logs():
    """
        This function renders the logs.html template when you visit the /logs URL.
    """
    with open('logs/app.log', 'r') as f:
        lines = f.readlines()
        last_lines = [line.strip() for line in lines[-10:]]
        
    return render_template("logs.html", logs=last_lines)



@app.route('/exit')
def exit_app():
    """
        This function redirects the user to Google and shuts down the Flask server.
        Effectively, this function exits the application.
    """
    app.logger.info("Exit page visited")

    Thread(target=shutdown_server).start()
    return "goodbye", 200


@app.route('/ping', methods=['POST'])
def ping():
    """
        This function is called by the client to 'ping' the server.
        It is used to monitor the connection between the client and server.
    """
    global LAST_PING
    LAST_PING = time.time()  # update the time of the last received 'ping'
    return "pong", 200



# Helper Functions
def open_browser():
    """
        This function opens the default web browser to the Flask server's URL.
    """
    app.logger.info("Opening browser to main application page")
    webbrowser.open_new('http://localhost:5000/')


def shutdown_server():
    """
        This function stops the Flask server after a delay.
    """
    app.logger.info("Shutting down server")
    time.sleep(0.25)
    os.kill(os.getpid(), signal.SIGINT)


def monitor_pings():
    """
        This function monitors the time between 'pings' from the client.
        If the client exits without sending a 'ping', the server will be stopped after some time.
    """
    global LAST_PING
    while True:
        time.sleep(5)
        if time.time() - LAST_PING > 10:  # if more than 10 seconds passed since the last ping, stop the server
            app.logger.warning('No ping received in the last 10 seconds, stopping server.')
            shutdown_server()


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
    global REDIRECT_URL
    REDIRECT_URL = config['APP']['on_exit']

    with open('config.ini', 'w') as config_file:
        config_data.write(config_file)


if __name__ == "__main__":
    """
        This is the main function that is executed when you run the script.
    """
    # Start the ping monitoring in a separate thread
    Thread(target=monitor_pings, daemon=True).start()
    # Open the web browser after 1 second, giving the app time to start up
    Timer(1, open_browser).start()

    # Setup some variables to be used in the app
    config = read_config()

    if "on_exit" in config['APP']:
        REDIRECT_URL = config['APP']['on_exit']

    if "name" in config['APP']:
        APP_NAME = config['APP']['name']

    if "owner" in config['APP']:
        OWNER = config['APP']['owner']

    if "version" in config['APP']:
        VERSION = config['APP']['version']

    if "created" in config['APP']:
        CREATED = config['APP']['created']


    # If debug is True, and use_reloader is True, then the server will be restarted when code changes
    app.run(use_reloader=False, debug=False)

