# SecureAPIs - Multi-Language Integration Guide

## The Key Insight: SecureAPIs as a Reverse Proxy/Service

**You don't need to port SecureAPIs to every language.** Instead, you deploy it as a **standalone service** that sits in front of any backend API, regardless of the language it's written in.

```
┌─────────────────────────────────────────────────────────────┐
│                    Internet / Clients                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP Request
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              SecureAPIs (Rust Binary/Service)                │
│         (Rate Limit, Validate, Check Auth, etc.)             │
└────────────────────────┬────────────────────────────────────┘
                         │ Cleaned HTTP Request
                         ↓
┌─────────────────────────────────────────────────────────────┐
│   Your API Backend (Can be in ANY language)                  │
│  ┌──────────────┬──────────────┬──────────────┐              │
│  │  Node.js     │  .NET        │  Java        │              │
│  │  Express     │  ASP.NET     │  Spring Boot │              │
│  │  FastAPI     │  FastAPI     │  Micronaut   │              │
│  │  Django      │  WCF         │  Quarkus     │              │
│  │  Go Gin      │  Asp.Core    │  Play        │              │
│  └──────────────┴──────────────┴──────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

## How Different Languages Use SecureAPIs

### Pattern 1: Reverse Proxy (Recommended)

**All languages work the same way:**

```
Client → SecureAPIs (Port 3000) → Your Backend (Port 5000)
         [Rust Binary]            [Any Language]
```

**Your backend doesn't know or care about SecureAPIs.** It just receives clean HTTP requests.

---

## Language-Specific Integration Examples

### 1. **.NET / C# / ASP.NET Core**

```csharp
// Your ASP.NET API runs normally on port 5000
// Configure to only listen on localhost (not exposed to internet)

// In Startup.cs or Program.cs
app.Urls.Add("http://localhost:5000");
app.Run();

// Users connect to SecureAPIs on port 3000
// SecureAPIs forwards safe requests to localhost:5000
```

**Deployment:**
```
1. Start SecureAPIs:    cargo run --release
2. Start .NET API:      dotnet run
3. Users hit:           https://yourapi.com (reverse proxy to 3000)
4. SecureAPIs forwards: localhost:5000
```

**No code changes needed in your .NET application!**

---

### 2. **Java / Spring Boot**

```java
// Your Spring Boot API runs normally on port 8080
// Just bind to localhost only

// application.properties
server.address=127.0.0.1
server.port=8080

// Users connect to SecureAPIs, not your Java app directly
```

**Deployment:**
```
1. Start SecureAPIs:         cargo run --release
2. Start Java Spring Boot:   java -jar app.jar
3. Users hit:                https://yourapi.com
4. SecureAPIs forwards:      localhost:8080
```

---

### 3. **Node.js / Express**

```javascript
// Your Express app runs on localhost:5000
// Users never connect directly

const express = require('express');
const app = express();

app.listen(5000, '127.0.0.1', () => {
    console.log('Express listening on 127.0.0.1:5000');
});

// SecureAPIs is on port 3000 and forwards to port 5000
```

**Nginx config (forwards 3000 → 5000):**
```nginx
server {
    listen 3000;
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
    }
}
```

---

### 4. **Python / FastAPI or Django**

```python
# FastAPI example - runs on localhost:8000
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/data")
async def get_data():
    return {"data": "safe"}

# Run: uvicorn main:app --host 127.0.0.1 --port 8000
```

**Users connect to SecureAPIs (port 3000), not your Python app (port 8000).**

---

### 5. **Go / Gin / Echo**

```go
// Your Go API runs on localhost:9000
// SecureAPIs sits in front

func main() {
    router := gin.Default()
    router.GET("/api/data", func(c *gin.Context) {
        c.JSON(200, gin.H{"data": "safe"})
    })
    router.Run("127.0.0.1:9000")
}
```

---

## Complete Multi-Language Architecture Example

### The Setup:

```
Internet/Clients (Port 443 HTTPS)
          ↓
   Load Balancer / Firewall
          ↓
   SecureAPIs (Port 3000) [Rust]
    - Rate limits: 100 req/min
    - Validates input
    - Checks JWT tokens
    - Logs threats
          ↓
   Internal Network (Private, no internet access)
          ↓
   ┌──────────────────┬──────────────────┬──────────────────┐
   ↓                  ↓                  ↓                  ↓
