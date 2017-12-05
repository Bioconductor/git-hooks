import subprocess
import datetime
import time
import re
import fcntl
from xml.etree.ElementTree import parse


ENTRY="""<item>
    <title>%s</title>
    <link>www.bioconductor.org</link>
    <description>%s</description>
    <author>%s</author>
    <pubDate>%s</pubDate>
</item>
"""

def limit_feed_length(fpath, length):
    """ This is run only once every day"""
    with open(fpath, "r+") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        doc = parse(f)
        fcntl.lockf(f, fcntl.LOCK_UN)
    root = doc.getroot()
    ## Get all RSS item
    channel_root = root.find("channel")
    items = channel_root.findall("item")
    ## check length
    if len(items) > length:
        extra_items = items[length:]
        for item in extra_items:
            channel_root.remove(item)
    with open(fpath, "w") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        doc.write(f, encoding="UTF-8", xml_declaration=True)
        fcntl.lockf(f, fcntl.LOCK_UN)
    return


def write_feed(entry, fpath):
    """Write feed to the beginning of the file"""
    with open(fpath, "r+") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        text = f.read()
        text = re.sub("<copyright/>\n",
                      "<copyright/>\n" + entry,
                      text)
        f.seek(0)
        f.write(text)
        f.flush()
        fcntl.lockf(f, fcntl.LOCK_UN)
    return

def rss_feed(oldrev, newrev, refname, fpath, length):
    """Post receive hook to check start Git RSS feed"""
    print("refname: ", refname)
    try:
        latest_commit = subprocess.check_output([
            "git", "log", oldrev + ".." + newrev,
            "--pretty=format:%h|%an|%s|%at"
        ])
    except Exception as e:
        print("Exception: %s" % e)
        pass
    if latest_commit:
        ## If more than one commit to unpack
        print(latest_commit)
        latest_commit = latest_commit.split("\n")
        print("latest_commit: ", latest_commit)
        for commit in latest_commit[::-1]:
            print("commit: ", commit)
            commit_id, author, commit_title, timestamp = commit.split("|")
            pubDate = datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

            ## Entry to the RSS feed
            ## title = commit_id,
            ## description = commit_title,
            ## author = author
            ## pubDate = pubDate
            entry = ENTRY % (commit_id,
                             commit_title,
                             author,
                             pubDate)
            print("entry", entry)
            ## Write FEED and sleep to avoid race condition
            try:
                print("writing feed")
                write_feed(entry, fpath)
                print("Written feed")
            except IOError as e:
                ## Avoid race condition during file write
                time.sleep(1)
                try:
                    ## Try writing to feed again after 2 secs
                    write_feed(entry, fpath)
                except IOError as e:
                    print("Error writing feed", e)
            ## Limit feed length to 200
            try:
                print("limiting feed")
                limit_feed_length(fpath, length)
                print("done limiting feed")
            except Exception as e:
                print("Error limiting feed size", e)
    return
