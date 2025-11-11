# Test script for SecureAPIs C# Example
# This script demonstrates various security features

Write-Host "Testing SecureAPIs C# Example Application" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$baseUrl = "http://localhost:5000"

# Test 1: Public endpoint (should work)
Write-Host "`n1. Testing public endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/public" -Method Get
    Write-Host "✓ Public endpoint works: $($response.message)" -ForegroundColor Green
} catch {
    Write-Host "✗ Public endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Rate limiting (make many requests quickly)
Write-Host "`n2. Testing rate limiting..." -ForegroundColor Yellow
$successCount = 0
$rateLimitCount = 0
for ($i = 1; $i -le 105; $i++) {
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/api/public" -Method Get -TimeoutSec 5
        $successCount++
    } catch {
        if ($_.Exception.Response.StatusCode -eq 429) {
            $rateLimitCount++
        }
    }
}
Write-Host "✓ Successful requests: $successCount" -ForegroundColor Green
Write-Host "✓ Rate limited requests: $rateLimitCount" -ForegroundColor Green

# Test 3: Input validation (try SQL injection)
Write-Host "`n3. Testing input validation..." -ForegroundColor Yellow
$sqlInjection = @{
    name = "'; DROP TABLE users; --"
    email = "test@example.com"
    message = "Hello world"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/public/contact" -Method Post -Body $sqlInjection -ContentType "application/json"
    Write-Host "✗ SQL injection not blocked!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ SQL injection blocked (400 Bad Request)" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected response: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 4: XSS attempt
Write-Host "`n4. Testing XSS protection..." -ForegroundColor Yellow
$xssAttempt = @{
    name = "<script>alert('xss')</script>"
    email = "test@example.com"
    message = "Hello world"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/public/contact" -Method Post -Body $xssAttempt -ContentType "application/json"
    Write-Host "✗ XSS not blocked!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host "✓ XSS blocked (400 Bad Request)" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected response: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 5: Valid input (should work)
Write-Host "`n5. Testing valid input..." -ForegroundColor Yellow
$validInput = @{
    name = "John Doe"
    email = "john@example.com"
    message = "This is a valid message"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/public/contact" -Method Post -Body $validInput -ContentType "application/json"
    Write-Host "✓ Valid input accepted: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Valid input rejected: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: JWT authentication (without token)
Write-Host "`n6. Testing JWT authentication (no token)..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/users" -Method Get
    Write-Host "✗ Unauthenticated request allowed!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✓ Unauthenticated request blocked (401 Unauthorized)" -ForegroundColor Green
    } else {
        Write-Host "✗ Unexpected response: $($_.Exception.Response.StatusCode)" -ForegroundColor Red
    }
}

# Test 7: JWT authentication (with valid token)
Write-Host "`n7. Testing JWT authentication (with token)..." -ForegroundColor Yellow
# This is a JWT token signed with "your-super-secret-jwt-key"
$jwtToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

$headers = @{
    "Authorization" = "Bearer $jwtToken"
}

try {
    $response = Invoke-RestMethod -Uri "$baseUrl/api/users" -Method Get -Headers $headers
    Write-Host "✓ Authenticated request successful: $($response.Count) users returned" -ForegroundColor Green
} catch {
    Write-Host "✗ Authenticated request failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 8: Security headers
Write-Host "`n8. Testing security headers..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/api/public" -Method Get
    $headers = $response.Headers

    $securityHeaders = @(
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security"
    )

    $foundHeaders = 0
    foreach ($header in $securityHeaders) {
        if ($headers.ContainsKey($header)) {
            $foundHeaders++
            Write-Host "✓ Found security header: $header" -ForegroundColor Green
        }
    }

    Write-Host "✓ Total security headers found: $foundHeaders/$($securityHeaders.Count)" -ForegroundColor Green

} catch {
    Write-Host "✗ Security headers test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "SecureAPIs C# Example Test Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green