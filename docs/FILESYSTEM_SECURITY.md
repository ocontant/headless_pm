# Filesystem Security Documentation

This document outlines the comprehensive security measures implemented in the Headless PM filesystem operations to prevent various attack vectors including shell injection, path traversal, and other security vulnerabilities.

## Security Overview

All filesystem operations in Headless PM are designed with security-first principles:

- **Defense in Depth**: Multiple layers of security validation
- **Input Sanitization**: Aggressive sanitization of all user inputs
- **Path Validation**: Comprehensive path security checks
- **Attack Prevention**: Protection against known attack vectors

## Sanitization Functions

### Project Name Sanitization

The `sanitize_project_name()` function ensures project names are safe for filesystem usage:

**Security Measures:**
- **Character Whitelist**: Only alphanumeric characters, hyphens, and underscores allowed
- **Shell Character Removal**: All shell special characters eliminated
- **Length Limits**: Maximum 50 characters to prevent buffer overflows
- **Pattern Validation**: Must match strict regex pattern `^[a-z0-9][a-z0-9\-_]*[a-z0-9]$`
- **Case Normalization**: Converted to lowercase for consistency

**Blocked Characters:**
```
| & ; ( ) < > ! ? * [ ] { } / \ .. $ ` " ' space tab newline ^ % = + : @ #
```

**Examples:**
- `"My Project!"` → `"myproject"`
- `"Test&&rm -rf /"` → `"testrm-rf"`
- `"../../../etc"` → `"etc"`

### Filename Sanitization

The `sanitize_filename()` function secures filenames while preserving functionality:

**Features:**
- **Extension Preservation**: Maintains file extensions (.txt, .md, etc.)
- **Same Character Rules**: Uses project name sanitization for the filename part
- **Length Management**: Balances filename and extension lengths
- **Directory Support**: Handles nested paths securely

**Examples:**
- `"document file.txt"` → `"documentfile.txt"`
- `"malicious&&rm.sh"` → `"maliciousrm.sh"`
- `"test$(whoami).log"` → `"testwhoami.log"`

## Path Security Validation

### validate_path_security()

Comprehensive path validation prevents various attack vectors:

**Security Checks:**
1. **Path Traversal Prevention**: Blocks `..`, absolute paths, and backslashes
2. **Null Byte Injection**: Prevents null bytes and control characters
3. **Base Directory Enforcement**: Ensures paths stay within allowed directories
4. **Real Path Validation**: Uses `os.path.realpath()` for final verification

**Attack Vectors Prevented:**
- Path traversal: `../../../etc/passwd`
- Null byte injection: `file.txt\x00.php`
- Absolute paths: `/etc/passwd`
- Windows paths: `C:\Windows\System32`
- Symbolic link attacks

## API Security Integration

### Enhanced API Endpoints

All project documentation API endpoints use layered security:

**File Creation (`POST /api/v1/projects/{id}/docs/{file_path}`):**
1. **Path Component Sanitization**: Each directory and filename sanitized separately
2. **Path Reconstruction**: Build safe path from sanitized components
3. **Security Validation**: Final path validation before filesystem operations
4. **Content Validation**: Check for null bytes and control characters
5. **Safe Directory Creation**: Secure directory creation with error handling

**File Retrieval (`GET /api/v1/projects/{id}/docs/{file_path}`):**
1. **Path Validation**: Comprehensive security checks
2. **Existence Verification**: Safe file existence checks
3. **Content Type Detection**: Safe content type handling
4. **Error Handling**: Secure error responses without information leakage

## Security Testing

Comprehensive test suite validates all security measures:

### Test Categories

1. **Project Name Tests**
   - Basic sanitization validation
   - Shell character removal verification
   - Path traversal prevention
   - Length limit enforcement
   - Pattern matching validation

2. **Filename Tests**
   - Extension preservation
   - Malicious filename sanitization
   - Special character handling

3. **Path Security Tests**
   - Valid path acceptance
   - Path traversal prevention
   - Null byte injection prevention
   - Absolute path rejection

4. **Integration Tests**
   - End-to-end security validation
   - Unicode and encoding safety
   - Real-world attack simulation

### Running Security Tests

```bash
# Run all security tests
python -m pytest tests/test_filesystem_security.py -v

