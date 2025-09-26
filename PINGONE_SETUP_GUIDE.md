# PingOne Setup Guide

Complete guide for setting up PingOne OIDC application for the SSO demo.

## 🚀 Quick Setup

### 1. Access PingOne Admin Console
1. Log in to [PingOne Admin Console](https://admin.pingone.com)
2. Select your environment
3. Navigate to **Applications** → **Applications**

### 2. Create New Application
1. Click **"+ New Application"**
2. Select **"Web App (OpenID Connect)"**
3. Click **"Next"**

### 3. Application Configuration

#### Basic Settings
- **Name**: `pingone-sso-demo` (or your preferred name)
- **Description**: `SSO Demo Application`
- **Logo**: Optional

#### OIDC Settings
- **Token Auth Method**: `Client Secret Basic` ⚠️ **CRITICAL**
- **Response Type**: `Code`
- **Grant Type**: `Authorization Code`
- **PKCE Enforcement**: `Optional` (recommended: `Required`)

#### Redirect URIs
Add these exact URIs (one per line):
```
http://localhost:3000/callback
http://localhost:3000
http://127.0.0.1:3000/callback
http://127.0.0.1:3000
```

#### Additional Settings
- **Allow Redirect URI Patterns**: `False`
- **JSON Web Key Set**: `Not Specified`
- **Pushed Authorization Request Status**: `Optional`
- **PAR Reference Timeout**: `60 Seconds`
- **Signing Key**: `PingOne Key Rotation Policy for Administrators`

### 4. Save and Get Credentials
1. Click **"Save"**
2. Note down the following from the application details:
   - **Client ID**
   - **Client Secret** (click "Show" to reveal)

### 5. Get Environment Information
1. Go to **Environments** → Your Environment
2. Note down:
   - **Environment ID** (from the URL or environment details)
   - **Region** (e.g., `sg` for Singapore, `us` for US)

## 🔧 Application Configuration

### Required Settings Summary
```
App Type: Web App (OpenID Connect)
Token Auth Method: Client Secret Basic
Response Type: Code
Grant Type: Authorization Code
PKCE Enforcement: Optional (or Required)
Redirect URIs: 
  - http://localhost:3000/callback
  - http://localhost:3000
  - http://127.0.0.1:3000/callback
  - http://127.0.0.1:3000
```

### ⚠️ Critical Configuration Points

#### 1. Token Auth Method
- **MUST** be set to `Client Secret Basic`
- Other methods (like `None` or `Client Secret Post`) will cause 401 errors

#### 2. Redirect URIs
- **MUST** include `/callback` for the main redirect
- **MUST** match exactly (no trailing slashes, correct protocol)
- Include both `localhost` and `127.0.0.1` variants

#### 3. PKCE Settings
- Can be `Optional` or `Required`
- The demo works with both settings
- `Required` is more secure for production

## 🌍 Regional Configuration

### Singapore Region (Default)
```
Issuer URL: https://auth.pingone.sg/{ENVIRONMENT_ID}/as
Auth URL: https://auth.pingone.sg/{ENVIRONMENT_ID}/as/authorize
Token URL: https://auth.pingone.sg/{ENVIRONMENT_ID}/as/token
JWKS URL: https://auth.pingone.sg/{ENVIRONMENT_ID}/as/jwks
```

### US Region
```
Issuer URL: https://auth.pingone.com/{ENVIRONMENT_ID}/as
Auth URL: https://auth.pingone.com/{ENVIRONMENT_ID}/as/authorize
Token URL: https://auth.pingone.com/{ENVIRONMENT_ID}/as/token
JWKS URL: https://auth.pingone.com/{ENVIRONMENT_ID}/as/jwks
```

### Europe Region
```
Issuer URL: https://auth.pingone.eu/{ENVIRONMENT_ID}/as
Auth URL: https://auth.pingone.eu/{ENVIRONMENT_ID}/as/authorize
Token URL: https://auth.pingone.eu/{ENVIRONMENT_ID}/as/token
JWKS URL: https://auth.pingone.eu/{ENVIRONMENT_ID}/as/jwks
```

## 🔐 Security Configuration

### Recommended Security Settings
1. **PKCE Enforcement**: `Required` (for production)
2. **Token Expiration**: Use default settings
3. **Refresh Token**: Enable if needed
4. **Scopes**: `openid profile email` (default)

### Production Considerations
- Use HTTPS redirect URIs
- Implement proper CORS policies
- Enable audit logging
- Regular security reviews

## 📝 Environment Variables Setup

### Backend Configuration (.env)
Create `.env` file from template:
```bash
copy env.example .env
```

Then update with your PingOne credentials:
```env
# PingOne Configuration
PINGONE_ISSUER=https://auth.pingone.sg/YOUR_ENVIRONMENT_ID/as
PINGONE_CLIENT_ID=your-client-id-here
PINGONE_CLIENT_SECRET=your-client-secret-here
PINGONE_REDIRECT_URI=http://localhost:3000/callback

# SSL Configuration
SSL_VERIFY=True
SSL_CERT_PATH=

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend Configuration (frontend/.env)
Create `frontend/.env` file from template:
```bash
copy frontend\env.example frontend\.env
```

Then update with your PingOne credentials:
```env
# PingOne Configuration
REACT_APP_PINGONE_AUTH_URL=https://auth.pingone.sg/YOUR_ENVIRONMENT_ID/as/authorize
REACT_APP_PINGONE_CLIENT_ID=your-client-id-here
REACT_APP_PINGONE_REDIRECT_URI=http://localhost:3000/callback

# Backend API
REACT_APP_BACKEND_URL=http://localhost:8000
```

## ✅ Verification Steps

### 1. Test Application Creation
1. Verify application appears in PingOne Admin Console
2. Check that all settings match the configuration above
3. Confirm Client ID and Secret are available

### 2. Test Redirect URIs
1. In PingOne Admin Console, test each redirect URI
2. Ensure they redirect properly to your application
3. Check for any validation errors

### 3. Test Token Exchange
1. Use the demo application to test login flow
2. Check backend logs for successful token exchange
3. Verify JWT validation works correctly

## 🐛 Common Setup Issues

### Issue 1: Application Not Found
**Symptoms**: 404 errors when accessing PingOne endpoints
**Solution**: Verify your Environment ID and region in the URLs

### Issue 2: Invalid Client
**Symptoms**: 401 errors during token exchange
**Solution**: Check Client ID and Secret are correct

### Issue 3: Redirect URI Mismatch
**Symptoms**: OAuth flow fails at redirect step
**Solution**: Ensure redirect URIs match exactly in PingOne and your app

### Issue 4: Unsupported Authentication Method
**Symptoms**: 401 "Request denied" during token exchange
**Solution**: Set Token Auth Method to "Client Secret Basic"

## 📚 Additional Resources

- [PingOne Developer Documentation](https://docs.pingidentity.com/)
- [OIDC Configuration Guide](https://docs.pingidentity.com/bundle/pingone/page/ojc1564022990477.html)
- [OAuth 2.0 Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting guide
2. Verify your PingOne configuration matches this guide
3. Check application logs for specific error messages
4. Review PingOne documentation for your specific region
