using Microsoft.AspNetCore.Mvc;

namespace SecureAPIsExample.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PublicController : ControllerBase
{
    private static int _requestCount = 0;

    [HttpGet]
    public ActionResult<string> Get()
    {
        // Even public endpoints get security benefits:
        // ✓ Rate limiting (100 requests/minute)
        // ✓ Input validation on query parameters
        // ✓ Security headers added to response
        // ✓ Threat detection

        Interlocked.Increment(ref _requestCount);

        return Ok(new
        {
            message = "Hello from SecureAPIs!",
            timestamp = DateTime.UtcNow,
            requestNumber = _requestCount,
            securedBy = "SecureAPIs Rust Engine"
        });
    }

    [HttpPost("contact")]
    public ActionResult<string> Contact([FromBody] ContactRequest request)
    {
        // SecureAPIs validates the input automatically:
        // ✓ SQL injection in name/message
        // ✓ XSS in HTML content
        // ✓ Command injection attempts
        // ✓ Malicious patterns

        if (string.IsNullOrWhiteSpace(request.Name) ||
            string.IsNullOrWhiteSpace(request.Email) ||
            string.IsNullOrWhiteSpace(request.Message))
        {
            return BadRequest("All fields are required");
        }

        // In a real app, you'd save this to a database
        // SecureAPIs has already validated the input is safe

        return Ok(new
        {
            status = "Message received",
            name = request.Name,
            email = request.Email,
            messageLength = request.Message.Length,
            validated = true
        });
    }

    [HttpGet("health")]
    public ActionResult<string> Health()
    {
        // Health check endpoint - still gets security headers
        return Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow,
            version = "1.0.0"
        });
    }
}

public class ContactRequest
{
    public string Name { get; set; } = "";
    public string Email { get; set; } = "";
    public string Message { get; set; } = "";
}