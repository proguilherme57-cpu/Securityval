# SecureAPIs Architecture Diagrams

Visual representations of how SecureAPIs integrates with any backend.

## Single Backend (Most Common)

```
┌──────────────────────────────────────────────────────────────┐
│                      Users/Internet                           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTPS Request
                         │ POST /api/users
                         │ {"username":"john","password":"..."}
                         ↓
                ┌─────────────────────────┐
                │  Firewall / LB / Proxy  │
                │  (Optional HTTPS)       │
                └───────────┬─────────────┘
                            │
                            │ HTTP
                            ↓
                ┌─────────────────────────────────────────┐
                │      SecureAPIs (Rust)                  │
                │      Port 3000                          │
                │  ┌─────────────────────────────────┐   │
                │  │ Security Checks:                │   │
                │  │ ✓ Rate Limit                    │   │
                │  │ ✓ JWT Validation                │   │
                │  │ ✓ Input Sanitization            │   │
                │  │ ✓ Threat Detection              │   │
                │  │ ✓ CORS Check                    │   │
                │  │ ✓ Headers Validation            │   │
                │  └─────────────────────────────────┘   │
                └───────────┬─────────────────────────────┘
                            │
                    BLOCKED? └─→ ❌ 403/429/400
                    
                    ALLOWED? └─→ ↓
                            
                ┌─────────────────────────────────┐
                │  Your Backend (ANY LANGUAGE)    │
                │  127.0.0.1:PORT                 │
                │  ┌───────────────────────────┐  │
                │  │ .NET Core (5000)          │  │
                │  │ Spring Boot (8080)        │  │
                │  │ Express.js (5001)         │  │
                │  │ FastAPI (8000)            │  │
                │  │ Gin/Go (9000)             │  │
                │  │ Laravel (5002)            │  │
                │  └───────────────────────────┘  │
                │  Business Logic                 │
                │  Database Access                │
                └─────────────┬───────────────────┘
                              │
                        ✓ Process Request
                        ✓ Return Response
                              │
                ┌─────────────────────────────┐
                │  SecureAPIs                 │
                │  ┌───────────────────────┐  │
                │  │ Add Security Headers  │  │
                │  │ Log Event             │  │
                │  │ Update Metrics        │  │
                │  └───────────────────────┘  │
                └─────────────┬───────────────┘
                              │
                              ↓
                    ← Response with Headers
                      200 OK
                      {"id":1,"username":"john"}
```

---

## Multi-Backend Routing

```
                         Internet
                            │
                            ↓
                  SecureAPIs (Port 3000)
                            │
                ┌───────────┼───────────┐
                │           │           │
                ↓           ↓           ↓
          /api/auth/*  /api/users/* /api/products/*
                │           │           │
    ┌───────────┘   ┌───────┴────┐    │
    │               │            │    │
    ↓               ↓            ↓    ↓
  .NET API      Java API     Node.js  Python
  Port 5000     Port 8080    Port 5001 Port 8000
  ASP.NET       Spring Boot  Express   FastAPI
```

---

## Microservices Architecture

```
                         ┌─────────┐
                         │  Client │
                         └────┬────┘
                              │
                              ↓
                       ┌──────────────┐
                       │ Load Balancer│
                       │ (HTTPS/TLS)  │
                       └──────┬───────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ↓             ↓             ↓
           SecureAPIs    SecureAPIs    SecureAPIs
           Instance 1    Instance 2    Instance 3
           (Port 3000)   (Port 3000)   (Port 3000)
                │             │             │
                └─────────────┼─────────────┘
                              │
                ┌─────────────┼──────────────────┐
                │             │                  │
                ↓             ↓                  ↓
           Microservice   Microservice       Microservice
           (.NET Core)    (Java)             (Python)
           Port 5000      Port 8080          Port 8000
```

---

## Kubernetes Deployment

```
┌──────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                     │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                 Ingress Controller                  │ │
│  │              (Handles HTTPS/TLS)                    │ │
│  └─────────────────┬───────────────────────────────────┘ │
│                    │                                      │
│  ┌─────────────────┴───────────────────────────────────┐ │
│  │         SecureAPIs Service (ClusterIP)              │ │
│  │                                                     │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │ Pod 1: SecureAPIs │ Pod 2: SecureAPIs       │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  └─────────────────┬───────────────────────────────────┘ │
│                    │                                      │
│  ┌─────────────────┴────────┬────────────────┐           │
│  │                          │                │           │
│  ↓                          ↓                ↓           │
│ ┌─────────────────┐  ┌─────────────┐  ┌──────────────┐  │
│ │ API Service 1   │  │ API Service │  │ API Service  │  │
│ │ (.NET Core)     │  │ (Java)      │  │ (Python)     │  │
│ │                 │  │             │  │              │  │
│ │ Deployment:     │  │ Deployment: │  │ Deployment:  │  │
│ │ Replicas: 3     │  │ Replicas: 2 │  │ Replicas: 2  │  │
│ └─────────────────┘  └─────────────┘  └──────────────┘  │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

---

## Request Flow Timeline

```
Time  Component           Action                      Status
────────────────────────────────────────────────────────────────
T0    Client             POST /api/users              ↓
      HTTPS with JWT

