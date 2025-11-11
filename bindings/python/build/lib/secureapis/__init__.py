"""
SecureAPIs Python Bindings

High-performance security middleware for Python applications.
"""

import os
import json
import ctypes
from ctypes import c_char_p, c_int, c_void_p, Structure, POINTER
from typing import Dict, Optional, Any


class SecureAPIsException(Exception):
    """Exception raised by SecureAPIs operations"""
    pass


class SecurityCheckResult(Structure):
    """Result structure for security checks"""
    _fields_ = [
        ("allowed", c_int),
        ("status_code", c_int),
        ("error_message", c_char_p),
        ("headers_json", c_char_p),
    ]


class SecureAPIsConfig:
    """Configuration for SecureAPIs"""

    def __init__(self):
        # Rate limiting
        self.rate_limit_requests_per_minute = 60
        self.enable_rate_limiting = True

        # Input validation
        self.enable_xss_protection = True
        self.enable_sql_injection_protection = True
        self.enable_input_validation = True

        # CSRF protection
        self.enable_csrf_protection = True

        # Authentication
        self.jwt_secret = None
        self.require_auth = False

        # Other settings
        self.max_request_size_kb = 1024

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary matching Rust SecurityConfig"""
        return {
            "rate_limit": {
                "enabled": self.enable_rate_limiting,
                "requests_per_window": self.rate_limit_requests_per_minute,
                "window_duration": {"secs": 60, "nanos": 0},
                "burst_size": 10,
                "per_ip": True,
                "per_user": False,
                "adaptive": False,
            },
            "validation": {
                "enabled": self.enable_input_validation,
                "sql_injection_check": self.enable_sql_injection_protection,
                "xss_check": self.enable_xss_protection,
                "command_injection_check": True,
                "path_traversal_check": True,
                "sanitize_input": True,
                "max_payload_size": self.max_request_size_kb * 1024,
                "max_header_size": 8192,
            },
            "auth": {
                "enabled": self.require_auth,
                "require_auth": self.require_auth,
                "jwt_secret": self.jwt_secret,
                "api_keys": [],
                "token_expiry": {"secs": 3600, "nanos": 0},
                "refresh_enabled": False,
                "mfa_enabled": False,
            },
            "monitoring": {
                "enabled": True,
                "log_requests": False,
                "log_responses": False,
                "log_security_events": True,
                "metrics_enabled": False,
                "trace_sampling_rate": 0.0,
            },
            "threat_detection": {
                "enabled": True,
                "anomaly_detection": False,
                "bot_detection": True,
                "known_patterns": True,
                "block_suspicious": True,
            },
            "https": {
                "enabled": False,
                "require_https": False,
                "hsts_max_age": 31536000,
                "hsts_include_subdomains": True,
            },
            "cors": {
                "enabled": False,
                "allow_origins": ["*"],
                "allow_all_origins": True,
                "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"],
                "allow_credentials": False,
                "max_age": 86400,
            },
            "csrf": {
                "enabled": self.enable_csrf_protection,
                "token_length": 32,
                "header_name": "X-CSRF-Token",
                "param_name": "_csrf",
            },
            "content_type": {
                "enabled": True,
                "allowed_types": [
                    "application/json",
                    "application/x-www-form-urlencoded",
                    "multipart/form-data",
                    "text/plain",
                ],
                "strict_mode": False,
            },
        }


class SecurityResult:
    """Result of a security check operation"""

    def __init__(self, allowed: bool, status_code: int,
                 error_message: Optional[str], headers_json: Optional[str]):
        self.allowed = allowed
        self.blocked = not allowed  # Add blocked property for compatibility
        self.status_code = status_code
        self.error_message = error_message
        self.headers_json = headers_json


class SecureAPIs:
    """Main SecureAPIs class"""

    def __init__(self, config: SecureAPIsConfig):
        # Load the native library
        lib_path = self._find_library()
        if lib_path:
            self._lib = ctypes.CDLL(lib_path)
        else:
            raise RuntimeError("Could not find SecureAPIs native library")

        # Configure function signatures
        self._lib.secureapis_create_config.argtypes = [c_char_p]
        self._lib.secureapis_create_config.restype = c_void_p

        self._lib.secureapis_free_security_layer.argtypes = [c_void_p]
        self._lib.secureapis_free_security_layer.restype = None

        self._lib.secureapis_check_request.argtypes = [
            c_void_p, c_char_p, c_char_p, c_char_p, c_char_p, c_char_p
        ]
        self._lib.secureapis_check_request.restype = c_void_p  # Returns SecurityCheckResult*

        self._lib.secureapis_free_result.argtypes = [c_void_p]
        self._lib.secureapis_free_result.restype = None

        self._lib.secureapis_free_string.argtypes = [c_char_p]
        self._lib.secureapis_free_string.restype = None

        # Create configuration
        config_json = json.dumps(config.to_dict()).encode('utf-8')
        self._config = self._lib.secureapis_create_config(config_json)

        if not self._config:
            raise SecureAPIsException("Failed to create SecureAPIs configuration")

    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, '_config') and self._config:
            self._lib.secureapis_free_security_layer(self._config)

    def check_request(self, method: str, path: str, headers: Dict[str, str],
                     body: str = "", ip_address: str = "127.0.0.1") -> SecurityResult:
        """Check if a request is allowed by security rules"""

        # Convert headers to JSON
        headers_json = json.dumps(headers).encode('utf-8')

        # Call native function
        result_ptr = self._lib.secureapis_check_request(
            self._config,
            method.encode('utf-8'),
            path.encode('utf-8'),
            headers_json,
            body.encode('utf-8'),
            ip_address.encode('utf-8')
        )

        if not result_ptr:
            raise SecureAPIsException("Security check failed")

        # Convert result to Python object
        result = ctypes.cast(result_ptr, POINTER(SecurityCheckResult)).contents

        # Extract values
        allowed = bool(result.allowed)
        status_code = result.status_code
        error_message = None
        headers_json_out = None

        if result.error_message:
            error_message = ctypes.c_char_p(result.error_message).value.decode('utf-8')

        if result.headers_json:
            headers_json_out = ctypes.c_char_p(result.headers_json).value.decode('utf-8')

        # Free the result
        self._lib.secureapis_free_result(result_ptr)

        return SecurityResult(allowed, status_code, error_message, headers_json_out)

    def _find_library(self) -> Optional[str]:
        """Find the native library file"""
        package_dir = os.path.dirname(__file__)

        # Try different library names based on platform
        if os.name == 'nt':  # Windows
            lib_names = ['secureapis.dll']
        elif os.uname().sysname == 'Darwin':  # macOS
            lib_names = ['libsecureapis.dylib']
        else:  # Linux/Unix
            lib_names = ['libsecureapis.so']

        for lib_name in lib_names:
            lib_path = os.path.join(package_dir, lib_name)
            if os.path.exists(lib_path):
                return lib_path

        return None