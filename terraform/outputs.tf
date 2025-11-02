# Terraform Outputs - All important values for deployment and access

# Region
output "aws_region" {
  description = "AWS Region"
  value       = var.aws_region
}

# Infrastructure
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = aws_subnet.private[*].id
}

# Database
output "database_endpoint" {
  description = "RDS endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.postgres.db_name
}

# Storage
output "s3_bucket" {
  description = "S3 bucket name for product images"
  value       = aws_s3_bucket.product_images.bucket
}

output "s3_bucket_public_url" {
  description = "S3 bucket public URL"
  value       = "https://${aws_s3_bucket.product_images.bucket}.s3.${var.aws_region}.amazonaws.com"
}

output "frontend_s3_bucket" {
  description = "S3 bucket name for frontend static files"
  value       = aws_s3_bucket.frontend.bucket
}

output "frontend_url" {
  description = "Frontend URL (CloudFront distribution)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID for cache invalidation"
  value       = aws_cloudfront_distribution.frontend.id
}

# Container Registry
output "ecr_repository" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

# Load Balancer
output "load_balancer_dns" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "api_url" {
  description = "Backend API URL (use this for frontend NEXT_PUBLIC_API_URL)"
  value       = "http://${aws_lb.main.dns_name}"
}

# ECS
output "ecs_cluster" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service" {
  description = "ECS service name"
  value       = aws_ecs_service.backend.name
}

# Parameter Store Paths
output "ssm_parameters" {
  description = "AWS Systems Manager Parameter Store paths"
  value = {
    database_url   = aws_ssm_parameter.database_url.name
    jwt_secret     = aws_ssm_parameter.jwt_secret.name
    openai_api_key = aws_ssm_parameter.openai_api_key.name
    s3_bucket_name = aws_ssm_parameter.s3_bucket_name.name
    cors_origins   = aws_ssm_parameter.cors_origins.name
    aws_region     = aws_ssm_parameter.aws_region.name
  }
}

# Cost Estimation
output "cost_estimate_monthly" {
  description = "Estimated monthly cost breakdown (USD)"
  value = {
    fargate_spot = "$2.70 (0.25 vCPU, 0.5GB RAM, 24/7)"
    rds_t3_micro = "$15.00 after free tier (first year free)"
    s3           = "$0.12 (1GB storage + 10k requests)"
    alb          = "$16.20 (730 hours + LCU charges)"
    nat_gateway  = "$32.85 (730 hours + data transfer)"
    total_year_1 = "$51 (with RDS free tier)"
    total_year_2 = "$66 (without RDS free tier)"
  }
}

# Next Steps
output "deployment_instructions" {
  description = "Quick deployment guide"
  value = <<-EOT

     Infrastructure deployed successfully!

     Next Steps:

    1. Build and push Docker image:
       aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${aws_ecr_repository.backend.repository_url}
       docker build -t ${aws_ecr_repository.backend.repository_url}:latest ./backend
       docker push ${aws_ecr_repository.backend.repository_url}:latest

    2. Update ECS service to use new image:
       aws ecs update-service --cluster ${aws_ecs_cluster.main.name} --service ${aws_ecs_service.backend.name} --force-new-deployment --region ${var.aws_region}

    3. Seed production database from local machine:
       export DATABASE_URL="${aws_db_instance.postgres.endpoint}"
       export S3_BUCKET_NAME="${aws_s3_bucket.product_images.bucket}"
       export AWS_REGION="${var.aws_region}"
       python -m backend.app.tools.seed_db --production

    4. Deploy frontend to S3:
       cd frontend && npm run build && npm run export
       aws s3 sync out/ s3://${aws_s3_bucket.frontend.bucket}/ --delete
       aws cloudfront create-invalidation --distribution-id ${aws_cloudfront_distribution.frontend.id} --paths "/*"

    5. Access your application:
       Frontend: https://${aws_cloudfront_distribution.frontend.domain_name}
       API:
       http://${aws_lb.main.dns_name}/health
       http://${aws_lb.main.dns_name}/products

     Monitor:
       - CloudWatch Logs: /ecs/${local.name_prefix}
       - ECS Console: ${aws_ecs_cluster.main.name}
       - RDS Console: ${aws_db_instance.postgres.identifier}

  EOT
}
