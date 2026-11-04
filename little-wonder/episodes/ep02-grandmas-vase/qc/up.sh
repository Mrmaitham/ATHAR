#!/bin/bash
# usage: up.sh <file> <presigned_url>
curl -sS -o /dev/null -w "%{http_code}\n" -X PUT -H "Content-Type: image/png" -H "If-None-Match: *" --data-binary @"$1" "$2"
