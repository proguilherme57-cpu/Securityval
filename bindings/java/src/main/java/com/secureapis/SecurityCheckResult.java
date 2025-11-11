package com.secureapis;

/**
 * Result of a security check operation
 */
public class SecurityCheckResult {
    private final boolean allowed;
    private final int statusCode;
    private final String errorMessage;
    private final String headersJson;

    public SecurityCheckResult(boolean allowed, int statusCode, String errorMessage, String headersJson) {
        this.allowed = allowed;
        this.statusCode = statusCode;
        this.errorMessage = errorMessage;
        this.headersJson = headersJson;
    }

    public boolean isAllowed() {
        return allowed;
    }

    public int getStatusCode() {
        return statusCode;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public String getHeadersJson() {
        return headersJson;
    }
}