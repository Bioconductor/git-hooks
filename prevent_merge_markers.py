#!/usr/bin/env python

"""Pre-receive hook to check for merge markers in commits.

This merge marker and merge conflict check pre-receive hook
tries to prevent maintainers from commiting files with <<<,
>>>, === merge markers in them. This keeps the commit history
clean.
"""

from __future__ import print_function

import os
import re
import subprocess
import sys


# Global variables used by pre-recieve hook
ZERO_COMMIT = "0000000000000000000000000000000000000000"
ERROR_MSG = """Error: You cannot push without resolving merge conflicts.

Please check the files in the commit pushed to the git-server
for merge conflict markers like '<<<<<<<', '========', '>>>>>>>'.
"""


# This code is DOES NOT RUN, it is only for testing
# import os
def search(rootdir):
    """
    Test code: list all the files in a directory
    recursively

    Output: list of all files
    """
    l = []
    # Walk the path in the root directory.
    # 'dirs' is unused as we just need the root and file
    for root, dirs, files in os.walk(rootdir):
        for filename in files:
            filepath = os.path.join(root, filename)
            l.append(filepath)
    return l


# This code is DOES NOT RUN, it is only for testing
def test_files(rootdir):
    """
    Test code: The package GlobalAncova has non standard,
    encoding on files. This function will test all files
    in the rootdir to check for the pattern.

    Output: List of matches of the pattern.
    """
    files = search(rootdir)
    matches = []
    for file in files:
        with open(file, "rb") as f:
            txt = f.read()
            print("file: ", file)
            match = pattern_match(txt)
            matches.append(match)
    return matches


def pattern_match(text):
    """
    Regex to match pattern in a text file which is a byte string.
    """
    pattern = re.compile(r"<<<<<<< HEAD")
    # Search for pattern in diff
    try:
        match = pattern.search(text.decode('UTF-8'))
    except UnicodeError:
        match = pattern.search(text.decode('iso8859'))
    return match


def prevent_merge_markers(oldrev, newrev, refname):
    """Prevent merge markers in files.

    This function prevents merge markers in commits.
    """
    if oldrev == ZERO_COMMIT:
        # https://stackoverflow.com/questions/40883798/how-to-get-git-diff-of-the-first-commit
        # 4b825dc642cb6eb9a060e54bf8d69288fbee4904 is the
        # id of the "empty tree" in Git and it's always
        # available in every repository.
        oldrev = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    # Get diff
    diff = subprocess.check_output(['git',
                                    'diff',
                                    oldrev + ".." + newrev])
    conflicts = pattern_match(diff)
    # If there are conflicts in string
    if conflicts:
        sys.exit(ERROR_MSG)
    return
