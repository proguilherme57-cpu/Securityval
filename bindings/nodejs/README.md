# SecureAPIs Node.js Bindings

Node.js bindings for SecureAPIs - high-performance security middleware written in Rust.

## Installation

### From Source

```bash
# Build the Rust library
npm run build:rust

# Build the Node.js bindings
npm run build
```

### From NPM (Future)

```bash
npm install secureapis
```

## Usage

### Express.js Middleware

```javascript
const express = require('express');
const { SecureAPIsMiddleware } = require('secureapis');

const app = express();

// Configure SecureAPIs
const config = {
  rateLimitRequests: 100,
  rateLimitWindowSeconds: 60,
  jwtSecret: 'your-jwt-secret',
  enableInputValidation: true,
  enableSecurityHeaders: true
};

// Add middleware
app.use(SecureAPIsMiddleware(config));

// Your routes
app.get('/api/users', (req, res) => {
  res.json({ users: [] });
});

app.listen(3000);
```

### Direct API Usage

```javascript
const { SecureAPIs } = require('secureapis');

const secureAPIs = new SecureAPIs({
  rateLimitRequests: 1000,
  rateLimitWindowSeconds: 300
});

// Check a request
const result = secureAPIs.checkRequest({
  method: 'POST',
  url: '/api/users',
  headers: { 'content-type': 'application/json' },
  body: '{"name":"John"}',
  ip: '192.168.1.1'
});

if (result.allowed) {
  console.log('Request allowed');
} else {
  console.log('Request blocked:', result.reason);
}
```

## Configuration Options

- `rateLimitRequests`: Number of requests allowed per window (default: 100)
- `rateLimitWindowSeconds`: Time window in seconds (default: 60)
- `jwtSecret`: Secret key for JWT validation
- `enableInputValidation`: Enable SQL injection/XSS protection (default: true)
- `enableSecurityHeaders`: Add security headers to responses (default: true)
- `enableCors`: Enable CORS support (default: false)

## Security Features

- **Rate Limiting**: Per-IP request limiting
- **JWT Authentication**: Bearer token validation
- **Input Validation**: SQL injection, XSS, command injection detection
- **Security Headers**: OWASP recommended headers
- **Threat Detection**: Pattern-based attack detection

## Performance

- **Latency**: ~50-100 microseconds per request
- **Memory**: ~50MB base memory usage
- **Throughput**: Thousands of requests/second

## Platform Support

- Linux (x64, arm64)
- macOS (x64, arm64)
- Windows (x64)