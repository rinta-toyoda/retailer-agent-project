# AWS Full-Stack Deployment Guide

Complete guide for deploying both backend (ECS) and frontend (S3 + CloudFront) to AWS.

## Architecture Overview

```
User Request
    │
    ├─→ CloudFront CDN (Frontend)
    │   └─→ S3 Bucket (Static Next.js files)
    │
    └─→ Application Load Balancer (Backend API)
        └─→ ECS Fargate Tasks
            ├─→ RDS PostgreSQL
            ├─→ S3 (Product Images)
            └─→ Parameter Store (Secrets)
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured: `aws configure`
3. **Terraform** >= 1.0: `brew install terraform`
4. **Docker** for building images
5. **Node.js** >= 18 for frontend build

## Quick Deployment (< 20 minutes)

```bash
# 1. Configure variables
cd terraform
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars  # Edit with your values

# 2. Deploy infrastructure (backend + frontend)
./deploy.sh init
./deploy.sh apply    # ~10 minutes

# 3. Deploy backend application
./deploy.sh push-image  # ~3 minutes
./deploy.sh seed-db     # ~1 minute

# 4. Deploy frontend application
./deploy.sh deploy-frontend  # ~2 minutes

# 5. Get URLs
terraform output frontend_url  # https://xxxxx.cloudfront.net
terraform output api_url       # http://xxxxx.us-east-1.elb.amazonaws.com
```

**Total time: ~16 minutes** [OK]

## Detailed Steps

### 1. Configure Variables

Create `terraform.tfvars`:

```hcl
project_name = "retailer-agent"
environment  = "production"
aws_region   = "us-east-1"

# Generate secrets
db_password     = "your-secure-password-here"
jwt_secret_key  = "your-jwt-secret-32-chars-minimum"
openai_api_key  = "sk-proj-your-openai-key"

# Will be updated after deployment
cors_origins = ["*"]  # Update with CloudFront URL after deployment
```

**Generate secure secrets:**
```bash
# JWT secret (32+ characters)
openssl rand -base64 32

# Database password
openssl rand -base64 24
```

### 2. Deploy Infrastructure

```bash
cd terraform

# Initialize Terraform
./deploy.sh init

# Preview changes
./deploy.sh plan

# Deploy (creates ~15 AWS resources)
./deploy.sh apply
```

**Resources created:**
- [OK] VPC with public/private subnets
- [OK] RDS PostgreSQL database
- [OK] S3 bucket for product images
- [OK] S3 bucket for frontend static files
- [OK] CloudFront CDN distribution
- [OK] ECS Fargate cluster
- [OK] Application Load Balancer
- [OK] ECR container registry
- [OK] IAM roles and policies
- [OK] CloudWatch log groups

### 3. Deploy Backend

```bash
# Build and push Docker image to ECR
./deploy.sh push-image

# Seed database with product data
./deploy.sh seed-db
```

### 4. Deploy Frontend

```bash
# Build Next.js static site and upload to S3
./deploy.sh deploy-frontend
```

This command:
1. Builds Next.js with `NEXT_PUBLIC_API_URL` set to backend URL
2. Exports static files to `out/` directory
3. Uploads to S3 frontend bucket
4. Invalidates CloudFront cache
5. Returns frontend URL

### 5. Update CORS (Important!)

After deployment, update CORS to allow frontend:

```bash
# Get frontend URL
FRONTEND_URL=$(terraform output -raw frontend_url)

# Update terraform.tfvars
nano terraform.tfvars
# Change: cors_origins = ["https://xxxxx.cloudfront.net"]

# Re-apply to update backend
terraform apply -auto-approve
```

### 6. Verify Deployment

```bash
# Check infrastructure status
./deploy.sh status

# Test backend API
API_URL=$(terraform output -raw api_url)
curl $API_URL/health
curl $API_URL/products

# Test frontend
FRONTEND_URL=$(terraform output -raw frontend_url)
open $FRONTEND_URL
```

## Cost Breakdown (2-day deployment)

| Service | Cost/Hour | 48 Hours | Notes |
|---------|-----------|----------|-------|
| **Fargate Spot** | $0.0037 | $0.18 | 0.25 vCPU, 0.5GB |
| **RDS t3.micro** | $0.017 | $0.82 | Free tier available |
| **ALB** | $0.0225 | $1.08 | Application Load Balancer |
| **NAT Gateway** | $0.045 | $2.16 | Data transfer |
| **S3** | - | $0.02 | Storage + requests |
| **CloudFront** | - | $0.10 | CDN distribution |
| **Data Transfer** | - | $0.50 | Moderate usage |
| **TOTAL** | | **~$4.86** | For 2 days |

**Monthly equivalent**: ~$72/month

## Redeployment (Updates)

### Update Backend Code

```bash
# Make code changes
# ...

