# SecureAPIs Java Bindings

Java bindings for SecureAPIs - high-performance security middleware written in Rust.

## Installation

### From Source

```bash
# Build the Rust library
mvn compile

# Or build everything
mvn package
```

### From Maven Central (Future)

```xml
<dependency>
    <groupId>com.secureapis</groupId>
    <artifactId>secureapis-java</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Usage

### Spring Boot Integration

```java
@Configuration
public class SecurityConfig {

    @Bean
    public SecureAPIsFilter secureAPIsFilter() {
        SecureAPIsConfig config = new SecureAPIsConfig();
        config.setRateLimitRequests(100);
        config.setRateLimitWindowSeconds(60);
        config.setJwtSecret("your-jwt-secret");
        config.setEnableInputValidation(true);
        config.setEnableSecurityHeaders(true);

        return new SecureAPIsFilter(config);
    }
}
```

### Servlet Filter

```java
@WebFilter("/*")
public class SecureAPIsWebFilter extends SecureAPIsFilter {

    public SecureAPIsWebFilter() {
        super(createConfig());
    }

    private static SecureAPIsConfig createConfig() {
        SecureAPIsConfig config = new SecureAPIsConfig();
        config.setRateLimitRequests(1000);
        config.setRateLimitWindowSeconds(300);
        return config;
    }
}
```

### Direct API Usage

```java
// Create configuration
SecureAPIsConfig config = new SecureAPIsConfig();
config.setRateLimitRequests(100);
config.setRateLimitWindowSeconds(60);

// Create instance
SecureAPIs secureAPIs = new SecureAPIs(config);

// Check a request
HttpServletRequest request = // ... your request
SecurityCheckResult result = secureAPIs.checkRequest(request);

if (!result.isAllowed()) {
    // Block the request
    response.setStatus(result.getStatusCode());
    response.getWriter().write("{\"error\":\"" + result.getErrorMessage() + "\"}");
    return;
}

// Request is allowed, continue processing
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