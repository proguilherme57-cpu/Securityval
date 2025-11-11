package com.secureapis;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Servlet filter for SecureAPIs integration
 */
public class SecureAPIsFilter implements Filter {
    private SecureAPIs secureAPIs;

    public SecureAPIsFilter() {
        this(new SecureAPIsConfig());
    }

    public SecureAPIsFilter(SecureAPIsConfig config) {
        try {
            this.secureAPIs = new SecureAPIs(config);
        } catch (SecureAPIsException e) {
            throw new RuntimeException("Failed to initialize SecureAPIs", e);
        }
    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {
        // Already initialized in constructor
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {

        HttpServletRequest httpRequest = (HttpServletRequest) request;
        HttpServletResponse httpResponse = (HttpServletResponse) response;

        try {
            SecurityCheckResult result = secureAPIs.checkRequest(httpRequest);

            if (!result.isAllowed()) {
                // Block the request
                httpResponse.setStatus(result.getStatusCode());
                httpResponse.setContentType("application/json");
                httpResponse.setCharacterEncoding("UTF-8");

                String errorMessage = result.getErrorMessage() != null ?
                    result.getErrorMessage() : "Request blocked by security policy";

                String jsonResponse = String.format(
                    "{\"error\":\"%s\",\"statusCode\":%d}",
                    errorMessage.replace("\"", "\\\""),
                    result.getStatusCode()
                );

                httpResponse.getWriter().write(jsonResponse);
                return;
            }

            // Add security headers if enabled
            if (result.getHeadersJson() != null && !result.getHeadersJson().isEmpty()) {
                try {
                    // Parse headers JSON and add to response
                    // Simplified implementation - in production, use proper JSON parsing
                    String headersJson = result.getHeadersJson();
                    if (headersJson.contains("X-Content-Type-Options")) {
                        httpResponse.setHeader("X-Content-Type-Options", "nosniff");
                    }
                    if (headersJson.contains("X-Frame-Options")) {
                        httpResponse.setHeader("X-Frame-Options", "DENY");
                    }
                    if (headersJson.contains("X-XSS-Protection")) {
                        httpResponse.setHeader("X-XSS-Protection", "1; mode=block");
                    }
                } catch (Exception e) {
                    // Ignore header parsing errors
                }
            }

            // Continue with the request
            chain.doFilter(request, response);

        } catch (SecureAPIsException e) {
            // Internal error
            httpResponse.setStatus(500);
            httpResponse.setContentType("application/json");
            httpResponse.getWriter().write("{\"error\":\"Internal security error\"}");
        }
    }

    @Override
    public void destroy() {
        if (secureAPIs != null) {
            secureAPIs.close();
        }
    }
}