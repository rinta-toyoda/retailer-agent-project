# Terraform Variables for Retailer AI Agent Infrastructure

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "retailer-agent"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "retailer"
  sensitive   = true
}

variable "db_password" {
  description = "Database master password (use strong password in production)"
  type        = string
  sensitive   = true
}

variable "jwt_secret_key" {
  description = "JWT secret key for authentication"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API key for LLM features"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro" # Free tier eligible
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20 # Free tier: 20GB
}

variable "fargate_cpu" {
  description = "Fargate CPU units (256 = 0.25 vCPU)"
  type        = number
  default     = 256
}

variable "fargate_memory" {
  description = "Fargate memory in MB"
  type        = number
  default     = 512
}

variable "fargate_desired_count" {
  description = "Desired number of Fargate tasks"
  type        = number
  default     = 1
}

variable "enable_fargate_spot" {
  description = "Use Fargate Spot for cost savings"
  type        = bool
  default     = true
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "cors_origins" {
  description = "Allowed CORS origins (comma-separated)"
  type        = string
  default     = "https://your-frontend.vercel.app"
}

variable "enable_deletion_protection" {
  description = "Enable deletion protection for RDS (recommended for production)"
  type        = bool
  default     = false # Set to true for production
}

variable "backup_retention_period" {
  description = "Number of days to retain automated backups"
  type        = number
  default     = 7
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "RetailerAIAgent"
    ManagedBy   = "Terraform"
    Environment = "Production"
  }
}
