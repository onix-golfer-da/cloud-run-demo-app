# Cloud Run Demo App (Repo 1: Application Team)

A FastAPI web service demonstrating Google Cloud Run native secrets retrieval:
1. **Environment Variable**: Reads `$APP_ENV` (injected via `secretKeyRef` from Secret Manager secret `demo-app-config`).
2. **Volume Mount**: Reads and displays X.509 certificate metadata from `/etc/ssl/demo/tls.crt` (mounted as a volume from Secret Manager secret `demo-tls-cert`).

---

## Architecture Role in DevOps CI/CD Demo

This repository acts as **Repo 1 ("Code Repo")**:
- App engineers develop, test, and containerize the application.
- On merge to `main`, the CI/CD pipeline:
  1. Builds and tags the Docker image with `sha-${GITHUB_SHA}` and `latest`.
  2. Pushes the container image to Google Artifact Registry.
  3. Publishes new secret versions to Secret Manager using `./scripts/publish_secrets.sh`.
  4. Triggers a cross-repo dispatch event to **Repo 2 (IaC / Platform repo)** with the new image metadata.

---

## Local Development & Testing

```bash
# 1. Create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app locally
uvicorn src.main:app --reload --port 8080

# 4. Visit http://localhost:8080 in your browser
```

### Test with Docker
```bash
docker build -t cloud-run-demo-app .
docker run -p 8080:8080 -e APP_ENV="docker-local" cloud-run-demo-app
```

---

## Initializing this as a Separate GitHub Repository

To push this codebase to its own standalone GitHub repository `https://github.com/onix-golfer-da/cloud-run-demo-app`:

```bash
# 1. From inside this folder:
cd cloud-run-demo-app

# 2. Initialize Git
git init -b main
git add .
git commit -m "feat: initial commit of cloud-run-demo-app"

# 3. Add remote (create the repo first on GitHub if not existing)
git remote add origin https://github.com/onix-golfer-da/cloud-run-demo-app.git

# 4. Push to main
git push -u origin main
```

### GitHub Repository Secrets Needed in `cloud-run-demo-app`
- `IAC_REPO_PAT`: A GitHub Personal Access Token (PAT) with `repo` scope to allow dispatching workflow triggers to `onix-net/dalberto-lab`.
- `GCP_WIF_PROVIDER` (Optional): The Workload Identity Provider resource name (if different from default).
- `GCP_SA_EMAIL` (Optional): The GCP Service Account email with permissions to push to Artifact Registry and add versions to Secret Manager.
