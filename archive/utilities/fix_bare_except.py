#!/usr/bin/env python3
"""
Fix bare except clauses in Python files.
Phase 3: Reliability & Monitoring

Replaces dangerous bare 'except:' with specific exception types.
"""

import re
import os
import sys

FILES_TO_FIX = [
    "ai-workflow-engine/main.py",
    "advanced-analytics/main.py",
    "real-time-trend-monitor/main.py",
    "automated-publisher/main.py",
    "trending-engine-coordinator/main.py",
    "rapid-content-generator/main.py",
    "ai-ml-engine/main.py",
    "system-runtime/main.py"
]


def fix_bare_except_in_file(file_path: str) -> bool:
    """
    Fix bare except clauses in a single file.

    Returns:
        True if changes were made, False otherwise
    """
    if not os.path.exists(file_path):
        print(f"⚠️  File not found: {file_path}")
        return False

    with open(file_path, 'r') as f:
        content = f.read()

    original = content
    lines = content.split('\n')
    modified_lines = []
    changes_made = 0

    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line has a bare except
        if re.match(r'^\s*except\s*:\s*(?:#.*)?$', line):
            # Get the indentation
            indent_match = re.match(r'^(\s*)except', line)
            indent = indent_match.group(1) if indent_match else ''

            # Check the next line to understand context
            next_line = lines[i + 1] if i + 1 < len(lines) else ""

            # Special case: WebSocket disconnect handling
            if 'active_connections.remove' in next_line or 'WebSocket' in next_line:
                replacement = f"{indent}except (WebSocketDisconnect, RuntimeError, ValueError):"
                modified_lines.append(replacement + "  # Phase 3: Specific exception handling")
                changes_made += 1
                print(f"  Line {i+1}: WebSocket disconnect pattern → specific exceptions")

            # Special case: Logging or error handling
            elif 'log' in next_line.lower() or 'print' in next_line.lower() or 'error' in next_line.lower():
                replacement = f"{indent}except Exception as e:"
                modified_lines.append(replacement + "  # Phase 3: Catch-all with logging")
                changes_made += 1
                print(f"  Line {i+1}: Logging pattern → Exception with variable")

            # General case
            else:
                replacement = f"{indent}except Exception as e:"
                modified_lines.append(replacement + "  # Phase 3: Specific exception handling")
                changes_made += 1
                print(f"  Line {i+1}: Bare except → Exception")
        else:
            modified_lines.append(line)

        i += 1

    if changes_made > 0:
        # Write the modified content
        new_content = '\n'.join(modified_lines)
        with open(file_path, 'w') as f:
            f.write(new_content)
        print(f"✅ Fixed {changes_made} bare except clause(s) in {file_path}")
        return True
    else:
        print(f"✓  No bare except clauses found in {file_path}")
        return False


def main():
    """Run the fix script on all target files."""
    print("=" * 60)
    print("Fixing Bare Except Clauses - Phase 3")
    print("=" * 60)
    print()

    total_files = 0
    total_changes = 0

    for file_path in FILES_TO_FIX:
        print(f"\nProcessing: {file_path}")
        print("-" * 60)

        if fix_bare_except_in_file(file_path):
            total_files += 1

    print()
    print("=" * 60)
    print(f"Summary: Fixed bare except clauses in {total_files} file(s)")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
