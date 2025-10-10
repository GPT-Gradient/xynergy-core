#!/usr/bin/env python3
"""
Script to add tenant isolation to all Xynergy platform services.
This script automatically updates service main.py files to include tenant awareness.
"""

import os
import re
from pathlib import Path

def add_tenant_imports(content):
    """Add tenant utility imports to the service"""
    # Find the import section
    import_pattern = r'(from phase2_utils import.*)'

    tenant_imports = '''
# Add shared modules to path
sys.path.append('/Users/sesloan/Dev/xynergy-platform/shared')

# Import Phase 2 utilities
from phase2_utils import PerformanceMonitor, CircuitBreaker, CircuitBreakerConfig
# Import tenant utilities
from tenant_utils import (
    TenantContext, get_tenant_context, require_tenant, check_feature_access,
    check_resource_limits, get_tenant_aware_firestore, add_tenant_middleware
)'''

    if 'from phase2_utils import' in content:
        content = re.sub(
            r'# Import Phase 2 utilities\nfrom phase2_utils import.*',
            tenant_imports,
            content
        )

    # Add sys import if not present
    if 'import sys' not in content:
        content = re.sub(
            r'(import os)',
            r'\1\nimport sys',
            content
        )

    # Add Depends import to FastAPI imports
    if 'from fastapi import' in content and 'Depends' not in content:
        content = re.sub(
            r'from fastapi import ([^,\n]+)',
            r'from fastapi import \1, Depends',
            content
        )

    return content

def add_tenant_middleware(content):
    """Add tenant middleware to the FastAPI app"""
    middleware_code = '''
# Add tenant isolation middleware
add_tenant_middleware(app)'''

    # Find CORS middleware section and add tenant middleware after it
    if 'CORSMiddleware' in content:
        content = re.sub(
            r'(\)\n\n# Configure logging)',
            r')\n' + middleware_code + r'\n\n# Configure logging',
            content
        )

    return content

def add_tenant_db_client(content):
    """Add tenant-aware Firestore client"""
    if 'db = firestore.Client()' in content:
        content = content.replace(
            'db = firestore.Client()',
            'db = firestore.Client()\ntenant_db = get_tenant_aware_firestore(db)'
        )

    return content

def update_service_endpoints(content, service_name):
    """Update service endpoints to include tenant awareness"""

    # Common patterns for endpoints that need tenant isolation
    endpoint_patterns = [
        r'@app\.post\("/[^"]*create[^"]*"\)',
        r'@app\.post\("/[^"]*add[^"]*"\)',
        r'@app\.post\("/[^"]*execute[^"]*"\)',
        r'@app\.get\("/[^"]*list[^"]*"\)',
        r'@app\.get\("/[^"]*dashboard[^"]*"\)'
    ]

    for pattern in endpoint_patterns:
        matches = re.finditer(pattern, content)
        for match in matches:
            # Skip health endpoints
            if '/health' in match.group():
                continue

            endpoint_line = match.group()

            # Add tenant decorators and dependencies
            tenant_decorators = f'''@require_tenant()
@check_feature_access("{service_name}")
{endpoint_line}'''

            content = content.replace(endpoint_line, tenant_decorators)

    # Update function signatures to include tenant context
    function_pattern = r'async def ([^(]+)\(([^)]*)\):'

    def add_tenant_param(match):
        func_name = match.group(1)
        params = match.group(2)

        # Skip health check and system functions
        if 'health' in func_name or 'status' in func_name:
            return match.group()

        # Add tenant context parameter
        if 'tenant_context' not in params:
            if params.strip():
                new_params = f"{params},\n    tenant_context: Optional[TenantContext] = Depends(get_tenant_context)"
            else:
                new_params = "tenant_context: Optional[TenantContext] = Depends(get_tenant_context)"

            return f"async def {func_name}({new_params}):"

        return match.group()

    content = re.sub(function_pattern, add_tenant_param, content)

    return content

def update_data_operations(content):
    """Update Firestore operations to use tenant-aware collections"""

    # Replace db.collection with tenant_db.collection
    content = re.sub(
        r'db\.collection\("([^"]+)"\)',
        r'tenant_db.collection("\1")',
        content
    )

    # Add tenant_id to document creation
    doc_creation_pattern = r'(\w+_doc = \{[^}]*)"([^"]*)":'

    def add_tenant_id(match):
        doc_content = match.group(1)
        if 'tenant_id' not in doc_content:
            return doc_content + '"tenant_id": tenant_context.tenant_id if tenant_context else None,\n                '
        return match.group()

    content = re.sub(doc_creation_pattern, add_tenant_id, content)

    return content

def process_service(service_path):
    """Process a single service to add tenant isolation"""
    print(f"Processing {service_path}...")

    with open(service_path, 'r') as f:
        content = f.read()

    # Skip if already has tenant utilities
    if 'tenant_utils' in content:
        print(f"  {service_path} already has tenant isolation")
        return

    service_name = Path(service_path).parent.name.replace('-', '_')

    # Apply transformations
    content = add_tenant_imports(content)
    content = add_tenant_middleware(content)
    content = add_tenant_db_client(content)
    content = update_service_endpoints(content, service_name)
    content = update_data_operations(content)

    # Create backup
    backup_path = service_path + '.backup'
    with open(backup_path, 'w') as f:
        f.write(open(service_path, 'r').read())

    # Write updated content
    with open(service_path, 'w') as f:
        f.write(content)

    print(f"  Updated {service_path} (backup: {backup_path})")

def main():
    """Main function to process all services"""
    platform_root = Path('/Users/sesloan/Dev/xynergy-platform')

    # Find all service main.py files
    service_files = []
    for service_dir in platform_root.iterdir():
        if service_dir.is_dir() and service_dir.name not in [
            'shared', 'tenant-management', 'executive-dashboard', 'terraform', '.git'
        ]:
            main_py = service_dir / 'main.py'
            if main_py.exists():
                service_files.append(str(main_py))

    print(f"Found {len(service_files)} services to update:")
    for service_file in service_files:
        print(f"  {service_file}")

    print("\nStarting tenant isolation updates...")

    for service_file in service_files:
        try:
            process_service(service_file)
        except Exception as e:
            print(f"  Error processing {service_file}: {e}")

    print("\nTenant isolation update completed!")
    print("\nNext steps:")
    print("1. Copy shared/tenant_utils.py to each service directory")
    print("2. Test each service individually")
    print("3. Deploy updated services")

if __name__ == "__main__":
    main()