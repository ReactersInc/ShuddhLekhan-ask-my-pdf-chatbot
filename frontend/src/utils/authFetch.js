/**
 * Authenticated Fetch Utility
 * 
 * This utility function automatically includes JWT token in requests
 * to backend API endpoints that require authentication.
 * 
 * Usage:
 *   const response = await authFetch('/documents/tree');
 *   const data = await authFetch('/documents/list', { method: 'POST' });
 */

import { API_URL } from '../config/config';

/**
 * Make authenticated API requests with JWT token
 * @param {string} endpoint - API endpoint (e.g., '/documents/tree')
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise<Response>} - Fetch response
 */
export const authFetch = async (endpoint, options = {}) => {
  // Get JWT token from localStorage
  const token = localStorage.getItem('token');
  
  if (!token) {
    throw new Error('No authentication token found. Please login again.');
  }

  // Prepare headers with Authorization
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
    ...options.headers
  };

  // Build full URL
  const url = endpoint.startsWith('http') ? endpoint : `${API_URL}${endpoint}`;

  // Make authenticated request
  const response = await fetch(url, {
    ...options,
    headers
  });

  // Handle 401 Unauthorized - redirect to login
  if (response.status === 401) {
    console.warn('Authentication failed. Redirecting to login...');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    window.location.href = '/auth';
    throw new Error('Authentication expired. Please login again.');
  }

  return response;
};

/**
 * Make authenticated API request and return JSON data
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise<any>} - Parsed JSON response
 */
export const authFetchJson = async (endpoint, options = {}) => {
  const response = await authFetch(endpoint, options);
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(errorData.message || errorData.error || `HTTP ${response.status}`);
  }
  
  return await response.json();
};

export default authFetch;
