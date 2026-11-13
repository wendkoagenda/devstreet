#!/bin/sh
# Provisionnement idempotent du bucket et de l'utilisateur applicatif MinIO (mc).
# Variables : MINIO_ROOT_USER, MINIO_ROOT_PASSWORD, S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_KEY.
set -eu

fail() {
  echo "ERREUR minio provision : $*" >&2
  exit 1
}

: "${MINIO_ROOT_USER:?MINIO_ROOT_USER manquant}"
: "${MINIO_ROOT_PASSWORD:?MINIO_ROOT_PASSWORD manquant}"
: "${S3_BUCKET_NAME:?S3_BUCKET_NAME manquant}"
: "${S3_ACCESS_KEY:?S3_ACCESS_KEY manquant}"
: "${S3_SECRET_KEY:?S3_SECRET_KEY manquant}"

ENDPOINT="http://minio-serveur:9000"
echo "== Provision MinIO bucket=$S3_BUCKET_NAME"

mc alias set local "$ENDPOINT" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"

mc mb --ignore-existing "local/${S3_BUCKET_NAME}"
# Lecture publique des objets (pas de listing) : meme modele que GCS public-read objet
mc anonymous set download "local/${S3_BUCKET_NAME}"

POLICY_FILE="/tmp/policy-${S3_BUCKET_NAME}.json"
cat > "$POLICY_FILE" <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::${S3_BUCKET_NAME}",
        "arn:aws:s3:::${S3_BUCKET_NAME}/*"
      ]
    }
  ]
}
EOF

mc admin policy create local "app-${S3_BUCKET_NAME}" "$POLICY_FILE" 2>/dev/null \
  || mc admin policy update local "app-${S3_BUCKET_NAME}" "$POLICY_FILE"

if mc admin user info local "$S3_ACCESS_KEY" >/dev/null 2>&1; then
  mc admin user add local "$S3_ACCESS_KEY" "$S3_SECRET_KEY" 2>/dev/null || true
else
  mc admin user add local "$S3_ACCESS_KEY" "$S3_SECRET_KEY"
fi
mc admin policy attach local "app-${S3_BUCKET_NAME}" --user "$S3_ACCESS_KEY" 2>/dev/null \
  || mc admin policy set local "app-${S3_BUCKET_NAME}" user="$S3_ACCESS_KEY"

echo "Provision MinIO OK."
