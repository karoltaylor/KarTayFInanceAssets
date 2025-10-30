# Security Policy

## Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public issue
2. Email the security team (if applicable) or create a private security advisory
3. Include the following information:
   - Type of vulnerability
   - Full paths of source file(s) related to the vulnerability
   - Location of the affected source code (tag/branch/commit or direct URL)
   - Step-by-step instructions to reproduce the issue
   - Proof-of-concept or exploit code (if possible)
   - Impact of the issue, including how an attacker might exploit it

## Security Best Practices

When deploying this application:

### 1. Environment Variables
- Never commit `.env` files to version control
- Use a secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)
- Rotate API keys regularly

### 2. Network Security
- Always use HTTPS in production
- Configure proper CORS settings (never use `allow_origins=["*"]` in production)
- Implement rate limiting to prevent abuse
- Use a Web Application Firewall (WAF)

### 3. Database Security
- Use strong authentication for MongoDB
- Enable MongoDB access control
- Use encrypted connections (TLS/SSL)
- Implement proper backup and recovery procedures
- Regularly update MongoDB to latest stable version

### 4. Application Security
- Keep all dependencies up to date
- Run security scans regularly (bandit, safety)
- Monitor application logs for suspicious activity
- Implement proper input validation
- Use parameterized queries to prevent injection attacks

### 5. API Security
- Implement authentication (OAuth2, JWT, API keys)
- Use HTTPS only
- Validate all input data
- Implement rate limiting
- Log all API access

### 6. Dependency Management
- Regularly update dependencies
- Use `safety check` to scan for known vulnerabilities
- Review security advisories for used packages
- Pin dependency versions in production

### 7. Infrastructure Security
- Use container security scanning (Trivy, etc.)
- Implement least privilege access
- Use network segmentation
- Enable audit logging
- Implement intrusion detection

## Security Checklist

Before deploying to production:

- [ ] All secrets moved to environment variables or secrets manager
- [ ] CORS properly configured (no wildcards)
- [ ] Rate limiting enabled
- [ ] HTTPS enforced
- [ ] MongoDB authentication enabled
- [ ] MongoDB connections encrypted
- [ ] Input validation implemented
- [ ] Security headers configured
- [ ] Logging and monitoring in place
- [ ] Dependencies scanned for vulnerabilities
- [ ] Regular security audits scheduled

## Known Security Considerations

### API Keys
This application requires external API keys (Alpha Vantage, FRED). These should:
- Be stored securely
- Have appropriate access restrictions
- Be rotated regularly
- Be monitored for unusual usage

### MongoDB
The application uses MongoDB. Ensure:
- Authentication is enabled
- Network access is restricted
- Connections use TLS
- Regular backups are performed

### External API Calls
The application makes calls to external APIs:
- Alpha Vantage
- FRED (Federal Reserve Economic Data)
- World Bank
- National Bank of Poland (NBP)

Ensure:
- API calls are made over HTTPS
- Responses are validated
- Errors are handled properly
- Rate limits are respected

## Security Updates

We regularly:
- Update dependencies to patch security vulnerabilities
- Scan code with security tools (Bandit, Safety)
- Review and update security practices
- Monitor security advisories for used packages

## Compliance

This application handles financial data. Consider:
- Data retention policies
- Privacy regulations (GDPR, CCPA, etc.)
- Financial data regulations
- Audit requirements

## Contact

For security concerns, please contact the repository maintainers.