T1    Load Balancer      Decrypt TLS                  ↓
                         Forward to SecureAPIs

T2    SecureAPIs         Check rate limit             ↓
                         (Token bucket algorithm)     
                         ✓ PASS

T3    SecureAPIs         Validate JWT token           ↓
                         (Verify signature & exp)
                         ✓ PASS

T4    SecureAPIs         Validate input               ↓
                         (SQL injection check)
                         ✓ PASS

T5    SecureAPIs         Check threat patterns        ↓
                         (Bot, anomalies)
                         ✓ PASS

T6    SecureAPIs         Add security headers         ↓
                         Forward to backend

T7    Backend API        Receive request              ↓
                         (No knowledge of security)
                         Process business logic

T8    Backend API        Query database               ↓
                         Generate response

T9    SecureAPIs         Add more security headers    ↓
                         Log metrics
                         Cache if applicable

T10   Load Balancer      Encrypt with TLS             ↓
                         Return to client

T11   Client             Receive response             ✓ COMPLETE
                         All headers checked
                         Data verified
```

**Total Time: 50-100 microseconds**

---

## Security Layers

```
Layer 7: Application Layer
  ├─ JWT Validation
  ├─ SQL Injection Prevention
  ├─ XSS Prevention
  └─ Command Injection Prevention

Layer 6: Presentation Layer
  ├─ Input Sanitization
  ├─ JSON/XML Validation
  └─ Content-Type Checks

Layer 5: Session Layer
  ├─ CSRF Token Validation
  ├─ Session Management
  └─ Cookie Security

Layer 4: Transport Layer
  ├─ TLS/SSL (External)
  ├─ Rate Limiting
  └─ Connection Timeouts

Layer 3: Network Layer
  ├─ IP Reputation
  ├─ DDoS Detection
  └─ IP Blocking

Layer 1-2: Physical/Data Link
  └─ (Handled by infrastructure)
```

---

## Performance Overview

```
Request Processing Pipeline
───────────────────────────

Input: HTTP Request
   │
   ├─ Rate Limiter:          2-5 μs
   │
   ├─ JWT Validation:        20-30 μs
   │
   ├─ Input Validation:      10-50 μs
   │
   ├─ Threat Detection:      5-15 μs
   │
   ├─ Security Headers:      1-3 μs
   │
   └─ Forward to Backend:    5-10 μs
   
   ├─ Network Transit:       100-500 μs (variable)
   │
   ├─ Backend Processing:    1-100 ms (depends on logic)
   │
   └─ Response to Client:    50-200 μs

Total Overhead from SecureAPIs: 50-100 μs
(Negligible compared to backend processing)
```

---

## Data Flow Diagram

```
Client Request
    │
    │ {
    │   "method": "POST",
    │   "headers": {..., "Authorization": "Bearer ..."},
    │   "body": {"username": "john"}
    │ }
    ↓
┌─────────────────────────────────────────────┐
│ SecureAPIs Request Handler                  │
│                                             │
│  1. Parse HTTP headers                      │
│  2. Extract JWT from Authorization header   │
│  3. Validate JWT signature & claims         │
│  4. Parse JSON body                         │
│  5. Validate body format                    │
│  6. Check for injection patterns            │
│  7. Check rate limit for this IP/user       │
│  8. Check threat patterns                   │
│                                             │
│  Result: Request object                     │
│  {                                          │
│    user_id: 123,                            │
│    method: "POST",                          │
│    path: "/api/users",                      │
│    validated_body: {...},                   │
│    ip: "192.168.1.1",                       │
│    timestamp: <now>                         │
│  }                                          │
└─────────────────────────────────────────────┘
    │
    ↓ (If all checks pass)
┌─────────────────────────────────────────────┐
│ Forward to Backend                          │
│                                             │
│ POST http://127.0.0.1:5000/api/users        │
│ Headers: [security headers + original]      │
│ Body: [same as received]                    │
└─────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────┐
│ Backend API (Any Language)                  │
│                                             │
│  • No knowledge of security checks         │
│  • Only receives valid requests            │
│  • Can focus on business logic             │
│  • No security code needed                 │
└─────────────────────────────────────────────┘
    │
    ↓ Response
    │ {
    │   "status": 201,
    │   "headers": {...},
    │   "body": {"id": 1, "username": "john"}
    │ }
    ↓
