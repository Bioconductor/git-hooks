#!/usr/bin/env python

"""
Bioconductor hook utilities
"""

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