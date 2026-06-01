#!/usr/bin/env bash
# Create Firestore vector indexes for internal RAG.
# Requires: gcloud CLI authenticated to your Firebase/GCP project.
#
# Usage:
#   export FIREBASE_PROJECT_ID=your-project
#   ./setup-index.sh

set -euo pipefail

PROJECT_ID="${FIREBASE_PROJECT_ID:?Set FIREBASE_PROJECT_ID}"
COLLECTION="${FIRESTORE_COLLECTION:-workspace_rag_internal}"
DIMENSION="${EMBEDDING_DIMENSION:-768}"

echo "Creating vector index on ${COLLECTION}.embedding (${DIMENSION} dims)..."

gcloud firestore indexes composite create \
  --project="${PROJECT_ID}" \
  --collection-group="${COLLECTION}" \
  --query-scope=COLLECTION \
  --field-config="field-path=embedding,vector-config={\"dimension\":\"${DIMENSION}\",\"flat\":{}}" \
  --database="(default)"

echo ""
echo "Optional: pre-filter indexes for domain / project / doc_type searches."
echo "Firestore will suggest composite indexes when you first run filtered queries."
echo "Example domain filter index:"
echo ""
echo "  gcloud firestore indexes composite create \\"
echo "    --project=${PROJECT_ID} \\"
echo "    --collection-group=${COLLECTION} \\"
echo "    --query-scope=COLLECTION \\"
echo "    --field-config=order=ASCENDING,field-path=domain \\"
echo "    --field-config=\"field-path=embedding,vector-config={\\\"dimension\\\":\\\"${DIMENSION}\\\",\\\"flat\\\":{}}\""
