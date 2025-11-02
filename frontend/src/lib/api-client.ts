import createClient from 'openapi-fetch';
import type { paths } from './api-types';
import { getToken } from './auth';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8100';

export const apiClient = createClient<paths>({
  baseUrl: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add auth token interceptor
apiClient.use({
  onRequest({ request }) {
    const token = getToken();
    if (token) {
      request.headers.set('Authorization', `Bearer ${token}`);
    }
    return request;
  },
  onResponse({ response }) {
    // Redirect to login on 401 Unauthorized
    if (response.status === 401) {
      if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return response;
  }
});

export const CART_ID = 'demo-cart-001';
export const CUSTOMER_ID = 1;

export default apiClient;
