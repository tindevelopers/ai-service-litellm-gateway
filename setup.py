#!/usr/bin/env python3
"""
AI Gateway Setup Script
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_requirements():
    """Check if required tools are installed"""
    print("🔍 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        return False
    
    # Check if pip is available
    if not shutil.which("pip"):
        print("❌ pip is not available")
        return False
    
    print("✅ Requirements check passed")
    return True

def setup_virtual_environment():
    """Set up Python virtual environment"""
    if not os.path.exists("venv"):
        run_command("python -m venv venv", "Creating virtual environment")
    else:
        print("✅ Virtual environment already exists")

def install_dependencies():
    """Install Python dependencies"""
    activate_cmd = "source venv/bin/activate" if os.name != 'nt' else "venv\\Scripts\\activate"
    run_command(f"{activate_cmd} && pip install --upgrade pip", "Upgrading pip")
    run_command(f"{activate_cmd} && pip install -r requirements-simple.txt", "Installing dependencies")

def setup_environment_file():
    """Set up environment configuration"""
    if not os.path.exists(".env"):
        # Try to use the TIN AGENTS development environment file
        tin_agents_dev_env = "ENV FILES /DOWNLOAD_ENV_DEVELOPMENT.env"
        if os.path.exists(tin_agents_dev_env):
            print("🔍 Found TIN AGENTS development environment file")
            print("📋 Creating AI Gateway .env file...")
            
            # Create a customized .env file for AI Gateway
            env_content = """# =============================================================================
# AI Gateway - Development Environment Configuration
# =============================================================================

# Basic Application Settings
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
PORT=8000
HOST=0.0.0.0

# Security
SECRET_KEY=development-secret-key-change-this-in-production
ALLOWED_HOSTS=["*"]

# AI Provider API Keys (Replace with your actual keys)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
COHERE_API_KEY=your-cohere-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here

# Azure OpenAI (optional)
AZURE_API_KEY=your-azure-api-key-here
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2023-12-01-preview

# Database Configuration (optional for basic testing)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/ai_gateway_dev
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis Configuration (optional for caching)
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=100

# LiteLLM Configuration
LITELLM_MASTER_KEY=dev-master-key-change-this
LITELLM_DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/litellm_dev

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Caching (disabled for development)
CACHE_TTL=3600
CACHE_ENABLED=false
SEMANTIC_CACHE_THRESHOLD=0.95

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090

# Cost Optimization
DEFAULT_MODEL=gpt-3.5-turbo
COST_TRACKING_ENABLED=true
BUDGET_LIMIT_USD=100.00

# Specialized Services
BLOG_DEFAULT_MODEL=gpt-4
SUPPORT_DEFAULT_MODEL=gpt-3.5-turbo
CLASSIFICATION_MODEL=gpt-3.5-turbo

# =============================================================================
# SETUP INSTRUCTIONS:
# 1. Replace 'your-*-api-key-here' with your actual API keys
# 2. At minimum, add an OpenAI API key to test the service
# 3. Database and Redis are optional for basic testing
# =============================================================================
"""
            
            with open(".env", "w") as f:
                f.write(env_content)
            
            print("✅ Created .env file with AI Gateway configuration")
            print("⚠️  IMPORTANT: Edit .env file with your actual API keys!")
            print("   At minimum, add your OpenAI API key to test the service")
            
        elif os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            print("✅ Created .env file from env.example")
            print("⚠️  Please edit .env file with your actual API keys and configuration")
        else:
            print("❌ No environment template found")
    else:
        print("✅ .env file already exists")

def display_next_steps():
    """Display next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit the .env file with your actual API keys:")
    print("   - OPENAI_API_KEY=your-actual-openai-key")
    print("   - ANTHROPIC_API_KEY=your-actual-anthropic-key")
    print("   - etc.")
    print("\n2. Start the development server:")
    print("   source venv/bin/activate")
    print("   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload")
    print("\n3. Test the API:")
    print("   curl http://localhost:8000/health")
    print("   curl http://localhost:8000/v1/models")
    print("\n4. View API documentation:")
    print("   http://localhost:8000/docs")
    print("\n📚 For more information, check the README.md file")

def main():
    """Main setup function"""
    print("🚀 AI Gateway Setup")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    setup_virtual_environment()
    install_dependencies()
    setup_environment_file()
    display_next_steps()

if __name__ == "__main__":
    main()
