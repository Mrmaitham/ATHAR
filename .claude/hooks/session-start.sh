#!/bin/bash
set -euo pipefail

# Only run in Claude Code on the web / remote sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg already installed: $(ffmpeg -version | head -1)"
  exit 0
fi

echo "Installing ffmpeg..."
apt-get update -y
apt-get install -y ffmpeg

ffmpeg -version | head -1
