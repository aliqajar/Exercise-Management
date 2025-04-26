/**
 * Authentication service for handling JWT tokens and API calls
 */

// Store tokens in localStorage
const setTokens = (accessToken, refreshToken) => {
  localStorage.setItem('accessToken', accessToken);
  localStorage.setItem('refreshToken', refreshToken);
};

// Remove tokens from localStorage
const clearTokens = () => {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
};

// Get access token from localStorage
const getAccessToken = () => {
  return localStorage.getItem('accessToken');
};

// Get refresh token from localStorage
const getRefreshToken = () => {
  return localStorage.getItem('refreshToken');
};

// Check if user is logged in
const isAuthenticated = () => {
  return !!getAccessToken();
};

// Register a new user
const register = async (username, password) => {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username,
      password,
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Registration failed');
  }

  return await response.json();
};

// Login user
const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  const response = await fetch('/auth/token', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || 'Login failed. Please check your credentials.');
  }

  const data = await response.json();
  setTokens(data.access_token, data.refresh_token);
  return data;
};

// Refresh access token
const refreshToken = async () => {
  const refresh = getRefreshToken();
  
  if (!refresh) {
    throw new Error('No refresh token available');
  }

  try {
    const response = await fetch('/auth/refresh', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        refresh_token: refresh,
      }),
    });

    if (!response.ok) {
      throw new Error('Token refresh failed');
    }

    const data = await response.json();
    setTokens(data.access_token, data.refresh_token);
    return data;
  } catch (error) {
    clearTokens();
    throw error;
  }
};

// Logout user
const logout = () => {
  clearTokens();
};

// Create authenticated fetch
const authFetch = async (url, options = {}) => {
  const token = getAccessToken();
  
  if (!token) {
    throw new Error('No access token available');
  }
  
  // Add authorization header
  const authOptions = {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  };
  
  let response = await fetch(url, authOptions);
  
  // If token is expired, try to refresh it
  if (response.status === 401) {
    try {
      await refreshToken();
      
      // Retry with new token
      authOptions.headers.Authorization = `Bearer ${getAccessToken()}`;
      response = await fetch(url, authOptions);
    } catch (error) {
      clearTokens();
      throw new Error('Authentication failed');
    }
  }
  
  return response;
};

export const authService = {
  register,
  login,
  logout,
  refreshToken,
  isAuthenticated,
  getAccessToken,
  getRefreshToken,
  authFetch,
}; 