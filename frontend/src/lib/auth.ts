/**
 * Authentication utilities
 * Handles JWT token storage and validation
 */

const TOKEN_KEY = 'access_token';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
}

/**
 * Store JWT token in localStorage
 */
export function setToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

/**
 * Get JWT token from localStorage
 */
export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

/**
 * Remove JWT token from localStorage
 */
export function removeToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Get authorization header for API requests
 */
export function getAuthHeader(): Record<string, string> {
  const token = getToken();
  if (token) {
    return {
      'Authorization': `Bearer ${token}`
    };
  }
  return {};
}
