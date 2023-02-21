#!/usr/bin/env python3

"""
Enable post receive hook message when pushing to deprecated master branch.
"""


def master_deprecation(oldrev, newrev, refname):
    """master branch deprecated hook.

    """
    if "master" in refname:
       print("Use of 'master' branch is deprecated on git.bioconductor.org;\n" +
              "  Access to 'master' will eventually be revoked.\n" +
              "  Please use 'devel' to update Bioconductor devel version.\n" +
              "  See: ")

    return

