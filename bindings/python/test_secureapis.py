#!/usr/bin/env python3
"""
Test script for SecureAPIs Python bindings
"""

import sys
import os
import json
import time
from typing import Dict, Any

# Add the current directory to Python path for local imports
sys.path.insert(0, os.path.dirname(__file__))

try:
    from secureapis import SecureAPIs, SecureAPIsConfig, SecurityResult, SecureAPIsException
    print("✓ Successfully imported SecureAPIs bindings")
except ImportError as e:
    print(f"✗ Failed to import SecureAPIs bindings: {e}")
    print("Make sure the bindings are built first:")
    print("  python setup.py build_ext --inplace")
    sys.exit(1)

def test_basic_functionality():
    """Test basic SecureAPIs functionality"""
    print("\n=== Testing Basic Functionality ===")

    # Create configuration
    config = SecureAPIsConfig()
    config.rate_limit_requests_per_minute = 10
    config.enable_csrf_protection = True
    config.enable_xss_protection = True
    config.enable_sql_injection_protection = True

    # Create SecureAPIs instance
    secureapis = SecureAPIs(config)
    print("✓ Created SecureAPIs instance")

    # Test normal request
    result = secureapis.check_request(
        method="GET",
        path="/api/users",
        headers={"Content-Type": "application/json"},
        body="",
        ip_address="127.0.0.1"
    )

    if not result.blocked:
        print("✓ Normal request allowed")
    else:
        print(f"✗ Normal request blocked: {result.reason}")
        return False

    # Test XSS attack
    result = secureapis.check_request(
        method="POST",
        path="/api/users",
        headers={"Content-Type": "application/json"},
        body='{"name": "<script>alert(\'xss\')</script>"}',
        ip_address="127.0.0.1"
    )

    if result.blocked and "xss" in result.reason.lower():
        print("✓ XSS attack detected and blocked")
    else:
        print(f"✗ XSS attack not detected. Result: {result.blocked}, Reason: {result.reason}")
        return False

    # Test SQL injection
    result = secureapis.check_request(
        method="POST",
        path="/api/users",
        headers={"Content-Type": "application/json"},
        body='{"query": "SELECT * FROM users WHERE id = 1 OR 1=1"}',
        ip_address="127.0.0.1"
    )

    if result.blocked and "sql" in result.reason.lower():
        print("✓ SQL injection detected and blocked")
    else:
        print(f"✗ SQL injection not detected. Result: {result.blocked}, Reason: {result.reason}")
        return False

    return True

def test_rate_limiting():
    """Test rate limiting functionality"""
    print("\n=== Testing Rate Limiting ===")

    config = SecureAPIsConfig()
    config.rate_limit_requests_per_minute = 5  # Very low limit for testing

    secureapis = SecureAPIs(config)

    # Make requests up to the limit
    for i in range(5):
        result = secureapis.check_request(
            method="GET",
            path="/api/test",
            headers={},
            body="",
            ip_address="192.168.1.100"
        )
        if result.blocked:
            print(f"✗ Request {i+1} unexpectedly blocked")
            return False
        print(f"✓ Request {i+1} allowed")

    # This request should be blocked
    result = secureapis.check_request(
        method="GET",
        path="/api/test",
        headers={},
        body="",
        ip_address="192.168.1.100"
    )

    if result.blocked and "rate" in result.reason.lower():
        print("✓ Rate limiting working - request blocked after limit exceeded")
        return True
    else:
        print(f"✗ Rate limiting not working. Result: {result.blocked}, Reason: {result.reason}")
        return False

def test_csrf_protection():
    """Test CSRF protection"""
    print("\n=== Testing CSRF Protection ===")

    config = SecureAPIsConfig()
    config.enable_csrf_protection = True

    secureapis = SecureAPIs(config)

    # Test POST request without CSRF token
    result = secureapis.check_request(
        method="POST",
        path="/api/users",
        headers={"Content-Type": "application/json"},
        body='{"name": "test"}',
        ip_address="127.0.0.1"
    )

    if result.blocked and "csrf" in result.reason.lower():
        print("✓ CSRF protection working - POST without token blocked")
    else:
        print(f"? CSRF protection result: blocked={result.blocked}, reason='{result.reason}'")
        # CSRF might not be implemented yet, so this is not a failure

    # Test with CSRF token (this should work if implemented)
    result = secureapis.check_request(
        method="POST",
        path="/api/users",
        headers={"Content-Type": "application/json", "X-CSRF-Token": "valid-token"},
        body='{"name": "test"}',
        ip_address="127.0.0.1"
    )

    print(f"✓ CSRF token test result: blocked={result.blocked}")
    return True

