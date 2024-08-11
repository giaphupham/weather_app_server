from init import *
from functools import wraps

def require_origin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        request_origin = request.headers.get('Origin')
        if not request_origin:
            response = jsonify({'error': 'Forbiden access!'})
            response.status_code = 403
            return response
        if request_origin not in ALLOW_ORIGINS:
            response = jsonify({'error': 'Forbiden access!'})
            response.status_code = 403
            return response
        return f(*args, **kwargs)
    return decorated_function

