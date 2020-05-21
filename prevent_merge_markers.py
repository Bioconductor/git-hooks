#!/usr/bin/env python
"""Pre-receive hook to check for merge markers in commits.

This merge marker and merge conflict check pre-receive hook
tries to prevent maintainers from commiting files with <<<,
>>>, === merge markers in them. This keeps the commit history
clean.
"""

from __future__ import print_function
import subprocess
import sys
import re


ZERO_COMMIT = "0000000000000000000000000000000000000000"


def git_diff_files_with_conflicts(oldrev, newrev):
    """Get list of files in diff."""
    diff = subprocess.check_output(['git',
                                    'diff',
                                    oldrev + ".." + newrev])
    pattern = re.compile(r"<<<<<<< HEAD")
    # Search for pattern in diff
    conflicts = pattern.search(diff.decode('UTF-8'))
    return conflicts


def prevent_merge_markers(oldrev, newrev, refname):
    """Prevent merge markers in files.

    This function prevents merge markers in commits.
    """
    conflicts = git_diff_files_with_conflicts(oldrev, newrev)
    # If there are conflicts in string
    if conflicts:
        message = ("Error: You cannot commit without resolving merge conflicts. \n") + conflicts.string
        sys.exit(message)
    return
