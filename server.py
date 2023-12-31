#!/venv/bin/python

from flask import Flask, render_template, request
from functools import wraps
import webview
import os
import time
import psutil
import random
import re


# Setup the Flask Server
gui_dir = os.path.join(os.path.dirname(__file__), 'gui')

if not os.path.exists(gui_dir):
    gui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gui')

templates_dir = os.path.join(gui_dir, 'templates')
static_dir = os.path.join(gui_dir, 'static')

server = Flask(__name__, static_folder=static_dir, template_folder=templates_dir)
server.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1  # disable caching


def verify_token(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        token = request.headers.get('token')
        if token == webview.token:
            return function(*args, **kwargs)
        else:
            raise Exception('Authentication error')
    return wrapper


@server.after_request
def add_header(response):
    """
        Disable caching
    """
    response.headers['Cache-Control'] = 'no-store'
    return response


@server.route('/', methods=['GET'])
def landing():
    """
        Render index.html. Initialization is performed asynchronously in initialize() function
        We also look for a route parameter, if given we set the template value 'route' to match.
    """
    server.logger.info("Landing page visited")

    route_param = request.args.get('route', '')
    route_pattern = re.compile(r'^([a-zA-Z0-9]{1,63})$')
    match = route_pattern.match(route_param)
    if match:
        uri_name = match.group(1)
        route = f"/{uri_name}"
        server.logger.info(f"Route parameter found: {route}")
    else:
        route = '/about'

    return render_template('index.html', token=webview.token, route=route)


@server.route("/about")
@verify_token
def home():
    """
        This function renders the home.html template when you visit the /home URL.
    """
    server.logger.info("About page visited")
    data = server._config_data["APP"]
    return render_template("about.html", data=data)


@server.route('/calc', methods=['GET', 'POST'])
@verify_token
def calculate():
    """
        This function renders the calculator.html template when you visit the /calc URL.
    """
    server.logger.info("Calculator page visited")

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

            server.logger.info("Calculation performed: {} {} {} = {}".format(num1, operation, num2, result))

            return render_template('calculator.html', result=str(result))
        except Exception as e:
            server.logger.error("Error occured: {}".format(str(e)))

            if str(e) == "division by zero":
                message = "You can't divide by zero"
            else:
                message = "Error occured, see logs for details"
            
            return render_template('calculator.html', error=message)

    return render_template('calculator.html')


@server.route("/system")
@verify_token
def system_info():
    """
        This function renders the system_info.html template when yogif_path=url_for('static', filename='img/loader.gif')u visit the /system URL.
    """
    server.logger.info("System info page visited")

    # Get running processes info
    processes = []
    for process in psutil.process_iter(['username', 'pid', 'name', 'memory_info', 'cpu_percent', 'status']):
        processes.append(process.info)

    # Get memory info
    memory_info = psutil.virtual_memory()

    # Get CPU info
    cpu_info = psutil.cpu_percent(interval=None)

    # Get Disk info
    disk_info = psutil.disk_usage('/')

    return render_template('system_info.html', processes=processes, memory_info=memory_info, cpu_info=cpu_info, disk_info=disk_info)


# Route to display system configuration using the config.html template
@server.route("/config", methods=["GET", "POST"])
@verify_token
def config():
    """
        This function renders the config.html template when you visit the /config URL.
        It also handles the form submission and updates the config.ini file with the submitted data.
    """
    server.logger.info("Configuration page visited")

    config = server._config_data
    
    if request.method == "GET":
        # Access values from the config.ini file
        app_name = config.get('APP', 'name')
        owner = config.get('APP', 'owner')
        version = config.get('APP', 'version')
        created = config.get('APP', 'created')
        return render_template('config.html', **{
            'app_name': app_name,
            'owner': owner,
            'version': version,
            'created': created,
        })    
    
    elif request.method == "POST":
        # Update the config values with the submitted form data
        config['APP']['name'] = request.form['name']
        config['APP']['owner'] = request.form['owner']
        config['APP']['version'] = request.form['version']
        config['APP']['created'] = request.form['created']

        #Simulate delay to show off loader, and simulate a failed update.
        random_delay = random.randint(1, 15)
        time.sleep(random_delay)

        # Determine if this was a successful update or not, randomly 50/50 chance
        if random.randint(0, 1) == 0:
            status = "Config update failed!"

            server.logger.warning("Config update failed!")

            return render_template('config.html', **{
                'app_name': config['APP']['name'],
                'owner': config['APP']['owner'],
                'version': config['APP']['version'],
                'created': config['APP']['created'],
                'error': status,
            })
        
        else:
            # Write the changes back to the config.ini file
            server.write_config(config)

            server.logger.info("Config updated successfully!")

            # Prepare the update status message
            status = "Config updated successfully!"
            return render_template('config.html', **{
                'app_name': config['APP']['name'],
                'owner': config['APP']['owner'],
                'version': config['APP']['version'],
                'created': config['APP']['created'],
                'success': status,
            })


@server.route("/logs")
@verify_token
def logs():
    """
        This function renders the logs.html template when you visit the /logs URL.
    """
    server.logger.info("Logs page visited")

    with open(server.log_file_name, 'r') as f:
        lines = f.readlines()
        last_lines = [line for line in lines[-100:]]
        last_lines = last_lines[::-1]  # reverse the list
        
    return render_template("logs.html", logs=last_lines)


@server.route("/docs")
@verify_token
def docs():
    """
        This function renders the docs.html template when you visit the /docs URL.
    """
    server.logger.info("Docs page visited")        
    return render_template("docs.html")


@server.route("/license")
@verify_token
def license():
    """
        This function renders the license.html template when you visit the /license URL.
    """
    server.logger.info("License page visited")        
    return render_template("license.html")
