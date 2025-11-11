# SecureAPIs - Setup with Common Languages

**Quick setup guide** for integrating SecureAPIs with the most popular backend languages.

## The Pattern (All Languages)

```
1. Start SecureAPIs on port 3000
2. Start your backend on localhost:5000+ (only internal access)
3. All users connect to port 3000
4. SecureAPIs forwards clean requests to your backend
```

---

## 1. .NET / C# / ASP.NET Core

### Setup Your .NET API

**Program.cs:**
```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();

var app = builder.Build();

// IMPORTANT: Only listen on localhost
app.Urls.Add("http://127.0.0.1:5000");

app.UseRouting();
app.UseAuthorization();

app.MapControllers();

app.Run();
```

**appsettings.json:**
```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information"
    }
  }
}
```

### Deployment

**PowerShell:**
```powershell
# Terminal 1: Start SecureAPIs
cd c:\projects\secureapis
cargo run --release

# Terminal 2: Start your .NET app
cd c:\your-dotnet-project
dotnet run

# Users connect to: https://yourapi.com (reverse proxy to 3000)
# SecureAPIs forwards to: localhost:5000
```

**Nginx config (on your server):**
```nginx
server {
    listen 80;
    server_name api.yourcompany.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### What Happens

```
Client: POST https://api.yourcompany.com/api/users
         ↓
Nginx (443 HTTPS)
         ↓
SecureAPIs (3000) validates:
  ✓ Rate limit (not exceeded)
  ✓ JWT token (valid)
  ✓ Input (no SQL injection)
         ↓
.NET API (localhost:5000) processes:
  ✓ Receive clean request
  ✓ Query database
  ✓ Return user data
         ↓
Client receives response
```

**Your .NET code never knows about security!** SecureAPIs handled it.

---

## 2. Java / Spring Boot

### Setup Your Java API

**application.properties:**
```properties
server.port=8080
server.address=127.0.0.1
server.servlet.context-path=/api

spring.application.name=my-secure-api
logging.level.root=INFO
```

**Application.java:**
```java
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

**Controller example:**
```java
@RestController
@RequestMapping("/users")
public class UserController {
    
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        // Just process the request - SecureAPIs already validated it
        return ResponseEntity.ok(userService.save(user));
    }
}
```

### Deployment

**Bash/PowerShell:**
```bash
# Terminal 1: Start SecureAPIs
cd c:\projects\secureapis
cargo run --release

# Terminal 2: Start Java app
cd c:\your-java-project
mvn spring-boot:run

# Users connect to: https://api.yourcompany.com
# SecureAPIs forwards: localhost:8080
```

### What Happens

```
Client: POST https://api.yourcompany.com/users
         ↓
Load Balancer (443)
         ↓
SecureAPIs (3000)
  ✓ Rate limit check
  ✓ JWT validation
  ✓ Input sanitization
         ↓
Spring Boot (localhost:8080)
  ✓ User controller
  ✓ Business logic
  ✓ Database access
         ↓
Response back to client
```

---

## 3. Node.js / Express

### Setup Your Express API

**server.js:**
```javascript
const express = require('express');
const app = express();

// Middleware
app.use(express.json());

// Routes
app.post('/api/users', (req, res) => {
    // SecureAPIs already validated the input
    const user = {
        id: 1,
        name: req.body.name,
        email: req.body.email
    };
    res.json(user);
});

// IMPORTANT: Only listen on localhost
const PORT = 5001;
const HOST = '127.0.0.1';

app.listen(PORT, HOST, () => {
    console.log(`Express running on ${HOST}:${PORT}`);
    console.log(`(SecureAPIs forwards from port 3000)`);
});
```

**package.json:**
```json
{
  "name": "my-secure-api",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": {
    "start": "node server.js",
    "dev": "nodemon server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

### Deployment

**PowerShell:**
```powershell
# Terminal 1: Start SecureAPIs
cd c:\projects\secureapis
cargo run --release

