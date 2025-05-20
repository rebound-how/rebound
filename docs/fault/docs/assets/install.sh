#!/usr/bin/env bash
set -euo pipefail

GITHUB_ORG="rebound-how"
GITHUB_REPO="rebound"
ASSET_TARGET="fault-cli"
TARGET_BIN_DIR="${TARGET_BIN_DIR:-$HOME/.local/bin}"
FILE_PATH="${TARGET_BIN_DIR}/fault"

# --------------------------------------------------
# Detect OS and Architecture
# --------------------------------------------------
UNAME_OUT="$(uname -s)"
MACHINE="$(uname -m)"

# Normalize OS
case "${UNAME_OUT}" in
    Linux*)   OS="linux" ;;
    Darwin*)  OS="macos" ;;
    MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
    *)        OS="unknown" ;;
esac

# Normalize ARCH
case "${MACHINE}" in
    x86_64)  ARCH="x86_64" ;;
    aarch64|arm64) ARCH="arm64" ;;
    # Add other mappings here if needed
    *)       ARCH="unknown" ;;
esac

if [[ "${OS}" == "unknown" || "${ARCH}" == "unknown" ]]; then
    echo "Error: Unsupported OS or architecture: ${UNAME_OUT} / ${MACHINE}"
    exit 1
fi

# --------------------------------------------------
# Fetch the latest release information
# --------------------------------------------------
LATEST_RELEASE_JSON="$(curl -s "https://api.github.com/repos/${GITHUB_ORG}/${GITHUB_REPO}/releases/latest")"
TAG_NAME="$(echo "$LATEST_RELEASE_JSON" | jq -r '.tag_name')"
echo "Latest release tag: $TAG_NAME"

# --------------------------------------------------
# Find the download URL
# --------------------------------------------------
ASSET_DOWNLOAD_URL="$(echo "$LATEST_RELEASE_JSON" \
  | jq -r '[.assets[] | select(.name | test("'${ASSET_TARGET}'-'${TAG_NAME}'-'${ARCH}'.*'${OS}'")) | .browser_download_url'][0])"

if [[ -z "${ASSET_DOWNLOAD_URL}" || "${ASSET_DOWNLOAD_URL}" == "null" ]]; then
  echo "Error: Could not find a release asset for OS=${OS} ARCH=${ARCH} in the latest release."
  exit 1
fi

# --------------------------------------------------
# Download the asset
# --------------------------------------------------
FILE_NAME="$(basename "${ASSET_DOWNLOAD_URL}")"

echo ${ASSET_DOWNLOAD_URL}

echo "Downloading ${FILE_NAME}..."
curl -sSL "${ASSET_DOWNLOAD_URL}" -o ${FILE_PATH}

chmod a+x ${FILE_PATH}
echo "Download completed to: ${FILE_PATH}"
${FILE_PATH} --version
