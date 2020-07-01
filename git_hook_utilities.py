#!/usr/bin/env python

"""
Bioconductor hook utilities
"""

import subprocess
from os import path

HOOKS_CONF = "file:///home/git/repositories/admin/hook_maintainer.git"
LOCAL_HOOKS_CONF = "file:////Users/ni41435_lca/Documents/bioc/hook_maintainer.git"


def indent_xml(elem, level=0):
    """
    Recursive function to indent xml entry in RSS feed.
    """
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        # Recurse (aka leap of faith)
        for elem in elem:
            indent_xml(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def get_hooks_conf():
    """This function does a simple 'git archive' clone process of
    hooks.conf.

    It clones the file in the /tmp directory. This function ignores
    the '#' characters in the file.

    """
    # NOTE: Change to HOOKS_CONF to LOCAL_HOOKS_CONF when testing
    cmd = "git archive --remote=" + HOOKS_CONF + " HEAD hooks.conf | tar -x"
    subprocess.check_output(cmd, shell=True, cwd="/tmp")
    if path.exists("/tmp/hooks.conf"):
        with open("/tmp/hooks.conf") as f:
            txt = f.read()
        txt = txt.splitlines()
        # Ignore '#' in the file
        conf = "\n".join([line for line in txt
                          if not line.startswith("#")])
    return conf
