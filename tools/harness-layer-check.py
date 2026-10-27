#!/usr/bin/env python3
"""
Harness Layer Conformance Check Tool

Read-only verification of workspace conformance to Harness Layer SPEC v0.1.
Usage: python3 tools/harness-layer-check.py <workspace-dir> [--project <dir>]
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import date


def check_l0_files(workspace: Path) -> list:
    """Check L0 required files exist and size budget."""
    results = []
    required = ['SOUL.md', 'IDENTITY.md', 'USER.md', 'AGENTS.md']
    missing = []
    total_size = 0
    
    for fname in required:
        fpath = workspace / fname
        if fpath.exists():
            size = fpath.stat().st_size
            total_size += size
            results.append(('PASS', f'L0-FILES {fname} exists ({size} bytes)'))
        else:
            missing.append(fname)
            results.append(('FAIL', f'L0-FILES {fname} missing'))
    
    # L0-SIZE check
    if total_size > 12288:
        results.append(('FAIL', f'L0-SIZE total {total_size} bytes > 12288'))
    else:
        results.append(('PASS', f'L0-SIZE total {total_size} bytes <= 12288'))
    
    return results


def check_l2_files(workspace: Path) -> list:
    """Check L2 required files and size budget."""
    results = []
    
    # MEMORY.md
    memory_path = workspace / 'MEMORY.md'
    if memory_path.exists():
        size = memory_path.stat().st_size
        if size > 32768:
            results.append(('FAIL', f'L2-SIZE MEMORY.md {size} bytes > 32768'))
        else:
            results.append(('PASS', f'L2-SIZE MEMORY.md {size} bytes <= 32768'))
        results.append(('PASS', 'L2-FILES MEMORY.md exists'))
    else:
        results.append(('FAIL', 'L2-FILES MEMORY.md missing'))
    
    # memory/ folder
    memory_dir = workspace / 'memory'
    if memory_dir.exists() and memory_dir.is_dir():
        results.append(('PASS', 'L2-FILES memory/ directory exists'))
    else:
        results.append(('FAIL', 'L2-FILES memory/ directory missing'))
    
    return results


def check_l3_state(workspace: Path) -> list:
    """Check STATE files are <= 15 lines."""
    results = []
    
    # Find STATE*.md in root and 1 level subdirectories (skip .git)
    state_files = []
    
    # Root level
    for f in workspace.glob('STATE*.md'):
        if '.git' not in f.parts:
            state_files.append(f)
    
    # 1 level subdirectories
    for subdir in workspace.iterdir():
        if subdir.is_dir() and subdir.name != '.git':
            for f in subdir.glob('STATE*.md'):
                state_files.append(f)
    
    if not state_files:
        results.append(('WARN', 'L3-STATE no STATE*.md files found'))
    else:
        for f in state_files:
            try:
                lines = f.read_text(encoding='utf-8').splitlines()
                line_count = len(lines)
                if line_count > 15:
                    results.append(('FAIL', f'L3-STATE {f.relative_to(workspace)} has {line_count} lines > 15'))
                else:
                    results.append(('PASS', f'L3-STATE {f.relative_to(workspace)} has {line_count} lines <= 15'))
            except Exception as e:
                results.append(('FAIL', f'L3-STATE {f.relative_to(workspace)} read error: {e}'))
    
    return results


def check_l3_decisions(workspace: Path, project_dir: Path | None) -> list:
    """Check DECISIONS.md exists."""
    results = []
    
    if project_dir:
        decisions_path = project_dir / 'DECISIONS.md'
        if decisions_path.exists():
            results.append(('PASS', f'L3-DECISIONS {decisions_path.relative_to(workspace)} exists'))
        else:
            results.append(('FAIL', f'L3-DECISIONS {decisions_path.relative_to(workspace)} missing (required with --project)'))
    else:
        decisions_path = workspace / 'DECISIONS.md'
        if decisions_path.exists():
            results.append(('PASS', 'L3-DECISIONS DECISIONS.md exists in workspace root'))
        else:
            results.append(('WARN', 'L3-DECISIONS DECISIONS.md missing in workspace root (no --project given)'))
    
    return results


def check_l2_daily(workspace: Path) -> list:
    """Check today's daily note exists (WARN only)."""
    results = []
    today = date.today().strftime('%Y-%m-%d')
    daily_path = workspace / 'memory' / f'{today}.md'
    
    if daily_path.exists():
        results.append(('PASS', f'L2-DAILY memory/{today}.md exists'))
    else:
        results.append(('WARN', f'L2-DAILY memory/{today}.md not found'))
    
    return results


def check_l4_log(workspace: Path) -> list:
    """Check L4 log exists (WARN only)."""
    results = []
    
    sessions_dir = workspace / 'sessions'
    history_file = workspace / 'history.jsonl'
    memory_history_file = workspace / 'memory' / 'history.jsonl'

    if sessions_dir.exists() and sessions_dir.is_dir():
        results.append(('PASS', 'L4-LOG sessions/ directory exists'))
    elif history_file.exists():
        results.append(('PASS', 'L4-LOG history.jsonl exists'))
    elif memory_history_file.exists():
        results.append(('PASS', 'L4-LOG memory/history.jsonl exists'))
    else:
        results.append(('WARN', 'L4-LOG no sessions/ directory or history.jsonl found'))
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Harness Layer Conformance Check')
    parser.add_argument('workspace', help='Workspace directory to check')
    parser.add_argument('--project', help='Project directory (relative to workspace)')
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        sys.exit(2)
    
    workspace = Path(args.workspace).resolve()
    
    if not workspace.exists() or not workspace.is_dir():
        print(f'ERROR: Workspace not found: {workspace}', file=sys.stderr)
        sys.exit(2)
    
    project_dir = None
    if args.project:
        project_dir = (workspace / args.project).resolve()
        if not project_dir.exists() or not project_dir.is_dir():
            print(f'ERROR: Project directory not found: {project_dir}', file=sys.stderr)
            sys.exit(2)
        # Ensure project_dir is within workspace
        try:
            project_dir.relative_to(workspace)
        except ValueError:
            print(f'ERROR: Project directory must be within workspace', file=sys.stderr)
            sys.exit(2)
    
    all_results = []
    
    # Run all checks
    all_results.extend(check_l0_files(workspace))
    all_results.extend(check_l2_files(workspace))
    all_results.extend(check_l3_state(workspace))
    all_results.extend(check_l3_decisions(workspace, project_dir))
    all_results.extend(check_l2_daily(workspace))
    all_results.extend(check_l4_log(workspace))
    
    # Print results
    pass_count = 0
    fail_count = 0
    warn_count = 0
    
    for status, msg in all_results:
        print(f'{status} {msg}')
        if status == 'PASS':
            pass_count += 1
        elif status == 'FAIL':
            fail_count += 1
        elif status == 'WARN':
            warn_count += 1
    
    print(f'SUMMARY pass={pass_count} fail={fail_count} warn={warn_count}')
    
    sys.exit(1 if fail_count > 0 else 0)


if __name__ == '__main__':
    main()
