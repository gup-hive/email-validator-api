# Email Validator API - Examples

This file contains example API calls for the Email Validator API.

## Base URL

```
http://localhost:5000
```

## Health Check

### Request

```bash
curl http://localhost:5000/health
```

### Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Validate Single Email

### Request

```bash
curl -X POST http://localhost:5000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "check_smtp": true
  }'
```

### Response

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

---

## Validate Without SMTP Check

### Request

```bash
curl -X POST http://localhost:5000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "check_smtp": false
  }'
```

### Response

Same format as above, but SMTP check is skipped (faster).

---

## Validate Multiple Emails (Batch)

### Request

```bash
curl -X POST http://localhost:5000/api/v1/validate/batch \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "user1@example.com",
      "user2@example.com",
      "admin@example.com",
      "test@tempmail.com"
    ],
    "check_smtp": false
  }'
```

### Response

```json
{
  "success": true,
  "data": {
    "results": [
      {
        "email": "user1@example.com",
        "is_valid": true,
        "quality_score": 75,
        "is_disposable": false,
        "is_role_based": false,
        "checks": { ... }
      },
      {
        "email": "user2@example.com",
        "is_valid": true,
        "quality_score": 75,
        "is_disposable": false,
        "is_role_based": false,
        "checks": { ... }
      },
      {
        "email": "admin@example.com",
        "is_valid": true,
        "quality_score": 65,
        "is_disposable": false,
        "is_role_based": true,
        "checks": { ... }
      },
      {
        "email": "test@tempmail.com",
        "is_valid": true,
        "quality_score": 45,
        "is_disposable": true,
        "is_role_based": false,
        "checks": { ... }
      }
    ],
    "statistics": {
      "total": 4,
      "valid": 4,
      "invalid": 0,
      "disposable": 1,
      "role_based": 1
    }
  }
}
```

---

## Upload CSV File

### Request

```bash
curl -X POST http://localhost:5000/api/v1/validate/csv \
  -F "file=@data/sample_emails.csv" \
  -F "email_column=email" \
  -F "check_smtp=false"
```

### Response

```json
{
  "success": true,
  "data": {
    "total_emails": 10,
    "cost": 0.01,
    "pricing": {
      "per_email": 0.001,
      "monthly_50k": 29.0
    },
    "statistics": {
      "valid": 8,
      "invalid": 2,
      "disposable": 1,
      "role_based": 5
    },
    "results": [
      {
        "email": "john.doe@example.com",
        "is_valid": true,
        "quality_score": 75,
        "checks": { ... }
      },
      ...
    ],
    "note": "Showing first 100 of 10 results. Use /api/v1/validate/csv/download to download full results."
  }
}
```

---

## Upload CSV and Download Results

### Request

```bash
curl -X POST http://localhost:5000/api/v1/validate/csv/download \
  -F "file=@data/sample_emails.csv" \
  -F "email_column=email" \
  -F "check_smtp=false" \
  -o results.csv
```

### Response

Downloads a CSV file named `results.csv` with all validation results.

### CSV Format

```csv
email,is_valid,quality_score,is_disposable,is_role_based,syntax_valid,domain_valid,smtp_valid,syntax_message,domain_message,smtp_message
john.doe@example.com,True,75,False,False,True,True,None,Valid syntax,Domain has 1 MX record(s),SMTP check skipped
jane.smith@example.com,True,75,False,False,True,True,None,Valid syntax,Domain has 1 MX record(s),SMTP check skipped
admin@example.com,True,65,False,True,True,True,None,Valid syntax,Domain has 1 MX record(s),SMTP check skipped
```

---

## Get Pricing

### Request

```bash
curl http://localhost:5000/api/v1/pricing
```

### Response

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

---

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "error": "Missing email in request body"
}
```

### 404 Not Found

```json
{
  "success": false,
  "error": "Endpoint not found"
}
```

### 500 Internal Server Error

```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

## Quality Score Interpretation

| Score | Quality | Description |
|-------|---------|-------------|
| 90-100 | Excellent | All checks passed, not disposable, not role-based |
| 70-89  | Good     | Most checks passed, maybe role-based |
| 50-69  | Fair     | Valid but disposable or role-based |
| 30-49  | Poor     | Valid domain but disposable |
| 0-29   | Bad      | Invalid syntax or no MX records |

---

## Tips for Integration

1. **Start without SMTP**: Set `check_smtp: false` for faster initial validation
2. **Use batch for large lists**: Process up to 1000 emails per request
3. **Download results**: Use `/csv/download` for large CSV files
4. **Monitor quality scores**: Filter emails based on your minimum score threshold
5. **Handle disposable emails**: Decide whether to exclude them from your lists

---

## Python Integration Example

```python
import requests
import pandas as pd

class EmailValidatorClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def validate_email(self, email, check_smtp=False):
        """Validate a single email"""
        response = requests.post(
            f"{self.base_url}/api/v1/validate",
            json={"email": email, "check_smtp": check_smtp}
        )
        return response.json()
    
    def validate_batch(self, emails, check_smtp=False):
        """Validate multiple emails"""
        response = requests.post(
            f"{self.base_url}/api/v1/validate/batch",
            json={"emails": emails, "check_smtp": check_smtp}
        )
        return response.json()
    
    def validate_csv_file(self, file_path, email_column="email", check_smtp=False):
        """Validate emails from a CSV file"""
        with open(file_path, 'rb') as f:
            response = requests.post(
                f"{self.base_url}/api/v1/validate/csv",
                files={"file": f},
                data={"email_column": email_column, "check_smtp": str(check_smtp).lower()}
            )
        return response.json()

# Usage
client = EmailValidatorClient()

# Single email
result = client.validate_email("user@example.com")
print(result['data']['is_valid'])  # True

# Batch
results = client.validate_batch(["user1@example.com", "user2@example.com"])
print(results['data']['statistics']['valid'])  # 2
```
