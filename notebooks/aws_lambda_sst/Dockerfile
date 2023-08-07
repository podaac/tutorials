# Stage 0 - Create from Python 3.10-alpine3.15 image
FROM amazon/aws-lambda-python:3.9
RUN yum update -y && yum install -y tcsh

# Stage 1 - Install dependencies
# FROM stage0 as stage1
COPY requirements.txt .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Stage 2 - Copy Generate code
# FROM stage1 as stage2
COPY . ${LAMBDA_TASK_ROOT}

# Stage 3 - Execute code
# FROM stage2 as stage3
LABEL version="0.1" \
    description="Containerized Lambda: SST"
CMD [ "sst.lambda_handler" ]