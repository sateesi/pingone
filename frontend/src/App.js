import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check if we're returning from PingOne with an authorization code
  useEffect(() => {
    // Check if we're on the callback route
    if (window.location.pathname === '/callback') {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const errorParam = urlParams.get('error');

      if (errorParam) {
        setError(`Authentication error: ${errorParam}`);
        return;
      }

      if (code && state) {
        handleCallback(code, state);
      }
    }
  }, []);

  const handleCallback = async (code, state) => {
    setLoading(true);
    setError(null);

    try {
      // Get the stored PKCE verifier from sessionStorage
      const codeVerifier = sessionStorage.getItem('pkce_code_verifier');
      if (!codeVerifier) {
        throw new Error('PKCE code verifier not found');
      }

      // Exchange authorization code for tokens
      const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
      const response = await axios.post(`${backendUrl}/api/auth/callback`, {
        code,
        state,
        code_verifier: codeVerifier
      });

      if (response.data.success) {
        setUser(response.data.user);
        // Clean up the URL
        window.history.replaceState({}, document.title, window.location.pathname);
      } else {
        setError(response.data.error || 'Authentication failed');
      }
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  // This function is kept for reference but not used
  const handleLogin = () => {
    // This function is replaced by handleLoginAsync
    handleLoginAsync();
  };

  const handleLogout = () => {
    setUser(null);
    sessionStorage.clear();
  };

  // PKCE helper functions
  const generateCodeVerifier = () => {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return base64URLEncode(array);
  };

  const generateCodeChallenge = (verifier) => {
    const encoder = new TextEncoder();
    const data = encoder.encode(verifier);
    return crypto.subtle.digest('SHA-256', data).then(hash => {
      return base64URLEncode(new Uint8Array(hash));
    });
  };

  const base64URLEncode = (array) => {
    return btoa(String.fromCharCode(...array))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
  };

  const generateRandomString = (length) => {
    const array = new Uint8Array(length);
    crypto.getRandomValues(array);
    return base64URLEncode(array);
  };

  // Handle async code challenge generation
  const handleLoginAsync = async () => {
    console.log('handleLoginAsync called');
    setLoading(true);
    setError(null);

    try {
      console.log('Generating PKCE parameters...');
      const codeVerifier = generateCodeVerifier();
      const codeChallenge = await generateCodeChallenge(codeVerifier);
      const state = generateRandomString(32);

      console.log('Code verifier:', codeVerifier);
      console.log('Code challenge:', codeChallenge);
      console.log('State:', state);

      sessionStorage.setItem('pkce_code_verifier', codeVerifier);
      sessionStorage.setItem('oauth_state', state);

      const authUrl = new URL(process.env.REACT_APP_PINGONE_AUTH_URL || 'https://auth.pingone.sg/1b8fa467-e41d-402a-8702-990c92c1f89b/as/authorize');
      authUrl.searchParams.set('response_type', 'code');
      authUrl.searchParams.set('client_id', process.env.REACT_APP_PINGONE_CLIENT_ID || 'd388aebf-7971-4acb-b9b0-6211a4931ed8');
      authUrl.searchParams.set('redirect_uri', process.env.REACT_APP_PINGONE_REDIRECT_URI || 'http://localhost:3000/callback');
      authUrl.searchParams.set('scope', 'openid profile email');
      authUrl.searchParams.set('code_challenge', codeChallenge);
      authUrl.searchParams.set('code_challenge_method', 'S256');
      authUrl.searchParams.set('state', state);

      console.log('Generated auth URL:', authUrl.toString());
      console.log('Redirect URI:', authUrl.searchParams.get('redirect_uri'));
      
      console.log('Redirecting to PingOne...');
      window.location.href = authUrl.toString();
    } catch (err) {
      console.error('Error in handleLoginAsync:', err);
      setError('Failed to generate authentication parameters');
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>PingOne SSO Demo</h1>
      
      {!user ? (
        <div>
          <p>Click the button below to sign in with PingOne:</p>
          <button 
            className="login-button" 
            onClick={handleLoginAsync}
            disabled={loading}
          >
            {loading ? 'Redirecting...' : 'Sign In with PingOne'}
          </button>
          
          {error && <div className="error">{error}</div>}
          {loading && !error && <div className="loading">Processing authentication...</div>}
        </div>
      ) : (
        <div className="user-info">
          <h2>Welcome!</h2>
          <p><strong>Hello {user.name || user.preferred_username || user.email}!</strong></p>
          <p>Email: {user.email}</p>
          {user.given_name && <p>First Name: {user.given_name}</p>}
          {user.family_name && <p>Last Name: {user.family_name}</p>}
          <button className="login-button" onClick={handleLogout}>
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}

export default App;