# Push new image
./deploy.sh push-image

# ECS automatically deploys new version
```

### Update Frontend Code

```bash
# Make code changes
# ...

# Rebuild and deploy
./deploy.sh deploy-frontend
```

### Update Infrastructure

```bash
# Modify .tf files
# ...

# Preview changes
./deploy.sh plan

# Apply changes
./deploy.sh apply
```

## Teardown (< 5 minutes)

```bash
cd terraform
./deploy.sh destroy  # Type 'destroy' to confirm
```

**Everything deleted:**
- [OK] All infrastructure
- [OK] Database (data lost!)
- [OK] S3 buckets (files lost!)
- [OK] ECS services
- [OK] Load balancers
- [OK] CloudFront distributions

## Troubleshooting

### Frontend not loading

```bash
# Check CloudFront distribution status
aws cloudfront list-distributions

# Check S3 bucket contents
aws s3 ls s3://$(terraform output -raw frontend_s3_bucket)/

# Redeploy frontend
./deploy.sh deploy-frontend
```

### Backend API not responding

```bash
# Check ECS service status
aws ecs describe-services \
    --cluster $(terraform output -raw ecs_cluster) \
    --services $(terraform output -raw ecs_service)

# Check CloudWatch logs
aws logs tail /ecs/retailer-agent-backend --follow

# Redeploy backend
./deploy.sh push-image
```

### CORS errors

```bash
# Update CORS in terraform.tfvars
cors_origins = ["https://xxxxx.cloudfront.net"]

# Apply changes
terraform apply -auto-approve

# Restart ECS service
aws ecs update-service \
    --cluster $(terraform output -raw ecs_cluster) \
    --service $(terraform output -raw ecs_service) \
    --force-new-deployment
```

### Database connection issues

```bash
# Check RDS status
aws rds describe-db-instances \
    --db-instance-identifier retailer-agent-db

# Check security group rules
aws ec2 describe-security-groups \
    --filters Name=tag:Name,Values=retailer-agent-rds-sg
```

## Monitoring

### CloudWatch Logs

```bash
# Backend logs
aws logs tail /ecs/retailer-agent-backend --follow

# CloudFront logs
aws logs tail /aws/cloudfront/retailer-agent-frontend --follow
```

### ECS Service Metrics

```bash
# Service status
./deploy.sh status

# Detailed ECS metrics
aws ecs describe-services \
    --cluster $(terraform output -raw ecs_cluster) \
    --services $(terraform output -raw ecs_service) \
    --query 'services[0].[runningCount,desiredCount,pendingCount]'
```

### Cost Monitoring

```bash
# Current month cost (requires billing access)
aws ce get-cost-and-usage \
    --time-period Start=2025-11-01,End=2025-11-02 \
    --granularity DAILY \
    --metrics BlendedCost \
    --group-by Type=SERVICE
```

## Security Considerations

### Secrets Management

- [OK] Secrets stored in AWS Parameter Store (encrypted)
- [OK] No secrets in Terraform state (references only)
- [OK] IAM roles with least privilege
- [OK] S3 buckets with private access (CloudFront OAI)

### Network Security

- [OK] Private subnets for database and ECS tasks
- [OK] Security groups with restricted access
- [OK] ALB in public subnet only
- [OK] CloudFront with HTTPS redirect

### Best Practices

1. **Rotate secrets regularly** (database password, JWT secret)
2. **Enable MFA** on AWS root account
3. **Monitor CloudWatch logs** for suspicious activity
4. **Use AWS WAF** for CloudFront (optional, adds cost)
5. **Enable S3 versioning** (already enabled)

## Advanced Configuration

### Custom Domain

Add Route53 and ACM certificate:

```hcl
# Add to terraform/frontend-cloudfront.tf
aliases = ["www.example.com"]

viewer_certificate {
  acm_certificate_arn = aws_acm_certificate.frontend.arn
  ssl_support_method  = "sni-only"
}
```

### Auto-scaling

Currently uses fixed 1 task. To enable auto-scaling:

```hcl
# Add to terraform/ecs.tf
resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.backend.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}
```

## Support

For issues:
1. Check CloudWatch logs first
2. Verify security groups and IAM roles
3. Run `./deploy.sh status` for infrastructure health
4. Check Terraform state: `terraform show`

## Summary

**Deployment time**: ~16 minutes
**Teardown time**: ~5 minutes
**2-day cost**: ~$5
**Monthly cost**: ~$72

**Benefits of AWS deployment:**
- [OK] Single platform (no Vercel)
- [OK] One-command teardown
- [OK] Professional infrastructure
- [OK] Global CDN (CloudFront)
- [OK] Auto-scaling capable
- [OK] Production-ready