# Run specific test category
python -m pytest tests/test_filesystem_security.py::TestProjectNameSanitization -v
```

## File Naming Standards

### Enforced Standards

All filesystem objects follow strict naming conventions:

**Project Directories:**
- Format: `projects/{sanitized-project-name}/`
- Example: `projects/headless-pm/docs/`

**Filenames:**
- Pattern: `^[a-z0-9][a-z0-9\-_]*(\.[a-z0-9]+)?$`
- No spaces allowed
- Only alphanumeric, hyphens, underscores, and extensions
- Extensions sanitized to alphanumeric only

**Directory Structure:**
```
projects/
├── headless-pm/           # Sanitized project name
│   ├── docs/             # Safe directory names only
│   │   ├── readme.md     # Sanitized filenames
│   │   └── api-guide.txt # Hyphens allowed
│   ├── shared/
│   └── instructions/
```

## Attack Prevention Examples

### Shell Injection Prevention

**Attack Attempt:**
```bash
POST /api/v1/projects/1/docs/$(rm -rf /).txt
```

**System Response:**
- Filename sanitized to: `rmrf.txt`
- Shell characters completely removed
- Safe file created without command execution

### Path Traversal Prevention

**Attack Attempt:**
```bash
GET /api/v1/projects/1/docs/../../../etc/passwd
```

**System Response:**
- HTTP 400 error: "Invalid file path: Path contains invalid traversal characters"
- No file access outside project directory
- Attack logged for security monitoring

### Null Byte Injection Prevention

**Attack Attempt:**
```bash
POST /api/v1/projects/1/docs/safe.txt\x00.php
```

**System Response:**
- HTTP 400 error: "Invalid file path: Path contains invalid control characters"
- Null byte detected and rejected
- No file created with dual extension

## Security Monitoring

### Logging

All security-related events are logged:

- Invalid path attempts
- Suspicious filename patterns
- Path traversal attempts
- Failed validation attempts

### Error Responses

Security errors return appropriate HTTP status codes:

- `400 Bad Request`: Invalid input format
- `422 Unprocessable Entity`: Validation failures
- `500 Internal Server Error`: Server-side security issues

**No Information Leakage**: Error messages provide minimal information to prevent reconnaissance.

## Best Practices

### For Developers

1. **Always Sanitize**: Never trust user input for filesystem operations
2. **Validate Paths**: Use `validate_path_security()` for all path operations
3. **Test Security**: Run security tests regularly
4. **Review Changes**: Security-review any filesystem-related code changes

### For API Users

1. **Use Safe Names**: Stick to alphanumeric characters and hyphens
2. **Avoid Special Characters**: Don't use shell special characters
3. **Check Responses**: Handle sanitization messages appropriately
4. **Report Issues**: Report any unexpected behavior

## Implementation Details

### Code Location

Security functions are implemented in:
- `src/services/project_utils.py` - Core sanitization functions
- `src/api/project_routes.py` - API endpoint security integration
- `tests/test_filesystem_security.py` - Comprehensive security tests

### Dependencies

Security implementation uses only Python standard library:
- `re` - Regular expression validation
- `os` - Path operations and validation
- `pathlib` - Path object handling

No external security libraries required, reducing attack surface.

## Compliance

This implementation follows security best practices:

- **OWASP Guidelines**: Addresses common web application vulnerabilities
- **CWE Prevention**: Mitigates Common Weakness Enumeration issues
- **Defense in Depth**: Multiple validation layers
- **Fail-Safe Design**: Secure by default with explicit allow lists

## Maintenance

### Regular Security Reviews

1. **Quarterly Reviews**: Review security functions and tests
2. **Vulnerability Scanning**: Regular security testing
3. **Update Validation**: Test security after any filesystem changes
4. **Documentation Updates**: Keep security docs current

### Security Updates

When updating security measures:

1. **Add Tests First**: Write tests for new attack vectors
2. **Implement Gradually**: Phased security enhancements
3. **Validate Thoroughly**: Comprehensive testing before deployment
4. **Document Changes**: Update security documentation

This security framework provides robust protection against filesystem-based attacks while maintaining usability and performance.