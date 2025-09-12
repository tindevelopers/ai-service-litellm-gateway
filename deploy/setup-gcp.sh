#!/bin/bash

# Google Cloud Platform Setup Script for AI Gateway
# This script sets up the necessary GCP resources for the AI Gateway platform

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION="us-central1"
SERVICE_NAME="ai-gateway"
DB_INSTANCE_NAME="ai-gateway-db"
REDIS_INSTANCE_NAME="ai-gateway-redis"
VPC_CONNECTOR_NAME="ai-gateway-connector"

echo "🚀 Setting up AI Gateway on Google Cloud Platform"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Enable required APIs
echo "📡 Enabling required Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com \
    vpcaccess.googleapis.com \
    secretmanager.googleapis.com \
    --project=$PROJECT_ID

# Create Cloud SQL instance (PostgreSQL)
echo "🗄️ Creating Cloud SQL PostgreSQL instance..."
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --project=$PROJECT_ID || echo "Database instance may already exist"

# Create database
echo "📊 Creating database..."
gcloud sql databases create ai_gateway \
    --instance=$DB_INSTANCE_NAME \
    --project=$PROJECT_ID || echo "Database may already exist"

# Create database user
echo "👤 Creating database user..."
gcloud sql users create ai_gateway_user \
    --instance=$DB_INSTANCE_NAME \
    --password=$(openssl rand -base64 32) \
    --project=$PROJECT_ID || echo "User may already exist"

# Create Redis instance
echo "🔴 Creating Redis instance..."
gcloud redis instances create $REDIS_INSTANCE_NAME \
    --size=1 \
    --region=$REGION \
    --redis-version=redis_7_0 \
    --tier=basic \
    --project=$PROJECT_ID || echo "Redis instance may already exist"

# Create VPC connector for Redis access
echo "🔗 Creating VPC connector..."
gcloud compute networks vpc-access connectors create $VPC_CONNECTOR_NAME \
    --region=$REGION \
    --subnet-project=$PROJECT_ID \
    --subnet=default \
    --min-instances=2 \
    --max-instances=10 \
    --machine-type=e2-micro \
    --project=$PROJECT_ID || echo "VPC connector may already exist"

# Create secrets in Secret Manager
echo "🔐 Creating secrets..."
echo -n "$(openssl rand -base64 32)" | gcloud secrets create secret-key --data-file=- --project=$PROJECT_ID || echo "Secret may already exist"
echo -n "your-openai-key-here" | gcloud secrets create openai-api-key --data-file=- --project=$PROJECT_ID || echo "Secret may already exist"
echo -n "your-anthropic-key-here" | gcloud secrets create anthropic-api-key --data-file=- --project=$PROJECT_ID || echo "Secret may already exist"

# Get database connection string
DB_CONNECTION_STRING="postgresql://ai_gateway_user:$(gcloud sql users describe ai_gateway_user --instance=$DB_INSTANCE_NAME --format='value(password)' --project=$PROJECT_ID)@/ai_gateway?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME"
echo -n "$DB_CONNECTION_STRING" | gcloud secrets create database-url --data-file=- --project=$PROJECT_ID || echo "Secret may already exist"

# Get Redis connection string
REDIS_HOST=$(gcloud redis instances describe $REDIS_INSTANCE_NAME --region=$REGION --format='value(host)' --project=$PROJECT_ID)
REDIS_PORT=$(gcloud redis instances describe $REDIS_INSTANCE_NAME --region=$REGION --format='value(port)' --project=$PROJECT_ID)
REDIS_CONNECTION_STRING="redis://$REDIS_HOST:$REDIS_PORT"
echo -n "$REDIS_CONNECTION_STRING" | gcloud secrets create redis-url --data-file=- --project=$PROJECT_ID || echo "Secret may already exist"

# Set up Cloud Build trigger
echo "🔨 Setting up Cloud Build trigger..."
gcloud builds triggers create github \
    --repo-name=ai-service-litellm-gateway \
    --repo-owner=tindevelopers \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml \
    --project=$PROJECT_ID || echo "Trigger may already exist"

echo "✅ GCP setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update your API keys in Secret Manager:"
echo "   gcloud secrets versions add openai-api-key --data-file=<your-openai-key-file>"
echo "   gcloud secrets versions add anthropic-api-key --data-file=<your-anthropic-key-file>"
echo ""
echo "2. Deploy your service:"
echo "   git push origin main"
echo ""
echo "3. Your service will be available at:"
echo "   https://$SERVICE_NAME-<hash>-uc.a.run.app"