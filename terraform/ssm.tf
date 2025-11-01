# AWS Systems Manager Parameter Store
# Storing sensitive configuration (not Secrets Manager for cost savings)

# Database connection string
resource "aws_ssm_parameter" "database_url" {
  name        = "/${var.project_name}/${var.environment}/database-url"
  description = "PostgreSQL connection string"
  type        = "SecureString"
  value       = "postgresql://${var.db_username}:${var.db_password}@${aws_db_instance.postgres.endpoint}/${aws_db_instance.postgres.db_name}"

  tags = {
    Name = "${local.name_prefix}-database-url"
  }
}

# JWT Secret Key
resource "aws_ssm_parameter" "jwt_secret" {
  name        = "/${var.project_name}/${var.environment}/jwt-secret-key"
  description = "JWT secret key for authentication"
  type        = "SecureString"
  value       = var.jwt_secret_key

  tags = {
    Name = "${local.name_prefix}-jwt-secret"
  }
}

# OpenAI API Key
resource "aws_ssm_parameter" "openai_api_key" {
  name        = "/${var.project_name}/${var.environment}/openai-api-key"
  description = "OpenAI API key for LLM features"
  type        = "SecureString"
  value       = var.openai_api_key

  tags = {
    Name = "${local.name_prefix}-openai-key"
  }
}

# S3 Bucket Name
resource "aws_ssm_parameter" "s3_bucket_name" {
  name        = "/${var.project_name}/${var.environment}/s3-bucket-name"
  description = "S3 bucket name for product images"
  type        = "String"
  value       = aws_s3_bucket.product_images.bucket

  tags = {
    Name = "${local.name_prefix}-s3-bucket"
  }
}

# CORS Origins
resource "aws_ssm_parameter" "cors_origins" {
  name        = "/${var.project_name}/${var.environment}/cors-origins"
  description = "Allowed CORS origins"
  type        = "String"
  value       = var.cors_origins

  tags = {
    Name = "${local.name_prefix}-cors-origins"
  }
}

# AWS Region
resource "aws_ssm_parameter" "aws_region" {
  name        = "/${var.project_name}/${var.environment}/aws-region"
  description = "AWS region"
  type        = "String"
  value       = var.aws_region

  tags = {
    Name = "${local.name_prefix}-aws-region"
  }
}

# Output parameter names for reference
output "parameter_store_paths" {
  description = "Parameter Store paths for application configuration"
  value = {
    database_url     = aws_ssm_parameter.database_url.name
    jwt_secret       = aws_ssm_parameter.jwt_secret.name
    openai_api_key   = aws_ssm_parameter.openai_api_key.name
    s3_bucket_name   = aws_ssm_parameter.s3_bucket_name.name
    cors_origins     = aws_ssm_parameter.cors_origins.name
    aws_region       = aws_ssm_parameter.aws_region.name
  }
}
