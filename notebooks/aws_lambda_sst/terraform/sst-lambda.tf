# AWS Lambda function
resource "aws_lambda_function" "aws_lambda_error_handler" {
  image_uri     = "${data.aws_ecr_repository.podaac_sst_repo.repository_url}:latest"
  function_name = "${var.prefix}-sst"
  role          = data.aws_iam_role.lambda_execution_role.arn
  package_type  = "Image"
  memory_size   = 6144
  timeout       = 900
}

# SSM Parameter Store EDL Credentials
resource "aws_ssm_parameter" "aws_ssm_parameter_edl_username" {
  name        = "${var.prefix}-sst-edl-username"
  description = "Earthdata Login username"
  type        = "SecureString"
  value       = var.edl_username
}

resource "aws_ssm_parameter" "aws_ssm_parameter_edl_password" {
  name        = "${var.prefix}-sst-edl-password"
  description = "Earthdata Login password"
  type        = "SecureString"
  value       = var.edl_password
}

# S3 Bucket to hold results
resource "aws_s3_bucket" "aws_s3_bucket_sst" {
  bucket = "${var.prefix}-sst"
  tags   = { Name = "${var.prefix}-sst" }
}

resource "aws_s3_bucket_public_access_block" "aws_s3_bucket_sst_public_block" {
  bucket                  = aws_s3_bucket.aws_s3_bucket_sst.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "aws_s3_bucket_sst_ownership" {
  bucket = aws_s3_bucket.aws_s3_bucket_sst.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "aws_s3_bucket_sst_encryption" {
  bucket = aws_s3_bucket.aws_s3_bucket_sst.bucket
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}