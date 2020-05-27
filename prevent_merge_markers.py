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


## This code is DOES NOT RUN, it is only for testing
## import os
def search(rootdir):
    """
    Test code: list all the files in a directory
    recursively

    Output: list of all files
    """
    l = []
    for root, dirs, files in os.walk(rootdir):
        for filename in files:
            filepath = os.path.join(root, filename)
            l.append(filepath)
    return l


## This code is DOES NOT RUN, it is only for testing
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
    diff = subprocess.check_output(['git',
                                    'diff',
                                    oldrev + ".." + newrev])
    conflicts = pattern_match(diff)
    # If there are conflicts in string
    if conflicts:
        message = "Error: You cannot push without resolving merge conflicts. \n" \
            + conflicts.string
        sys.exit(message)
    return
