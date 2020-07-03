#!/usr/bin/env python

"""Post-receive hook to trigger a build for a new package.

This hook checks the version number in the DESCRIPTION file, and if
there is a version increment triggers a POST request to single package
builder 'start_build' API endpoint.

The version check follows the guidelines of the Bioconductor
project. The guidelines are given at this link,
http://bioconductor.org/developers/how-to/version-numbering/.
"""

from os import path, getcwd
from requests import post
import logging
from requests.exceptions import HTTPError
from prevent_bad_version_numbers import git_diff
from prevent_bad_version_numbers import git_diff_files
from prevent_bad_version_numbers import get_version_bump
from prevent_bad_version_numbers import check_version_format
from prevent_bad_version_numbers import throw_error


# Global variables for this file
ZERO_COMMIT = "0000000000000000000000000000000000000000"
API_ENDPOINT = "https://issues.bioconductor.org/start_build"
ERROR_MSG = """Error: Please bump the version again and push.

The build did not start as expected. If the issue persists,
please reach out at bioc-devel@r-project.org or post on the
Github issue where your package is being reviewed.

%s
"""


def version_bumped(prev_version, new_version):
    """Check version in master branch."""
    x0, y0, z0 = map(int, prev_version.split("."))
    x, y, z = map(int, new_version.split("."))
    return z0 != z


def trigger_build(newrev):
    """Trigger build on SPB by sending POST request.
    """
    pkgname = path.basename(getcwd()).replace(".git", "")
    build_info = {"pkgname": pkgname, "commit_id": newrev}
    try:
        response = post(API_ENDPOINT, json=build_info)
        response.raise_for_status()
#        for key in build_info:
#            logging.DEBUG(key, build_info[key])
#        logging.DEBUG(response.content)
    except HTTPError as err:
        # Whoops it wasn't a 200
        # API_ENDPOINT will provide error message response.error()
        print(ERROR_MSG % str(err))
    return


def package_start_build(oldrev, newrev, refname):
    """Trigger build based on version bump in new package.

    The function takes in the standard arguments for a hook and sends
    a POST request to single package builder API endpoint.
    """
    # new package build should only happen on master branch
    if oldrev == ZERO_COMMIT:
        oldrev = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    files_modified = git_diff_files(oldrev, newrev)

    for fname in files_modified:
        if "DESCRIPTION" in fname:
            diff = git_diff(oldrev, newrev, fname)
            prev_version, new_version = get_version_bump(diff)
            if (prev_version is None) and (new_version is None):
                continue
            # If version has been bumped
            if version_bumped(prev_version, new_version):
                # start build
                trigger_build(newrev)
    return
