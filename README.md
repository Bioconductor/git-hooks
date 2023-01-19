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

2. RSS feed: rss_feed.py


### Package Type specific

Please note: there are currently different hooks activated for software vs
workflow/data experiment/annotation. Please see pre-receive-hook-software vs 
pre-receive-hook-dataexp-workflow for distinctions.


### Testing locally

Checkout git-hooks

```
git clone git@github.com:Bioconductor/git-hooks.git
```	 

Checkout gitolite-admin. This is NOT on github; it is only live version
This is ONLY needed if you are going to push changes live or are debugging an
issue. It is suppose to be a copy of what is in this git-hooks repo but is not
actually git tracked/synced with the git-hooks repo

We hope that what is in gitollite-admin is the same as this git-hooks repo. 
Periodically this should be checked and kept in sync!

```
git clone git@git.bioconductor.org:gitolite-admin
```

Checkout hook_maintainer and make a bare repo of it

```
git clone git@git.bioconductor.org:admin/hook_maintainer
git clone --bare hook_maintainer
```

Checkout a package repository that you would like to test hooks on.
```
git clone git@git.bioconductor.org:packages/BiocFileCache
```

It might get confusing as we need to mimic the git server. We will now make a
bare clone of the locally cloned package. In these notes when I refer to package
repository it will be the original cloned and the `bare package` repository will
refer to the repo created by the following command and have a .git added.
e.g. BiocfileCache was original the following  will create BiocFileCache.git

```
## e.g. git clone --bare /home/lori/temp/BiocFileCache
git clone --bare <path to local cloned repo>
```

Navigate to the hooks directory in the bare package repository and copy the
hooks in the cloned git-hooks directory 

```
cd BiocFileCache.git/hooks
cp -r /home/lori/temp/git-hooks/* .
```

Remove sample hooks provided and move our replacement as default hook file.
Note:  
   pre-receive-hook-software  is software packages hooks
   pre-receive-hook-dataexp-workflow is current workflow, data experiment, and annotation hook
   post-receive-hook applies to all  
```
rm -rf *.sample
cp pre-receive-hook-software pre-receive
```

Set utilites to use local hook maintainer. These changes are in git_hook_utilities.py
Around line 11 update LOCAL_HOOKS_CONF to be the local bare repository of hook_maintainer.

```
## recommend to use full path and not relative path
LOCAL_HOOKS_CONF = "file://///home/lori/temp/hook_maintainer.git"
```
Also in git_hooks_utilities.py around line 43 change HOOKS_CONF to LOCAL_HOOKS_CONF
e.g.
`cmd = "git archive --remote=" + HOOKS_CONF + " HEAD hooks.conf | tar -x"`
becomes
`cmd = "git archive --remote=" + LOCAL_HOOKS_CONF + " HEAD hooks.conf | tar -x"`

Very IMPORTANT step! Change remote of originally clone repo to be set to mock local server
e.g

```
git remote -v

## originally:  origin	git@git.bioconductor.org:packages/BiocFileCache
## after this:  origin	/home/lori/temp/BiocFileCache.git
## e.g git remote set-url origin /home/lori/temp/BiocFileCache.git

git remote set-url origin <path to bare package repo>

```

The local testing structure should now be set. Make changes, commit, and try to
push from the original clone package repo (NOT bare package) 


### Live location

These hooks currently need to be uploaded manually to
git@git.bioconductor.org:gitolite-admin/local/hooks/repo-specific in order to be live.



## Contact information

Bioconductor Core team <bioconductorcoreteam@gmail.com>

Lori Shepherd Kern <lori.shepherd@roswellpark.org>