.NET API         Java API           Node.js API       Python API
(Port 5000)      (Port 8080)        (Port 5001)       (Port 8000)
Business Logic   Business Logic     Business Logic    Business Logic
```

### What Each Service Does:

**SecureAPIs (Rust):**
- ✅ Authenticate JWT tokens
- ✅ Enforce rate limits
- ✅ Validate input
- ✅ Block malicious requests
- ✅ Log all activity

**Your Backends (Any Language):**
- ✅ Process clean requests
- ✅ Access database
- ✅ Run business logic
- ✅ Return results
- ❌ Don't worry about security - SecureAPIs already handled it

---

## Configuration: Routing to Multiple Backends

SecureAPIs can route different paths to different backends:

```rust
// In your SecureAPIs config
SecurityConfig::new()
    .add_backend_route("/api/dotnet/*", "localhost:5000")
    .add_backend_route("/api/java/*", "localhost:8080")
    .add_backend_route("/api/node/*", "localhost:5001")
    .add_backend_route("/api/python/*", "localhost:8000")
```

---

## Deployment Scenarios

### Scenario 1: Single Backend (Most Common)

```
Client → SecureAPIs → Your .NET/Java/Python App
```

```bash
# Terminal 1: Run SecureAPIs
cargo run --example production_setup

# Terminal 2: Run your backend (any language)
# For .NET:  dotnet run
# For Java:  java -jar app.jar
# For Node:  npm start
# For Python: python main.py
```

### Scenario 2: Multiple Backends with API Gateway

```
Client → SecureAPIs (3000) → Load Balancer → Microservices
                              - .NET (5000)
                              - Java (8080)
                              - Node (5001)
```

### Scenario 3: Kubernetes Deployment

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api-security-stack
spec:
  containers:
  # SecureAPIs gateway
  - name: secureapis
    image: secureapis:latest
    ports:
    - containerPort: 3000
    
  # Your .NET API
  - name: dotnet-api
    image: yourcompany/dotnet-api:latest
    ports:
    - containerPort: 5000
    
  # Your Java API
  - name: java-api
    image: yourcompany/java-api:latest
    ports:
    - containerPort: 8080
```

---

## HTTP Request Flow (Language-Agnostic)

All HTTP requests follow the same pattern:

```
1. Request comes in: POST /api/users
   {
     "username": "john",
     "password": "secret123"
   }

2. SecureAPIs (Rust) processes:
   ✓ Rate limit check - PASS
   ✓ Input validation - PASS
   ✓ JWT validation - PASS
   ✓ SQL injection check - PASS
   ✓ Add security headers - Added

3. Forward to backend: http://localhost:5000/api/users
   Same request, now verified

4. Backend (any language) processes:
   ✓ Receive request
   ✓ Run business logic
   ✓ Return response

5. Response goes back:
   200 OK
   {
     "id": 123,
     "username": "john"
   }

6. SecureAPIs returns to client with security headers
```

**Key: The request is IDENTICAL whether your backend is Rust, Java, .NET, Python, or Go!**

---

## Client Integration (Language-Agnostic)

Clients don't care about your backend language. They just make HTTP requests:

### JavaScript Client:
```javascript
const response = await fetch('https://api.example.com/users', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({ username: 'john' })
});
```

### Python Client:
```python
import requests

response = requests.post(
    'https://api.example.com/users',
    json={'username': 'john'},
    headers={'Authorization': f'Bearer {token}'}
)
```

### C# Client:
```csharp
using (var client = new HttpClient())
{
    var response = await client.PostAsJsonAsync(
        "https://api.example.com/users",
        new { username = "john" }
    );
}
```

### Java Client:
```java
HttpClient client = HttpClient.newHttpClient();
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .POST(BodyPublishers.ofString("{\"username\":\"john\"}"))
    .header("Content-Type", "application/json")
    .build();
```

**All clients work the same way - they just make HTTP requests to SecureAPIs!**

---

## Configuration Sharing Across Backends

SecureAPIs provides a **unified security configuration** for all backends:

```rust
// One config for ALL your services
SecurityConfig::new()
    // JWT validation (shared)
    .with_jwt_validation("your-secret-key")
    
    // Rate limiting (shared across all backends)
    .with_rate_limit(100, 60)  // 100 req/min total
    
    // Input validation (shared)
    .with_input_sanitization(true)
    
    // CORS (shared)
    .with_cors_config(cors_policy)
```

**Benefit:** You configure security ONCE, and it applies to:
- .NET services on port 5000
- Java services on port 8080
- Node.js services on port 5001
- Python services on port 8000
- Any other service

---

## Monitoring Multi-Language Stack

SecureAPIs dashboard shows metrics for ALL services:

