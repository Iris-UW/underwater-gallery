#!/usr/bin/env python3
"""Deploy to GitHub Pages via git subtree push to gh-pages branch."""

import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
WEB_DIR = os.path.join(PROJECT_DIR, 'web')


def run(cmd, cwd=None, check=True):
    print(f'  → {" ".join(cmd)}')
    result = subprocess.run(cmd, cwd=cwd or PROJECT_DIR, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f'  ✗ Error: {result.stderr.strip()}')
        sys.exit(1)
    return result


def main():
    # Ensure we're on main
    run(['git', 'checkout', 'main'])
    print('📦 Committing changes on main...')

    # Stage all changes
    run(['git', 'add', '-A'])

    # Check if there's anything to commit
    result = run(['git', 'diff', '--cached', '--quiet'], check=False)
    if result.returncode == 0:
        print('  (nothing to commit)')
    else:
        run(['git', 'commit', '-m', f'🔧 Site update: i18n fixes, deploy prep'])

    # Push main
    print('🚀 Pushing main...')
    run(['git', 'push', 'origin', 'main'])

    # Deploy web/ to gh-pages
    print('📤 Deploying web/ to gh-pages branch...')
    run(['git', 'subtree', 'push', '--prefix', 'web', 'origin', 'gh-pages'])

    # Determine site URL
    result = run(['git', 'remote', 'get-url', 'origin'])
    remote = result.stdout.strip()
    # Extract org/repo from remote URL
    import re
    m = re.search(r'github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?$', remote)
    if m:
        org, repo = m.groups()
        print(f'\n✅ Deployed! Your site is live at:')
        print(f'   https://{org}.github.io/{repo}/')
        print(f'\n⏱  It may take 1-2 minutes for GitHub Pages to rebuild.')
    else:
        print(f'\n✅ Deployed! Check your GitHub Pages settings for the URL.')


if __name__ == '__main__':
    main()
