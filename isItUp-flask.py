# Tristan Howell
# Site Connectivity Checker

# arg parser
# continually check every x seconds to see if status changes
# check for 10 sites and see if status changes

from flask import Flask, redirect, url_for, request
import socket
import multiprocessing.pool
import functools

app = Flask(__name__)

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

def status(domain):
    """
    Need to add user in or argparse to accept sites to test
    """
    # domain = input('Enter Domain or IP: ')
    port = 80
    str_return = ''
    if connect(domain, port) == 0:
        str_return = f'{domain}:{port} is up'
    else:
        str_return = f'{domain}:{port} seems to be down'
    return str_return

def display_chart():
    """Might need to make this all a class so sites are stored in a dict with domain name : status and displayed here"""
    pass

@app.route('/success/<name>')
def success(name):
   return status(name)

@app.route('/login',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      user = request.form['nm']
      return redirect(url_for('success',name = user))
   else:
      user = request.args.get('nm')
      return redirect(url_for('success',name = user))

if __name__ == '__main__':
   app.run(debug = True)