# Terminal 2: Start Node.js
cd c:\your-node-project
npm install
npm start

# Users hit: https://api.yourcompany.com
# Nginx forwards to: localhost:3000 (SecureAPIs)
# SecureAPIs forwards to: localhost:5001 (Express)
```

### What Happens

```
Client Request
       ↓
SecureAPIs checks:
  ✓ Rate limit
  ✓ JWT token
  ✓ Input validation
       ↓
Express Route Handler
  ✓ req.body is clean
  ✓ Process business logic
  ✓ Send response
       ↓
Client receives response with security headers
```

---

## 4. Python / FastAPI

### Setup Your FastAPI

**main.py:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="My Secure API")

class User(BaseModel):
    name: str
    email: str

@app.post("/api/users")
async def create_user(user: User):
    """
    SecureAPIs already:
    - Validated rate limit
    - Checked JWT token
    - Validated input format
    - Blocked malicious requests
    """
    return {
        "id": 1,
        "name": user.name,
        "email": user.email
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    # IMPORTANT: Only listen on localhost
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
```

**requirements.txt:**
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
```

### Deployment

**PowerShell:**
```powershell
# Terminal 1: Start SecureAPIs
cd c:\projects\secureapis
cargo run --release

# Terminal 2: Start Python
cd c:\your-python-project
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py

# Users connect to: https://api.yourcompany.com
# Proxies to: localhost:3000 (SecureAPIs)
# Which forwards to: localhost:8000 (FastAPI)
```

### What Happens

```
Client: POST https://api.yourcompany.com/api/users
         ↓
SecureAPIs (Rust)
  - Rate limited? Check
  - JWT valid? Check
  - Input safe? Check
         ↓
FastAPI (Python on localhost:8000)
  - Receive validated User object
  - Process with business logic
  - Return clean response
         ↓
Client gets response
```

---

## 5. Python / Django

### Setup Your Django API

**settings.py:**
```python
ALLOWED_HOSTS = ['127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'myapp',
]

REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ]
}
```

**urls.py:**
```python
from django.urls import path
from myapp.views import UserCreateView

urlpatterns = [
    path('api/users/', UserCreateView.as_view(), name='create-user'),
]
```

**views.py:**
```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserCreateView(APIView):
    def post(self, request):
        # SecureAPIs already validated everything
        user_data = {
            'id': 1,
            'name': request.data.get('name'),
            'email': request.data.get('email')
        }
        return Response(user_data, status=status.HTTP_201_CREATED)
```

### Deployment

```powershell
# Terminal 1: SecureAPIs
cd c:\projects\secureapis
cargo run --release

# Terminal 2: Django
cd c:\your-django-project
python manage.py runserver 127.0.0.1:8000

# Users: https://api.yourcompany.com
# Proxy: localhost:3000
# Backend: localhost:8000
```

---

## 6. Go / Gin

### Setup Your Go API

**main.go:**
```go
package main

import (
    "github.com/gin-gonic/gin"
    "log"
)

func main() {
    router := gin.Default()
    
    router.POST("/api/users", createUser)
    router.GET("/health", health)
    
    // IMPORTANT: Only listen on localhost
    if err := router.Run("127.0.0.1:9000"); err != nil {
        log.Fatal(err)
    }
}

func createUser(c *gin.Context) {
    type User struct {
        Name  string `json:"name"`
        Email string `json:"email"`
    }
    
    var user User
    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }
    
    // SecureAPIs already validated this
    c.JSON(201, gin.H{
        "id":    1,
        "name":  user.Name,
        "email": user.Email,
    })
}

func health(c *gin.Context) {
    c.JSON(200, gin.H{"status": "ok"})
}
```

**go.mod:**
```
module my-secure-api

go 1.21

require github.com/gin-gonic/gin v1.9.1
```

### Deployment

```bash
# Terminal 1: SecureAPIs
cd c:\projects\secureapis
cargo run --release

