# SecureAPIs Python Bindings

Python bindings for SecureAPIs - a high-performance Rust security library that provides comprehensive web security middleware for Python applications.

## Features

- **High Performance**: Rust-based security checks with minimal overhead
- **Comprehensive Security**: Rate limiting, CSRF protection, XSS prevention, SQL injection detection, and more
- **Framework Integration**: Native support for Django, Flask, and FastAPI
- **Easy Configuration**: Simple configuration with sensible defaults
- **Cross-Platform**: Works on Windows, Linux, and macOS

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/your-org/secureapis.git
cd secureapis

# Build the bindings
python bindings/python/setup.py build_ext --inplace
```

### Using pip (when published)

```bash
pip install secureapis
```

## Quick Start

### Basic Usage

```python
from secureapis import SecureAPIs, SecureAPIsConfig

# Create configuration
config = SecureAPIsConfig()
config.rate_limit_requests_per_minute = 100
config.enable_csrf_protection = True
config.enable_xss_protection = True

# Create SecureAPIs instance
secureapis = SecureAPIs(config)

# Check a request
result = secureapis.check_request(
    method="POST",
    path="/api/users",
    headers={"Content-Type": "application/json", "X-CSRF-Token": "valid-token"},
    body='{"name": "John Doe"}',
    ip_address="192.168.1.100"
)

if result.blocked:
    print(f"Request blocked: {result.reason}")
else:
    print("Request allowed")
```

### Django Integration

Add to your Django `settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware
    'secureapis.django_middleware.SecureAPIsMiddleware',
]

# SecureAPIs Configuration
SECUREAPIS_CONFIG = {
    'rate_limit_requests_per_minute': 100,
    'enable_csrf_protection': True,
    'enable_xss_protection': True,
    'enable_sql_injection_protection': True,
    'max_request_size_kb': 1024,
}
```

### Flask Integration

```python
from flask import Flask
from secureapis.flask_middleware import SecureAPIsFlask

app = Flask(__name__)

# Configure SecureAPIs
config = SecureAPIsConfig()
config.rate_limit_requests_per_minute = 100
config.enable_csrf_protection = True

# Initialize middleware
secureapis = SecureAPIsFlask(app, config)

@app.route('/api/users')
def get_users():
    # Request is automatically checked by middleware
    return {'users': []}
```

### FastAPI Integration

```python
from fastapi import FastAPI, Request, HTTPException
from secureapis import SecureAPIs, SecureAPIsConfig

app = FastAPI()
secureapis = SecureAPIs(SecureAPIsConfig())

@app.middleware("http")
async def secureapis_middleware(request: Request, call_next):
    # Convert FastAPI request to SecureAPIs format
    method = request.method
    path = str(request.url.path)
    headers = dict(request.headers)
    body = await request.body()
    ip = request.client.host if request.client else "unknown"

    result = secureapis.check_request(method, path, headers, body.decode(), ip)

    if result.blocked:
        raise HTTPException(status_code=403, detail=result.reason)

    response = await call_next(request)
    return response
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `rate_limit_requests_per_minute` | int | 60 | Maximum requests per minute per IP |
| `enable_csrf_protection` | bool | True | Enable CSRF token validation |
| `enable_xss_protection` | bool | True | Enable XSS attack detection |
| `enable_sql_injection_protection` | bool | True | Enable SQL injection detection |
| `enable_ip_reputation_check` | bool | False | Enable IP reputation checking |
| `max_request_size_kb` | int | 1024 | Maximum request body size in KB |
| `blocked_ips` | list | [] | List of blocked IP addresses |
| `allowed_origins` | list | ["*"] | CORS allowed origins |
| `trusted_hosts` | list | [] | Trusted host domains |

## Security Features

### Rate Limiting
- Configurable requests per minute per IP
- Automatic blocking of abusive clients
- Sliding window algorithm for fairness

### CSRF Protection
- Automatic token generation and validation
- Support for custom token headers
- Session-based token management

### XSS Prevention
- Input sanitization
- HTML entity encoding
- JavaScript injection detection

### SQL Injection Detection
- Pattern-based detection
- Parameterized query validation
- Database-specific escaping

### IP Reputation
- Integration with threat intelligence feeds
- Configurable blocklists
- Geographic filtering options

## Performance

SecureAPIs is built with performance in mind:
- **Zero-copy operations** where possible
- **Minimal memory allocations**
- **SIMD-accelerated pattern matching**
- **Concurrent request processing**

Typical overhead: < 1ms per request on modern hardware.

## Error Handling

```python
from secureapis import SecureAPIsException

try:
    result = secureapis.check_request(...)
except SecureAPIsException as e:
    print(f"Security check failed: {e}")
```

## Logging

SecureAPIs integrates with Python's logging system:

```python
import logging
logging.basicConfig(level=logging.INFO)

# SecureAPIs will log security events
```

## Development

### Building from Source

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build the Rust library
cargo build --release

# Build Python bindings
cd bindings/python
python setup.py build_ext --inplace
```

### Running Tests

```bash
cd bindings/python
python test_secureapis.py
```

### Cross-Platform Building

The bindings support Windows, Linux, and macOS. The build system automatically detects the platform and builds the appropriate native library.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## Support

- **Issues**: GitHub Issues
- **Documentation**: Full docs at docs.secureapis.com
- **Community**: Discord server