# Flask / Webview / HTMX Based Application

The Flask / Webview / HTMX Application is a hybrid desktop application that merges the powers of Python-based web development, native desktop functionalities, and hypermedia driven frontend interactions. Designed to provide the convenience of web technology, performance of a native application, and simplicity of Python programming.

## Underlying Technologies

This application leverages the capabilities of three powerful technologies:

1. [**Flask**](https://flask.palletsprojects.com/en/2.3.x/#): A web framework written in Python, renowned for its simplicity and minimalistic approach. Despite its "micro" classification, Flask is versatile and capable of powering complex web applications. 

2. [**Pywebview**](https://pywebview.flowrl.com/): A lightweight library for creating web-based desktop applications. Pywebview uses native WebView components to display web content in a separate application window, eliminating the need for C++ or Java.

3. [**HTMX**](https://htmx.org/): An incredibly lightweight and powerful front-end library. HTMX allows developers to handle AJAX, CSS Transitions, WebSockets, and Server Sent Events directly in HTML, facilitating the front-end to backend communication without needing JavaScript.

## Installation

Follow the steps below to set up and run this application on your local machine:

1. Create a Python 3 virtual environment:
   ```
   python3 -m venv env
   ```
2. Activate the virtual environment:
   ```
   source env/bin/activate  # for Linux/macOS
   env\Scripts\activate  # for Windows
   ```
3. Install the required dependencies into the virtual environment based on your operating system:
   ```
   pip install -r linux_requirements.txt  # for Linux
   pip install -r mac_requirements.txt  # for macOS
   ```
4. Run the application:
   ```
   python main.py
   ```

## Packaging for Desktop

You can also package this application as a standalone desktop application for Linux, macOS, or Windows. Refer to the Pywebview documentation on [freezing](https://pywebview.flowrl.com/3.7/guide/freezing.html) for detailed instructions on how to do this.

## Features

With the combined capabilities of Flask, Pywebview, and HTMX, this application provides the expansive Python ecosystem and the versatility of web development while preserving a native look and feel. Enjoy features like real-time updates, smooth navigation, dynamic content loading, and more.

## License

This project is licensed under the terms of the MIT license.
