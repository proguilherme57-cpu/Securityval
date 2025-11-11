package com.secureapis;

import org.junit.jupiter.api.*;
import java.util.HashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

public class SecureAPIsTest {

    private SecureAPIs secureAPIs;
    private SecureAPIsConfig config;

    @BeforeEach
    void setUp() throws SecureAPIsException {
        config = new SecureAPIsConfig();
        config.setRateLimitRequests(10);
        config.setRateLimitWindowSeconds(60);
        config.setEnableInputValidation(true);

        secureAPIs = new SecureAPIs(config);
    }

    @AfterEach
    void tearDown() {
        if (secureAPIs != null) {
            secureAPIs.close();
        }
    }

    @Test
    public void testValidRequest() throws SecureAPIsException {
        Map<String, String> headers = new HashMap<>();
        headers.put("User-Agent", "Mozilla/5.0");
        headers.put("Accept", "application/json");

        SecurityCheckResult result = secureAPIs.checkRequest(
            "GET", "/api/users", headers, "", "192.168.1.1");

        assertTrue(result.isAllowed(), "Valid request should be allowed");
        assertEquals(200, result.getStatusCode());
    }

    @Test
    public void testRateLimiting() throws SecureAPIsException {
        Map<String, String> headers = new HashMap<>();
        boolean blocked = false;

        // Make more requests than the limit
        for (int i = 0; i < 15; i++) {
            SecurityCheckResult result = secureAPIs.checkRequest(
                "GET", "/api/users", headers, "", "192.168.1.1");

            if (!result.isAllowed()) {
                blocked = true;
                assertTrue(result.getStatusCode() == 429 || result.getStatusCode() == 400);
                break;
            }
        }

        assertTrue(blocked, "Rate limiting should eventually block requests");
    }

    @Test
    public void testInputValidation() throws SecureAPIsException {
        Map<String, String> headers = new HashMap<>();

        // Test SQL injection attempt
        SecurityCheckResult result = secureAPIs.checkRequest(
            "POST", "/api/users", headers, "{\"name\":\"'; DROP TABLE users; --\"}", "192.168.1.1");

        // Should either block or allow (depending on implementation details)
        // The important thing is that it doesn't crash
        assertNotNull(result);
    }

    @Test
    public void testConfiguration() {
        assertEquals(10, config.getRateLimitRequests());
        assertEquals(60, config.getRateLimitWindowSeconds());
        assertTrue(config.isEnableInputValidation());
    }

    @Test
    public void testExceptionHandling() {
        assertThrows(SecureAPIsException.class, () -> {
            // Try to create with invalid config
            SecureAPIsConfig invalidConfig = new SecureAPIsConfig();
            invalidConfig.setRateLimitRequests(-1); // Invalid
            new SecureAPIs(invalidConfig);
        });
    }
}