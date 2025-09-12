#!/bin/bash

# Deploy AI Gateway to GitHub and trigger Actions
# This script helps with authentication and deployment

set -e

echo "🚀 AI Gateway - GitHub Deployment Script"
echo "========================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI found"
    
    # Check if authenticated
    if gh auth status &> /dev/null; then
        echo "✅ GitHub CLI authenticated"
        
        # Push using GitHub CLI
        echo "📤 Pushing to GitHub..."
        git push origin main
        
        echo "🔄 Triggering GitHub Actions..."
        echo "   Visit: https://github.com/tindevelopers/ai-service-litellm-gateway/actions"
        
        # Open the Actions page
        gh repo view --web --branch main
        
    else
        echo "⚠️  GitHub CLI not authenticated"
        echo "   Run: gh auth login"
        exit 1
    fi
    
else
    echo "⚠️  GitHub CLI not found"
    echo ""
    echo "📋 Manual deployment steps:"
    echo "1. Authenticate with GitHub:"
    echo "   - Install GitHub CLI: brew install gh"
    echo "   - Login: gh auth login"
    echo "   - Or set up SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    echo ""
    echo "2. Push to GitHub:"
    echo "   git push origin main"
    echo ""
    echo "3. View GitHub Actions:"
    echo "   https://github.com/tindevelopers/ai-service-litellm-gateway/actions"
    echo ""
    echo "4. Required GitHub Secrets for deployment:"
    echo "   - GCP_SA_KEY: Google Cloud Service Account JSON key"
    echo "   - GCP_PROJECT_ID: Google Cloud Project ID"
    echo "   - SECRET_KEY: Application secret key"
    echo "   - OPENAI_API_KEY: OpenAI API key"
    echo "   - ANTHROPIC_API_KEY: Anthropic API key"
    echo "   - GOOGLE_API_KEY: Google API key"
fi

echo ""
echo "🎯 Next Steps:"
echo "1. ✅ Code committed and ready to push"
echo "2. 📤 Push to GitHub to trigger Actions"
echo "3. 🔍 Monitor GitHub Actions workflow"
echo "4. 🚀 Automatic deployment to Google Cloud Run"
echo "5. ✅ Health check validation"
echo ""
echo "📚 Documentation:"
echo "- GitHub Actions: .github/workflows/ci-cd.yml"
echo "- API Docs: http://your-deployed-url/docs"
echo "- Health Check: http://your-deployed-url/health"
