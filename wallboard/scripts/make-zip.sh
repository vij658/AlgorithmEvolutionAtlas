#!/bin/sh
# Builds wallboard.zip (source, docs, screenshots; no runtime data).
set -e
cd "$(dirname "$0")/../.."
rm -f wallboard/wallboard.zip
zip -qr wallboard/wallboard.zip wallboard \
  -x 'wallboard/data/*' 'wallboard/node_modules/*' 'wallboard/screenshots/*' 'wallboard/wallboard.zip' '*/.DS_Store'
echo "wrote wallboard/wallboard.zip ($(du -h wallboard/wallboard.zip | cut -f1))"
