# 🚀 RAG Server Production Deployment Guide

## Overview
This guide covers deploying your RAG server to EC2 with real AWS services (S3, DynamoDB, Lambda) instead of LocalStack.

## Prerequisites

### 1. AWS Account Setup
- AWS Account with appropriate permissions
- AWS CLI configured with credentials
- IAM user with EC2, S3, DynamoDB, Lambda permissions

### 2. Docker Hub Account
- Docker Hub account for storing images
- Docker Hub credentials configured

### 3. EC2 Requirements
- EC2 instance (t3.medium or larger recommended)
- Security group with ports 80, 443, 22 open
- Key pair for SSH access

## Step 1: Build and Push Docker Images

### 1.1 Build Images Locally
```bash
# Build all services
docker-compose build

# Or build individually
docker build -t rag_server-pdf_services:latest ./pdf_services
docker build -t rag_server-rag_module:latest ./rag_module
docker build -t rag_server-aws_service:latest ./aws_service
docker build -t rag_server-metrics_summary:latest ./metrics_lambda
docker build -t rag_server-query_log_api:latest ./metrics_lambda
```

### 1.2 Push to Docker Hub
```powershell
# Windows PowerShell
.\scripts\push_docker_images.ps1
```

**Important:** Edit the script first to replace `yourdockerhub` with your actual Docker Hub username.

## Step 2: AWS Infrastructure Setup

### 2.1 Create Production Environment File
```bash
cp env.production.example .env.production
```

Edit `.env.production` with your actual AWS credentials and configuration:

```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_actual_access_key
AWS_SECRET_ACCESS_KEY=your_actual_secret_key
AWS_DEFAULT_REGION=us-east-1
AWS_REGION=us-east-1

# S3 Configuration
S3_BUCKET_NAME=your-rag-server-bucket
S3_UPLOAD_FOLDER=uploads
S3_PROCESSED_FOLDER=processed

# DynamoDB Configuration
DYNAMODB_TABLE_NAME=rag_server_queries
DYNAMODB_METRICS_TABLE=rag_server_metrics

# Lambda Configuration
LAMBDA_FUNCTION_NAME=rag-metrics-function
LAMBDA_RUNTIME=python3.9
LAMBDA_HANDLER=handler.lambda_handler
LAMBDA_TIMEOUT=300
LAMBDA_MEMORY_SIZE=512

# Security
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this
```

### 2.2 Setup AWS Resources
```bash
# Create S3 bucket
aws s3 mb s3://your-rag-server-bucket --region us-east-1

# Create DynamoDB tables
aws dynamodb create-table \
    --table-name rag_server_queries \
    --attribute-definitions AttributeName=query_id,AttributeType=S \
    --key-schema AttributeName=query_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1

aws dynamodb create-table \
    --table-name rag_server_metrics \
    --attribute-definitions AttributeName=metric_id,AttributeType=S \
    --key-schema AttributeName=metric_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region us-east-1
```

### 2.3 Create IAM Role for Lambda
```bash
# Create Lambda execution role
aws iam create-role \
    --role-name RAG-Lambda-Execution-Role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }'

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name RAG-Lambda-Execution-Role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create and attach custom policy for S3 and DynamoDB access
aws iam put-role-policy \
    --role-name RAG-Lambda-Execution-Role \
    --policy-name RAG-Lambda-Policy \
    --policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                "Resource": "arn:aws:s3:::your-rag-server-bucket/*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                "Resource": [
                    "arn:aws:dynamodb:us-east-1:*:table/rag_server_queries",
                    "arn:aws:dynamodb:us-east-1:*:table/rag_server_metrics"
                ]
            }
        ]
    }'
```

## Step 3: Deploy Lambda Functions

### 3.1 Create Lambda Deployment Package
```bash
cd metrics_lambda
zip -r lambda_function.zip . -x "package/*" "__pycache__/*" "*.pyc"
cd ..
```

### 3.2 Deploy Lambda Function
```bash
# Get the role ARN
ROLE_ARN=$(aws iam get-role --role-name RAG-Lambda-Execution-Role --query 'Role.Arn' --output text)

# Create Lambda function
aws lambda create-function \
    --function-name rag-metrics-function \
    --runtime python3.9 \
    --handler handler.lambda_handler \
    --role $ROLE_ARN \
    --zip-file fileb://metrics_lambda/lambda_function.zip \
    --timeout 300 \
    --memory-size 512 \
    --region us-east-1
```

## Step 4: EC2 Instance Setup

### 4.1 Launch EC2 Instance
- **AMI**: Amazon Linux 2
- **Instance Type**: t3.medium (or larger)
- **Storage**: 20GB minimum
- **Security Group**: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

### 4.2 Connect to EC2 Instance
```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

### 4.3 Install Dependencies
```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install -y git

# Install Python and pip
sudo yum install -y python3 python3-pip

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Logout and login again to apply docker group changes
exit
# SSH back in
```

### 4.4 Clone Repository and Setup
```bash
# Clone repository
git clone https://github.com/Srijith1881/RAG-server.git
cd RAG-server

