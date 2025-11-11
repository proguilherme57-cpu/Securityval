package com.secureapis;

/**
 * Exception thrown by SecureAPIs operations
 */
public class SecureAPIsException extends Exception {
    public SecureAPIsException(String message) {
        super(message);
    }

    public SecureAPIsException(String message, Throwable cause) {
        super(message, cause);
    }
}