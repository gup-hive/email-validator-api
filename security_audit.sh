#!/bin/bash

# Email Validator API - Security Audit Script
# Run this script to verify security requirements before deployment

echo "🔒 Email Validator API - Security Audit"
echo "====================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ $1 exists${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 missing${NC}"
        return 1
    fi
}

# Function to check for hardcoded secrets
check_secrets() {
    echo ""
    echo "🔍 Checking for hardcoded secrets..."
    
    # Check for common secrets patterns
    patterns=(
        "password\s*=\s*['\"][^'\"]*['\"]"
        "api_key\s*=\s*['\"][^'\"]*['\"]"
        "secret\s*=\s*['\"][^'\"]*['\"]"
        "token\s*=\s*['\"][^'\"]*['\"]"
        "private_key\s*=\s*['\"][^'\"]*['\"]"
        "password\s*=\s*[0-9a-zA-Z]{10,}"
        "api_key\s*=\s*[0-9a-zA-Z]{10,}"
    )
    
    found_issues=0
    
    for file in app*.py config.py; do
        if [ -f "$file" ]; then
            echo "  Checking $file..."
            for pattern in "${patterns[@]}"; do
                if grep -E -i "$pattern" "$file" >/dev/null 2>&1; then
                    echo -e "    ${RED}⚠️  Potential hardcoded secret found:${NC}"
                    grep -n -E -i "$pattern" "$file"
                    found_issues=1
                fi
            done
        fi
    done
    
    if [ $found_issues -eq 0 ]; then
        echo -e "  ${GREEN}✅ No hardcoded secrets found${NC}"
    fi
}

# Function to check for TODO and FIXME comments
check_todo_comments() {
    echo ""
    echo "🔍 Checking for incomplete code (TODO/FIXME)..."
    
    todo_count=$(grep -r -i "TODO\|FIXME\|XXX" --include="*.py" --include="*.md" . | wc -l)
    
    if [ $todo_count -gt 0 ]; then
        echo -e "  ${YELLOW}⚠️  Found $todo_count TODO/FIXME comments:${NC}"
        grep -r -i "TODO\|FIXME\|XXX" --include="*.py" --include="*.md" .
    else
        echo -e "  ${GREEN}✅ No TODO/FIXME comments found${NC}"
    fi
}

# Function to check input validation
check_input_validation() {
    echo ""
    echo "🔍 Checking input validation..."
    
    # Check for basic input validation in main app file
    if [ -f "app.py" ] || [ -f "app_secure.py" ]; then
        app_file=$(ls app*.py | head -1)
        echo "  Checking $app_file..."
        
        # Check for email validation
        if grep -i "validate.*email\|email.*validate" "$app_file" >/dev/null; then
            echo -e "  ${GREEN}✅ Email validation found${NC}"
        else
            echo -e "  ${RED}❌ Email validation missing${NC}"
        fi
        
        # Check for rate limiting
        if grep -i "rate.*limit\|limit.*rate" "$app_file" >/dev/null; then
            echo -e "  ${GREEN}✅ Rate limiting found${NC}"
        else
            echo -e "  ${RED}❌ Rate limiting missing${NC}"
        fi
        
        # Check for authentication
        if grep -i "api.*key\|auth\|token" "$app_file" >/dev/null; then
            echo -e "  ${GREEN}✅ Authentication found${NC}"
        else
            echo -e "  ${RED}❌ Authentication missing${NC}"
        fi
    fi
}

# Function to check file permissions
check_permissions() {
    echo ""
    echo "🔍 Checking file permissions..."
    
    # Check for sensitive files
    sensitive_files=(".env" ".env.example" "config.py")
    
    for file in "${sensitive_files[@]}"; do
        if [ -f "$file" ]; then
            perms=$(stat -c "%a" "$file")
            if [[ "$perms" == "644" ]]; then
                echo -e "  ${GREEN}✅ $file has safe permissions ($perms)${NC}"
            else
                echo -e "  ${YELLOW}⚠️  $file has unrestricted permissions ($perms)${NC}"
            fi
        fi
    done
}

