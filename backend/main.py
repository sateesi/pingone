import os
import hashlib
import base64
import secrets
import requests
import ssl
import certifi
import urllib3
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from jose import jwt, jwk, JWTError
import json

# Disable SSL warnings if SSL_VERIFY is False
if os.getenv("SSL_VERIFY", "True").lower() == "false":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration from environment variables
PINGONE_ISSUER = os.getenv("PINGONE_ISSUER", "https://auth.pingone.sg/1b8fa467-e41d-402a-8702-990c92c1f89b/as")
PINGONE_CLIENT_ID = os.getenv("PINGONE_CLIENT_ID", "d388aebf-7971-4acb-b9b0-6211a4931ed8")
PINGONE_CLIENT_SECRET = os.getenv("PINGONE_CLIENT_SECRET", "j8j4hVhRlAVbXc0pxuD-eNxR6~.O5W-zskvJVms8hGpw6wVGb73.dQtECr3n8MOD")
PINGONE_REDIRECT_URI = os.getenv("PINGONE_REDIRECT_URI", "http://localhost:3000/callback")
PINGONE_TOKEN_URL = f"{PINGONE_ISSUER}/token"
PINGONE_JWKS_URL = f"{PINGONE_ISSUER}/jwks"

# Backend configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
BACKEND_DEBUG = os.getenv("BACKEND_DEBUG", "True").lower() == "true"

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# SSL configuration
SSL_VERIFY = os.getenv("SSL_VERIFY", "True").lower() == "true"
SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", certifi.where())

# Create SSL context
ssl_context = ssl.create_default_context(cafile=SSL_CERT_PATH)
if not SSL_VERIFY:
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

app = FastAPI(title="PingOne SSO Backend", version="1.0.0")

# CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache for JWKS
jwks_cache = {"keys": None, "expires": 0}

class TokenExchangeRequest(BaseModel):
    code: str
    state: str
    code_verifier: str

class TokenResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    error: Optional[str] = None

def get_jwks():
    """Get JWKS from PingOne with caching"""
    import time
    current_time = time.time()
    
    if jwks_cache["keys"] and current_time < jwks_cache["expires"]:
        return jwks_cache["keys"]
    
    try:
        response = requests.get(PINGONE_JWKS_URL, timeout=10, verify=SSL_VERIFY)
        response.raise_for_status()
        jwks_data = response.json()
        
        # Cache for 1 hour
        jwks_cache["keys"] = jwks_data
        jwks_cache["expires"] = current_time + 3600
        
        return jwks_data
    except Exception as e:
        print(f"Error fetching JWKS: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch JWKS")

def verify_jwt_token(token: str) -> dict:
    try:
        jwks = get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(status_code=400, detail="Token missing key ID")

        # Find the matching JWK
        key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
        if not key:
            raise HTTPException(status_code=400, detail="Key not found in JWKS")

        # ✅ Directly pass the JWK dict, not jwk.construct()
        payload = jwt.decode(
            token,
            key,                        # <-- pass the dict directly
            algorithms=["RS256"],
            audience=PINGONE_CLIENT_ID,
            issuer=PINGONE_ISSUER,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_at_hash": False   # 👈 add this line
            }
        )
        return payload

    except JWTError as e:
        print(f"JWT verification error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Token verification error: {e}")
        raise HTTPException(status_code=500, detail="Token verification failed")


@app.get("/")
async def root():
    return {"message": "PingOne SSO Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/auth/callback", response_model=TokenResponse)
async def handle_auth_callback(request: TokenExchangeRequest):
    """Handle OAuth callback and exchange authorization code for tokens"""
    try:
        # Exchange authorization code for tokens
        # Use Basic Authentication as configured in PingOne
        import base64
        
        # Create basic auth header
        credentials = f"{PINGONE_CLIENT_ID}:{PINGONE_CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        token_data = {
            "grant_type": "authorization_code",
            "code": request.code,
            "redirect_uri": PINGONE_REDIRECT_URI,
            "code_verifier": request.code_verifier
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {encoded_credentials}"
        }
        
        response = requests.post(
            PINGONE_TOKEN_URL,
            data=token_data,
            headers=headers,
            timeout=30,
            verify=SSL_VERIFY
        )
        
        if response.status_code != 200:
            error_detail = response.text
            print(f"Token exchange failed: {response.status_code} - {error_detail}")
            print(f"Request data: {token_data}")
            print(f"Request headers: {headers}")
            print(f"Request URL: {PINGONE_TOKEN_URL}")
            return TokenResponse(
                success=False,
                error=f"Token exchange failed: {response.status_code} - {error_detail}"
            )
        
        token_response = response.json()
        access_token = token_response.get("access_token")
        id_token = token_response.get("id_token")
        
        if not id_token:
            return TokenResponse(
                success=False,
                error="No ID token received"
            )
        
        # Verify and decode the ID token
        user_info = verify_jwt_token(id_token)
        
        # Extract user information
        user = {
            "sub": user_info.get("sub"),
            "email": user_info.get("email"),
            "name": user_info.get("name"),
            "given_name": user_info.get("given_name"),
            "family_name": user_info.get("family_name"),
            "preferred_username": user_info.get("preferred_username"),
            "email_verified": user_info.get("email_verified", False)
        }
        
        return TokenResponse(
            success=True,
            user=user
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Auth callback error: {e}")
        return TokenResponse(
            success=False,
            error=f"Authentication failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
