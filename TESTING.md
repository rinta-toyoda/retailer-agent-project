# Testing Guide

Comprehensive testing documentation for the Retailer AI Agent project.

## Quick Start

Run all tests with the unified command:
```bash
task test
```

**Current Status**: ✅ All tests passing (119 total tests)
- Backend: 51 tests passing (26 ProductRepository, 16 CartService, 5 Simple, 4 API)
- Frontend: 68 tests passing (43 Auth, 25 API Client)

## Table of Contents

- [Overview](#overview)
- [Backend Testing](#backend-testing)
  - [Setup](#backend-setup)
  - [Running Tests](#running-backend-tests)
  - [Test Structure](#backend-test-structure)
  - [Writing Tests](#writing-backend-tests)
- [Frontend Testing](#frontend-testing)
  - [Setup](#frontend-setup)
  - [Running Tests](#running-frontend-tests)
  - [Test Structure](#frontend-test-structure)
  - [Writing Tests](#writing-frontend-tests)
- [Test Coverage](#test-coverage)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Overview

This project uses:
- **Backend**: pytest with pytest-asyncio and pytest-cov for Python/FastAPI testing
- **Frontend**: Jest with React Testing Library for TypeScript/Next.js testing

### Test Types

| Type | Purpose | Location | Tools |
|------|---------|----------|-------|
| **Unit Tests** | Test individual functions, classes, methods | `backend/tests/unit/`, `frontend/src/__tests__/` | pytest, Jest |
| **Integration Tests** | Test API endpoints and component integration | `backend/tests/integration/` | pytest with TestClient |
| **Feature Tests** | Test complete user workflows | `backend/tests/integration/` | pytest with TestClient |

## Backend Testing

### Backend Setup

Testing dependencies are already included in `requirements.txt`:

```txt
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-cov==5.0.0
```

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Running Backend Tests

**Run all tests:**
```bash
cd backend
pytest
```

**Run with verbose output:**
```bash
pytest -v
```

**Run specific test file:**
```bash
pytest tests/unit/test_cart_service.py
```

**Run specific test class:**
```bash
pytest tests/unit/test_cart_service.py::TestCartService
```

**Run specific test:**
```bash
pytest tests/unit/test_cart_service.py::TestCartService::test_add_to_cart_new_cart
```

**Run with coverage:**
```bash
pytest --cov=app --cov-report=html
```

Coverage report will be in `htmlcov/index.html`.

**Run only unit tests:**
```bash
pytest tests/unit/
```

**Run only integration tests:**
```bash
pytest tests/integration/
```

**Run with markers:**
```bash
pytest -m "not slow"  # Skip slow tests
pytest -m "integration"  # Only integration tests
```

### Backend Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests for services/repositories
│   ├── __init__.py
│   ├── test_cart_service.py
│   ├── test_product_repository.py
│   └── test_checkout_service.py
└── integration/             # API endpoint tests
    ├── __init__.py
    ├── test_api_products.py
    ├── test_api_cart.py
    └── test_api_checkout.py
```

### Backend Fixtures

Available in `conftest.py`:

| Fixture | Description | Usage |
|---------|-------------|-------|
| `db_session` | Fresh SQLite in-memory database for each test | Auto-creates/drops tables |
| `client` | FastAPI TestClient with database override | For API endpoint testing |
| `test_user` | Regular user with credentials | username: testuser, password: testpass123 |
| `test_admin` | Admin user with superuser privileges | username: admin, password: admin123 |
| `test_product` | Single product with inventory (100 units) | SKU: TEST-001, price: $99.99 |
| `test_products` | List of 5 products with inventory | SKUs: TEST-001 through TEST-005 |
| `test_cart` | Cart with 2 items of test_product | cart_id: test-cart-001 |
| `auth_headers` | Authorization headers for test_user | {"Authorization": "Bearer <token>"} |
| `admin_headers` | Authorization headers for test_admin | {"Authorization": "Bearer <token>"} |

### Writing Backend Tests

**Example Unit Test:**

```python
# tests/unit/test_cart_service.py
from app.services.cart_service import CartService

class TestCartService:
    def test_add_to_cart_new_cart(self, db_session, test_user, test_product):
        """Test adding item to a new cart."""
        service = CartService(db_session)

        result = service.add_to_cart(
            cart_id="new-cart-001",
            product_id=test_product.id,
            quantity=3,
            customer_id=test_user.id
        )

        assert result["cart_id"] == "new-cart-001"
        assert result["item_count"] == 1
        assert result["total"] == test_product.price * 3
```

**Example Integration Test:**

```python
# tests/integration/test_api_products.py
class TestProductsAPI:
    def test_get_products(self, client, test_products):
        """Test GET /products endpoint."""
        response = client.get("/products")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5

    def test_get_product_by_id(self, client, test_product):
        """Test GET /products/{id} endpoint."""
        response = client.get(f"/products/{test_product.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name
```

**Testing with Authentication:**

```python
def test_protected_endpoint(self, client, auth_headers):
    """Test endpoint requiring authentication."""
    response = client.post(
        "/cart/add",
        json={"cart_id": "test", "product_id": 1, "quantity": 1, "customer_id": 1},
        headers=auth_headers
    )

    assert response.status_code == 200
```

### Backend Test Markers

Add markers to organize tests:

```python
import pytest

@pytest.mark.slow
def test_expensive_operation():
    """This test takes a long time."""
    pass

@pytest.mark.integration
def test_api_endpoint():
    """Integration test for API."""
    pass
```

Run with: `pytest -m "not slow"` or `pytest -m integration`

## Frontend Testing

### Frontend Setup

Install testing dependencies:

```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest jest-environment-jsdom @types/jest
```

Testing dependencies are defined in `package.json`:

```json
{
  "devDependencies": {
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/user-event": "^14.5.1",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "@types/jest": "^29.5.11"
  }
}
```

### Running Frontend Tests

**Run all tests:**
```bash
cd frontend
npm test
```

**Run in watch mode:**
```bash
npm run test:watch
```

**Run with coverage:**
```bash
npm run test:coverage
```

Coverage report will be in `coverage/` directory.

**Run specific test file:**
```bash
npm test auth.test.ts
```

**Update snapshots:**
```bash
npm test -- -u
```

### Frontend Test Structure

```
frontend/src/
├── lib/
│   └── __tests__/           # Test files for utilities
│       ├── auth.test.ts     # Authentication utility tests (43 tests)
│       └── api-client.test.ts # API client tests (25 tests)
├── components/              # Components to test
├── app/                     # Pages (tested via components)
└── __tests__/               # Additional test files (future)
```

### Frontend Configuration Files

**jest.config.js:**
```javascript
const nextJest = require('next/jest')

const createJestConfig = nextJest({
  dir: './',
})

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/__tests__/**',
  ],
}

module.exports = createJestConfig(customJestConfig)
```

**jest.setup.js:**
```javascript
import '@testing-library/jest-dom'

// Mock environment variables
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8100'

// Mock localStorage
global.localStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}

// Mock fetch
global.fetch = jest.fn()
```

### Writing Frontend Tests

**Example Utility Test:**

```typescript
// src/__tests__/auth.test.ts
import { getToken, setToken, isAuthenticated } from '../lib/auth'

describe('Authentication Utils', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('should store token in localStorage', () => {
    setToken('test-token')
    expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'test-token')
  })

  it('should retrieve token from localStorage', () => {
    (localStorage.getItem as jest.Mock).mockReturnValue('test-token')
    expect(getToken()).toBe('test-token')
  })

  it('should check if user is authenticated', () => {
    (localStorage.getItem as jest.Mock).mockReturnValue('test-token')
    expect(isAuthenticated()).toBe(true)
  })
})
```

**Example Component Test:**

```typescript
// src/__tests__/ProductCard.test.tsx
import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import ProductCard from '../components/ProductCard'

const mockProduct = {
  id: 1,
  name: 'Test Product',
  price: 99.99,
  brand: 'TestBrand',
  in_stock: true,
}

describe('ProductCard Component', () => {
  it('renders product information', () => {
    render(<ProductCard product={mockProduct} />)

    expect(screen.getByText('Test Product')).toBeInTheDocument()
    expect(screen.getByText('$99.99')).toBeInTheDocument()
  })

  it('calls onAddToCart when button clicked', () => {
    const mockAddToCart = jest.fn()
    render(<ProductCard product={mockProduct} onAddToCart={mockAddToCart} />)

    const button = screen.getByText(/add to cart/i)
    fireEvent.click(button)

    expect(mockAddToCart).toHaveBeenCalledWith(mockProduct)
  })

  it('disables button when out of stock', () => {
    const outOfStock = { ...mockProduct, in_stock: false }
    render(<ProductCard product={outOfStock} />)

    const button = screen.getByText(/add to cart/i)
    expect(button).toBeDisabled()
  })
})
```

**Testing User Interactions:**

```typescript
import userEvent from '@testing-library/user-event'

it('handles form submission', async () => {
  const user = userEvent.setup()
  render(<LoginForm />)

  await user.type(screen.getByLabelText('Username'), 'testuser')
  await user.type(screen.getByLabelText('Password'), 'password123')
  await user.click(screen.getByText('Login'))

  expect(screen.getByText('Welcome')).toBeInTheDocument()
})
```

**Testing Async Components:**

```typescript
it('loads and displays products', async () => {
  render(<ProductList />)

  expect(screen.getByText('Loading...')).toBeInTheDocument()

  const products = await screen.findByText('Test Product')
  expect(products).toBeInTheDocument()
})
```

## Test Coverage

### Backend Coverage Goals

- **Services**: 90%+ coverage
- **Repositories**: 85%+ coverage
- **API Endpoints**: 95%+ coverage
- **Domain Models**: 80%+ coverage

### Frontend Coverage Goals

- **Components**: 80%+ coverage
- **Utilities**: 90%+ coverage
- **Pages**: 70%+ coverage

### Viewing Coverage Reports

**Backend:**
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

**Frontend:**
```bash
cd frontend
npm run test:coverage
open coverage/lcov-report/index.html
```

### Coverage in CI/CD

Add to GitHub Actions workflow:

```yaml
- name: Run backend tests with coverage
  run: |
    cd backend
    pytest --cov=app --cov-report=xml

- name: Upload backend coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./backend/coverage.xml
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage
```

## Best Practices

### General Testing Principles

1. **AAA Pattern**: Arrange, Act, Assert
   ```python
   def test_example():
       # Arrange: Set up test data
       product = create_test_product()

       # Act: Execute the function
       result = service.process(product)

       # Assert: Verify the outcome
       assert result.success is True
   ```

2. **Test One Thing**: Each test should verify one behavior
3. **Descriptive Names**: Test names should describe what they verify
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Tests**: Keep unit tests fast (<100ms each)

### Backend Best Practices

- Use fixtures for common test data
- Test both success and failure cases
- Verify database state changes
- Mock external services (OpenAI, S3)
- Test edge cases (empty carts, out of stock, etc.)

### Frontend Best Practices

- Prefer user-centric queries (`getByRole`, `getByLabelText`)
- Test behavior, not implementation
- Mock API calls with realistic data
- Test accessibility (ARIA labels, keyboard navigation)
- Avoid testing internal state

### What to Test

**Do Test:**
- Business logic and algorithms
- API request/response handling
- User interactions (clicks, form submissions)
- Edge cases and error conditions
- Authentication and authorization
- Data validation

**Don't Test:**
- Third-party libraries
- Framework internals
- Trivial getters/setters
- Generated code

### Mocking Guidelines

**Backend:**
```python
from unittest.mock import Mock, patch

@patch('app.infra.llm_client.OpenAIChatLLMClient')
def test_with_mock_llm(mock_llm):
    mock_llm.return_value.recommend_products.return_value = [...]
    # Test code using mocked LLM
```

**Frontend:**
```typescript
global.fetch = jest.fn(() =>
  Promise.resolve({
    json: () => Promise.resolve({ data: 'mocked' }),
  })
) as jest.Mock
```

### Debugging Tests

**Backend:**
```bash
# Run with print statements
pytest -s

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l
```

**Frontend:**
```bash
# Debug specific test
npm test -- --testNamePattern="should render"

# No coverage (faster)
npm test -- --no-coverage

# Verbose output
npm test -- --verbose
```

## Common Issues and Solutions

### Backend Issues

**Issue**: `sqlalchemy.exc.InvalidRequestError: Table 'x' is already defined`
**Solution**: Ensure `Base.metadata.drop_all()` is called in fixture teardown

**Issue**: Tests pass individually but fail when run together
**Solution**: Clear database state between tests, use `scope="function"` for fixtures

**Issue**: Slow tests
**Solution**: Use in-memory SQLite, mock external services, parallelize with `pytest-xdist`

### Frontend Issues

**Issue**: `ReferenceError: localStorage is not defined`
**Solution**: Add mock in `jest.setup.js`

**Issue**: `Cannot find module '@/lib/auth'`
**Solution**: Check `moduleNameMapper` in `jest.config.js`

**Issue**: Async warnings
**Solution**: Use `await` with `findBy` queries, wrap in `act()` if needed

## Running Tests in Docker

**Backend:**
```bash
docker-compose exec backend pytest
```

**Frontend:**
```bash
docker-compose exec frontend npm test
```

**Both:**
```bash
docker-compose exec backend pytest && docker-compose exec frontend npm test
```

## Continuous Testing

**Backend watch mode** (requires pytest-watch):
```bash
pip install pytest-watch
cd backend
ptw
```

**Frontend watch mode:**
```bash
cd frontend
npm run test:watch
```

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Testing Library](https://testing-library.com/)
- [Jest Documentation](https://jestjs.io/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Next.js Testing](https://nextjs.org/docs/testing)

---

**Quick Commands Reference:**

```bash
# Backend
cd backend && pytest                    # Run all backend tests
cd backend && pytest -v --cov=app      # Verbose with coverage
cd backend && pytest tests/unit/       # Only unit tests

# Frontend
cd frontend && npm test                 # Run all frontend tests
cd frontend && npm run test:watch       # Watch mode
cd frontend && npm run test:coverage    # With coverage

# Docker
docker-compose exec backend pytest                  # Backend in Docker
docker-compose exec frontend npm test               # Frontend in Docker
```
