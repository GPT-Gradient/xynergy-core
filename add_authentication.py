#!/usr/bin/env python3
"""
Add Authentication to Critical Endpoints
Systematically adds API key authentication to sensitive endpoints across all services.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Critical endpoints that MUST have authentication
CRITICAL_ENDPOINT_PATTERNS = [
    r'@app\.post\("/execute"',          # Workflow execution
    r'@app\.post\("/api/generate"',     # AI generation
    r'@app\.post\("/campaigns/create"', # Marketing campaigns
    r'@app\.post\("/api/route"',        # AI routing
    r'@app\.post\("/workflows/create"', # Workflow creation
    r'@app\.post\("/business/execute"', # Business operations
    r'@app\.put\(',                      # All PUT operations
    r'@app\.delete\(',                   # All DELETE operations
]

# Services that need authentication added
SERVICES_NEEDING_AUTH = [
    "marketing-engine",
    "content-hub",
    "system-runtime",
    "project-management",
    "analytics-data-layer",
    "scheduler-automation-engine",
    "reports-export",
]

# Auth import snippet
AUTH_IMPORT = """
# Import centralized authentication
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from auth import verify_api_key, verify_api_key_optional
"""


def check_has_auth_import(content: str) -> bool:
    """Check if file already has auth import."""
    return "from auth import" in content or "verify_api_key" in content


def add_auth_import(content: str) -> str:
    """Add auth import after other imports."""
    # Find the last import statement
    import_pattern = r'(from\s+\w+\s+import\s+[^\n]+|import\s+[^\n]+)'
    matches = list(re.finditer(import_pattern, content))

    if not matches:
        return content

    # Insert after last import
    last_import_end = matches[-1].end()
    return content[:last_import_end] + "\n" + AUTH_IMPORT + content[last_import_end:]


def add_auth_to_endpoint(content: str, endpoint_pattern: str) -> Tuple[str, int]:
    """
    Add authentication dependency to endpoints matching pattern.

    Returns:
        Tuple of (modified_content, number_of_endpoints_modified)
    """
    count = 0

    # Find endpoints matching pattern
    pattern = rf'({endpoint_pattern}[^)]*\))'
    matches = list(re.finditer(pattern, content))

    for match in reversed(matches):  # Reverse to maintain positions
        endpoint_def = match.group(1)

        # Skip if already has dependencies with verify_api_key
        if "dependencies=[Depends(verify_api_key)]" in endpoint_def:
            continue

        # Check if it has dependencies parameter
        if "dependencies=" in endpoint_def:
            # Has dependencies, need to add to existing list
            # This is complex, skip for manual review
            continue

        # Add dependencies parameter before closing paren
        new_endpoint = endpoint_def.replace(
            ")",
            ", dependencies=[Depends(verify_api_key)])"
        )

        content = content[:match.start()] + new_endpoint + content[match.end():]
        count += 1

    return content, count


def process_service(service_path: Path) -> dict:
    """Process a single service file."""
    result = {
        "service": service_path.parent.name,
        "auth_import_added": False,
        "endpoints_secured": 0,
        "errors": []
    }

    try:
        with open(service_path, 'r') as f:
            content = f.read()

        original_content = content
        modified = False

        # Add auth import if needed
        if not check_has_auth_import(content):
            # Check if it needs Depends import
            if "from fastapi import" in content and "Depends" not in content:
                # Add Depends to FastAPI import
                content = re.sub(
                    r'(from fastapi import [^)]+)(\))',
                    r'\1, Depends\2',
                    content
                )
                if "from fastapi import" in content and ")" not in content:
                    # Single line import
                    content = re.sub(
                        r'(from fastapi import [^\n]+)',
                        r'\1, Depends',
                        content,
                        count=1
                    )

            content = add_auth_import(content)
            result["auth_import_added"] = True
            modified = True

        # Add auth to critical endpoints
        for pattern in CRITICAL_ENDPOINT_PATTERNS:
            new_content, count = add_auth_to_endpoint(content, pattern)
            if count > 0:
                content = new_content
                result["endpoints_secured"] += count
                modified = True

        # Write back if modified
        if modified and content != original_content:
            with open(service_path, 'w') as f:
                f.write(content)

    except Exception as e:
        result["errors"].append(str(e))

    return result


def main():
    """Main execution function."""
    platform_root = Path(__file__).parent

    print("🔐 Xynergy Platform - Authentication Hardening")
    print("=" * 60)
    print(f"Adding authentication to {len(SERVICES_NEEDING_AUTH)} services...\n")

    results = []

    for service_name in SERVICES_NEEDING_AUTH:
        service_path = platform_root / service_name / "main.py"

        if not service_path.exists():
            print(f"  ⚠ {service_name}/main.py not found")
            continue

        print(f"Processing {service_name}...")
        result = process_service(service_path)
        results.append(result)

        if result["errors"]:
            print(f"  ❌ Errors: {', '.join(result['errors'])}")
        else:
            if result["auth_import_added"]:
                print(f"  ✅ Added auth import")
            if result["endpoints_secured"] > 0:
                print(f"  ✅ Secured {result['endpoints_secured']} endpoint(s)")
            if not result["auth_import_added"] and result["endpoints_secured"] == 0:
                print(f"  ✓ Already secured or no critical endpoints")

    print("\n" + "=" * 60)
    total_imports = sum(1 for r in results if r["auth_import_added"])
    total_secured = sum(r["endpoints_secured"] for r in results)
    total_errors = sum(len(r["errors"]) for r in results)

    print(f"✅ Auth imports added: {total_imports}")
    print(f"✅ Endpoints secured: {total_secured}")
    print(f"❌ Errors: {total_errors}")

    print("\n🎯 Next steps:")
    print("  1. Review changes: git diff")
    print("  2. Manually secure endpoints with complex decorators")
    print("  3. Set XYNERGY_API_KEYS environment variable")
    print("  4. Test each service with/without API key")
    print("  5. Update API documentation with auth requirements")


if __name__ == "__main__":
    main()
