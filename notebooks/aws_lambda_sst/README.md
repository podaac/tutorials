# AWS Lambda example for SST calculations

This program uses AWS Lambda to calculate a global mean on the MUR 25km dataset.

Full documentation is available in /docs/documentation.md

## Files

sst.py - the code to be run by AWS Lambda. This gets packaged in a Docker container to be deployed to AWS.

sst-global-mean-exploratory.ipynb - a notebook that explores the MUR25 dataset and runs through the global mean calculation offline. Can be run locally outside of AWS to trial run the code deployed to Lambda in sst.py

podaac-lambda-invoke-sst-global-mean.ipynb - the main notebook to invoke the Lambda code. Finds the files in Earthdata cloud, invokes Lambda on each, and plots the results as a timeseries.

Dockerfile - the instructions for Docker to build the container image with to deploy to AWS Lambda

requirements.txt - the required python packages to include in the Dockerfile. These may be different than the packages required to run the notebooks

terraform - terraform deploys AWS infrastructure. This folder contains the terraform configuration files
    > terraform.tfvars
    > main.tf
    > sst-lambda.tf
    > variables.tf

## AWS Infrastructure

This program includes the following AWS services:

- Lambda function to execute science code, deployed via Docker container.
- AWS IAM role for Lambda function to execute as
- AWS Parameter Store to manage Earthdata login credentials
- S3 bucket to store the output of the Lambda function

## Deploy AWS Resources with Terraform

Deploys AWS infrastructure and stores state in an S3 backend.

To deploy:

1. Edit `terraform.tfvars` for environment to deploy to.
2. Initialize terraform: `terraform init`
3. Plan terraform modifications: `terraform plan -out=tfplan`
4. Apply terraform modifications: `terraform apply tfplan`

## Run the notebook to invoke the Lambda function

Run aws_lambda_sst/podaac-lambda-invoke-sst-global-mean.ipynb.