# Create necessary directories
mkdir -p uploads chroma_db nginx/ssl

# Copy and configure environment
cp env.production.example .env.production
nano .env.production  # Edit with your actual values
```

## Step 5: Production Docker Compose

### 5.1 Create Production Docker Compose
Create `docker-compose.production.yml`:

```yaml
version: '3.8'
services:
  pdf_services:
    image: yourdockerhub/pdf_services:latest
    ports:
      - "8001:8001"
    env_file: .env.production
    volumes:
      - ./uploads:/app/uploads
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  rag_module:
    image: yourdockerhub/rag_module:latest
    ports:
      - "8002:8002"
    env_file: .env.production
    volumes:
      - ./chroma_db:/app/chroma_db
    restart: unless-stopped
    depends_on:
      - pdf_services
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  aws_service:
    image: yourdockerhub/aws_service:latest
    ports:
      - "8003:8003"
    env_file: .env.production
    restart: unless-stopped
    depends_on:
      - pdf_services
      - rag_module
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    restart: unless-stopped
    depends_on:
      - aws_service
      - rag_module
      - pdf_services

volumes:
  chroma_db:
```

### 5.2 Create Nginx Configuration
Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream pdf_services {
        server pdf_services:8001;
    }

    upstream rag_module {
        server rag_module:8002;
    }

    upstream aws_service {
        server aws_service:8003;
    }

    server {
        listen 80;
        server_name _;

        location /pdf/ {
            proxy_pass http://pdf_services/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /rag/ {
            proxy_pass http://rag_module/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /api/ {
            proxy_pass http://aws_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location / {
            proxy_pass http://aws_service/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Step 6: Deploy and Start Services

### 6.1 Start Services
```bash
# Start all services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps

# View logs
docker-compose -f docker-compose.production.yml logs -f
```

### 6.2 Verify Deployment
```bash
# Check if services are running
curl http://localhost/health
curl http://localhost/pdf/health
curl http://localhost/rag/health
curl http://localhost/api/health
```

## Step 7: Lambda Function Integration

### 7.1 Test Lambda Function
```bash
# Test Lambda function
aws lambda invoke \
    --function-name rag-metrics-function \
    --payload '{"test": "data"}' \
    response.json

cat response.json
```

### 7.2 Setup API Gateway (Optional)
If you want to expose Lambda functions via API Gateway:

```bash
# Create API Gateway
aws apigateway create-rest-api \
    --name "RAG-Server-API" \
    --description "API for RAG Server Lambda functions"

# Follow AWS documentation to create resources, methods, and integrate with Lambda
```

## Step 8: Monitoring and Maintenance

### 8.1 Setup CloudWatch Logs
```bash
# Lambda logs are automatically sent to CloudWatch
# View logs in AWS Console or via CLI
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/rag-metrics-function"
```

### 8.2 Setup CloudWatch Alarms
```bash
# Create alarm for Lambda errors
aws cloudwatch put-metric-alarm \
    --alarm-name "RAG-Lambda-Errors" \
    --alarm-description "Alarm when Lambda function has errors" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 1 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 1 \
    --dimensions Name=FunctionName,Value=rag-metrics-function
```

### 8.3 Backup Strategy
```bash
# Backup S3 data
aws s3 sync s3://your-rag-server-bucket s3://your-rag-server-backup-bucket

# Backup DynamoDB (consider using AWS Backup service)
aws dynamodb create-backup \
    --table-name rag_server_queries \
    --backup-name "rag-server-backup-$(date +%Y%m%d)"
```

## Troubleshooting

### Common Issues

1. **Docker images not found**
   - Ensure images are pushed to Docker Hub
   - Check Docker Hub credentials

2. **AWS credentials not working**
   - Verify AWS credentials in `.env.production`
   - Check IAM permissions

3. **Lambda function errors**
   - Check CloudWatch logs
   - Verify IAM role permissions

4. **Services not starting**
   - Check Docker logs: `docker-compose logs [service-name]`
   - Verify environment variables

### Useful Commands
```bash
# View all logs
docker-compose -f docker-compose.production.yml logs -f

# Restart specific service
docker-compose -f docker-compose.production.yml restart [service-name]

# Update images
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

# Check resource usage
docker stats

# SSH into container
docker-compose -f docker-compose.production.yml exec [service-name] bash
```

## Security Considerations

1. **Use HTTPS**: Configure SSL certificates for production
2. **IAM Roles**: Use IAM roles instead of access keys when possible
3. **Security Groups**: Restrict access to necessary ports only
4. **Secrets Management**: Use AWS Secrets Manager for sensitive data
5. **Regular Updates**: Keep Docker images and system packages updated

## Cost Optimization

1. **EC2 Instance**: Use appropriate instance size
2. **S3 Lifecycle**: Configure lifecycle policies for old data
3. **DynamoDB**: Use on-demand billing for variable workloads
4. **Lambda**: Monitor execution time and memory usage

Your RAG server is now deployed and ready for production use! 🎉 