┌─────────────────────────────────────────────┐
│ SecureAPIs Response Handler                 │
│                                             │
│  1. Receive response                        │
│  2. Add security headers                    │
│  3. Log event                               │
│  4. Update metrics/monitoring               │
│  5. Cache if applicable                     │
│  6. Return to client                        │
└─────────────────────────────────────────────┘
    │
    ↓ (to Client)
    Response {
      status: 201,
      headers: {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Strict-Transport-Security": "...",
        ... (other security headers)
      },
      body: {"id": 1, "username": "john"}
    }
```

---

## Threat Detection Flow

```
Request Arrives
    ↓
    
Is it in rate limit?
    ├─ YES → Continue
    └─ NO → 429 Too Many Requests

Is JWT valid?
    ├─ YES → Continue
    └─ NO → 401 Unauthorized

Is input format valid?
    ├─ YES → Continue
    └─ NO → 400 Bad Request

Does it contain SQL injection pattern?
    ├─ YES → 403 Forbidden
    └─ NO → Continue

Does it contain XSS pattern?
    ├─ YES → 403 Forbidden
    └─ NO → Continue

Does IP have bad reputation?
    ├─ YES → 403 Forbidden
    └─ NO → Continue

Is behavior anomalous?
    ├─ YES → Log & Monitor → Continue or Block
    └─ NO → Continue

✓ PASS ALL CHECKS

Forward to backend
```

---

## Monitoring & Observability

```
SecureAPIs Metrics
───────────────────

Real-time Dashboard Shows:
├─ Requests/sec (current rate)
├─ Rate-limited requests (count)
├─ Failed JWT validations (count)
├─ Invalid inputs blocked (count)
├─ Threats detected (count)
├─ Latency (p50, p95, p99)
├─ Error rates by type
├─ Top blocked IPs
├─ Top attack patterns
└─ Current threat level (🟢🟡🔴)

Time-series Graphs:
├─ Request volume over time
├─ Security events over time
├─ Latency distribution
├─ Backend response times
└─ Error rates over time

Logging:
├─ All blocked requests (with reason)
├─ JWT validation failures
├─ SQL injection attempts
├─ Rate limit violations
├─ Suspicious IP activity
└─ Backend errors
```

---

## Deployment Decision Tree

```
Start: I want to protect my API

Q1: What language is your backend?
├─ .NET/C# → See SETUP_COMMON_LANGUAGES.md (Section 1)
├─ Java → See SETUP_COMMON_LANGUAGES.md (Section 2)
├─ Node.js → See SETUP_COMMON_LANGUAGES.md (Section 3)
├─ Python → See SETUP_COMMON_LANGUAGES.md (Section 4)
├─ Go → See SETUP_COMMON_LANGUAGES.md (Section 6)
└─ Other → Follows the same pattern

Q2: Do you have multiple services?
├─ Single service → Single SecureAPIs instance
├─ Multiple services → SecureAPIs with path-based routing
└─ Microservices → Deploy SecureAPIs per namespace (Kubernetes)

Q3: What's your scale?
├─ < 100 req/sec → Single instance
├─ 100-1000 req/sec → 2-3 instances + load balancer
└─ > 1000 req/sec → Kubernetes deployment with horizontal scaling

Q4: What's your infrastructure?
├─ VPS/Server → Docker + Nginx reverse proxy
├─ Kubernetes → Native K8s deployment
├─ Cloud (AWS/GCP/Azure) → Load balancer + instances
└─ Serverless → SecureAPIs in Lambda/Cloud Functions (edge)

→ RESULT: Your deployment architecture
```

---

## Quick Reference: All Languages Same Pattern

| Language | Port | Binding | SecureAPIs Route |
|----------|------|---------|------------------|
| .NET Core | 5000 | localhost | 127.0.0.1:5000 |
| Java | 8080 | localhost | 127.0.0.1:8080 |
| Node.js | 5001 | localhost | 127.0.0.1:5001 |
| Python FastAPI | 8000 | localhost | 127.0.0.1:8000 |
| Python Django | 8000 | localhost | 127.0.0.1:8000 |
| Go Gin | 9000 | localhost | 127.0.0.1:9000 |
| Ruby Rails | 3000 | localhost | 127.0.0.1:3000 |
| PHP Laravel | 8001 | localhost | 127.0.0.1:8001 |

**All follow the same pattern:**
```
Client → SecureAPIs (3000) → Backend (localhost:PORT)
```

---

See the documentation:
- [MULTILANGUAGE_INTEGRATION.md](MULTILANGUAGE_INTEGRATION.md) - Detailed explanation
- [SETUP_COMMON_LANGUAGES.md](SETUP_COMMON_LANGUAGES.md) - Copy-paste examples
- [QUICK_START_DEPLOYMENT.md](../QUICK_START_DEPLOYMENT.md) - Quick setup
- [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md) - Production setup
