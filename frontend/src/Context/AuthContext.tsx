import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { IUser } from '../Models/User';

interface AuthTokens {
  accessToken: string;
  refreshToken?: string;
  expiresAt: number;
}

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: IUser | null;
  login: () => void;
  logout: () => void;
  getAccessToken: () => string | null;
  handleCallback: (code: string, state: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState<IUser | null>(null);
  const [tokens, setTokens] = useState<AuthTokens | null>(null);

  // OAuth2 configuration from environment variables
  const clientId = import.meta.env.VITE_OAUTH_CLIENT_ID;
  const authority = import.meta.env.VITE_OAUTH_AUTHORITY;
  const redirectUri = import.meta.env.VITE_OAUTH_REDIRECT_URI;
  const scope = import.meta.env.VITE_OAUTH_SCOPE || 'openid profile email';

  // Generate PKCE code verifier and challenge
  const generateCodeVerifier = (): string => {
    const array = new Uint8Array(32);
    crypto.getRandomValues(array);
    return base64URLEncode(array);
  };

  const base64URLEncode = (buffer: Uint8Array): string => {
    const base64 = btoa(String.fromCharCode(...Array.from(buffer)));
    return base64.replace(/\+/g, '-').replace(/\//g, '_').replace(/=/g, '');
  };

  const generateCodeChallenge = async (verifier: string): Promise<string> => {
    const encoder = new TextEncoder();
    const data = encoder.encode(verifier);
    const hash = await crypto.subtle.digest('SHA-256', data);
    return base64URLEncode(new Uint8Array(hash));
  };

  const generateRandomState = (): string => {
    const array = new Uint8Array(16);
    crypto.getRandomValues(array);
    return base64URLEncode(array);
  };

  // Initialize auth state from storage
  useEffect(() => {
    const initAuth = async () => {
      try {
        const storedTokens = sessionStorage.getItem('auth_tokens');
        const storedUser = sessionStorage.getItem('auth_user');

        if (storedTokens && storedUser) {
          const parsedTokens: AuthTokens = JSON.parse(storedTokens);
          const parsedUser: IUser = JSON.parse(storedUser);

          // Check if token is expired
          if (parsedTokens.expiresAt > Date.now()) {
            setTokens(parsedTokens);
            setUser(parsedUser);
            setIsAuthenticated(true);
          } else {
            // Token expired, try to refresh if refresh token exists
            if (parsedTokens.refreshToken) {
              await refreshAccessToken(parsedTokens.refreshToken);
            } else {
              // Clear expired tokens
              clearAuthData();
            }
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuthData();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  // Auto-refresh token before expiry
  useEffect(() => {
    if (!tokens || !tokens.refreshToken) return;

    const timeUntilExpiry = tokens.expiresAt - Date.now();
    const refreshTime = timeUntilExpiry - 5 * 60 * 1000; // Refresh 5 minutes before expiry

    if (refreshTime > 0) {
      const timeoutId = setTimeout(() => {
        refreshAccessToken(tokens.refreshToken!);
      }, refreshTime);

      return () => clearTimeout(timeoutId);
    }
  }, [tokens]);

  const clearAuthData = () => {
    sessionStorage.removeItem('auth_tokens');
    sessionStorage.removeItem('auth_user');
    sessionStorage.removeItem('pkce_verifier');
    sessionStorage.removeItem('oauth_state');
    setTokens(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  const login = async () => {
    if (!clientId || !authority || !redirectUri) {
      console.error('OAuth2 configuration is missing. Please set environment variables.');
      return;
    }

    try {
      // Generate PKCE parameters
      const codeVerifier = generateCodeVerifier();
      const codeChallenge = await generateCodeChallenge(codeVerifier);
      const state = generateRandomState();

      // Store for later verification
      sessionStorage.setItem('pkce_verifier', codeVerifier);
      sessionStorage.setItem('oauth_state', state);

      // Build authorization URL
      const params = new URLSearchParams({
        client_id: clientId,
        response_type: 'code',
        redirect_uri: redirectUri,
        scope: scope,
        state: state,
        code_challenge: codeChallenge,
        code_challenge_method: 'S256',
      });

      const authUrl = `${authority}/authorize?${params.toString()}`;
      window.location.href = authUrl;
    } catch (error) {
      console.error('Error initiating login:', error);
    }
  };

  const handleCallback = async (code: string, state: string) => {
    if (!clientId || !authority || !redirectUri) {
      throw new Error('OAuth2 configuration is missing');
    }

    try {
      // Verify state parameter
      const storedState = sessionStorage.getItem('oauth_state');
      if (state !== storedState) {
        throw new Error('Invalid state parameter - possible CSRF attack');
      }

      // Retrieve PKCE code verifier
      const codeVerifier = sessionStorage.getItem('pkce_verifier');
      if (!codeVerifier) {
        throw new Error('PKCE verifier not found');
      }

      // Exchange authorization code for tokens
      const tokenResponse = await fetch(`${authority}/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'authorization_code',
          client_id: clientId,
          code: code,
          redirect_uri: redirectUri,
          code_verifier: codeVerifier,
        }),
      });

      if (!tokenResponse.ok) {
        throw new Error('Failed to exchange authorization code for tokens');
      }

      const tokenData = await tokenResponse.json();

      // Parse and store tokens
      const authTokens: AuthTokens = {
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token,
        expiresAt: Date.now() + tokenData.expires_in * 1000,
      };

      // Decode JWT to get user info (simple base64 decode of payload)
      const payload = JSON.parse(atob(tokenData.access_token.split('.')[1]));
      const userData: IUser = {
        id: payload.sub,
        name: payload.name || payload.preferred_username || 'User',
        email: payload.email || '',
        picture: payload.picture,
      };

      // Store in session storage
      sessionStorage.setItem('auth_tokens', JSON.stringify(authTokens));
      sessionStorage.setItem('auth_user', JSON.stringify(userData));

      // Update state
      setTokens(authTokens);
      setUser(userData);
      setIsAuthenticated(true);

      // Clean up PKCE data
      sessionStorage.removeItem('pkce_verifier');
      sessionStorage.removeItem('oauth_state');
    } catch (error) {
      console.error('Error handling OAuth callback:', error);
      clearAuthData();
      throw error;
    }
  };

  const refreshAccessToken = async (refreshToken: string) => {
    if (!clientId || !authority) {
      clearAuthData();
      return;
    }

    try {
      const tokenResponse = await fetch(`${authority}/token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          grant_type: 'refresh_token',
          client_id: clientId,
          refresh_token: refreshToken,
        }),
      });

      if (!tokenResponse.ok) {
        throw new Error('Failed to refresh token');
      }

      const tokenData = await tokenResponse.json();

      const authTokens: AuthTokens = {
        accessToken: tokenData.access_token,
        refreshToken: tokenData.refresh_token || refreshToken,
        expiresAt: Date.now() + tokenData.expires_in * 1000,
      };

      sessionStorage.setItem('auth_tokens', JSON.stringify(authTokens));
      setTokens(authTokens);
    } catch (error) {
      console.error('Error refreshing token:', error);
      clearAuthData();
    }
  };

  const logout = () => {
    clearAuthData();

    // Optional: Redirect to OAuth provider logout endpoint
    // if (authority && clientId) {
    //   const logoutUrl = `${authority}/logout?client_id=${clientId}&returnTo=${redirectUri}`;
    //   window.location.href = logoutUrl;
    // }
  };

  const getAccessToken = (): string | null => {
    if (!tokens || tokens.expiresAt <= Date.now()) {
      return null;
    }
    return tokens.accessToken;
  };

  const value: AuthContextType = {
    isAuthenticated,
    isLoading,
    user,
    login,
    logout,
    getAccessToken,
    handleCallback,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
