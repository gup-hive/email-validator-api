# Email Validator API - Quick Start Guide

This guide will help you get the Email Validator API up and running in minutes.

## Option 1: Run Locally

### Step 1: Install Dependencies

```bash
cd projects/email-validator
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Start the API

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Step 3: Test the API

Open a new terminal and test:

```bash
# Health check
curl http://localhost:5000/health

# Validate an email
curl -X POST http://localhost:5000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

## Option 2: Use the Startup Script

```bash
cd projects/email-validator
./start.sh
```

This will automatically create the virtual environment, install dependencies, and start the server.

## Option 3: Run with Docker (Coming Soon)

```bash
docker build -t email-validator .
docker run -p 5000:5000 email-validator
```

## Testing

Run the test script:

```bash
python tests/test_validator.py
```

## Common Issues

### Port 5000 already in use

Change the port in `app.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)  # Use 5001 instead
```

### Permission denied on start.sh

```bash
chmod +x start.sh
./start.sh
```

### DNS resolution issues

If you're behind a corporate firewall, you may need to configure DNS settings in your `/etc/resolv.conf`.

## Next Steps

1. Read the full [README.md](README.md) for detailed API documentation
2. Check out the example API calls below
3. Integrate with your application using the REST API

## Example API Calls

### Python

```python
import requests

# Validate single email
response = requests.post(
    'http://localhost:5000/api/v1/validate',
    json={'email': 'user@example.com'}
)
result = response.json()
print(result)
```

### JavaScript

```javascript
const response = await fetch('http://localhost:5000/api/v1/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: 'user@example.com' })
});
const result = await response.json();
console.log(result);
```

## Support

For issues and questions, please open an issue on GitHub.
