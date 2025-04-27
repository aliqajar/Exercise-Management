import axios from 'axios';

// Set default base URL for all axios requests
// Try without the /api suffix first - many FastAPI/Flask apps don't use this prefix
axios.defaults.baseURL = 'http://localhost:8000';

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
  try {
    // Test if localStorage is working
    localStorage.setItem('test', 'test');
    const testValue = localStorage.getItem('test');
    if (testValue !== 'test') {
      console.error('localStorage test failed!');
    } else {
      localStorage.removeItem('test');
    }
    
    // Get the actual token
    const token = localStorage.getItem('accessToken');
    console.log('Retrieved token from localStorage:', token ? 'exists' : 'missing', 
                token ? `(${token.substring(0, 10)}...)` : '');
    return token;
  } catch (e) {
    console.error('Error accessing localStorage:', e);
    return null;
  }
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
  try {
    console.log('Attempting registration to:', axios.defaults.baseURL + '/auth/register');
    
    const response = await axios.post('/auth/register', {
      username,
      password
    });
    return response.data;
  } catch (error) {
    console.error('Registration failed:', error.response?.status, error.message);
    console.error('Error response data:', error.response?.data);
    throw new Error(error.response?.data?.detail || 'Registration failed');
  }
};

// Login user
const login = async (username, password) => {
  try {
    // For login we need to use form data format
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    console.log('Attempting login to:', axios.defaults.baseURL + '/auth/token');
    
    const response = await axios.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    console.log('Login successful, tokens received:', response.data);
    setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  } catch (error) {
    console.error('Login failed:', error.response?.status, error.message);
    console.error('Error response data:', error.response?.data);
    throw new Error(error.response?.data?.detail || 'Login failed. Please check your credentials.');
  }
};

// Refresh access token
const refreshToken = async () => {
  const refresh = getRefreshToken();
  
  if (!refresh) {
    throw new Error('No refresh token available');
  }

  try {
    const response = await axios.post('/auth/refresh', {
      refresh_token: refresh
    });

    setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  } catch (error) {
    console.error('Token refresh failed:', error.response?.status, error.message);
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
  
  // Configure axios request
  const config = {
    method: options.method || 'GET',
    url: url,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': options.headers?.['Content-Type'] || 'application/json'
    }
  };
  
  // Add body if present
  if (options.body) {
    config.data = JSON.parse(options.body);
  }
  
  console.log('Making axios request:', {
    url,
    method: config.method,
    headers: config.headers,
    data: config.data ? 'present' : 'none'
  });
  
  try {
    const response = await axios(config);
    console.log('Axios response:', response.status);
    
    // Convert axios response to fetch-like response
    return {
      ok: response.status >= 200 && response.status < 300,
      status: response.status,
      json: async () => response.data,
      text: async () => JSON.stringify(response.data)
    };
  } catch (error) {
    console.error('Axios error:', error.response?.status, error.message);
    
    // Handle token expiration
    if (error.response?.status === 401) {
      try {
        console.log('Got 401, refreshing token...');
        await refreshToken();
        
        // Update with new token and retry
        config.headers['Authorization'] = `Bearer ${getAccessToken()}`;
        const retryResponse = await axios(config);
        
        return {
          ok: retryResponse.status >= 200 && retryResponse.status < 300,
          status: retryResponse.status,
          json: async () => retryResponse.data,
          text: async () => JSON.stringify(retryResponse.data)
        };
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        clearTokens();
        throw new Error('Authentication failed: ' + refreshError.message);
      }
    }
    
    // Return a fetch-like error response
    return {
      ok: false,
      status: error.response?.status || 500,
      json: async () => error.response?.data || { detail: error.message },
      text: async () => JSON.stringify(error.response?.data || { detail: error.message })
    };
  }
};

// Get user ID from JWT token
const getCurrentUserId = () => {
  try {
    const token = getAccessToken();
    if (!token) return null;
    
    // Decode JWT without library
    // JWT token has three parts: header.payload.signature
    const payload = token.split('.')[1];
    // Base64 decode and parse JSON
    const decoded = JSON.parse(atob(payload));
    
    return decoded.sub; // 'sub' field contains the username
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
};

// Get username from JWT token (sub claim)
const getCurrentUsername = () => {
  try {
    const token = getAccessToken();
    if (!token) return null;
    
    // JWT token has three parts: header.payload.signature
    const payload = token.split('.')[1];
    // Base64 decode and parse JSON
    const decoded = JSON.parse(atob(payload));
    
    return decoded.sub; // 'sub' field contains the username
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
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
  getCurrentUserId,
  getCurrentUsername,
}; 