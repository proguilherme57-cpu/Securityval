const { SecureAPIs, SecureAPIsMiddleware } = require('./index.js');

console.log('Testing SecureAPIs Node.js bindings...\n');

// Test 1: Basic functionality
console.log('1. Testing basic functionality...');
try {
    const secureAPIs = new SecureAPIs({
        rateLimitRequests: 10,
        rateLimitWindowSeconds: 60,
        enableInputValidation: true
    });

    console.log('✓ SecureAPIs instance created');

    const version = secureAPIs.getVersion();
    console.log('✓ Version:', version);

} catch (error) {
    console.error('✗ Basic functionality test failed:', error.message);
}

// Test 2: Request checking
console.log('\n2. Testing request checking...');
try {
    const secureAPIs = new SecureAPIs({
        rateLimitRequests: 5,
        rateLimitWindowSeconds: 60
    });

    // Valid request
    const validRequest = {
        method: 'GET',
        url: '/api/users',
        ip: '192.168.1.1'
    };

    const result1 = secureAPIs.checkRequest(validRequest);
    console.log('✓ Valid request result:', result1);

    // Make multiple requests to test rate limiting
    console.log('Testing rate limiting...');
    let blockedCount = 0;
    for (let i = 0; i < 7; i++) {
        const result = secureAPIs.checkRequest(validRequest);
        if (!result.allowed) {
            blockedCount++;
        }
    }
    console.log(`✓ Rate limiting: ${blockedCount} requests blocked`);

} catch (error) {
    console.error('✗ Request checking test failed:', error.message);
}

// Test 3: Input validation
console.log('\n3. Testing input validation...');
try {
    const secureAPIs = new SecureAPIs({
        enableInputValidation: true
    });

    // SQL injection attempt
    const sqlRequest = {
        method: 'POST',
        url: '/api/users',
        body: "'; DROP TABLE users; --",
        ip: '192.168.1.1'
    };

    const sqlResult = secureAPIs.checkRequest(sqlRequest);
    console.log('✓ SQL injection detection:', !sqlResult.allowed ? 'BLOCKED' : 'ALLOWED');

    // XSS attempt
    const xssRequest = {
        method: 'POST',
        url: '/api/contact',
        body: '<script>alert("xss")</script>',
        ip: '192.168.1.1'
    };

    const xssResult = secureAPIs.checkRequest(xssRequest);
    console.log('✓ XSS detection:', !xssResult.allowed ? 'BLOCKED' : 'ALLOWED');

} catch (error) {
    console.error('✗ Input validation test failed:', error.message);
}

// Test 4: Middleware creation
console.log('\n4. Testing middleware creation...');
try {
    const middleware = SecureAPIsMiddleware({
        rateLimitRequests: 100,
        enableSecurityHeaders: true
    });

    console.log('✓ Middleware created successfully');
    console.log('✓ Middleware is a function:', typeof middleware === 'function');

} catch (error) {
    console.error('✗ Middleware creation test failed:', error.message);
}

console.log('\n=====================================');
console.log('SecureAPIs Node.js bindings test complete!');
console.log('=====================================\n');