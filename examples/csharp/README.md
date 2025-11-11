# SecureAPIs C# Example Application

This is a complete ASP.NET Core application demonstrating how to integrate SecureAPIs as middleware.

## Features Demonstrated

- ✅ Rate limiting (100 requests/minute)
- ✅ JWT authentication
- ✅ Input validation (SQL injection, XSS protection)
- ✅ Security headers
- ✅ Threat detection
- ✅ CORS support
- ✅ Request/response logging

## Running the Example

1. **Build the bindings:**
```bash
.\build_csharp_bindings.bat
```

2. **Run the example:**
```bash
cd examples/csharp
dotnet run
```

3. **Test the API:**
```bash
# Get users (requires JWT)
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c" \
     http://localhost:5000/api/users

# Create user (will validate input)
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"John Doe","email":"john@example.com"}' \
     http://localhost:5000/api/users

# Test rate limiting (make 101 requests quickly)
for i in {1..101}; do curl -s http://localhost:5000/api/public; done
```

## Code Structure

```
examples/csharp/
├── SecureAPIsExample.csproj    # Project file
├── Program.cs                   # Application entry point
├── Controllers/
│   ├── UsersController.cs       # Protected API endpoints
│   └── PublicController.cs      # Public endpoints
├── Models/
│   └── User.cs                  # Data models
└── appsettings.json            # Configuration
```