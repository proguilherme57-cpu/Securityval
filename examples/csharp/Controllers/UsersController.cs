using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace SecureAPIsExample.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private static readonly List<User> _users = new()
    {
        new User { Id = 1, Name = "John Doe", Email = "john@example.com" },
        new User { Id = 2, Name = "Jane Smith", Email = "jane@example.com" }
    };

    [HttpGet]
    [Authorize] // Requires JWT token
    public ActionResult<IEnumerable<User>> GetUsers()
    {
        // SecureAPIs has already validated:
        // ✓ JWT token in Authorization header
        // ✓ Rate limiting (100 requests/minute)
        // ✓ Request size and format
        // ✓ Added security headers to response

        return Ok(_users);
    }

    [HttpGet("{id}")]
    [Authorize]
    public ActionResult<User> GetUser(int id)
    {
        var user = _users.FirstOrDefault(u => u.Id == id);
        if (user == null)
        {
            return NotFound();
        }

        return Ok(user);
    }

    [HttpPost]
    [Authorize]
    public ActionResult<User> CreateUser(CreateUserRequest request)
    {
        // SecureAPIs has already validated:
        // ✓ Input for SQL injection: request.Name, request.Email
        // ✓ Input for XSS attacks
        // ✓ Request size limits
        // ✓ Malicious patterns

        if (string.IsNullOrWhiteSpace(request.Name) || string.IsNullOrWhiteSpace(request.Email))
        {
            return BadRequest("Name and email are required");
        }

        var user = new User
        {
            Id = _users.Max(u => u.Id) + 1,
            Name = request.Name,
            Email = request.Email
        };

        _users.Add(user);

        return CreatedAtAction(nameof(GetUser), new { id = user.Id }, user);
    }

    [HttpPut("{id}")]
    [Authorize]
    public IActionResult UpdateUser(int id, UpdateUserRequest request)
    {
        var user = _users.FirstOrDefault(u => u.Id == id);
        if (user == null)
        {
            return NotFound();
        }

        // SecureAPIs validates input automatically
        user.Name = request.Name ?? user.Name;
        user.Email = request.Email ?? user.Email;

        return NoContent();
    }

    [HttpDelete("{id}")]
    [Authorize]
    public IActionResult DeleteUser(int id)
    {
        var user = _users.FirstOrDefault(u => u.Id == id);
        if (user == null)
        {
            return NotFound();
        }

        _users.Remove(user);
        return NoContent();
    }
}

public class CreateUserRequest
{
    public string Name { get; set; } = "";
    public string Email { get; set; } = "";
}

public class UpdateUserRequest
{
    public string? Name { get; set; }
    public string? Email { get; set; }
}