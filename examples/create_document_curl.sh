#!/bin/bash

# Example script showing how to create documents via curl with proper JSON escaping

# Method 1: Using single quotes (simplest)
echo "Method 1: Single quotes around JSON"
curl -X POST "http://localhost:6969/api/v1/documents?author_id=frontend_dev_principal_001" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-key" \
  -d '{
    "doc_type": "update",
    "title": "Frontend Running Successfully",
    "content": "The frontend is now running on port 3000. Health check endpoint is responding correctly.",
    "project_context": "headless-pm"
  }'

echo -e "\n\n"

# Method 2: Using heredoc for complex content
echo "Method 2: Using heredoc for complex JSON"
curl -X POST "http://localhost:6969/api/v1/documents?author_id=backend_dev_001" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-key" \
  -d @- <<EOF
{
  "doc_type": "critical_issue",
  "title": "Database Connection Issue",
  "content": "## Problem Description\nThe database connection is timing out.\n\n## Error Details\n- Error: Connection timeout\n- Code: ETIMEDOUT\n- Frequency: Every request\n\n@pm @architect Please review this critical issue.",
  "project_context": "headless-pm"
}
EOF

echo -e "\n\n"

# Method 3: Using a JSON file
echo "Method 3: Using a JSON file"
cat > /tmp/document.json <<EOF
{
  "doc_type": "standup",
  "title": "Daily Standup - Frontend Team",
  "content": "## Yesterday\n- Completed user profile UI\n- Fixed responsive design issues\n\n## Today\n- Implementing dashboard widgets\n- Testing API integration\n\n## Blockers\n- Waiting for backend API documentation",
  "project_context": "headless-pm"
}
EOF

curl -X POST "http://localhost:6969/api/v1/documents?author_id=frontend_dev_001" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-key" \
  -d @/tmp/document.json

echo -e "\n\n"

# Method 4: Using jq for safe JSON generation
echo "Method 4: Using jq for dynamic JSON (if jq is installed)"
if command -v jq &> /dev/null; then
  TITLE="Service Started Successfully"
  CONTENT="The API service is running on port 8000. All health checks passing."
  
  JSON=$(jq -n \
    --arg dt "service_status" \
    --arg t "$TITLE" \
    --arg c "$CONTENT" \
    --arg p "headless-pm" \
    '{doc_type: $dt, title: $t, content: $c, project_context: $p}')
  
  curl -X POST "http://localhost:6969/api/v1/documents?author_id=backend_dev_001" \
    -H "Content-Type: application/json" \
    -H "X-API-Key: development-key" \
    -d "$JSON"
else
  echo "jq not installed, skipping method 4"
fi

echo -e "\n\nTips for avoiding JSON escaping issues:"
echo "1. Use single quotes around JSON when possible"
echo "2. Use heredoc (<<EOF) for multi-line content"
echo "3. Save complex JSON to a file first"
echo "4. Use jq to programmatically generate valid JSON"
echo "5. Avoid mixing quote types within the JSON"