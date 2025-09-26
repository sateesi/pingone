# PingOne SSO Troubleshooting Guide

This guide covers common issues and their solutions for the PingOne SSO demo application.

## 🔧 Common Issues and Solutions

### 1. Redirect URI Mismatch

**Error Message:**
```
Redirect URI mismatch
```

**Cause:** The redirect URI in your PingOne application doesn't match what the frontend is sending.

**Solution:**
1. In PingOne Admin Console, go to your application settings
2. Add these exact redirect URIs:
   - `http://localhost:3000/callback`
   - `http://localhost:3000`
   - `http://127.0.0.1:3000/callback`
   - `http://127.0.0.1:3000`

**Verification:**
- Check that the URI includes `/callback` for the main redirect
- Ensure no trailing slashes or extra characters

### 2. Token Exchange Failed (401 Unauthorized)

**Error Message:**
```
Token exchange failed: 401
Request denied: Unsupported authentication method
```

**Cause:** Incorrect authentication method configuration in PingOne.

**Solution:**
1. In PingOne Admin Console, go to your application settings
2. Set **Token Auth Method** to: `Client Secret Basic`
3. Verify your **Client Secret** is correct
4. Ensure **Client ID** matches your configuration

**Verification:**
- Check that `PINGONE_CLIENT_SECRET` in your `.env` file matches PingOne
- Verify `PINGONE_CLIENT_ID` is correct

### 3. JWT Verification Failed

**Error Message:**
```
Unable to find an algorithm for key: {'kty': 'RSA', 'e': 'AQAB', ...}
```

**Cause:** The JWT library couldn't auto-detect the signing algorithm.

**Solution:** ✅ **RESOLVED** - The current implementation:
- Passes JWK dictionary directly to `jwt.decode()`
- Explicitly sets `algorithms=["RS256"]`
- Includes proper verification options

**Code Fix Applied:**
```python
payload = jwt.decode(
    token,
    key,                        # JWK dict directly
    algorithms=["RS256"],       # Explicit algorithm
    audience=PINGONE_CLIENT_ID,
    issuer=PINGONE_ISSUER,
    options={
        "verify_signature": True,
        "verify_aud": True,
        "verify_iss": True,
        "verify_at_hash": False
    }
)
```

### 4. SSL Certificate Verification Issues

**Error Message:**
```
SSL: CERTIFICATE_VERIFY_FAILED certificate verify failed: unable to get local issuer certificate
```

**Cause:** SSL certificate verification is disabled or misconfigured.

**Solution:** ✅ **RESOLVED** - The current implementation:
- Uses `SSL_VERIFY=True` by default
- Properly validates certificates using system CA bundle
- No insecure requests in production

**Configuration:**
```env
# In your .env file
SSL_VERIFY=True
SSL_CERT_PATH=
```

### 5. Frontend Redirect Loop

**Issue:** After clicking "Sign In with PingOne", the same page loads again.

**Cause:** Incorrect redirect URI configuration or missing callback handling.

**Solution:** ✅ **RESOLVED** - The current implementation:
- Uses correct redirect URI: `http://localhost:3000/callback`
- Handles `/callback` route in React Router
- Properly configured Nginx routing

**Verification:**
- Check browser console for redirect URL
- Ensure `/callback` route is handled in `App.js`
- Verify Nginx configuration includes callback route

### 6. Import Errors in IDE

**Error Message:**
```
Import "jose" could not be resolved from source
Import "jose.exceptions" could not be resolved from source
```

**Cause:** IDE not recognizing installed packages in Docker container.

**Solution:**
- This is an IDE-specific issue, not a code problem
- The code works correctly in Docker
- For IDE support, install packages locally:
  ```bash
  pip install python-jose[cryptography]
  ```

### 7. Docker Build Failures

**Error Message:**
```
npm error A complete log of this run can be found in: /root/.npm/_logs/...
```

**Cause:** Node.js dependency installation issues.

**Solution:** ✅ **RESOLVED** - The current implementation:
- Uses `npm install --silent` instead of `npm ci`
- Removed unnecessary dependencies
- Optimized Dockerfile for faster builds

### 8. Missing Environment Variables

**Error Message:**
```
Missing required environment variables: PINGONE_CLIENT_ID, PINGONE_ISSUER
ValueError: Missing required environment variables: PINGONE_CLIENT_ID, PINGONE_ISSUER. Please check your .env file.
```

**Solution:**
1. Create environment files from templates:
   ```bash
   copy env.example .env
   copy frontend\env.example frontend\.env
   ```
2. Update all required variables in both files
3. Ensure no variables are empty or commented out
4. Restart the application

### 9. Port Already in Use

**Error Message:**
```
Bind for 0.0.0.0:8000 failed: port is already allocated
```

**Solution:**
1. Stop existing containers:
   ```bash
   docker-compose down
   ```
2. Check for running containers:
   ```bash
   docker ps
   ```
3. Stop conflicting containers:
   ```bash
   docker stop <container-id>
   ```

## 🔍 Debugging Steps

### 1. Enable Debug Logging
Set debug mode in your `.env` file:
```env
BACKEND_DEBUG=True
```

### 2. Check Container Logs
```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
```

### 3. Verify Environment Variables
```bash
# Check if environment files exist
ls -la .env frontend/.env

# Verify content
cat .env
cat frontend/.env

# If files don't exist, create from templates
copy env.example .env
copy frontend\env.example frontend\.env
```

### 4. Test Backend Health
```bash
curl http://localhost:8000/health
```

### 5. Test Frontend
Open browser developer tools (F12) and check:
- Console for error messages
- Network tab for failed requests
- Application tab for stored tokens

## 🚀 Performance Optimization

### 1. Docker Build Optimization
- Use multi-stage builds (already implemented)
- Cache dependencies properly
- Use Alpine Linux images for smaller size

### 2. Frontend Optimization
- Enable gzip compression in Nginx
- Use production React build
- Implement proper caching headers

### 3. Backend Optimization
- Cache JWKS responses (already implemented)
- Use connection pooling
- Implement proper error handling

## 📋 Pre-deployment Checklist

Before deploying to production:

- [ ] SSL verification enabled (`SSL_VERIFY=True`)
- [ ] Proper domain names in redirect URIs
- [ ] Secrets stored securely (not in code)
- [ ] CORS origins configured correctly
- [ ] HTTPS enabled
- [ ] Error logging configured
- [ ] Health checks implemented
- [ ] Monitoring setup

## 🆘 Getting Help

If you're still experiencing issues:

1. Check the application logs
2. Verify your PingOne configuration
3. Test with a simple curl request
4. Review the main README.md for setup instructions
5. Check the PingOne documentation

## 📚 Additional Resources

- [PingOne Developer Documentation](https://docs.pingidentity.com/)
- [OAuth 2.0 RFC](https://tools.ietf.org/html/rfc6749)
- [PKCE RFC](https://tools.ietf.org/html/rfc7636)
- [JWT RFC](https://tools.ietf.org/html/rfc7519)
