#!/usr/bin/env python

"""Post-receive hook for rss feeds

The RSS feeds for git log. The feeds are split into RELEASE and devel
gitlog.xml files.
"""

import fcntl
import logging
import subprocess
import sys
from os.path import abspath, basename
from xml.etree.ElementTree import fromstring, parse
from git_hook_utilities import indent_xml


# Global variables used by post-recieve hook
ZERO_COMMIT = "0000000000000000000000000000000000000000"
BASE_PATH = "/home/git/rss/"
ENTRY = """
    <item>
      <title>%s</title>
      <link>https://bioconductor.org/packages/%s/</link>
      <description><![CDATA[ %s ]]></description>
      <author><![CDATA[ %s ]]></author>
      <pubDate>%s</pubDate>
      <guid>%s</guid>
    </item>
"""


def rss_feed(oldrev, newrev, refname, length):
    """Post receive hook to check start Git RSS feed"""
    entry_list = []
    try:
        latest_commit = subprocess.check_output([
            "git", "log", oldrev + ".." + newrev,
            "--pretty=format:%H|%an|%ae|%ai"
        ])
        # Get package name
        package_path = subprocess.check_output([
            "git", "rev-parse", "--absolute-git-dir"]).strip()
        package_name = basename(abspath(package_path)).replace(".git", "")
    except Exception as err:
        logging.error("Exception: %s" % err)
        pass
    if latest_commit:
        # If more than one commit to unpack
        latest_commit = latest_commit.split("\n")
        # Reverse if there are multiple commits
        for commit in latest_commit[::-1]:
            commit_id, author, email, timestamp = commit.split("|")
            commit_msg = subprocess.check_output(["git", "log",
                                                  "--pretty=format:%B",
                                                  "-n", "1", commit_id])
            # link for correct branch
            if "RELEASE" in refname:
                link = package_name
            else:
                link = "devel/" + package_name

            entry = ENTRY % (package_name,
                             link,
                             commit_msg,
                             author + " <" + email + ">",
                             timestamp,
                             commit_id)
            # Add entry as element in xml.etree
            entry_list.append(fromstring(entry))
    return entry_list


def write_and_limit_feed(entry_list, length, feed):
    """
    Write a new entry to the RSS feed.
    """
    doc = parse(feed)
    root = doc.getroot()

    # Get items
    channel_root = root.find("channel")
    items = channel_root.findall("item")
    # Write feed
    for entry in entry_list:
        # 5 is the entry position in the feed
        channel_root.insert(5, entry)
    # Remove extra elements
    if len(items) > length:
        extra_items = items[length:]
        for extra_item in extra_items:
            channel_root.remove(extra_item)
    indent_xml(channel_root)
    feed.seek(0)
    feed.truncate()
    # Write feed
    doc.write(feed)
    feed.write("\n")
    feed.flush()
    return feed


def write_rss_feed(oldrev, newrev, refname, length=499):
    """RSS feed hook.

    """
    # Path to feed.xml
    fpath = BASE_PATH + "gitlog.xml"
    fpath_release = BASE_PATH + "gitlog.release.xml"

    # Run function for RSS feed
    feed = open(fpath, "r+")
    feed_release = open(fpath_release, 'r+')

    # Obtain a lock
    fcntl.lockf(feed, fcntl.LOCK_EX)

    # Split feed into correct files
    try:
        if "RELEASE" in refname:  # RSS-feed post-receive hook
            entry = rss_feed(oldrev, newrev, refname, length)
            write_and_limit_feed(entry, length, feed_release)
        else:
            entry = rss_feed(oldrev, newrev, refname, length)
            write_and_limit_feed(entry, length, feed)
    except Exception as err:
        print("Note: failed to update RSS feed;" +
              "git repository updated successfully.")
        logging.error(err)
    # Url for sending the RSS feed
    url = 'biocadmin@staging.bioconductor.org' + \
        ':/home/biocadmin/bioc-test-web/bioconductor.org' + \
        '/assets/developers/rss-feeds/.'
    # Run subprocess command
    cmd = ['scp', 'gitlog.xml', 'gitlog.release.xml', url]
    subprocess.check_call(cmd, cwd=BASE_PATH)

    # Release the lock
    fcntl.lockf(feed, fcntl.LOCK_UN)
    feed.close()
    feed_release.close()
    return


# This is only run when changed to 'True'
# It is used for local testing
if False:
    fh = "/tmp/gitlog.xml"
    test_feed = open(fh, "r+")
    refname = None
    revs = subprocess.check_output([
        "git", "log", "-2", "--format=%H"
    ]).splitlines()
    newrev = revs[0].strip()
    oldrev = revs[1].strip()
    rss_feed(oldrev, newrev, refname, 5)
    sample_entry = """
    <item>
      <title>2309fc133512c4e25d8942c3d0ae6fc198bf9ba9</title>
      <link>https://www.bioconductor.org</link>
      <description><![CDATA[
on't import "$<-" method from the IRanges package (the IRanges package
     does not export such method)]]></description>
      <author>Nitesh</author>
      <pubDate>2017-12-08 17:26:18</pubDate>
    </item>
    """
    rss_entry = fromstring(sample_entry)
    write_and_limit_feed([rss_entry], 5, fh)
    test_feed.close()
    sys.exit(0)
