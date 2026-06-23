# Security Policy

## Overview

Gilfi is a security and network analysis toolkit designed for educational purposes, authorized security testing, and network administration. This document outlines our security policies, responsible disclosure procedures, and security best practices.

## Supported Versions

We actively maintain and provide security updates for the following versions:

| Version | Supported          | Status |
| ------- | ------------------ | ------ |
| < 1.0   | :x:                | No longer supported |

## Reporting a Vulnerability

### How to Report

If you discover a security vulnerability in Gilfi, please report it responsibly:

1. **DO NOT** open a public GitHub issue
2. **DO NOT** disclose the vulnerability publicly until it has been addressed
3. Email security details to the project maintainers (see contact information in repository)
4. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
   - Your contact information

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Vulnerability Assessment**: Within 7 days
- **Fix Development**: Depends on severity (critical: 7 days, high: 14 days, medium: 30 days)
- **Public Disclosure**: After fix is released and users have had time to update (typically 30 days)

### Severity Classification

- **Critical**: Remote code execution, authentication bypass, data breach
- **High**: Privilege escalation, significant data exposure
- **Medium**: Denial of service, information disclosure
- **Low**: Minor information leakage, configuration issues

## Security Architecture

### Frontend Security

The PyQt6 frontend implements the following security measures:

- **Input Validation**: All user inputs are validated before processing
- **API Communication**: HTTPS-ready (localhost HTTP for development)
- **No Credential Storage**: No passwords or sensitive data stored locally
- **Thread Safety**: Proper thread management to prevent race conditions

### Backend Security

The Flask backend implements:

- **Request Validation**: All API requests validated before processing
- **CORS Configuration**: Restricted to localhost by default
- **Error Handling**: Sanitized error messages (no stack traces in production)
- **Resource Limits**: Timeouts and size limits on operations
- **Container Isolation**: Runs in Docker container with limited privileges

### Module-Specific Security

#### Hash Module
- **No Plaintext Storage**: Hashes are computed on-demand, not stored
- **Wordlist Security**: Read-only access to wordlist files
- **Memory Management**: Efficient processing to prevent memory exhaustion

#### Password Analyzer
- **Local Processing**: All analysis done locally, no external transmission
- **No Logging**: Passwords are never logged or stored
- **Secure Generation**: Uses `secrets` module for cryptographically secure random generation

#### Network Module
- **Rate Limiting**: Built-in delays to prevent network flooding
- **Target Validation**: IP address and port range validation
- **Permission Checks**: Requires appropriate network permissions

#### RSA Module
- **Key Generation**: Secure random prime generation
- **No Key Storage**: Keys generated per-session only
- **Input Validation**: Validates plaintext before encryption

#### Ask-Gilfi Module
- **Local LLM**: Runs Ollama locally, no data sent to external services
- **Prompt Sanitization**: User prompts sanitized before processing
- **Resource Limits**: Memory and CPU limits enforced

## Known Security Considerations

### By Design

The following are intentional design decisions with security implications:

1. **Local Network Access**: Port and network scanning require network access
2. **Wordlist Access**: Hash cracking requires access to wordlist files
3. **System Commands**: Some modules execute system-level operations
4. **Docker Privileges**: Backend container requires network access

### Limitations

1. **Authentication**: No built-in authentication (designed for single-user local use)
2. **Encryption**: API communication over localhost HTTP (not HTTPS)
3. **Audit Logging**: Limited logging of security-relevant events
4. **Rate Limiting**: Basic rate limiting only

## Secure Deployment

### Development Environment

```bash
# Use virtual environment
python3 -m venv gilfi-env
source gilfi-env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run backend in container (recommended)
./backend-docker.sh
```

### Production Environment

1. **Container Security**:
   ```bash
   # Run with limited privileges
   docker-compose -f docker-compose.backend.yaml up -d
   
   # Verify container security
   docker inspect gilfi_backend
   ```

2. **Network Security**:
   - Bind backend to localhost only (default: `0.0.0.0:8000`)
   - Use firewall rules to restrict access
   - Consider VPN for remote access

