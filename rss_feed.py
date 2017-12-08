import subprocess
import datetime
import re
from os.path import basename
import fcntl
from xml.etree.ElementTree import parse

ENTRY="""    <item>
      <title>%s</title>
      <link>https://www.bioconductor.org</link>
      <description>%s</description>
      <author>%s</author>
      <pubDate>%s</pubDate>
    </item>
"""

def limit_feed_length(fpath, length):
    """ This is run everytime the feed reaches limit"""
    with open(fpath, "r+") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        doc = parse(f)
        root = doc.getroot()
        ## Get all RSS item
        channel_root = root.find("channel")
        items = channel_root.findall("item")
        ## check length
        if len(items) > length:
            extra_items = items[length:]
            for item in extra_items:
                channel_root.remove(item)
        doc.write(f)
        fcntl.lockf(f, fcntl.LOCK_UN)
    return


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
        package_name = basename(package_path)
    except Exception as e:
        print("Exception: %s" % e)
        pass
    if latest_commit:
        ## If more than one commit to unpack
        latest_commit = latest_commit.split("\n")
        ## Reverse if there are multiple commits
        for commit in latest_commit[::-1]:
            # print("commit: ", commit)
            commit_id, author, commit_msg, timestamp = commit.split("|")
            pubDate = datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

            ## Entry to the RSS feed
            ## title = commit_id,
            ## description = commit_msg,
            ## author = author
            ## pubDate = pubDate
            entry = ENTRY % (commit_id,
                             package_name + "\n"+ commit_msg,
                             author,
                             pubDate)
            ## Write FEED and sleep to avoid race condition
            try:
                write_feed(entry, fpath)
            except IOError as e:
                print("Error writing feed", e)
            ## Limit feed length to 200
            try:
                limit_feed_length(fpath, length)
            except Exception as e:
                print("Error limiting feed size", e)
    return
