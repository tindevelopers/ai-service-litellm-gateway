# Multi-Environment Deployment

This repository now supports automatic deployment to multiple environments:

## 🚀 Deployment Environments

### Production (main branch)
- **Service**: ai-gateway  
- **URL**: https://ai-gateway-njauor5rvq-uc.a.run.app
- **Resources**: 1Gi memory, 10 max instances
- **Trigger**: Push to main branch

### Staging (staging branch)  
- **Service**: ai-gateway-staging
- **Resources**: 512Mi memory, 5 max instances
- **Trigger**: Push to staging branch

### Development (develop branch)
- **Service**: ai-gateway-dev  
- **Resources**: 512Mi memory, 2 max instances
- **Trigger**: Push to develop branch

## 🔄 Workflow
1. Develop features in feature branches
2. Merge to develop → Deploys to development environment
3. Merge to staging → Deploys to staging environment  
4. Merge to main → Deploys to production environment