```
Dashboard at http://localhost:3000
├── Total Requests: 1,234
├── Blocked Requests: 45
├── Threat Level: 🟡 Medium
└── Breakdown:
    ├── Rate Limited: 12
    ├── Invalid Input: 15
    ├── Auth Failed: 10
    ├── Other: 8
```

**You don't need to check each backend's logs!** SecureAPIs shows everything in one place.

---

## Best Practices

### ✅ DO:
- Run SecureAPIs on a public port (3000, 443)
- Run backends on localhost-only (127.0.0.1)
- Configure SecureAPIs with all protections enabled
- Monitor SecureAPIs dashboard in production
- Use HTTPS in front of SecureAPIs (via Nginx/LoadBalancer)

### ❌ DON'T:
- Expose backend ports directly to internet
- Disable security features
- Run SecureAPIs on the same machine as backends for large scale
- Make changes to backends for security (SecureAPIs handles it)

---

## Common Questions

### Q: Do I need to rewrite my Java/C#/.NET code?
**A:** No! Zero changes required. SecureAPIs sits in front as a reverse proxy.

### Q: Can I use SecureAPIs with microservices?
**A:** Yes! Use it as an API Gateway in front of multiple services.

### Q: What if I want different security rules for different backends?
**A:** Use path-based routing:
```rust
.add_route_config("/api/strict/*", strict_config)
.add_route_config("/api/normal/*", normal_config)
```

### Q: Does my backend need to know about SecureAPIs?
**A:** No. It just receives normal HTTP requests. Completely transparent.

### Q: How do I handle authentication across multiple backends?
**A:** SecureAPIs validates JWT tokens once, then forwards to any backend.

### Q: Can I use this with existing API gateways (Kong, AWS API Gateway)?
**A:** Yes! SecureAPIs can be:
- **Before** your gateway (first defense)
- **Instead of** your gateway (simpler architecture)
- **Alongside** your gateway (layered security)

---

## Migration Path for Existing APIs

### Step 1: Start with your existing backend (any language)
```
Client → Your API (port 5000)  ← Exposed to internet
```

### Step 2: Add SecureAPIs in front
```
Client → SecureAPIs (3000) → Your API (localhost:5000)
```

### Step 3: Configure your infrastructure
- Point DNS to SecureAPIs (port 3000)
- Use HTTPS at the edge
- Keep backend on localhost

### Step 4: Monitor and adjust
- Check SecureAPIs dashboard
- Adjust rate limits based on traffic
- Enable/disable features as needed

**No code changes needed in your backend!**

---

## Example: Real-World Multi-Language Company

**Scenario:** Company with multiple teams and languages

```
Company API Platform
│
├─ SecureAPIs Gateway (Rust) ← Unified Security
│  ├─ Rate limiting: 1000 req/min per user
│  ├─ JWT validation
│  ├─ Input sanitization
│  └─ Threat detection
│
├─ /api/auth/* → C#/.NET Auth Service
│  (Handles login, JWT generation)
│
├─ /api/users/* → Java Service
│  (User management)
│
├─ /api/products/* → Node.js Service
│  (Product catalog)
│
└─ /api/reports/* → Python Service
   (Analytics and reports)

External Traffic (HTTPS)
  → Nginx/LoadBalancer (443)
  → SecureAPIs (3000)
  → Service Router (based on path)
  → Appropriate backend service
```

**Each team uses their preferred language, SecureAPIs handles security for all!**

---

## Summary

**The Key Insight:**

SecureAPIs is NOT a library to import into your code. It's a **standalone security service** that protects ALL your APIs, regardless of what language they're written in.

```
Language        Backend        SecureAPIs Usage
─────────────────────────────────────────────────
.NET/C#         ASP.NET        Standalone reverse proxy
Java            Spring Boot    Standalone reverse proxy
Node.js         Express        Standalone reverse proxy
Python          FastAPI        Standalone reverse proxy
Go              Gin            Standalone reverse proxy
Rust            Axum           Standalone reverse proxy
PHP             Laravel        Standalone reverse proxy
Ruby            Rails          Standalone reverse proxy
```

**You run ONE SecureAPIs instance, and it protects services in any language!**

---

## Next Steps

1. **Understand the architecture** - You now know SecureAPIs acts as a reverse proxy
2. **Deploy example** - `cargo run --example production_setup`
3. **Configure for your backend** - Update routes and security settings
4. **Test the flow** - Make requests and see security in action
5. **Deploy to production** - Follow DEPLOYMENT_GUIDE.md

See [QUICK_START_DEPLOYMENT.md](QUICK_START_DEPLOYMENT.md) for setup instructions.
