"""
Flask middleware for SecureAPIs integration
"""

from flask import request, jsonify, g
from secureapis import SecureAPIs, SecureAPIsConfig
import json


class SecureAPIsFlask:
    """Flask extension for SecureAPIs security checks"""

    def __init__(self, app=None, config=None):
        self.secureapis = None

        if config is None:
            config = SecureAPIsConfig()

        if app is not None:
            self.init_app(app, config)

    def init_app(self, app, config=None):
        """Initialize the extension with a Flask app"""

        if config is None:
            config = SecureAPIsConfig()

        # Apply Flask app config if available
        if hasattr(app, 'config'):
            flask_config = app.config.get('SECUREAPIS_CONFIG', {})
            for key, value in flask_config.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        self.secureapis = SecureAPIs(config)

        # Register before_request handler
        app.before_request(self._check_request)

    def _check_request(self):
        """Check the current request"""
        if not self.secureapis:
            return  # Not initialized yet

        # Extract request information
        method = request.method
        url = request.url
        headers = dict(request.headers)
        ip = self._get_client_ip()

        # Read body for POST/PUT/PATCH requests
        body = ""
        if method in ['POST', 'PUT', 'PATCH']:
            body = request.get_data(as_text=True) or ""

        # Check request
        result = self.secureapis.check_request(method, url, headers, body, ip)

        if not result.allowed:
            # Block the request
            error_message = result.error_message or "Request blocked by security policy"
            return jsonify({
                "error": error_message,
                "statusCode": result.status_code
            }), result.status_code

        # Store result for after_request handler
        g.secureapis_result = result

    def _get_client_ip(self):
        """Get the client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers['X-Forwarded-For'].split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers['X-Real-IP']
        else:
            return request.remote_addr or '127.0.0.1'


def secureapis_before_request():
    """Decorator for manual request checking"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            # This would need to be implemented with a global SecureAPIs instance
            return f(*args, **kwargs)
        return wrapper
    return decorator