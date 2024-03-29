# Bioconductor git-hooks 

This repository hosts the git hooks which are deployed on each Bioconductor package. 

## Naming convention

The name of the repository is `git-hooks` because of the way Bioconductor manages the it's git-server using **gitolite**. The hooks are meant to be placed in a directory called `local`, because of a design decision made in 2016 we called the directory which stores the git hooks `local/hooks/repo-specific`. Hence, the name `git-hooks`, to describe what happens in them. 

This repository acts as a submodule within the Bioconductor git server which manages the hooks.

## Hooks

The hooks are written in Python. They currently check each package for,

### Pre-receive hooks

1. Bad version numbers: prevent_bad_version_numbers.py

2. Duplicate commits: prevent_duplicate_commits.py

3. Merge conflicts: prevent_merge_markers.py

4. Large files: prevent_large_files.py

### Post-receive hooks

1. New package build: new_package_build.py

1. RSS feed: rss_feed.py

## Contact information

Bioconductor Core team <maintainer@bioconductor.org>

Nitesh Turaga <nitesh@ds.dfci.harvard.edu>

Martin Morgan <martin.morgan@roswellpark.org>
