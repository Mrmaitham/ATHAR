#!/bin/bash
# usage: put.sh FILE 'UPLOAD_URL'
curl -sS -o /dev/null -w "%{http_code}\n" -X PUT -H "Content-Type: image/png" -H "If-None-Match: *" --data-binary @"$1" "$2"
