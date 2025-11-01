#!/bin/bash
# Quick Deployment Script for Retailer AI Agent Infrastructure
# Usage: ./deploy.sh [init|plan|apply|destroy|status]

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TERRAFORM_DIR="$PROJECT_ROOT/terraform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd "$TERRAFORM_DIR"

# Check if terraform.tfvars exists
check_tfvars() {
    if [ ! -f "terraform.tfvars" ]; then
        echo -e "${RED}terraform.tfvars not found${NC}"
        echo ""
        echo "Please create terraform.tfvars from the example:"
        echo -e "${BLUE}  cp terraform.tfvars.example terraform.tfvars${NC}"
        echo -e "${BLUE}  nano terraform.tfvars${NC}"
        echo ""
        echo "Required variables:"
        echo "  - db_password"
        echo "  - jwt_secret_key"
        echo "  - openai_api_key"
        echo "  - cors_origins"
        exit 1
    fi
}

# Initialize Terraform
init_terraform() {
    echo -e "${BLUE} Initializing Terraform...${NC}"
    terraform init
    echo -e "${GREEN} Terraform initialized${NC}"
}

# Plan infrastructure changes
plan_terraform() {
    check_tfvars
    echo -e "${BLUE} Planning infrastructure changes...${NC}"
    terraform plan
}

# Apply infrastructure
apply_terraform() {
    check_tfvars
    echo -e "${YELLOW}This will create AWS resources that may incur costs${NC}"
    echo "Estimated monthly cost: ~$57 (Year 1), ~$72 (Year 2+)"
    echo ""
    read -p "Continue? (yes/no): " -r
    if [ "$REPLY" != "yes" ]; then
        echo "Deployment cancelled"
        exit 0
    fi

    echo -e "${BLUE} Deploying infrastructure...${NC}"
    terraform apply

    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN} Infrastructure deployed successfully!${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Build and push Docker image:"
        echo -e "${BLUE}   ./deploy.sh push-image${NC}"
        echo ""
        echo "2. Seed production database:"
        echo -e "${BLUE}   ./deploy.sh seed-db${NC}"
        echo ""
        echo "3. Deploy frontend to Vercel with API URL:"
        terraform output -raw api_url
        echo ""
    fi
}

# Destroy infrastructure
destroy_terraform() {
    echo -e "${RED}WARNING: This will destroy all infrastructure!${NC}"
    echo "This includes:"
    echo "  - RDS database (all data will be lost)"
    echo "  - S3 bucket with images"
    echo "  - ECS cluster and services"
    echo "  - All networking resources"
    echo ""
    read -p "Are you ABSOLUTELY SURE? Type 'destroy' to confirm: " -r
    if [ "$REPLY" != "destroy" ]; then
        echo "Destruction cancelled"
        exit 0
    fi

    echo -e "${RED}Destroying infrastructure...${NC}"
    terraform destroy
}

# Show current status
show_status() {
    echo -e "${BLUE} Infrastructure Status${NC}"
    echo ""

    if [ ! -f "terraform.tfstate" ]; then
        echo "No infrastructure deployed yet"
        exit 0
    fi

    echo "Key Outputs:"
    echo ""

    if terraform output api_url &> /dev/null; then
        echo -e "${GREEN}API URL:${NC}"
        terraform output -raw api_url
        echo ""
    fi

    if terraform output ecr_repository &> /dev/null; then
        echo -e "${GREEN}ECR Repository:${NC}"
        terraform output -raw ecr_repository
        echo ""
    fi

    if terraform output database_endpoint &> /dev/null; then
        echo -e "${GREEN}Database Endpoint:${NC}"
        terraform output -raw database_endpoint
        echo ""
    fi

    if terraform output s3_bucket &> /dev/null; then
        echo -e "${GREEN}S3 Bucket:${NC}"
        terraform output -raw s3_bucket
        echo ""
    fi

    echo ""
    echo "ECS Service Status:"
    if terraform output ecs_cluster &> /dev/null; then
        CLUSTER=$(terraform output -raw ecs_cluster)
        SERVICE=$(terraform output -raw ecs_service)
        aws ecs describe-services \
            --cluster "$CLUSTER" \
            --services "$SERVICE" \
            --query 'services[0].[desiredCount,runningCount,status]' \
            --output table 2>/dev/null || echo "Unable to fetch ECS status"
    fi
}