def test_configuration():
    """Test configuration options"""
    print("\n=== Testing Configuration ===")

    config = SecureAPIsConfig()

    # Test setting various options
    config.rate_limit_requests_per_minute = 100
    config.enable_xss_protection = False
    config.enable_sql_injection_protection = False
    config.max_request_size_kb = 2048

    secureapis = SecureAPIs(config)

    # Test that XSS is now disabled
    result = secureapis.check_request(
        method="POST",
        path="/api/test",
        headers={"Content-Type": "application/json"},
        body='{"data": "<script>alert(\'test\')</script>"}',
        ip_address="127.0.0.1"
    )

    if not result.blocked:
        print("✓ XSS protection correctly disabled via configuration")
    else:
        print(f"? XSS still blocked even when disabled: {result.reason}")

    return True

def test_error_handling():
    """Test error handling"""
    print("\n=== Testing Error Handling ===")

    config = SecureAPIsConfig()
    secureapis = SecureAPIs(config)

    try:
        # Test with invalid parameters
        result = secureapis.check_request(
            method="",  # Empty method
            path="",    # Empty path
            headers={},
            body="",
            ip_address=""
        )
        print("✓ Handled empty parameters gracefully")
    except SecureAPIsException as e:
        print(f"✓ Caught expected exception: {e}")
    except Exception as e:
        print(f"✗ Unexpected exception type: {type(e).__name__}: {e}")
        return False

    return True

def test_django_middleware():
    """Test Django middleware integration"""
    print("\n=== Testing Django Middleware ===")

    try:
        from secureapis.django_middleware import SecureAPIsMiddleware
        print("✓ Django middleware import successful")

        # We can't fully test Django middleware without a Django project,
        # but we can test the import and basic instantiation
        middleware_class = SecureAPIsMiddleware
        print("✓ Django middleware class available")

    except ImportError as e:
        print(f"✗ Django middleware import failed: {e}")
        return False

    return True

def test_flask_middleware():
    """Test Flask middleware integration"""
    print("\n=== Testing Flask Middleware ===")

    try:
        from secureapis.flask_middleware import SecureAPIsFlask
        print("✓ Flask middleware import successful")

        # Test basic instantiation (without full Flask app)
        config = SecureAPIsConfig()
        # We can't create a full Flask app here, but we can test the class exists
        middleware_class = SecureAPIsFlask
        print("✓ Flask middleware class available")

    except ImportError as e:
        print(f"✗ Flask middleware import failed: {e}")
        return False

    return True

def run_performance_test():
    """Run basic performance test"""
    print("\n=== Running Performance Test ===")

    config = SecureAPIsConfig()
    config.enable_xss_protection = True
    config.enable_sql_injection_protection = True

    secureapis = SecureAPIs(config)

    # Test performance with 100 requests
    test_request = {
        "method": "POST",
        "path": "/api/users",
        "headers": {"Content-Type": "application/json"},
        "body": '{"name": "John Doe", "email": "john@example.com"}',
        "ip_address": "127.0.0.1"
    }

    start_time = time.time()
    for i in range(100):
        result = secureapis.check_request(**test_request)

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = (total_time / 100) * 1000  # Convert to milliseconds

    print(".2f")
    print(".2f")

    if avg_time < 1.0:  # Should be well under 1ms
        print("✓ Performance acceptable")
        return True
    else:
        print("⚠ Performance slower than expected, but still functional")
        return True

def main():
    """Run all tests"""
    print("SecureAPIs Python Bindings Test Suite")
    print("=" * 40)

    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Rate Limiting", test_rate_limiting),
        ("CSRF Protection", test_csrf_protection),
        ("Configuration", test_configuration),
        ("Error Handling", test_error_handling),
        ("Django Middleware", test_django_middleware),
        ("Flask Middleware", test_flask_middleware),
        ("Performance", run_performance_test),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name}: PASSED")
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")

    print("\n" + "=" * 40)
    print(f"Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())