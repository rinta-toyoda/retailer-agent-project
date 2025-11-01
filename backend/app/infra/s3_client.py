"""
S3 Client for Image Storage
Uses LocalStack for local development and AWS S3 for production.
Marking Criteria: 4.4 (Advanced Technologies - Cloud Storage)
"""

import os
import uuid
from typing import Optional
import boto3
from botocore.exceptions import ClientError


class S3Client:
    """
    S3 client for uploading and managing product images.
    Supports both LocalStack (development) and AWS S3 (production).
    """

    def __init__(self):
        """Initialize S3 client with LocalStack or AWS configuration."""
        self.bucket_name = os.getenv("S3_BUCKET_NAME", "retailer-product-images")
        self.region = os.getenv("AWS_REGION", "us-east-1")

        # LocalStack configuration for local development
        endpoint_url = os.getenv("S3_ENDPOINT_URL")  # e.g., http://localstack:4566

        public_url_override = os.getenv("S3_PUBLIC_URL")

        if endpoint_url:
            # LocalStack configuration
            self.s3_client = boto3.client(
                "s3",
                endpoint_url=endpoint_url,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
                region_name=self.region
            )
            if public_url_override:
                self.public_url_base = f"{public_url_override.rstrip('/')}/{self.bucket_name}"
            else:
                self.public_url_base = f"{endpoint_url.rstrip('/')}/{self.bucket_name}"
        else:
            # AWS S3 configuration
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=self.region
            )
            self.public_url_base = public_url_override or f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com"

        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError:
            try:
                if self.region == "us-east-1":
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                else:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={"LocationConstraint": self.region}
                    )

                # Set bucket policy for public read access
                self._set_public_read_policy()
                self._set_cors_policy()

                print(f"Created S3 bucket: {self.bucket_name}")
            except ClientError as e:
                print(f"Could not create bucket: {e}")

    def _set_public_read_policy(self):
        """Set bucket policy to allow public read access to images."""
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }
            ]
        }

        try:
            import json
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(policy)
            )
        except ClientError as e:
            print(f"Could not set bucket policy: {e}")

    def _set_cors_policy(self):
        """Set CORS policy to allow browser access to images."""
        cors_configuration = {
            'CORSRules': [
                {
                    'AllowedOrigins': ['*'],
                    'AllowedMethods': ['GET', 'HEAD'],
                    'AllowedHeaders': ['*'],
                    'MaxAgeSeconds': 3000
                }
            ]
        }

        try:
            self.s3_client.put_bucket_cors(
                Bucket=self.bucket_name,
                CORSConfiguration=cors_configuration
            )
        except ClientError as e:
            print(f"Could not set CORS policy: {e}")

    def upload_image(
        self,
        file_content: bytes,
        content_type: str,
        filename: Optional[str] = None
    ) -> str:
        """
        Upload image to S3 and return public URL.

        Args:
            file_content: Binary content of the image file
            content_type: MIME type (e.g., 'image/jpeg', 'image/png')
            filename: Optional original filename (will generate UUID if not provided)

        Returns:
            Public URL of the uploaded image
        """
        # Generate unique filename
        file_ext = self._get_extension_from_content_type(content_type)
        unique_filename = filename or f"{uuid.uuid4()}{file_ext}"
        s3_key = f"products/{unique_filename}"

        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                CacheControl="max-age=31536000"  # Cache for 1 year
            )

            # Return public URL
            return f"{self.public_url_base}/{s3_key}"

        except ClientError as e:
            raise ValueError(f"Failed to upload image: {str(e)}")

    def delete_image(self, image_url: str) -> bool:
        """
        Delete image from S3 by URL.

        Args:
            image_url: Full S3 URL of the image

        Returns:
            True if deletion was successful
        """
        try:
            # Extract S3 key from URL
            s3_key = image_url.replace(f"{self.public_url_base}/", "")

            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True

        except ClientError as e:
            print(f"Failed to delete image: {e}")
            return False

    @staticmethod
    def _get_extension_from_content_type(content_type: str) -> str:
        """Get file extension from MIME type."""
        extensions = {
            "image/jpeg": ".jpg",
            "image/jpg": ".jpg",
            "image/png": ".png",
            "image/gif": ".gif",
            "image/webp": ".webp",
        }
        return extensions.get(content_type.lower(), ".jpg")


# Global S3 client instance
_s3_client_instance = None


def get_s3_client() -> S3Client:
    """Get or create global S3 client instance."""
    global _s3_client_instance
    if _s3_client_instance is None:
        _s3_client_instance = S3Client()
    return _s3_client_instance
