# PingOne SSO Demo Application

A minimal full-stack application demonstrating SSO (Single Sign-On) with PingOne using the Authorization Code + PKCE flow.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- PingOne account with OIDC application configured

### 1. Clone and Setup
```bash
git clone <your-repo>
cd pingone
```

### 2. Configure Environment Variables
Create environment files and update with your PingOne credentials:

```bash
# Create backend environment file
copy env.example .env

# Create frontend environment file  
copy frontend\env.example frontend\.env
```

**⚠️ Important**: All environment variables are now required. The application will fail to start if any required variables are missing.

Update the following in both `.env` and `frontend\.env`:
- `PINGONE_CLIENT_ID` - Your PingOne application client ID
- `PINGONE_CLIENT_SECRET` - Your PingOne application client secret
- `PINGONE_ISSUER` - Your PingOne environment issuer URL
- `PINGONE_REDIRECT_URI` - Must match your PingOne app configuration

### 3. Run the Application
```bash
docker-compose up --build
```

### 4. Test the Application
1. Open http://localhost:3000
2. Click "Sign In with PingOne"
3. Complete authentication with your PingOne credentials
4. You should see "Hello <username>" after successful login

## 🏗️ Architecture

### Frontend (React + Nginx)
- **Port**: 3000
- **Framework**: React 18
- **Features**:
  - PKCE code generation using Web Crypto API
  - OAuth 2.0 Authorization Code flow
  - JWT token handling
  - User session management

### Backend (FastAPI)
- **Port**: 8000
- **Framework**: FastAPI
- **Features**:
  - Token exchange with PingOne
  - JWT signature verification using JWKS
  - CORS handling
  - SSL certificate validation

### Key Components

#### Frontend (`frontend/src/App.js`)
- Generates PKCE code challenge and verifier
- Handles OAuth redirect flow
- Manages user authentication state
- Calls backend for token exchange

#### Backend (`backend/main.py`)
- Exchanges authorization code for tokens
- Validates JWT signatures using PingOne JWKS
- Returns user information to frontend

## 🔧 PingOne Configuration

### Required Application Settings
1. **App Type**: Web App (OpenID Connect)
2. **Token Auth Method**: Client Secret Basic
3. **Response Type**: Code
4. **Grant Type**: Authorization Code
5. **PKCE Enforcement**: Optional (but recommended)
6. **Redirect URIs**: 
   - `http://localhost:3000/callback`
   - `http://localhost:3000`
   - `http://127.0.0.1:3000/callback`
   - `http://127.0.0.1:3000`

### Environment Variables
The application uses environment files for configuration:

#### Backend (.env)
```env
# PingOne Configuration
PINGONE_ISSUER=https://auth.pingone.sg/YOUR-ENVIRONMENT-ID/as
PINGONE_CLIENT_ID=your-client-id
PINGONE_CLIENT_SECRET=your-client-secret
PINGONE_REDIRECT_URI=http://localhost:3000/callback

# SSL Configuration
SSL_VERIFY=True
SSL_CERT_PATH=

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

#### Frontend (frontend/.env)
```env
# PingOne Configuration
REACT_APP_PINGONE_AUTH_URL=https://auth.pingone.sg/YOUR-ENVIRONMENT-ID/as/authorize
REACT_APP_PINGONE_CLIENT_ID=your-client-id
REACT_APP_PINGONE_REDIRECT_URI=http://localhost:3000/callback

# Backend API
REACT_APP_BACKEND_URL=http://localhost:8000
```

**Note**: The docker-compose.yml no longer references environment files directly. Environment variables are loaded from `.env` and `frontend/.env` files automatically by the applications.

## 🔐 Security Features

### JWT Verification
- Validates JWT signatures using PingOne JWKS
- Verifies audience and issuer claims
- Uses RS256 algorithm for signature verification
- Proper SSL certificate validation

### PKCE Implementation
- Uses Web Crypto API for secure code generation
- SHA256 code challenge method
- State parameter for CSRF protection

### SSL/TLS
- Proper certificate validation enabled
- Uses system CA certificates
- No insecure requests in production

## 🐛 Troubleshooting

### Common Issues

#### 1. Redirect URI Mismatch
**Error**: `Redirect URI mismatch`
**Solution**: Ensure the redirect URI in your PingOne application matches exactly:
- `http://localhost:3000/callback` (with `/callback`)

#### 2. Token Exchange Failed (401)
**Error**: `Token exchange failed: 401`
**Solution**: Verify your PingOne application settings:
- Token Auth Method: `Client Secret Basic`
- Client Secret is correct
- Client ID matches your configuration

#### 3. JWT Verification Failed
**Error**: `Unable to find an algorithm for key`
**Solution**: This is resolved in the current implementation by:
- Passing JWK dictionary directly to `jwt.decode()`
- Explicitly setting `algorithms=["RS256"]`
- Adding proper verification options

#### 4. SSL Certificate Issues
**Error**: `SSL: CERTIFICATE_VERIFY_FAILED`
**Solution**: Ensure `SSL_VERIFY=True` in your environment (default)

### Debug Mode
Enable debug logging by setting `BACKEND_DEBUG=True` in your `.env` file.

## 📁 Project Structure

```
pingone/
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   ├── index.js        # React entry point
│   │   └── index.css       # Basic styling
│   ├── public/
│   │   └── index.html      # HTML template
│   ├── nginx.conf          # Nginx configuration
│   ├── Dockerfile          # Frontend container
│   ├── package.json        # Node.js dependencies
│   ├── env.example         # Frontend environment template
│   └── .env                # Frontend environment (create from template)
├── backend/
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container
├── docker-compose.yml      # Multi-container setup
├── env.example             # Backend environment template
├── .env                    # Backend environment (create from template)
└── README.md              # This file
```

## 🚀 Production Deployment

### Environment Variables
- Set `SSL_VERIFY=True` for production
- Use proper domain names for redirect URIs
- Store secrets securely (not in version control)

### Security Considerations
- Enable HTTPS in production
- Use proper CORS origins
- Implement proper session management
- Regular security updates

## 📚 Learning Resources

This demo covers:
- OAuth 2.0 Authorization Code flow
- PKCE (Proof Key for Code Exchange)
- JWT token validation
- OpenID Connect integration
- Docker containerization
- SSL/TLS certificate handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational purposes. Please ensure you comply with PingOne's terms of service when using their services.