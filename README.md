# Email Validator API

A comprehensive email validation API that checks syntax, domain MX records, SMTP mailbox existence, disposable emails, and role-based addresses. Perfect for cleaning email lists and reducing bounce rates.

## Features

- ✅ **Syntax Validation** - RFC 5322 compliant email format checking
- 🌐 **Domain Verification** - MX record DNS validation
- 📧 **SMTP Verification** - Checks if mailbox actually exists
- 🗑️ **Disposable Email Detection** - Identifies temporary email services
- 👤 **Role-based Email Detection** - Flags admin@, info@, etc.
- 📊 **Bulk Validation** - Process entire email lists via CSV upload
- 🚀 **Fast API** - RESTful API built with Flask

## Pricing

- **Pay as you go**: $0.001 per email
- **Monthly plan**: $29/month for 50,000 emails

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. Clone or download this project:
```bash
cd projects/email-validator
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
export FLASK_ENV=development
export SECRET_KEY=your-secret-key-here
```

5. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Production Deployment

For production, use gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Health Check

```
GET /health
```

Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### Validate Single Email

```
POST /api/v1/validate
```

Validate a single email address with all checks.

**Request Body:**
```json
{
  "email": "user@example.com",
  "check_smtp": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "email": "user@example.com",
    "is_valid": true,
    "is_disposable": false,
    "is_role_based": false,
    "quality_score": 100,
    "checks": {
      "syntax": {
        "valid": true,
        "message": "Valid syntax"
      },
      "domain": {
        "valid": true,
        "message": "Domain has 2 MX record(s)",
        "mx_records": ["alt1.aspmx.l.google.com", "alt2.aspmx.l.google.com"]
      },
      "smtp": {
        "valid": true,
        "message": "Mailbox exists (RCPT TO confirmed)",
        "smtp_response": "250 2.1.5 OK"
      },
      "disposable": {
        "is_disposable": false,
        "message": "Domain example.com is not a disposable email service"
      },
      "role_based": {
        "is_role_based": false,
        "role": null,
        "message": "Email is not role-based"
      }
    }
  }
}
```

### Validate Multiple Emails

```
POST /api/v1/validate/batch
```

Validate multiple emails in a single request.

**Request Body:**
```json
{
  "emails": ["user1@example.com", "user2@example.com", "invalid-email"],
  "check_smtp": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [...],
    "statistics": {
      "total": 3,
      "valid": 2,
      "invalid": 1,
      "disposable": 0,
      "role_based": 0
    }
  }
}
```

### Validate CSV Upload

```
POST /api/v1/validate/csv
```

Upload a CSV file and validate all emails.

**Form Data:**
- `file`: CSV file
- `email_column`: Column name containing emails (default: 'email')
- `check_smtp`: Whether to check SMTP (default: 'true')

**CSV Format:**
```csv
email,name
user1@example.com,John Doe
user2@example.com,Jane Smith
```

**Response:**
```json
{
  "success": true,
  "data": {
    "total_emails": 2,
    "cost": 0.002,
    "pricing": {
      "per_email": 0.001,
      "monthly_50k": 29.0
    },
    "statistics": {
      "valid": 2,
      "invalid": 0,
      "disposable": 0,
      "role_based": 0
    },
    "results": [...]
  }
}
```

### Validate CSV and Download Results

```
POST /api/v1/validate/csv/download
```

Upload a CSV file and download validation results as CSV.

**Form Data:** Same as `/api/v1/validate/csv`

**Response:** Downloads `email_validation_results.csv`

### Get Pricing

```
GET /api/v1/pricing
```

Get current pricing information.

**Response:**
```json
{
  "success": true,
  "data": {
    "per_email": 0.001,
    "monthly_plans": [
      {
        "name": "Pay as you go",
        "emails": 0,
        "price": 0,
        "price_per_email": 0.001
      },
      {
        "name": "Starter",
        "emails": 50000,
        "price": 29.0,
        "price_per_email": 0.00058
      }
    ]
  }
}
```

## Response Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request data
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server error

## Quality Score

Each validation returns a quality score (0-100) based on:

- Valid syntax: +30 points
- Valid domain with MX records: +30 points
- SMTP verified: +30 points (or +15 if inconclusive)
- Disposable email: -30 points
- Role-based email: -10 points

## Usage Examples

### cURL

```bash
# Validate single email
curl -X POST http://localhost:5000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "check_smtp": true}'

# Validate batch
curl -X POST http://localhost:5000/api/v1/validate/batch \
  -H "Content-Type: application/json" \
  -d '{"emails": ["user1@example.com", "user2@example.com"]}'

# Upload CSV
curl -X POST http://localhost:5000/api/v1/validate/csv \
  -F "file=@emails.csv" \
  -F "email_column=email"
```

### Python

```python
import requests

# Validate single email
response = requests.post('http://localhost:5000/api/v1/validate', json={
    'email': 'user@example.com',
    'check_smtp': True
})
result = response.json()

# Validate batch
response = requests.post('http://localhost:5000/validate/batch', json={
    'emails': ['user1@example.com', 'user2@example.com']
})
results = response.json()

# Upload CSV
files = {'file': open('emails.csv', 'rb')}
data = {'email_column': 'email', 'check_smtp': 'true'}
response = requests.post('http://localhost:5000/api/v1/validate/csv', files=files, data=data)
```

### JavaScript

```javascript
// Validate single email
const response = await fetch('http://localhost:5000/api/v1/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    check_smtp: true
  })
});
const result = await response.json();

// Upload CSV
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('email_column', 'email');
formData.append('check_smtp', 'true');

const response = await fetch('http://localhost:5000/api/v1/validate/csv', {
  method: 'POST',
  body: formData
});
const result = await response.json();
```

## Architecture

```
email-validator/
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── requirements.txt                # Python dependencies
├── validators/                     # Validation modules
│   ├── __init__.py
│   ├── syntax_validator.py        # Email syntax validation
│   ├── domain_validator.py        # MX record validation
│   ├── smtp_validator.py          # SMTP mailbox verification
│   ├── disposable_detector.py     # Disposable email detection
│   ├── role_based_detector.py     # Role-based email detection
│   └── email_validator.py         # Main validator orchestrator
├── data/                          # Data files
│   └── disposable_domains.txt     # List of disposable domains
├── tests/                         # Test files
└── README.md                      # This file
```

## Configuration

Edit `config.py` to customize:

- `SECRET_KEY` - Flask secret key
- `MAX_FILE_SIZE` - Maximum CSV upload size (default: 16MB)
- `RATE_LIMIT` - Rate limit per minute
- `SMTP_TIMEOUT` - SMTP connection timeout (default: 10s)
- `MX_TIMEOUT` - DNS query timeout (default: 5s)
- Pricing constants

## Performance

- Single email validation: ~2-5 seconds (with SMTP)
- Batch validation: Parallel processing for efficiency
- CSV upload: Processes large files efficiently

## Security

- Input validation on all endpoints
- CORS enabled for cross-origin requests
- Rate limiting (configurable)
- File size limits on uploads

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License

## Support

For support and questions, please open an issue on GitHub.