# Terminal 2: Go app
cd c:\your-go-project
go run main.go

# Users: https://api.yourcompany.com
# Proxy: localhost:3000
# Backend: localhost:9000
```

---

## Architecture Comparison

All languages follow the same pattern:

```
┌─────────────────────────────────────────────────────────────┐
│                    Client (Internet)                         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS/TLS
                         ↓
        ┌────────────────────────────────┐
        │ Nginx/Load Balancer            │
        │ (Port 443)                      │
        └────────────┬─────────────────────┘
                     │ HTTP
                     ↓
        ┌────────────────────────────────┐
        │ SecureAPIs (Rust Binary)       │
        │ Port 3000                      │
        │ • Rate limit                   │
        │ • JWT validation               │
        │ • Input validation             │
        │ • Threat detection             │
        └────────────┬─────────────────────┘
                     │ HTTP (Internal only)
                     ↓
        ┌────────────────────────────────┐
        │ Your Backend (ANY Language)    │
        │ Localhost:PORT                 │
        │ • .NET (5000)                  │
        │ • Java (8080)                  │
        │ • Node (5001)                  │
        │ • Python (8000)                │
        │ • Go (9000)                    │
        └────────────────────────────────┘
```

---

## Configuration for Your Language

Regardless of language, configure SecureAPIs once:

```rust
// src/examples/production_setup.rs (or create your own)

let security_config = SecurityConfig::new()
    .with_rate_limit(100, 60)           // 100 req/min
    .with_jwt_validation("your-secret")  // JWT tokens
    .with_input_sanitization(true)       // Block bad input
    .with_cors_config(cors)              // CORS policy
    .add_backend_route("/", "127.0.0.1:5000") // YOUR PORT
    .strict_mode();
```

This **single configuration** protects ALL requests to your backend, regardless of its language!

---

## Multi-Service Setup

If you have multiple services in different languages:

```rust
let security_config = SecurityConfig::new()
    .with_rate_limit(100, 60)
    .with_jwt_validation(secret)
    
    // Route different paths to different backends
    .add_backend_route("/api/auth/*", "127.0.0.1:5000")    // .NET
    .add_backend_route("/api/users/*", "127.0.0.1:8080")   // Java
    .add_backend_route("/api/products/*", "127.0.0.1:5001") // Node
    .add_backend_route("/api/reports/*", "127.0.0.1:8000"); // Python
```

Now:
- Users connect to SecureAPIs (port 3000)
- Different paths route to different backends
- All traffic goes through SecureAPIs first
- Unified security configuration

---

## Troubleshooting

### "Connection refused" error
✅ Check your backend is running on the correct localhost port
```powershell
# Check if port is in use
netstat -ano | findstr :5000
```

### "Cannot reach backend"
✅ Make sure backend is bound to 127.0.0.1, not 0.0.0.0
```csharp
// .NET - correct
app.Urls.Add("http://127.0.0.1:5000");

// Python - correct
uvicorn.run(app, host="127.0.0.1", port=8000)
```

### Rate limiting too strict
✅ Adjust in SecureAPIs config:
```rust
.with_rate_limit(1000, 60)  // Increase limit
```

### JWT validation failing
✅ Make sure secret key matches in SecureAPIs and your backend
```rust
.with_jwt_validation("your-same-secret-key")
```

---

## Summary

1. **Pick your language** (.NET, Java, Node, Python, Go, etc.)
2. **Configure your backend to listen on localhost only**
3. **Start SecureAPIs** (port 3000)
4. **Start your backend** (localhost:XXXX)
5. **Users connect to SecureAPIs** (port 3000)
6. **SecureAPIs forwards to your backend**

**That's it!** No code changes, no language-specific integrations, just one simple pattern that works for everything.

See [QUICK_START_DEPLOYMENT.md](QUICK_START_DEPLOYMENT.md) for quick setup, or [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production.
