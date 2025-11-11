"""
Django middleware for SecureAPIs integration
"""

from django.http import JsonResponse
from django.conf import settings
from secureapis import SecureAPIs, SecureAPIsConfig


class SecureAPIsMiddleware:
    """Django middleware for SecureAPIs security checks"""

    def __init__(self, get_response):
        self.get_response = get_response

        # Get configuration from Django settings
        config_dict = getattr(settings, 'SECUREAPIS_CONFIG', {})
        config = SecureAPIsConfig()

        # Apply configuration
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.secureapis = SecureAPIs(config)

    def __call__(self, request):
        # Extract request information
        method = request.method
        url = request.get_full_path()
        headers = dict(request.headers)
        ip = self._get_client_ip(request)

        # Read body for POST/PUT/PATCH requests
        body = ""
        if method in ['POST', 'PUT', 'PATCH']:
            if hasattr(request, 'body'):
                body = request.body.decode('utf-8', errors='ignore')

        # Check request
        result = self.secureapis.check_request(method, url, headers, body, ip)

        if not result.allowed:
            # Block the request
            error_message = result.error_message or "Request blocked by security policy"
            return JsonResponse({
                "error": error_message,
                "statusCode": result.status_code
            }, status=result.status_code)

        # Add security headers to response
        response = self.get_response(request)

        if result.headers_json:
            import json
            try:
                headers = json.loads(result.headers_json)
                for key, value in headers.items():
                    response[key] = value
            except:
                pass  # Ignore header parsing errors

        return response

    def _get_client_ip(self, request):
        """Get the client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'