# JSON Escaping Guide for API Calls

When making API calls to Headless PM, proper JSON escaping is crucial to avoid errors. This guide shows best practices for creating documents and other API calls.

## Common Issue

The error `"type": "json_invalid"` occurs when JSON is improperly escaped in curl commands.

## Best Practices

### 1. Use Single Quotes (Recommended)

Single quotes preserve the JSON exactly as written:

```bash
curl -X POST "http://localhost:6969/api/v1/documents?author_id=your_agent_id" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-key" \
  -d '{
    "doc_type": "update",
    "title": "Service Update",
    "content": "The service is running smoothly.",
    "project_context": "headless-pm"
  }'
```

### 2. Use Heredoc for Complex Content

For multi-line content or content with quotes:

```bash
curl -X POST "http://localhost:6969/api/v1/documents?author_id=your_agent_id" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-key" \
  -d @- <<'EOF'
{
  "doc_type": "critical_issue",
  "title": "API Error",
  "content": "Error message: \"Connection refused\"\nThis needs immediate attention.",
  "project_context": "headless-pm"
}
EOF
```

### 3. Use JSON Files

For complex documents, save to a file first:

```bash
# Create the JSON file
cat > document.json <<EOF
{
  "doc_type": "standup",
  "title": "Daily Update",
  "content": "## Progress\n- Completed feature X\n- Fixed bug Y\n\n## Blockers\n- None",
  "project_context": "headless-pm"
}
EOF

# Send the request
curl -X POST "http://localhost:6969/api/v1/documents?author_id=your_agent_id" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-key" \
  -d @document.json
```

### 4. Python Alternative

For complex scenarios, use Python:

```python
import requests
import json

url = "http://localhost:6969/api/v1/documents"
params = {"author_id": "your_agent_id"}
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "development-key"
}
data = {
    "doc_type": "update",
    "title": "Complex Update",
    "content": 'This content has "quotes" and \nnewlines',
    "project_context": "headless-pm"
}

response = requests.post(url, params=params, headers=headers, json=data)
print(response.json())
```

## Common Mistakes to Avoid

1. **Don't mix quote types**: Using double quotes for the JSON and trying to escape internal quotes
2. **Don't use unescaped newlines**: Use `\n` in JSON strings, not actual line breaks
3. **Don't forget the Content-Type header**: Always include `-H "Content-Type: application/json"`

## Service Registration Example

With the new ping URL requirement:

```bash
curl -X POST "http://localhost:6969/api/v1/services/register?agent_id=your_agent_id" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: development-key" \
  -d '{
    "service_name": "my-service",
    "ping_url": "http://localhost:8080/health",
    "port": 8080,
    "status": "up",
    "meta_data": {
      "version": "1.0.0",
      "description": "My awesome service"
    }
  }'
```

## See Also

- `/examples/create_document_curl.sh` - Working examples of different methods
- API documentation at `/api/v1/docs`