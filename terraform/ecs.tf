# ECS Fargate Cluster and Service Configuration

# CloudWatch Log Group for ECS
resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/${local.name_prefix}"
  retention_in_days = 7 # Reduce for cost savings

  tags = {
    Name = "${local.name_prefix}-ecs-logs"
  }
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${local.name_prefix}-cluster"

  configuration {
    execute_command_configuration {
      logging = "OVERRIDE"
      log_configuration {
        cloud_watch_log_group_name = aws_cloudwatch_log_group.ecs.name
      }
    }
  }

  tags = {
    Name = "${local.name_prefix}-cluster"
  }
}

# Enable Container Insights (optional, costs extra)
resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = var.enable_fargate_spot ? ["FARGATE_SPOT", "FARGATE"] : ["FARGATE"]

  default_capacity_provider_strategy {
    capacity_provider = var.enable_fargate_spot ? "FARGATE_SPOT" : "FARGATE"
    weight            = 1
    base              = 1
  }
}

# Security Group for Fargate Tasks
resource "aws_security_group" "fargate" {
  name        = "${local.name_prefix}-fargate-sg"
  description = "Security group for Fargate tasks"
  vpc_id      = aws_vpc.main.id

  # Allow inbound from ALB
  ingress {
    description     = "HTTP from ALB"
    from_port       = 8100
    to_port         = 8100
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Allow all outbound (for RDS, S3, internet)
  egress {
    description = "Allow all outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${local.name_prefix}-fargate-sg"
  }
}

# ECS Task Definition
resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.name_prefix}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([
    {
      name      = "backend"
      image     = "${aws_ecr_repository.backend.repository_url}:latest"
      essential = true

      portMappings = [
        {
          containerPort = 8100
          protocol      = "tcp"
        }
      ]

      # Environment variables from Parameter Store
      secrets = [
        {
          name      = "DATABASE_URL"
          valueFrom = aws_ssm_parameter.database_url.arn
        },
        {
          name      = "JWT_SECRET_KEY"
          valueFrom = aws_ssm_parameter.jwt_secret.arn
        },
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_ssm_parameter.openai_api_key.arn
        }
      ]

      # Non-sensitive environment variables
      environment = [
        {
          name  = "APP_ENV"
          value = "production"
        },
        {
          name  = "DEBUG"
          value = "false"
        },
        {
          name  = "API_HOST"
          value = "0.0.0.0"
        },
        {
          name  = "API_PORT"
          value = "8100"
        },
        {
          name  = "CORS_ORIGINS"
          value = var.cors_origins
        },
        {
          name  = "S3_BUCKET_NAME"
          value = aws_s3_bucket.product_images.bucket
        },
        {
          name  = "AWS_REGION"
          value = var.aws_region
        },
        {
          name  = "LLM_ENABLED"
          value = "true"
        },
        {
          name  = "LLM_PROVIDER"
          value = "openai"
        },
        {
          name  = "LLM_MODEL"
          value = "gpt-4o-mini"
        },
        {
          name  = "LLM_TEMPERATURE"
          value = "0.2"
        },
        {
          name  = "LLM_MAX_TOOL_CALLS"
          value = "4"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "backend"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8100/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = {
    Name = "${local.name_prefix}-backend-task"
  }
}

# ECS Service
resource "aws_ecs_service" "backend" {
  name            = "${local.name_prefix}-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.fargate_desired_count
  launch_type     = var.enable_fargate_spot ? null : "FARGATE"

  # Use Fargate Spot if enabled
  dynamic "capacity_provider_strategy" {
    for_each = var.enable_fargate_spot ? [1] : []
    content {
      capacity_provider = "FARGATE_SPOT"
      weight            = 100
      base              = 1
    }
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.fargate.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8100
  }

  # Wait for ALB to be ready
  depends_on = [
    aws_lb_listener.http,
    aws_iam_role_policy_attachment.ecs_task_execution
  ]

  tags = {
    Name = "${local.name_prefix}-backend-service"
  }
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "ECS service name"
  value       = aws_ecs_service.backend.name
}
