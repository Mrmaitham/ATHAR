#!/bin/bash
# reads "file|url" lines on stdin, PUTs each png from /home/user/lw_chain
cd /home/user/lw_chain
while IFS='|' read -r f u; do [ -z "$f" ] && continue; c=$(curl -s -o /dev/null -w "%{http_code}" -X PUT -H "Content-Type: image/png" -H "If-None-Match: *" --data-binary @"$f" "$u"); echo "$f $c"; done
