# Deploy Trigger for litellm-proxy (Cloud Run)

This guide explains how to create a Cloud Build trigger that automatically deploys to the **litellm-proxy** Cloud Run service when you push to your Git repository.

**Target:**
- **Service:** litellm-proxy
- **Region:** europe-west9
- **Project:** api-ai-blog-writer

---

## Option 1: Via Cloud Run Console (Recommended)

1. **Open Cloud Run**
   - Go to [Cloud Run](https://console.cloud.google.com/run?project=api-ai-blog-writer)
   - Or: [Direct link to litellm-proxy](https://console.cloud.google.com/run/detail/europe-west9/litellm-proxy?project=api-ai-blog-writer)

2. **Connect the repository**
   - Click the **litellm-proxy** service
   - Click **Connect to repo** (or **Edit & deploy new revision** → **Set up continuous deployment**)

3. **Choose Cloud Build**
   - Select **Cloud Build** (or Developer Connect if you prefer GitLab/Bitbucket)
   - Authenticate with GitHub if prompted
   - Select your repository (e.g. `tindevelopers/ai-service-litellm-gateway`)

4. **Build configuration**
   - **Branch:** `^main$` (or your default branch)
   - **Build type:** Dockerfile
   - **Source location:** `Dockerfile` (or `ai-service-litellm-gateway/Dockerfile` if the app lives in that subdir)
   - **Build context:** `.` (or `ai-service-litellm-gateway` if using subdir)

5. **Save**
   - Click **Save** and complete the setup

Cloud Run will create a Cloud Build trigger and deploy on each push to the configured branch.

---

## Option 2: Via Cloud Build Console

1. **Open Cloud Build Triggers**
   - [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers?project=api-ai-blog-writer)

2. **Create trigger**
   - Click **Create trigger**
   - **Name:** `deploy-litellm-proxy`
   - **Event:** Push to a branch
   - **Source:** Connect your GitHub repo (or use existing connection)
   - **Branch:** `^main$`
   - **Configuration:** Cloud Build configuration file
   - **Location:** Repository
   - **Cloud Build configuration file:** `cloudbuild-litellm-proxy.yaml`

3. **Substitutions (optional)**
   - Leave defaults or override `_REGION`, `_SERVICE`, etc. if needed

4. **Save**

---

## Option 3: Via gcloud CLI

### Prerequisites

- Artifact Registry repo `litellm-proxy` in `europe-west9`:
  ```bash
  gcloud artifacts repositories create litellm-proxy \
    --repository-format=docker \
    --location=europe-west9 \
    --project=api-ai-blog-writer
  ```

- Secrets in Secret Manager (SECRET_KEY, DATABASE_URL, REDIS_URL)

- GitHub repo connected to Cloud Build (see [Connect a repository](https://cloud.google.com/build/docs/automating-builds/create-manage-triggers#connect_repo))

### Create the trigger

```bash
gcloud builds triggers create github \
  --name="deploy-litellm-proxy" \
  --repo-name=ai-service-litellm-gateway \
  --repo-owner=tindevelopers \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-litellm-proxy.yaml \
  --project=api-ai-blog-writer
```

Replace `tindevelopers` with your GitHub org/user.

### Manual deploy (no trigger)

```bash
gcloud builds submit \
  --config=cloudbuild-litellm-proxy.yaml \
  --project=api-ai-blog-writer
```

---

## Build config file

The trigger uses `cloudbuild-litellm-proxy.yaml`, which:

- Builds the Docker image
- Pushes to `europe-west9-docker.pkg.dev/api-ai-blog-writer/litellm-proxy/`
- Deploys to Cloud Run service `litellm-proxy` in `europe-west9`

### If your app is in a subdirectory

If the app (Dockerfile, `src/`, `requirements-simple.txt`) lives in `ai-service-litellm-gateway/`, either:

1. **Change build context in the trigger**
   - Build context directory: `ai-service-litellm-gateway`
   - Dockerfile: `ai-service-litellm-gateway/Dockerfile`

2. **Or** add a `cloudbuild-litellm-proxy.yaml` in that subdir and point the trigger to it.

---

## Required IAM roles

The Cloud Build service account needs:

- `roles/run.admin` (Cloud Run Admin)
- `roles/artifactregistry.admin` (or Writer)
- `roles/iam.serviceAccountUser`

See [Cloud Run continuous deployment](https://cloud.google.com/run/docs/continuous-deployment) for full role details.

---

## Verify

After setup:

1. Push a commit to `main`
2. Check [Cloud Build history](https://console.cloud.google.com/cloud-build/builds?project=api-ai-blog-writer)
3. Check [Cloud Run revisions](https://console.cloud.google.com/run/detail/europe-west9/litellm-proxy/revisions?project=api-ai-blog-writer)
