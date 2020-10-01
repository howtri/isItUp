# Tristan Howell
# Site Connectivity Checker

# arg parser
# continually check every x seconds to see if status changes
# check for 10 sites and see if status changes


import socket
import multiprocessing.pool
import functools
import dbactions

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

def status(domain, port=80):
    """
    Need to add user in or argparse to accept sites to test
    """
    try:
        dbactions.initialize_table()
    except:
        print('Table already initialized')

    if connect(domain, port) == 0:
        print(f'{domain}:{port} is up')
        dbactions.write_table(domain, port, 'OK')
    else:
        print(f'{domain}:{port} seems to be down')
        dbactions.write_table(domain, port, 'DOWN')

    print(display_chart(dbactions.read_table()))

def display_chart(data):
    """status and displayed here"""
    top_bottom = '--------------------------------------------'
    format1 = ' ' * 20
    table = top_bottom + '\n'

    for row in data:
        table += f'{row[0] + format1[len(row[0]):]} | {row[1]} | {row[2]} \n'

    table += top_bottom
    return table

def main():
    domain = input('Enter Domain or IP: ')
    status(domain)

if __name__ == '__main__':
    main()