terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

# Configure the AWS Provider
provider "aws" {
  default_tags {
    tags = local.default_tags
  }
  region  = var.aws_region
  profile = var.profile
}

# Data sources
data "aws_caller_identity" "current" {}

data "aws_ecr_repository" "podaac_sst_repo" {
  name = var.ecr_repo
}

data "aws_iam_role" "lambda_execution_role" {
  name = var.lambda_role
}

# Local variables
locals {
  account_id = data.aws_caller_identity.current.account_id
  default_tags = length(var.default_tags) == 0 ? {
    application : var.app_name,
  } : var.default_tags
}