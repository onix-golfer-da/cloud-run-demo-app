#!/usr/bin/env bash
# =============================================================================
# publish_secrets.sh — Publishes secret payloads to Google Secret Manager
# Run by the App repo CI/CD pipeline on release.
# =============================================================================
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-migration-lab-uak1}"
SECRET_ENV="${SECRET_ENV_NAME:-demo-app-config}"
SECRET_CERT="${SECRET_CERT_NAME:-demo-tls-cert}"
APP_VERSION="${APP_VERSION:-v1.0.0}"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  App Repo: Publishing Secrets to Google Secret Manager       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo "  Project    : ${PROJECT_ID}"
echo "  App Version: ${APP_VERSION}"
echo ""

# 1. Update/Add version to Environment Secret
echo "▶ [1/2] Updating '${SECRET_ENV}' with current release payload..."
PAYLOAD="release-${APP_VERSION} (updated $(date -u +'%Y-%m-%d %H:%M:%S UTC'))"

if gcloud secrets describe "${SECRET_ENV}" --project="${PROJECT_ID}" &>/dev/null; then
  printf "%s" "${PAYLOAD}" | gcloud secrets versions add "${SECRET_ENV}" \
    --data-file=- --project="${PROJECT_ID}"
  echo "  ✓ Added new version to ${SECRET_ENV}"
else
  printf "%s" "${PAYLOAD}" | gcloud secrets create "${SECRET_ENV}" \
    --replication-policy="automatic" \
    --data-file=- --project="${PROJECT_ID}"
  echo "  ✓ Created secret ${SECRET_ENV} with initial payload"
fi

# 2. Update/Add version to Certificate Secret
echo ""
echo "▶ [2/2] Generating and updating '${SECRET_CERT}'..."
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

openssl req -x509 \
  -newkey rsa:2048 \
  -keyout "${TMP_DIR}/demo.key" \
  -out    "${TMP_DIR}/demo.crt" \
  -days 365 \
  -nodes \
  -subj "/C=US/ST=Ohio/L=Cleveland/O=App Team/OU=DevOps/CN=app-${APP_VERSION}.cloudrun.demo" \
  2>/dev/null

if gcloud secrets describe "${SECRET_CERT}" --project="${PROJECT_ID}" &>/dev/null; then
  gcloud secrets versions add "${SECRET_CERT}" \
    --data-file="${TMP_DIR}/demo.crt" --project="${PROJECT_ID}"
  echo "  ✓ Added new version to ${SECRET_CERT}"
else
  gcloud secrets create "${SECRET_CERT}" \
    --replication-policy="automatic" \
    --data-file="${TMP_DIR}/demo.crt" --project="${PROJECT_ID}"
  echo "  ✓ Created secret ${SECRET_CERT} with initial certificate"
fi

echo ""
echo "✅ Secrets successfully published to Secret Manager!"
