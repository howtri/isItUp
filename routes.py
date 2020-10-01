# Tristan Howell
# Site Connectivity Checker

# arg parser
# continually check every x seconds to see if status changes
# flip the order of db and add the option to recheck sites with notifications if one changes

from flask import Flask, redirect, url_for, request, render_template, flash
import socket
import multiprocessing.pool
import functools
# from app import app
import dbactions
app = Flask(__name__)

# https://www.codementor.io/@sagaragarwal94/building-a-basic-restful-api-in-python-58k02xsiq

@app.route('/')
def index():
    return render_template('start.html')


def timeout(time):
    """Timeout decorator, time is seconds until timeout error raised"""
    def timeout_decorator(fn):
        """Wrap original function."""
        @functools.wraps(fn)
        def wrap(*args, **kwargs):
            """Creates multiprocessing pool to run function and timer"""
            try:
                pool = multiprocessing.pool.ThreadPool(processes=1)
                async_result = pool.apply_async(fn, args, kwargs)
                # raises a TimeoutError if execution exceeds max_timeout
                return async_result.get(time)
            # for some reason this won't display more info if excepted 'as timeoutError' to display
            except Exception:
                print(f'Connection timed out')
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
        return available

    except socket.gaierror as dnsError:
        print(f'Domain name failed to resolve to IP. Error: {dnsError}')
    except Exception as genericError:
        print(f'Something else went wrong. Error: {genericError}')
    finally:
        tcp_connect.close()


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
            port_in = int(domain)
            port = port_in
        except:
            print('Domain could not be converted to int')

    # sanitizes the domain by removing any / or ;
    sanitized = sanitize(domain)

    try:
        dbactions.initialize_table()
    except:
        print('Table already initialized')

    # connect method returns 0 when the connection was successful
    if connect(sanitized, port) == 0:
        connected = f'{sanitized}:{port} is up \n'
        dbactions.write_table(sanitized, port, 'OK')
    else:
        connected = f'{sanitized}:{port} seems to be down \n'
        dbactions.write_table(sanitized, port, 'DOWN')

    result = dbactions.read_table()
    return render_template("display.html",result = result, connected = connected)


@app.route('/run', methods=['POST', 'GET'])
def run():
    """
    Handles POST or GET method from / route
    """
    if request.method == 'POST':
        domain = request.form['domname']
        return redirect(url_for('status', domain=domain))
    else:
        domain = request.args.get('domname')
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

if __name__ == '__main__':
   app.run(debug = True)