# Function to check dependency security
check_dependencies() {
    echo ""
    echo "🔍 Checking dependency security..."
    
    if [ -f "requirements.txt" ]; then
        echo "  Checking for known vulnerabilities..."
        
        # Check if pip-audit is available
        if command -v pip-audit >/dev/null 2>&1; then
            echo "  Running pip-audit..."
            pip-audit --path .
        else
            echo "  ${YELLOW}⚠️  pip-audit not available, skipping vulnerability check${NC}"
            echo "  Install with: pip install pip-audit"
        fi
    else
        echo -e "  ${RED}❌ requirements.txt not found${NC}"
    fi
}

# Function to check API documentation
check_api_docs() {
    echo ""
    echo "🔍 Checking API documentation..."
    
    doc_files=("README.md" "API.md" "API_EXAMPLES.md")
    
    for file in "${doc_files[@]}"; do
        if check_file "$file"; then
            # Check if API endpoints are documented
            if grep -i "api.*endpoint\|endpoint.*api" "$file" >/dev/null; then
                echo -e "  ${GREEN}✅ API endpoints documented${NC}"
            else
                echo -e "  ${YELLOW}⚠️  API endpoints not well documented${NC}"
            fi
        fi
    done
}

# Function to check Docker security
check_docker() {
    echo ""
    echo "🔍 Checking Docker configuration..."
    
    if check_file "Dockerfile"; then
        # Check for non-root user
        if grep -i "user.*[0-9]\|user.*nobody" "Dockerfile" >/dev/null; then
            echo -e "  ${GREEN}✅ Non-root user configured${NC}"
        else
            echo -e "  ${YELLOW}⚠️  Consider running as non-root user${NC}"
        fi
        
        # Check for latest tag
        if grep -i "latest" "Dockerfile" >/dev/null; then
            echo -e "  ${YELLOW}⚠️  Using 'latest' tag (consider specific version)${NC}"
        else
            echo -e "  ${GREEN}✅ Using specific version tags${NC}"
        fi
    fi
}

# Function to check environment files
check_env_files() {
    echo ""
    echo "🔍 Checking environment configuration..."
    
    if check_file ".env.example"; then
        # Check if .env is in .gitignore
        if grep -q "\.env" ".gitignore" 2>/dev/null; then
            echo -e "  ${GREEN}✅ .env file ignored by git${NC}"
        else
            echo -e "  ${RED}❌ .env file not in .gitignore${NC}"
        fi
    fi
}

# Main audit process
echo ""
echo "🚀 Starting security audit..."
echo ""

# Check required files
echo "📁 Checking required files:"
check_file "app.py" || check_file "app_secure.py"
check_file "requirements.txt"
check_file "Dockerfile"
check_file "docker-compose.yml"
check_file ".env.example"
check_file "README.md"
check_file "metadata.json"

echo ""
echo "🔒 Running security checks..."
check_secrets
check_todo_comments
check_input_validation
check_permissions
check_dependencies
check_api_docs
check_docker
check_env_files

echo ""
echo "📊 Security Audit Summary"
echo "========================"

# Check if security version exists
if [ -f "app_secure.py" ]; then
    echo -e "${GREEN}✅ Secure version available (app_secure.py)${NC}"
else
    echo -e "${YELLOW}⚠️  Consider creating secure version${NC}"
fi

# Final recommendation
echo ""
echo "🎯 Recommendations:"
echo "1. Always use app_secure.py in production"
echo "2. Set strong API keys in production"
echo "3. Configure proper rate limiting"
echo "4. Set up HTTPS in production"
echo "5. Monitor API usage and abuse"
echo "6. Keep dependencies updated"

echo ""
echo "Audit completed! 🎉"