# Build and push Docker image
push_image() {
    echo -e "${BLUE} Building and pushing Docker image...${NC}"

    if [ ! -f "terraform.tfstate" ]; then
        echo -e "${RED} Infrastructure not deployed yet${NC}"
        echo "Run: ./deploy.sh apply"
        exit 1
    fi

    ECR_REPO=$(terraform output -raw ecr_repository)
    REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
    REGISTRY=$(echo "$ECR_REPO" | cut -d'/' -f1)

    echo "Logging into ECR..."
    aws ecr get-login-password --region "$REGION" | \
        docker login --username AWS --password-stdin "$REGISTRY"

    echo "Building image..."
    cd "$PROJECT_ROOT"
    docker build -t "$ECR_REPO:latest" ./backend

    echo "Pushing image..."
    docker push "$ECR_REPO:latest"

    echo -e "${GREEN} Image pushed successfully${NC}"
    echo ""
    echo "Updating ECS service..."
    CLUSTER=$(terraform -chdir=terraform output -raw ecs_cluster)
    SERVICE=$(terraform -chdir=terraform output -raw ecs_service)
    aws ecs update-service \
        --cluster "$CLUSTER" \
        --service "$SERVICE" \
        --force-new-deployment \
        --region "$REGION"

    echo -e "${GREEN} ECS service updated${NC}"
}

# Seed production database
seed_db() {
    echo -e "${BLUE} Seeding production database...${NC}"

    if [ ! -f "terraform.tfstate" ]; then
        echo -e "${RED} Infrastructure not deployed yet${NC}"
        exit 1
    fi

    DB_ENDPOINT=$(terraform output -raw database_endpoint)
    S3_BUCKET=$(terraform output -raw s3_bucket)
    REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")

    echo "Using:"
    echo "  Database: $DB_ENDPOINT"
    echo "  S3 Bucket: $S3_BUCKET"
    echo "  Region: $REGION"
    echo ""

    cd "$PROJECT_ROOT"
    export DATABASE_URL="$DB_ENDPOINT"
    export S3_BUCKET_NAME="$S3_BUCKET"
    export AWS_REGION="$REGION"
    unset S3_ENDPOINT_URL

    python -m backend.app.tools.seed_db --production

    echo -e "${GREEN} Database seeded${NC}"
}

# Main command router
case "${1:-help}" in
    init)
        init_terraform
        ;;
    plan)
        plan_terraform
        ;;
    apply)
        apply_terraform
        ;;
    destroy)
        destroy_terraform
        ;;
    status)
        show_status
        ;;
    push-image)
        push_image
        ;;
    seed-db)
        seed_db
        ;;
    help|*)
        echo "Retailer AI Agent - Deployment Script"
        echo ""
        echo "Usage: ./deploy.sh [command]"
        echo ""
        echo "Commands:"
        echo "  init        - Initialize Terraform"
        echo "  plan        - Preview infrastructure changes"
        echo "  apply       - Deploy infrastructure to AWS"
        echo "  destroy     - Destroy all infrastructure"
        echo "  status      - Show current infrastructure status"
        echo "  push-image  - Build and push Docker image to ECR"
        echo "  seed-db     - Seed production database"
        echo "  help        - Show this help message"
        echo ""
        echo "Quick Start:"
        echo "  1. cp terraform.tfvars.example terraform.tfvars"
        echo "  2. Edit terraform.tfvars with your values"
        echo "  3. ./deploy.sh init"
        echo "  4. ./deploy.sh apply"
        echo "  5. ./deploy.sh push-image"
        echo "  6. ./deploy.sh seed-db"
        ;;
esac
