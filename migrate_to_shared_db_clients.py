#!/usr/bin/env python3
"""
Migrate services to use shared GCP database clients.
Phase 4: Database Optimization

Replaces direct client instantiation with shared connection pooling.
"""

import re
import os
import sys

# Services to migrate
SERVICES_TO_MIGRATE = [
    "executive-dashboard/main.py",
    "ai-workflow-engine/main.py",
    "advanced-analytics/main.py",
    "performance-scaling/main.py",
    "content-hub/main.py",
    "trending-engine-coordinator/main.py",
    "qa-engine/main.py",
    "market-intelligence-service/main.py",
    "project-management/main.py",
    "xynergy-competency-engine/main.py",
    "real-time-trend-monitor/main.py",
    "automated-publisher/main.py",
    "internal-ai-service/main.py",
    "monetization-integration/main.py",
    "reports-export/main.py",
    "system-runtime/main.py",
    "rapid-content-generator/main.py",
    "scheduler-automation-engine/main.py",
    "marketing-engine/main.py",
    "ai-assistant/main.py",
]


def migrate_service_to_shared_clients(file_path: str) -> bool:
    """
    Migrate a service to use shared GCP clients.

    Returns:
        True if changes were made, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False

    with open(file_path, 'r') as f:
        content = f.read()

    original = content
    changes_made = 0

    # Step 1: Add shared client imports if not present
    if "from gcp_clients import" not in content and ("firestore.Client()" in content or "bigquery.Client()" in content):
        # Find the imports section
        import_section_match = re.search(r'(from google\.cloud import.*?\n)', content)
        if import_section_match:
            # Add shared imports after GCP imports
            insert_pos = import_section_match.end()
            shared_imports = """
# Phase 4: Shared database client imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from gcp_clients import get_firestore_client, get_bigquery_client, get_publisher_client, gcp_clients

"""
            # Only add if not already present
            if "from gcp_clients import" not in content:
                content = content[:insert_pos] + shared_imports + content[insert_pos:]
                changes_made += 1
                print(f"  Added shared client imports")

    # Step 2: Replace Firestore client instantiation
    firestore_pattern = r'^db = firestore\.Client\(\)'
    if re.search(firestore_pattern, content, re.MULTILINE):
        content = re.sub(
            firestore_pattern,
            'db = get_firestore_client()  # Phase 4: Shared connection pooling',
            content,
            flags=re.MULTILINE
        )
        changes_made += 1
        print(f"  Replaced Firestore client with shared client")

    # Step 3: Replace BigQuery client instantiation
    bigquery_pattern = r'^bigquery_client = bigquery\.Client\(\)'
    if re.search(bigquery_pattern, content, re.MULTILINE):
        content = re.sub(
            bigquery_pattern,
            'bigquery_client = get_bigquery_client()  # Phase 4: Shared connection pooling',
            content,
            flags=re.MULTILINE
        )
        changes_made += 1
        print(f"  Replaced BigQuery client with shared client")

    # Step 4: Replace Publisher client instantiation
    publisher_pattern = r'^publisher = pubsub_v1\.PublisherClient\(\)'
    if re.search(publisher_pattern, content, re.MULTILINE):
        content = re.sub(
            publisher_pattern,
            'publisher = get_publisher_client()  # Phase 4: Shared connection pooling',
            content,
            flags=re.MULTILINE
        )
        changes_made += 1
        print(f"  Replaced Publisher client with shared client")

    # Step 5: Add shutdown handler if not present
    if changes_made > 0 and '@app.on_event("shutdown")' not in content:
        # Find the end of the file before if __name__ == "__main__"
        main_match = re.search(r'if __name__ == "__main__":', content)
        if main_match:
            insert_pos = main_match.start()
            shutdown_handler = '''
@app.on_event("shutdown")
async def shutdown_event():
    """Clean up shared database connections - Phase 4: Connection pooling"""
    gcp_clients.close_all_connections()

'''
            content = content[:insert_pos] + shutdown_handler + content[insert_pos:]
            changes_made += 1
            print(f"  Added shutdown handler for connection cleanup")

    if changes_made > 0:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✅ Migrated {file_path} ({changes_made} changes)")
        return True
    else:
        print(f"✓  No migration needed for {file_path}")
        return False


def main():
    """Run the migration script on all target services."""
    print("=" * 60)
    print("Database Client Migration - Phase 4")
    print("=" * 60)
    print()

    total_migrated = 0
    total_files = 0

    for file_path in SERVICES_TO_MIGRATE:
        print(f"\nProcessing: {file_path}")
        print("-" * 60)

        if migrate_service_to_shared_clients(file_path):
            total_migrated += 1
        total_files += 1

    print()
    print("=" * 60)
    print(f"Summary: Migrated {total_migrated}/{total_files} services")
    print("=" * 60)
    print()
    print("Benefits:")
    print("  ✅ Reduced connection overhead")
    print("  ✅ Better resource utilization")
    print("  ✅ Automatic connection cleanup")
    print("  ✅ Thread-safe client access")
    print()
    print("Expected savings: $200-400/month")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
