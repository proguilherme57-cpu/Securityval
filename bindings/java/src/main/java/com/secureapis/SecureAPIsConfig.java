package com.secureapis;

/**
 * Configuration for SecureAPIs security checks
 */
public class SecureAPIsConfig {
    private int rateLimitRequests = 100;
    private int rateLimitWindowSeconds = 60;
    private String jwtSecret;
    private boolean enableInputValidation = true;
    private boolean enableSecurityHeaders = true;
    private boolean enableCors = false;

    public SecureAPIsConfig() {}

    // Getters and setters
    public int getRateLimitRequests() {
        return rateLimitRequests;
    }

    public void setRateLimitRequests(int rateLimitRequests) {
        this.rateLimitRequests = rateLimitRequests;
    }

    public int getRateLimitWindowSeconds() {
        return rateLimitWindowSeconds;
    }

    public void setRateLimitWindowSeconds(int rateLimitWindowSeconds) {
        this.rateLimitWindowSeconds = rateLimitWindowSeconds;
    }

    public String getJwtSecret() {
        return jwtSecret;
    }

    public void setJwtSecret(String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }

    public boolean isEnableInputValidation() {
        return enableInputValidation;
    }

    public void setEnableInputValidation(boolean enableInputValidation) {
        this.enableInputValidation = enableInputValidation;
    }

    public boolean isEnableSecurityHeaders() {
        return enableSecurityHeaders;
    }

    public void setEnableSecurityHeaders(boolean enableSecurityHeaders) {
        this.enableSecurityHeaders = enableSecurityHeaders;
    }

    public boolean isEnableCors() {
        return enableCors;
    }

    public void setEnableCors(boolean enableCors) {
        this.enableCors = enableCors;
    }
}