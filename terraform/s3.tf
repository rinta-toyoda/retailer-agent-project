# S3 Bucket for Product Images
# Public read access for product images

resource "aws_s3_bucket" "product_images" {
  bucket = "${local.name_prefix}-product-images"

  tags = {
    Name = "${local.name_prefix}-product-images"
  }
}

# Enable versioning for accidental deletion protection
resource "aws_s3_bucket_versioning" "product_images" {
  bucket = aws_s3_bucket.product_images.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Block public ACLs but allow bucket policy
resource "aws_s3_bucket_public_access_block" "product_images" {
  bucket = aws_s3_bucket.product_images.id

  block_public_acls       = true
  block_public_policy     = false # Allow bucket policy for public read
  ignore_public_acls      = true
  restrict_public_buckets = false
}

# Bucket policy for public read access
resource "aws_s3_bucket_policy" "product_images" {
  bucket = aws_s3_bucket.product_images.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.product_images.arn}/*"
      }
    ]
  })

  depends_on = [aws_s3_bucket_public_access_block.product_images]
}

# CORS configuration for web access
resource "aws_s3_bucket_cors_configuration" "product_images" {
  bucket = aws_s3_bucket.product_images.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "HEAD"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3600
  }
}

# Lifecycle policy to delete old versions after 30 days
resource "aws_s3_bucket_lifecycle_configuration" "product_images" {
  bucket = aws_s3_bucket.product_images.id

  rule {
    id     = "delete-old-versions"
    status = "Enabled"

    # Empty filter to apply to all objects
    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "product_images" {
  bucket = aws_s3_bucket.product_images.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

output "s3_bucket_name" {
  description = "S3 bucket name for product images"
  value       = aws_s3_bucket.product_images.bucket
}

output "s3_bucket_url" {
  description = "S3 bucket public URL"
  value       = "https://${aws_s3_bucket.product_images.bucket}.s3.${var.aws_region}.amazonaws.com"
}