3. **File Permissions**:
   ```bash
   # Restrict wordlist access
   chmod 600 data/wordlist/*
   
   # Protect configuration files
   chmod 600 docker-compose.backend.yaml
   ```

4. **Update Regularly**:
   ```bash
   # Pull latest images
   docker-compose pull
   
   # Update Python dependencies
   pip install --upgrade -r requirements.txt
   ```

## Security Best Practices

### For Users

1. **Authorized Use Only**: Only use Gilfi on systems you own or have explicit permission to test
2. **Keep Updated**: Regularly update to the latest version
3. **Secure Environment**: Run on trusted systems with updated OS and security patches
4. **Network Isolation**: Consider running in isolated network environment for testing
5. **Data Protection**: Be cautious with wordlists and sensitive data

### For Developers

1. **Input Validation**: Always validate and sanitize user inputs
2. **Error Handling**: Never expose sensitive information in error messages
3. **Dependency Management**: Keep dependencies updated and audit for vulnerabilities
4. **Code Review**: All security-relevant changes require review
5. **Testing**: Include security test cases in test suites

### For System Administrators

1. **Access Control**: Limit who can run Gilfi on your systems
2. **Monitoring**: Monitor for unusual network activity
3. **Logging**: Enable and review system logs
4. **Backup**: Regular backups of configuration and data
5. **Incident Response**: Have a plan for security incidents

## Ethical Use Policy

### Permitted Uses

✅ **Educational purposes** - Learning about security concepts  
✅ **Authorized security testing** - With explicit written permission  
✅ **Personal password management** - Analyzing your own passwords  
✅ **Network administration** - Managing your own networks  
✅ **Security research** - In controlled environments  

### Prohibited Uses

❌ **Unauthorized access** - Accessing systems without permission  
❌ **Malicious activities** - Using for harmful purposes  
❌ **Privacy violations** - Intercepting or accessing private data  
❌ **Illegal activities** - Any use that violates applicable laws  
❌ **Credential theft** - Stealing or cracking others' passwords  

## Legal Disclaimer

**IMPORTANT**: Users are solely responsible for ensuring their use of Gilfi complies with all applicable laws and regulations. The developers:

- Assume **NO LIABILITY** for misuse of this software
- Do **NOT ENDORSE** unauthorized security testing
- Provide this tool **AS-IS** without warranties
- Are **NOT RESPONSIBLE** for any damages resulting from use

By using Gilfi, you agree to:
- Use it only for lawful purposes
- Obtain proper authorization before testing systems
- Comply with all applicable laws and regulations
- Accept full responsibility for your actions

## Security Checklist

Before deploying Gilfi, verify:

- [ ] Running latest stable version
- [ ] Backend container properly configured
- [ ] Network access appropriately restricted
- [ ] File permissions correctly set
- [ ] Dependencies up to date
- [ ] Firewall rules configured
- [ ] Monitoring and logging enabled
- [ ] Backup procedures in place
- [ ] Incident response plan documented
- [ ] Users trained on ethical use

## Vulnerability Disclosure History

### Version 1.0.0 (2026-04-28)
- Initial release
- No vulnerabilities reported

## Security Resources

### Internal Documentation
- [System Architecture](documentation/architecture/SYSTEM_ARCHITECTURE.md)
- [API Specification](documentation/api/API_SPECIFICATION.md)
- [Backend README](src/backend/README.md)
- [Frontend README](src/frontend/README.md)

### External Resources
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [Docker Security](https://docs.docker.com/engine/security/)

## Security Contacts

For security-related inquiries:
- Review the GitHub repository for contact information
- Check the project's main README for maintainer details
- Use GitHub's security advisory feature for vulnerability reports

## Acknowledgments

We appreciate responsible disclosure from security researchers and the community. Contributors who report valid security issues will be acknowledged (with permission) in our security advisories.

---

**Last Updated**: 2026-05-06  
**Version**: 1.0  
**Next Review**: 2026-08-06
