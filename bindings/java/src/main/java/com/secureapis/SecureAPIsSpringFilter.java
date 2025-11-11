package com.secureapis;

import org.springframework.web.filter.OncePerRequestFilter;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

/**
 * Spring Boot filter for SecureAPIs integration
 */
public class SecureAPIsSpringFilter extends OncePerRequestFilter {
    private final SecureAPIs secureAPIs;

    public SecureAPIsSpringFilter(SecureAPIsConfig config) throws SecureAPIsException {
        this.secureAPIs = new SecureAPIs(config);
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {

        try {
            SecurityCheckResult result = secureAPIs.checkRequest(request);

            if (!result.isAllowed()) {
                // Block the request
                response.setStatus(result.getStatusCode());
                response.setContentType("application/json");
                response.setCharacterEncoding("UTF-8");

                String errorMessage = result.getErrorMessage() != null ?
                    result.getErrorMessage() : "Request blocked by security policy";

                String jsonResponse = String.format(
                    "{\"error\":\"%s\",\"statusCode\":%d}",
                    errorMessage.replace("\"", "\\\""),
                    result.getStatusCode()
                );

                response.getWriter().write(jsonResponse);
                return;
            }

            // Add security headers if enabled
            if (result.getHeadersJson() != null && !result.getHeadersJson().isEmpty()) {
                try {
                    // Parse headers JSON and add to response
                    String headersJson = result.getHeadersJson();
                    if (headersJson.contains("X-Content-Type-Options")) {
                        response.setHeader("X-Content-Type-Options", "nosniff");
                    }
                    if (headersJson.contains("X-Frame-Options")) {
                        response.setHeader("X-Frame-Options", "DENY");
                    }
                    if (headersJson.contains("X-XSS-Protection")) {
                        response.setHeader("X-XSS-Protection", "1; mode=block");
                    }
                } catch (Exception e) {
                    // Ignore header parsing errors
                }
            }

            // Continue with the request
            filterChain.doFilter(request, response);

        } catch (SecureAPIsException e) {
            // Internal error
            response.setStatus(500);
            response.setContentType("application/json");
            response.getWriter().write("{\"error\":\"Internal security error\"}");
        }
    }
}