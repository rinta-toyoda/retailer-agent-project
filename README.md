# Retailer AI Agent System

A complete e-commerce platform demonstrating AI agent capabilities with natural language search, intelligent recommendations, and full checkout functionality.

## Prerequisites

### Required Software
- **Docker Desktop** (version 24.0+) with Docker Compose
- **Git** for cloning the repository
- **OpenAI API Key** - Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## How to Run

**IMPORTANT**: This project uses Docker exclusively. Local development is not supported.

### Quick Start with Task Commands

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Agent
   ```

2. **Add your OpenAI API key**
   ```bash
   # Edit .env file and add your OpenAI API key
   # OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
   ```

3. **Install and start everything**
   ```bash
   # This command will:
   # - Build all Docker images
   # - Start all services (database, backend, frontend, localstack)
   # - Seed the database with sample products
   task install
   ```

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8100
   - **API Documentation**: http://localhost:8100/docs

### Other Task Commands

```bash
# Reset database with fresh data
task reset

# Stop services and clean up
task destroy

# Start services (after install)
task up
```

## Team Contributions

| SID | Percentage | Contributions |
|-----|------------|---------------|
| 123456789 | 20% | Frontend development: Product pages, cart UI, checkout flow. React components and Next.js routing. |
| 234567890 | 20% | Backend API: Cart service, checkout flow, payment integration. FastAPI endpoints and business logic. |
| 345678901 | 20% | AI Agent implementation: Natural language search, recommendation engine. OpenAI integration and reasoning. |
| 456789012 | 20% | Database design and repository layer: Models, migrations, data access patterns. PostgreSQL schema. |
| 567890123 | 20% | Infrastructure and deployment: Docker setup, CI/CD, S3 integration. DevOps and system architecture. |

## Project Overview

This system implements a **Retailer AI Agent** with:
- **AI Natural Language Search** - Conversational product search using OpenAI GPT-4
- **Intelligent Recommendations** - Personalized suggestions based on purchase history
- **Complete E-Commerce Flow** - Cart, checkout with payment simulation, order tracking
- **Admin Dashboard** - Inventory management with stock monitoring

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Next.js 14 + TypeScript |
| **Backend** | FastAPI + Python 3.11 |
| **Database** | PostgreSQL 15 |
| **ORM** | SQLAlchemy |
| **Storage** | LocalStack S3 (AWS S3 compatible) |
| **AI/LLM** | OpenAI GPT-4 |
| **Containerization** | Docker Compose |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND (Next.js/TS)                      │
│  ┌────────┐  ┌──────┐  ┌─────────┐  ┌───────┐  ┌───────┐ │
│  │ Home   │  │ Cart │  │Checkout │  │ Admin │  │ Login │ │
│  │ Page   │  │ Page │  │  Page   │  │ Page  │  │ Page  │ │
│  └────────┘  └──────┘  └─────────┘  └───────┘  └───────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST + JWT Auth
┌─────────────────────────┼───────────────────────────────────┐
│                BACKEND API (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Controllers: Cart │ Checkout │ Search │ Admin       │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Services: CartService │ CheckoutService │ AgentService│  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Repositories: Product │ Cart │ Order │ Inventory    │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Infrastructure: Database │ S3 │ OpenAI │ JWT Auth   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│          DATABASE (PostgreSQL)                              │
│  products │ carts │ orders │ inventory_items │ users       │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### 1. AI Natural Language Search
- Parse conversational queries: "find breathable red running shoes"
- Extract intent and attributes using OpenAI
- Return top 3 matching products with relevance scores
- Confidence-based clarification requests

### 2. Intelligent Recommendations
- Analyze customer purchase history
- Extract user preferences (categories, brands, colors)
- Generate 4 personalized product recommendations
- Fallback to popular products for new customers

### 3. Complete Checkout Flow
- Add/remove items from cart
- Stock reservation during checkout preparation
- Payment simulation with dummy Stripe integration
- Order creation and history tracking

### 4. Admin Inventory Management
- View all products with images and descriptions
- Set absolute stock quantities
- Low stock monitoring with visual alerts
- Real-time inventory statistics

## API Endpoints

### Cart Management
- `POST /cart/add` - Add product to cart
- `POST /cart/remove` - Remove product from cart
- `GET /cart/{cart_id}` - Get cart details

### Checkout
- `POST /checkout/prepare` - Create checkout session with stock reservation
- `POST /checkout/finalize` - Complete payment and create order

### Search
- `GET /search?q={query}` - Keyword search
- `GET /search/nl?q={query}` - AI natural language search

### Recommendations
- `GET /recommendations?customer_id={id}&limit=4` - Get AI recommendations

### Admin
- `POST /admin/stock/set` - Set absolute stock quantity
- `GET /admin/inventory` - View all inventory

### Products
- `GET /products?limit={n}` - List products
- `GET /products/{id}` - Get product details

## Project Structure

```
Agent/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── controllers/       # API request handlers
│   │   ├── services/          # Business logic
│   │   ├── repositories/      # Data access layer
│   │   ├── domain/            # Domain models
│   │   ├── infra/             # Infrastructure (DB, S3, OpenAI)
│   │   ├── schemas/           # Request/response schemas
│   │   ├── tools/             # AI agent tools
│   │   └── main.py            # FastAPI application
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # Next.js TypeScript frontend
│   ├── src/
│   │   ├── app/               # Pages (App Router)
│   │   ├── components/        # React components
│   │   ├── lib/               # API client and utilities
│   │   └── types/             # TypeScript definitions
│   ├── package.json
│   └── Dockerfile
├── assets/                     # Product images for seeding
├── docker-compose.yml          # Service orchestration
├── Taskfile.yml                # Task automation
└── .env.example                # Environment template
```

## Marking Criteria Alignment

### 4.1 Implementation of Stage 1 Requirements (8 Marks)

**Fully Implemented Flows:**
- **Cart Management** - Add/Remove products, total calculation
- **Checkout** - Prepare (stock reservation) + Finalize (payment + order)
- **Recommendations** - AI-driven personalized suggestions
- **Search** - Keyword and natural language search
- **Admin Inventory** - Stock management with visual dashboard

**Database Models:**
- Product, Cart, CartItem, Order, OrderItem, InventoryItem, StockReservation, User

### 4.2 AI Agent Capabilities (5 Marks)

**AgentService** (`app/services/agent_service.py`):
- Natural language understanding with intent parsing
- Confidence scoring and clarification logic
- Recommendation reasoning with preference extraction
- Transparent decision-making with reasoning logs

**LLM Integration** (`app/infra/llm_client.py`):
- OpenAI GPT-4 with function calling
- Database tool for dynamic product queries
- Fallback mechanism for reliability

### 4.3 Agile Development (6 Marks)

See `AGILE_NOTES.md` for:
- Sprint structure and planning
- User stories with acceptance criteria
- Team roles and retrospectives

### 4.4 Advanced Technologies (6 Marks)

- Next.js 14 with App Router and TypeScript
- FastAPI with async operations
- Docker Compose for containerization
- OpenAI GPT-4 for natural language processing
- LocalStack S3 for image storage
- JWT authentication with protected routes
- Clean architecture with repository pattern

## Testing

The project includes a comprehensive testing infrastructure:

**Run all tests:**
```bash
task test
```

**Current test status:** ✅ All 5 backend unit tests passing

**Test infrastructure includes:**
- Backend: pytest with FastAPI TestClient for API testing
- Frontend: Jest configured for TypeScript/Next.js components
- Fixtures for database, users, products, and authentication
- Coverage reporting capabilities

See `TESTING.md` for detailed testing documentation.

**Available test commands:**
```bash
task test              # Run all tests (backend + frontend)
task test:backend      # Run backend tests only
task test:frontend     # Run frontend tests only
task test:coverage     # Run tests with coverage reports
```
