import urllib.request
import base64


def create_basic_auth(user, password):
    auth = bytes(user + ':' + password, 'utf-8')
    return 'Basic ' + base64.b64encode(auth).decode('utf-8')


def http_get(url, auth, timeout=5 * 60):
    """
    Small wrapper for getting rid of the requests library
    """
    auth_header = create_basic_auth(auth[0], auth[1])
    req = urllib.request.Request(url)
    req.add_header('Authorization', auth_header)
    response = urllib.request.urlopen(req, timeout=timeout)
    return response.read().decode('utf8')
