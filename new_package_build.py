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
from requests.exceptions import HTTPError
from prevent_bad_version_numbers import git_diff
from prevent_bad_version_numbers import git_diff_files
from prevent_bad_version_numbers import get_version_bump
from prevent_bad_version_numbers import check_version_format
from prevent_bad_version_numbers import throw_error


ZERO_COMMIT = "0000000000000000000000000000000000000000"
ERROR_MSG = """Error: Illegal version bump from '%s' to '%s'.

For new packages in the build report, the version number should
always be in the form 'major.minor.patch', where 'majoy.minor'
should always be '0.99'. Only increment 'patch' number.

If you want a build to start, increment the 'patch' number in your
version.

Check http://bioconductor.org/developers/how-to/version-numbering/
for details.
"""

def check_version_bump_new_package(prev_version, new_version):
    """Check version in master branch."""
    # Check format of version
    prev_version, new_version = check_version_format(prev_version, new_version)
    x_0, y_0, z_0 = map(int, prev_version.split("."))
    x_1, y_1, z_1 = map(int, new_version.split("."))
    # Check if a new package,
    # if new, package should have 0.99.z as version number
    if x_1 != 0 and x_0 != 0 and y_1 != 99 and y_0 != 99:
        throw_error(prev_version, new_version)
    if not z_1 >= z_0:
        throw_error(prev_version, new_version)
    return


def trigger_build(newrev):
    """Trigger build on SPB by sending POST request.
    """
    pkgname = path.basename(getcwd()).replace(".git", "")
    build_info = {pkgname: newrev}
    try:
        response = post('https://httpbin.org/post', data=build_info)
        response.raise_for_status()
    except HTTPError as err:
        # Whoops it wasn't a 200
        msg = "Error: please bump the version again. \n" + \
            "The build did not start as expected. \n"
        print(msg, str(err))
    return response.status_code


def new_package_build(oldrev, newrev, refname):
    """Trigger build based on version bump in new package.

    The function takes in the standard arguments for a hook and sends
    a POST request to single package builder API endpoint.
    """
    # new package build should only happen on master branch
    assert refname == "master"
    if oldrev == ZERO_COMMIT:
        oldrev = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    files_modified = git_diff_files(oldrev, newrev)

    for fname in files_modified:
        if "DESCRIPTION" in fname:
            diff = git_diff(oldrev, newrev, fname)
            prev_version, new_version = get_version_bump(diff)
            if (prev_version is None) and (new_version is None):
                continue
            check_version_bump_new_package(prev_version, new_version)
            trigger_build(newrev)
            print("New build is initiated with commit: " + newrev)
    return
