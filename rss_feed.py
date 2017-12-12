import subprocess
import datetime
import re
from os.path import basename, abspath
import fcntl
from xml.etree.ElementTree import parse
import logging
logging.basicConfig(filename='post-recieve.log',level=logging.DEBUG)


ENTRY="""    <item>
      <title>%s</title>
      <link>https://www.bioconductor.org</link>
      <description>%s</description>
      <author>%s</author>
      <pubDate>%s</pubDate>
      <guid>%s</guid>
    </item>
"""


# FIXME Remove locks
def limit_feed_length(fpath, length):
    """ This is run everytime the feed reaches limit"""
    with open(fpath, "r+") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        doc = parse(f)
        root = doc.getroot()
        # Get all RSS item
        channel_root = root.find("channel")
        items = channel_root.findall("item")
        # check length
        if len(items) > length:
            extra_items = items[length:]
            for item in extra_items:
                channel_root.remove(item)
        f.seek(0)
        f.truncate()
        doc.write(f)
        f.write("\n")
        fcntl.lockf(f, fcntl.LOCK_UN)
    return


# FIXME Remove locks
def write_feed(entry, fpath):
    """Write feed to the beginning of the file"""
    with open(fpath, "r+") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        text = f.read()
        text = re.sub(r'<copyright />\n',
                      '<copyright />\n' + entry,
                      text)
        f.seek(0)
        f.write(text)
        f.flush()
        fcntl.lockf(f, fcntl.LOCK_UN)
    return


def rss_feed(oldrev, newrev, refname, fpath, length):
    """Post receive hook to check start Git RSS feed"""
    try:
        latest_commit = subprocess.check_output([
            "git", "log", oldrev + ".." + newrev,
            "--pretty=format:%H|%an|%s|%at"
        ])
        # Get package name
        package_path = subprocess.check_output([
            "git", "rev-parse", "--show-toplevel"]).strip()
        package_name = basename(abspath(package_path)).replace(".git", "")
    except Exception as e:
        logging.error("Exception: %s" % e)
        pass
    if latest_commit:
        # If more than one commit to unpack
        latest_commit = latest_commit.split("\n")
        # Reverse if there are multiple commits
        for commit in latest_commit[::-1]:
            logging.info("commit: ", commit)
            commit_id, author, commit_msg, timestamp = commit.split("|")
            pubDate = datetime.datetime.fromtimestamp(
                        float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

            # Entry to the RSS feed
            # title = package_name,
            # description = commit_msg,
            # author = author
            # pubDate = pubDate
            # guid = commit_id
            entry = ENTRY % (package_name,
                             commit_msg,
                             author,
                             pubDate,
                             commit_id)
            # Write FEED and sleep to avoid race condition
            try:
                write_feed(entry, fpath)
            except IOError as e:
                logging.error("Error writing feed", e)
            # Limit feed length to 200
            try:
                limit_feed_length(fpath, length)
            except Exception as e:
                logging.error("Error limiting feed size", e)
    return
