#!/bin/bash

# Setup script for Google Cloud MCP credentials
# This script helps you set up the necessary credentials for the Google Cloud MCP server

set -e

PROJECT_ID=${1:-"your-project-id"}
SERVICE_ACCOUNT_NAME="ai-gateway-mcp"
KEY_FILE=".gcp/service-account-key.json"

echo "🔐 Setting up Google Cloud MCP credentials"
echo "Project ID: $PROJECT_ID"

# Create .gcp directory if it doesn't exist
mkdir -p .gcp

# Create service account for MCP
echo "👤 Creating service account for MCP..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="AI Gateway MCP Service Account" \
    --description="Service account for MCP server to manage Cloud Run deployments" \
    --project=$PROJECT_ID || echo "Service account may already exist"

# Grant necessary permissions
echo "🔑 Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Create and download service account key
echo "🔑 Creating service account key..."
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
    --project=$PROJECT_ID

# Update MCP configuration with correct project ID
echo "📝 Updating MCP configuration..."
sed -i.bak "s/your-project-id/$PROJECT_ID/g" .cursor/mcp.json
rm .cursor/mcp.json.bak

echo "✅ MCP credentials setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Restart Cursor to load the new MCP configuration"
echo "2. The Google Cloud MCP server will now be available in your project"
echo "3. You can use natural language commands to deploy to Cloud Run"
echo ""
echo "🔒 Security note:"
echo "The service account key is stored in .gcp/service-account-key.json"
echo "This file is already added to .gitignore for security"