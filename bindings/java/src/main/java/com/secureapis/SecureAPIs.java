package com.secureapis;

import com.sun.jna.*;
import com.sun.jna.ptr.PointerByReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.Map;
import java.util.HashMap;

/**
 * Main SecureAPIs class providing security functionality
 */
public class SecureAPIs implements AutoCloseable {
    private static final ObjectMapper objectMapper = new ObjectMapper();

    // Native library interface
    private interface SecureAPIsNative extends Library {
        SecureAPIsNative INSTANCE = Native.load("secureapis", SecureAPIsNative.class);

        Pointer secureapis_create_config(String configJson);
        void secureapis_free_config(Pointer config);
        int secureapis_check_request(Pointer config, String method, String url,
                                   String headersJson, String body, String ip,
                                   PointerByReference output, int outputSize);
        void secureapis_free_string(Pointer str);
    }

    private final Pointer config;
    private boolean closed = false;

    /**
     * Create a new SecureAPIs instance with configuration
     */
    public SecureAPIs(SecureAPIsConfig config) throws SecureAPIsException {
        try {
            String configJson = objectMapper.writeValueAsString(config);
            this.config = SecureAPIsNative.INSTANCE.secureapis_create_config(configJson);
            if (this.config == null) {
                throw new SecureAPIsException("Failed to create SecureAPIs configuration");
            }
        } catch (Exception e) {
            throw new SecureAPIsException("Failed to initialize SecureAPIs", e);
        }
    }

    /**
     * Check if a request is allowed by security rules
     */
    public SecurityCheckResult checkRequest(String method, String url, Map<String, String> headers,
                                          String body, String ip) throws SecureAPIsException {
        if (closed) {
            throw new SecureAPIsException("SecureAPIs instance is closed");
        }

        try {
            String headersJson = objectMapper.writeValueAsString(headers != null ? headers : new HashMap<>());
            PointerByReference output = new PointerByReference();
            int outputSize = 4096;

            int result = SecureAPIsNative.INSTANCE.secureapis_check_request(
                config, method, url, headersJson, body != null ? body : "", ip, output, outputSize);

            if (result < 0) {
                throw new SecureAPIsException("Security check failed");
            }

            Pointer outputPtr = output.getValue();
            String outputStr = outputPtr != null ? outputPtr.getString(0) : "";

            // Parse result (simplified - in real implementation, parse JSON)
            boolean allowed = result == 0;
            int statusCode = allowed ? 200 : 400;
            String errorMessage = allowed ? null : "Request blocked by security policy";

            return new SecurityCheckResult(allowed, statusCode, errorMessage, null);

        } catch (Exception e) {
            throw new SecureAPIsException("Security check failed", e);
        }
    }

    /**
     * Check an HttpServletRequest
     */
    public SecurityCheckResult checkRequest(javax.servlet.http.HttpServletRequest request)
            throws SecureAPIsException {
        String method = request.getMethod();
        String url = request.getRequestURI() +
                    (request.getQueryString() != null ? "?" + request.getQueryString() : "");
        String ip = getClientIp(request);

        // Extract headers
        Map<String, String> headers = new HashMap<>();
        java.util.Enumeration<String> headerNames = request.getHeaderNames();
        while (headerNames.hasMoreElements()) {
            String headerName = headerNames.nextElement();
            headers.put(headerName, request.getHeader(headerName));
        }

        // Read body if present
        String body = "";
        try {
            if (request.getContentLength() > 0) {
                java.io.BufferedReader reader = request.getReader();
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    sb.append(line);
                }
                body = sb.toString();
            }
        } catch (Exception e) {
            // Ignore body read errors
        }

        return checkRequest(method, url, headers, body, ip);
    }

    private String getClientIp(javax.servlet.http.HttpServletRequest request) {
        String ip = request.getHeader("X-Forwarded-For");
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getHeader("X-Real-IP");
        }
        if (ip == null || ip.isEmpty() || "unknown".equalsIgnoreCase(ip)) {
            ip = request.getRemoteAddr();
        }
        return ip != null ? ip : "127.0.0.1";
    }

    @Override
    public void close() {
        if (!closed && config != null) {
            SecureAPIsNative.INSTANCE.secureapis_free_config(config);
            closed = true;
        }
    }
}