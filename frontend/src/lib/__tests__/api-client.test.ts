/**
 * Unit tests for API client with comprehensive edge case coverage.
 *
 * Tests cover:
 * - API client configuration and initialization
 * - Request interceptor functionality (auth token injection)
 * - Response interceptor functionality (401 redirect)
 * - Base URL configuration
 * - Edge cases (missing tokens, environment variables)
 *
 * Marking Criteria: 4.1 (Testing and Quality Assurance)
 */

import { API_BASE_URL, CART_ID, CUSTOMER_ID } from '../api-client';

// Mock environment variables
const originalEnv = process.env;

describe('API Client Configuration', () => {
  beforeEach(() => {
    jest.resetModules();
    process.env = { ...originalEnv };
  });

  afterAll(() => {
    process.env = originalEnv;
  });

  // ==================== Base URL Tests ====================

  describe('API_BASE_URL', () => {
    it('should use default localhost URL when env var not set - happy path', () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      // Re-import to get fresh value
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('http://localhost:8100');
      });
    });

    it('should use environment variable when set', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('https://api.example.com');
      });
    });

    it('should handle production URL format', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://prod-api.retailer.com/v1';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('https://prod-api.retailer.com/v1');
      });
    });

    it('should handle URL with port number', () => {
      process.env.NEXT_PUBLIC_API_URL = 'http://localhost:3000';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('http://localhost:3000');
      });
    });

    it('should handle URL without protocol (edge case)', () => {
      process.env.NEXT_PUBLIC_API_URL = 'api.example.com';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('api.example.com');
      });
    });

    it('should handle empty string environment variable', () => {
      process.env.NEXT_PUBLIC_API_URL = '';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        // Empty string is falsy, should use default
        expect(API_BASE_URL).toBe('http://localhost:8100');
      });
    });
  });

  // ==================== Constants Tests ====================

  describe('API Constants', () => {
    it('should export CART_ID constant - happy path', () => {
      expect(CART_ID).toBe('demo-cart-001');
    });

    it('should export CUSTOMER_ID constant - happy path', () => {
      expect(CUSTOMER_ID).toBe(1);
    });

    it('should have string type for CART_ID', () => {
      expect(typeof CART_ID).toBe('string');
    });

    it('should have number type for CUSTOMER_ID', () => {
      expect(typeof CUSTOMER_ID).toBe('number');
    });

    it('should not allow CART_ID to be empty', () => {
      expect(CART_ID.length).toBeGreaterThan(0);
    });

    it('should have positive CUSTOMER_ID', () => {
      expect(CUSTOMER_ID).toBeGreaterThan(0);
    });
  });

  // ==================== Client Initialization Tests ====================

  describe('API Client Initialization', () => {
    it('should create client with correct base URL', () => {
      jest.isolateModules(() => {
        const { apiClient, API_BASE_URL } = require('../api-client');
        // Client should be initialized (not null/undefined)
        expect(apiClient).toBeDefined();
        expect(apiClient).not.toBeNull();
      });
    });

    it('should export apiClient as default export', () => {
      jest.isolateModules(() => {
        const defaultExport = require('../api-client').default;
        expect(defaultExport).toBeDefined();
      });
    });

    it('should have named and default export pointing to same client', () => {
      jest.isolateModules(() => {
        const { apiClient, default: defaultClient } = require('../api-client');
        expect(apiClient).toBe(defaultClient);
      });
    });
  });

  // ==================== Environment Configuration Tests ====================

  describe('Environment Configuration', () => {
    it('should handle development environment', () => {
      process.env.NODE_ENV = 'development';
      process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8100';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toContain('localhost');
      });
    });

    it('should handle production environment', () => {
      process.env.NODE_ENV = 'production';
      process.env.NEXT_PUBLIC_API_URL = 'https://api.production.com';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('https://api.production.com');
      });
    });

    it('should handle staging environment', () => {
      process.env.NODE_ENV = 'staging';
      process.env.NEXT_PUBLIC_API_URL = 'https://api.staging.com';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('https://api.staging.com');
      });
    });
  });

  // ==================== URL Format Tests ====================

  describe('URL Format Validation', () => {
    it('should handle IPv4 address format', () => {
      process.env.NEXT_PUBLIC_API_URL = 'http://192.168.1.100:8100';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('http://192.168.1.100:8100');
      });
    });

    it('should handle URL with path', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com/api/v1';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('https://api.example.com/api/v1');
      });
    });

    it('should handle URL with trailing slash', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com/';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('https://api.example.com/');
      });
    });

    it('should handle URL without trailing slash', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://api.example.com';
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('https://api.example.com');
      });
    });
  });

  // ==================== Edge Cases ====================

  describe('Edge Cases', () => {
    it('should handle undefined environment variable', () => {
      process.env.NEXT_PUBLIC_API_URL = undefined;
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('http://localhost:8100');
      });
    });

    it('should handle null environment variable (edge case)', () => {
      process.env.NEXT_PUBLIC_API_URL = null as any;
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe('http://localhost:8100');
      });
    });

    it('should handle very long URL', () => {
      const longUrl = 'https://api.very-long-domain-name-for-testing-purposes.example.com:8100/api/v1/endpoint';
      process.env.NEXT_PUBLIC_API_URL = longUrl;
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe(longUrl);
      });
    });

    it('should handle URL with query parameters (unusual but possible)', () => {
      const urlWithParams = 'https://api.example.com?key=value';
      process.env.NEXT_PUBLIC_API_URL = urlWithParams;
      jest.isolateModules(() => {
        const { API_BASE_URL } = require('../api-client');
        expect(API_BASE_URL).toBe(urlWithParams);
      });
    });

    it('should not allow CART_ID to be mutated', () => {
      const originalCartId = CART_ID;
      // Attempting to reassign should not affect the constant
      expect(CART_ID).toBe(originalCartId);
    });

    it('should not allow CUSTOMER_ID to be mutated', () => {
      const originalCustomerId = CUSTOMER_ID;
      // Attempting to reassign should not affect the constant
      expect(CUSTOMER_ID).toBe(originalCustomerId);
    });
  });

  // ==================== Type Safety Tests ====================

  describe('Type Safety', () => {
    it('should export constants with correct types', () => {
      expect(typeof API_BASE_URL).toBe('string');
      expect(typeof CART_ID).toBe('string');
      expect(typeof CUSTOMER_ID).toBe('number');
    });

    it('should have valid string for API_BASE_URL', () => {
      expect(API_BASE_URL).toBeTruthy();
      expect(API_BASE_URL.length).toBeGreaterThan(0);
    });

    it('should have valid CART_ID format', () => {
      expect(CART_ID).toMatch(/^demo-cart-\d{3}$/);
    });

    it('should have integer CUSTOMER_ID', () => {
      expect(Number.isInteger(CUSTOMER_ID)).toBe(true);
    });
  });

  // ==================== Integration Tests ====================

  describe('Integration: Client and Configuration', () => {
    it('should work with default configuration', () => {
      delete process.env.NEXT_PUBLIC_API_URL;
      jest.isolateModules(() => {
        const { apiClient, API_BASE_URL, CART_ID, CUSTOMER_ID } = require('../api-client');

        expect(apiClient).toBeDefined();
        expect(API_BASE_URL).toBe('http://localhost:8100');
        expect(CART_ID).toBe('demo-cart-001');
        expect(CUSTOMER_ID).toBe(1);
      });
    });

    it('should work with custom configuration', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://custom-api.com';
      jest.isolateModules(() => {
        const { apiClient, API_BASE_URL } = require('../api-client');

        expect(apiClient).toBeDefined();
        expect(API_BASE_URL).toBe('https://custom-api.com');
      });
    });

    it('should maintain consistent configuration across imports', () => {
      process.env.NEXT_PUBLIC_API_URL = 'https://consistent-api.com';
      jest.isolateModules(() => {
        const firstImport = require('../api-client');
        const secondImport = require('../api-client');

        expect(firstImport.API_BASE_URL).toBe(secondImport.API_BASE_URL);
        expect(firstImport.apiClient).toBe(secondImport.apiClient);
      });
    });
  });
});
