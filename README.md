# Retailer AI Agent System

A complete e-commerce platform demonstrating AI agent capabilities with natural language search, intelligent recommendations, and full checkout functionality.

## Prerequisites

### Required Software
- **Docker Desktop** (version 24.0+) with Docker Compose
- **Git** for cloning the repository
- **OpenAI API Key** - Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Task Command** - Get from [taskfile.dev](https://taskfile.dev/docs/installation)

## How to Run

**IMPORTANT**: This project uses Docker exclusively. Local development is not supported.

### Quick Start with Task Commands

1. **Install and start everything**
   ```bash
   # This command will:
   # - Build all Docker images
   # - Start all services (database, backend, frontend, localstack)
   # - Seed the database with sample products
   task install
   ```

2. **Add your OpenAI API key**
   ```bash
   # Edit .env file and add your OpenAI API key
   # OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
   ```
   
3. **Refresh environment variables**
   ```bash
   task up
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

## Project Overview

This system implements a **Retailer AI Agent** with:
- **AI Natural Language Search** - Conversational product search using OpenAI GPT-4
- **Intelligent Recommendations** - Personalized suggestions based on purchase history
- **Complete E-Commerce Flow** - Cart, checkout with payment simulation, order tracking
- **Admin Dashboard** - Inventory management with stock monitoring

## Technology Stack

| Component            | Technology                         |
|----------------------|------------------------------------|
| **Frontend**         | Next.js 14 + TypeScript + Tailwind |
| **Backend**          | FastAPI + Python 3.11              |
| **Database**         | PostgreSQL 15                      |
| **ORM**              | SQLAlchemy                         |
| **Storage**          | LocalStack S3 (AWS S3 compatible)  |
| **AI/LLM**           | OpenAI GPT-4                       |
| **Containerization** | Docker Compose                     |
| **Deployment**       | ECS                                |


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
- Stock reservation during checkout preparation
- Payment simulation with dummy Stripe integration
- Order creation and history tracking

### 4. Adding/Removing items from cart

### 5. Admin Inventory Management
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

### 4.1 Implementation of Stage 1 Requirements

**Fully Implemented Flows:**
- **Cart Management** - Add/Remove products, total calculation
- **Checkout** - Prepare (stock reservation) + Finalize (payment + order)
- **Recommendations** - AI-driven personalized suggestions
- **Search** - Keyword and natural language search
- **Admin Inventory** - Stock management with visual dashboard

**Database Models:**
- Product, Cart, CartItem, Order, OrderItem, InventoryItem, StockReservation, User

### 4.2 AI Agent Capabilities

**AgentService** (`app/services/agent_service.py`):
- Natural language understanding with intent parsing
- Confidence scoring and clarification logic
- Recommendation reasoning with preference extraction
- Transparent decision-making with reasoning logs

**LLM Integration** (`app/infra/llm_client.py`):
- OpenAI GPT-4 with function calling
- Database tool for dynamic product queries
- Fallback mechanism for reliability

## Testing

The project includes a comprehensive testing infrastructure:

**Run all tests:**
```bash
task test
```

**Available test commands:**
```bash
task test              # Run all tests (backend + frontend)
task test:backend      # Run backend tests only
task test:frontend     # Run frontend tests only
task test:coverage     # Run tests with coverage reports
```

## Deploying (Optional)
AWS Deployment Guide

Complete guide for deploying the Retailer AI Agent to AWS production infrastructure.

### Infrastructure Overview

The Terraform configuration deploys a production-ready AWS architecture:

```
Internet
   │
   ├─→ Application Load Balancer (Public Subnets)
   │        │
   │        └─→ ECS Fargate Tasks (Private Subnets)
   │                 │
   │                 ├─→ RDS PostgreSQL (Private Subnets)
   │                 ├─→ S3 Bucket (Product Images)
   │                 └─→ Parameter Store (Secrets)
   │
   └─→ Vercel Frontend
```

### Components

- **ECS Fargate**: Serverless containers with Spot instances (70% cost savings)
- **RDS PostgreSQL**: Free tier eligible t3.micro instance
- **Application Load Balancer**: HTTP/HTTPS traffic routing
- **S3**: Public bucket for product images
- **VPC**: Custom VPC with public/private subnets across 2 AZs
- **Parameter Store**: Secure storage for API keys and secrets

### Cost Estimate

| Service | Specification | Monthly Cost |
|---------|--------------|--------------|
| Fargate Spot | 0.25 vCPU, 0.5GB | ~$2.70 |
| RDS t3.micro | PostgreSQL 15 | FREE (Year 1), ~$15 (Year 2+) |
| ALB | Application Load Balancer | ~$16.20 |
| NAT Gateway | Single NAT | ~$32.85 |
| S3 | 1GB storage + requests | ~$0.12 |
| Data Transfer | Moderate usage | ~$5 |
| **TOTAL** | | **~$57/month** (Year 1) |

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate IAM permissions
2. **AWS CLI** installed and configured
3. **Terraform** >= 1.0 installed
4. **Docker** installed locally
5. **OpenAI API Key** from [platform.openai.com](https://platform.openai.com/api-keys)

### Install Required Tools

**macOS:**
```bash
# Install Terraform
brew install terraform

# Install AWS CLI
brew install awscli

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output (json)
```

**Linux:**
```bash
# Install Terraform
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt-get update && sudo apt-get install terraform

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

## Deployment Process

### Step 1: Configure Infrastructure Variables

```bash
cd terraform

# Copy the template
cp terraform.tfvars.example terraform.tfvars

# Generate secure secrets
echo "JWT Secret (copy this): $(openssl rand -base64 32)"
echo "DB Password (copy this): $(openssl rand -base64 24)"

# Edit the configuration file
nano terraform.tfvars
```

**Required Configuration:**

```hcl
# terraform.tfvars

# Database Configuration
db_password = "YOUR_GENERATED_DB_PASSWORD"  # Use the generated password above

# Security
jwt_secret_key = "YOUR_GENERATED_JWT_SECRET"  # Use the generated secret above

# OpenAI Configuration
openai_api_key = "sk-proj-YOUR_OPENAI_KEY"  # From platform.openai.com

# CORS Configuration (update after deploying frontend)
cors_origins = "http://localhost:3000"  # Will update with Vercel URL later

# Optional: Override defaults
# project_name = "retailer-syd"
# environment = "prod"
# aws_region = "ap-southeast-2"
```

### Step 2: Initialize Terraform

```bash
cd terraform

# Initialize Terraform backend and download providers
./deploy.sh init
```

**Expected Output:**
```
[OK] Initializing Terraform...
[OK] Terraform initialized
```

### Step 3: Review Infrastructure Plan

```bash
# Preview what will be created
./deploy.sh plan
```

Review the output. Should show approximately **45 resources** to be created:
- 1 VPC with 4 subnets (2 public, 2 private)
- 1 NAT Gateway and Internet Gateway
- 1 RDS PostgreSQL instance
- 1 S3 bucket with lifecycle policies
- 1 ECS cluster with Fargate service
- 1 Application Load Balancer with target groups
- IAM roles and security groups
- Parameter Store entries for secrets

### Step 4: Deploy Infrastructure

```bash
# Apply the infrastructure changes
./deploy.sh apply
```

When prompted `Do you want to perform these actions?`, type `yes` and press Enter.

**Deployment Time:** 15-20 minutes (RDS provisioning is the slowest)

**Expected Output:**
```
Apply complete! Resources: 45 added, 0 changed, 0 destroyed.

Outputs:
api_url = "http://retailer-agent-prod-alb-1234567890.us-east-1.elb.amazonaws.com"
database_endpoint = "postgresql://retailer:password@retailer-agent-prod-db.xxx.us-east-1.rds.amazonaws.com:5432/retailer_db"
ecr_repository = "123456789012.dkr.ecr.us-east-1.amazonaws.com/retailer-agent-prod-backend"
ecs_cluster = "retailer-agent-prod-cluster"
ecs_service = "retailer-agent-prod-service"
s3_bucket = "retailer-agent-prod-product-images"
vpc_id = "vpc-xxxxxxxxx"
```

**Save these outputs** - you'll need them for the next steps.

### Step 5: Build and Push Docker Image

```bash
cd terraform

# Use the deploy script (handles everything automatically)
./deploy.sh push-image
```

Or manually:

```bash
cd /path/to/project/root

# Login to AWS ECR
aws ecr get-login-password --region ap-southeast-2 | \
  docker login --username AWS --password-stdin $(terraform -chdir=terraform output -raw ecr_repository | cut -d'/' -f1)

# Build backend Docker image (with linux/amd64 platform)
docker build --platform linux/amd64 -t $(terraform -chdir=terraform output -raw ecr_repository):latest ./backend

# Push image to ECR
docker push $(terraform -chdir=terraform output -raw ecr_repository):latest
```

**Expected Output:**
```
Login Succeeded
[+] Building 45.3s
Successfully tagged 123456789012.dkr.ecr.us-east-1.amazonaws.com/retailer-agent-prod-backend:latest
Pushing image...
latest: digest: sha256:abc123... size: 2841
```

### Step 6: Deploy Backend to ECS

```bash
# Force ECS to pull and deploy the new image
aws ecs update-service \
  --cluster $(terraform -chdir=terraform output -raw ecs_cluster) \
  --service $(terraform -chdir=terraform output -raw ecs_service) \
  --force-new-deployment \
  --region us-east-1

# Monitor deployment status
aws ecs describe-services \
  --cluster $(terraform -chdir=terraform output -raw ecs_cluster) \
  --services $(terraform -chdir=terraform output -raw ecs_service) \
  --region us-east-1 \
  --query 'services[0].deployments[0].{status:status,running:runningCount,desired:desiredCount}'
```

**Wait 3-5 minutes** for the service to stabilize. Check status with:
```bash
./deploy.sh status
```

### Step 7: Seed Production Database

```bash
cd terraform

# Use the deploy script (runs seed in ECS task with network access to RDS)
./deploy.sh seed-db
```

The script will:
- Start a one-time ECS Fargate task
- Run the seed script inside AWS (has network access to private RDS)
- Wait for completion and report status

**Expected Output:**
```
[OK] Uploading product images to S3...
[OK] Creating database tables...
[OK] Seeding products (30 items)...
[OK] Creating admin user...
[OK] Database seeded successfully!
```

This will:
- Upload all product images from `assets/` to S3
- Create database schema
- Insert 30 sample products
- Create admin user (username: `admin`, password: `admin123`)

### Step 8: Verify Backend Deployment

```bash
# Get the API URL
export API_URL=$(terraform -chdir=terraform output -raw api_url)
echo "API URL: $API_URL"

# Test health endpoint
curl $API_URL/health

# Expected: {"status":"healthy"}

# Test login
curl -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Expected: {"access_token":"eyJ...","token_type":"bearer"}

# Save token for testing
export TOKEN=$(curl -s -X POST $API_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Test products endpoint
curl $API_URL/products -H "Authorization: Bearer $TOKEN"

# Expected: [{"id":1,"name":"CloudRunner Pro",...}, ...]

# Test recommendations
curl "$API_URL/recommendations?customer_id=1&limit=4"

# Expected: {"customer_id":1,"recommendations":[...]}
```

### Step 9: Deploy Frontend to S3 + CloudFront

```bash
cd terraform

# Deploy frontend (builds Next.js, uploads to S3, invalidates CloudFront cache)
./deploy.sh deploy-frontend
```

The script will:
- Build Next.js static site with API URL
- Export to static files
- Upload to S3 frontend bucket
- Invalidate CloudFront cache
- Return the CloudFront URL
