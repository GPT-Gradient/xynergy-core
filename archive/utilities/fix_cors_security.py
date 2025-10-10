#!/usr/bin/env python3
"""
Automated CORS Security Fix Script
Fixes wildcard CORS configuration across all Xynergy platform services.
"""

import os
import re
from pathlib import Path

# Services to fix (excluding documentation files)
SERVICES_TO_FIX = [
    "keyword-revenue-tracker",
    "attribution-coordinator",
    "trust-safety-validator",
    "plagiarism-detector",
    "fact-checking-service",
    "validation-coordinator",
    "automated-publisher",
    "rapid-content-generator",
    "real-time-trend-monitor",
    "trending-engine-coordinator",
    "competitive-analysis-service",
    "market-intelligence-service",
    "research-coordinator",
    "tenant-management",
    "advanced-analytics",
    "ai-workflow-engine",
    "scheduler-automation-engine",
    "system-runtime",
    "ai-ml-engine",
    "reports-export",
    "project-management",
    "content-hub",
    "executive-dashboard",
    "performance-scaling",
    "security-compliance",
    "monetization-integration",
    "xynergy-competency-engine",
    "qa-engine",
    "security-governance",
]

# Secure CORS configuration template
SECURE_CORS_CONFIG = '''# CORS configuration - Production security hardening
ALLOWED_ORIGINS = [
    "https://xynergy-platform.com",
    "https://api.xynergy.dev",
    "https://*.xynergy.com",
    os.getenv("ADDITIONAL_CORS_ORIGIN", "")  # For staging environments
]
# Remove empty strings from list
ALLOWED_ORIGINS = [origin for origin in ALLOWED_ORIGINS if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)'''

# Pattern to find insecure CORS configuration
INSECURE_CORS_PATTERN = re.compile(
    r'app\.add_middleware\s*\(\s*CORSMiddleware\s*,\s*allow_origins\s*=\s*\["\*"\]\s*,\s*allow_credentials\s*=\s*True\s*,\s*allow_methods\s*=\s*\["\*"\]\s*,\s*allow_headers\s*=\s*\["\*"\]\s*,?\s*\)',
    re.MULTILINE | re.DOTALL
)


def fix_cors_in_file(file_path: Path) -> bool:
    """Fix CORS configuration in a single file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Check if file has insecure CORS
        if 'allow_origins=["*"]' not in content:
            print(f"  ✓ {file_path.parent.name}/main.py already secure or no CORS config")
            return False

        # Replace insecure CORS with secure configuration
        new_content = re.sub(
            r'app\.add_middleware\s*\(\s*CORSMiddleware\s*,\s*allow_origins\s*=\s*\["\*"\]\s*,'
            r'\s*allow_credentials\s*=\s*True\s*,\s*allow_methods\s*=\s*\["\*"\]\s*,'
            r'\s*allow_headers\s*=\s*\["\*"\]\s*,?\s*\)',
            SECURE_CORS_CONFIG,
            content,
            flags=re.MULTILINE | re.DOTALL
        )

        if new_content == content:
            print(f"  ⚠ {file_path.parent.name}/main.py - Pattern not matched, manual fix needed")
            return False

        # Write fixed content
        with open(file_path, 'w') as f:
            f.write(new_content)

        print(f"  ✅ {file_path.parent.name}/main.py - CORS fixed")
        return True

    except Exception as e:
        print(f"  ❌ Error fixing {file_path}: {e}")
        return False


def main():
    """Main execution function."""
    platform_root = Path(__file__).parent
    fixed_count = 0
    skipped_count = 0
    error_count = 0

    print("🔒 Xynergy Platform - CORS Security Fix")
    print("=" * 60)
    print(f"Scanning {len(SERVICES_TO_FIX)} services...\n")

    for service_name in SERVICES_TO_FIX:
        service_path = platform_root / service_name / "main.py"

        if not service_path.exists():
            print(f"  ⚠ {service_name}/main.py not found")
            skipped_count += 1
            continue

        result = fix_cors_in_file(service_path)
        if result:
            fixed_count += 1
        elif "Error" in str(result):
            error_count += 1
        else:
            skipped_count += 1

    print("\n" + "=" * 60)
    print(f"✅ Fixed: {fixed_count} services")
    print(f"⚠  Skipped: {skipped_count} services")
    print(f"❌ Errors: {error_count} services")
    print("\n🎯 Next steps:")
    print("  1. Review changes: git diff")
    print("  2. Test health endpoints for each service")
    print("  3. Update ADDITIONAL_CORS_ORIGIN env var for staging")
    print("  4. Deploy and monitor")


if __name__ == "__main__":
    main()
