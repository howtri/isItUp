# Tristan Howell
# Site Connectivity Checker webapp using Flask, sqlite, and Nginx. Deployed with Ansible

from flask import Flask, redirect, url_for, request, render_template
import flask_restful
import logging
import socket
import multiprocessing.pool
import functools
from app import app
from app import dbactions


logging.basicConfig(filename='./app/logs/routes.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    """Landing page for the app, asks for a domain name and sends data via POST to /run"""
    return render_template('start.html')


def timeout(time):
    """Timeout decorator, time is seconds until timeout error raised"""

    def timeout_decorator(fn):
        """Wrap original"""
        @functools.wraps(fn)
        def wrap(*args, **kwargs):
            """Creates multiprocessing pool to run function and timer"""
            try:
                pool = multiprocessing.pool.ThreadPool(processes=1)
                async_result = pool.apply_async(fn, args, kwargs)
                # raises a TimeoutError if execution exceeds max_timeout
                return async_result.get(time)
            # for some reason this won't display more info if excepted 'as timeoutError' to display
            except Exception as generic_exception:
                print(f'Connection timed out. Error: {generic_exception}')
            finally:
                pool.close()
        return wrap
    return timeout_decorator


@timeout(5)
def connect(domain, port):
    """
    Attempts to establish a connection with the passed domain and port via tcp socket connection
    available is 0 for success
    """
    try:
        tcp_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        available = tcp_connect.connect_ex((domain, port))
        logging.info(f'TCP connection to {domain}:{port}. Status {available}')
        tcp_connect.close()
        return available

    except socket.gaierror as dnsError:
        logging.info(f'Domain name failed to resolve to IP. Error: {dnsError} Domain: {domain}:{port}')

    except Exception as genericError:
        logging.error(f'Something else went wrong. Error: {genericError} Domain: {domain}:{port}')


@app.route('/connect/<domain>')
def status(domain, port=80):
    """
    Passed domain name from / route, initializes table if not initialized,
    controls db communication, makes connect() call to determine up or down site,
    displays the display.html page
    """
    # if user passed a domain with port as domain:port we split and ensure port is an int
    if ':' in domain:
        split = domain.split(':')
        domain = split[0]

        try:
            # ensures that the str following : is a number and is 5 or less digits
            if len(port_in) <= 5:
                port_in = int(split[1])
                port = port_in

        except ValueError as notInt:
            logging.info(f'Port could not be converted to int. Error {notInt} Domain: {domain}:{port}' )

    # sanitizes the domain by removing any / or ;
    sanitized = sanitize(domain)
    logging.info(f'sanitized Domain: {domain}:{port}')

    try:
        # initializes sqlite DB table DOMAINSTATS
        dbactions.initialize_table()
    except:
        logging.info('Table already initialized')

    # connect method returns 0 when the connection was successful
    if connect(sanitized, port) == 0:
        # connection succeeded
        connected = f'{sanitized}:{port} is up \n'
        dbactions.write_table(sanitized, port, 'OK')
    else:
        # connection failed
        connected = f'{sanitized}:{port} seems to be down \n'
        dbactions.write_table(sanitized, port, 'DOWN')

    result = dbactions.read_table()
    return render_template("display.html", result=result, connected=connected)


@app.route('/run', methods=['POST', 'GET'])
def run():
    """
    Handles POST or GET method from / route
    """
    if request.method == 'POST':
        domain = request.form['domname']
        logging.info(f'POST Request for {domain}')
        return redirect(url_for('status', domain=domain))
    else:
        domain = request.args.get('domname')
        logging.info(f'GET Request for {domain}')
        return redirect(url_for('status', domain=domain))


def sanitize(domain):
    """
    Basic attempt to prevent SQL injection or small issues the app isn't yet built to handle
    """
    if ';' in domain:
        domain = domain[:domain.index(';')]
    if '/' in domain:
        domain = domain[:domain.index('/')]
    return domain

# def export_json():
#     """
#     Outputs all connection information as JSON for GET request
#     """
