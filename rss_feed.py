import subprocess
import datetime
import time
import re
from xml.dom.minidom import parseString
import fcntl

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

    with open(fpath, "r") as f:
        fcntl.lockf(f, fcntl.LOCK_EX)
        data = f.read()
        fcntl.lockf(f, fcntl.LOCK_UN)
    dom = parseString(data)
    if len(dom.getElementsByTagName('item')) > length:
        # If more than length get all elements at the end
        last = dom.getElementsByTagName('item')[length:]
        for item in last:
            dom.documentElement.removeChild(item)

        ## Mutex on file
        xf = open(fpath, "w")
        fcntl.lockf(xf, fcntl.LOCK_EX)
        dom.writexml(xf)
        fcntl.lockf(xf, fcntl.LOCK_UN)
        xf.close()
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
    try:
        latest_commit = subprocess.check_output([
            "git", "log", oldrev + ".." + newrev,
            "--pretty=format:%h|%an|%B|%at"
        ])
    except Exception as e:
        print("Exception: %s" % e)
        pass
    if latest_commit:
        ## If more than one commit to unpack
        latest_commit = latest_commit.split()
        print("latest_commit: ", latest_commit)
        for commit in latest_commit:
            print("commit: ", commit)
            commit_id, author, commit_message, timestamp = commit.split("|")
            pubDate = datetime.datetime.fromtimestamp(
                    float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

            ## Entry to the RSS feed
            ## title = commit_id, description = commit_message, author = author
            ## pubDate = pubDate
            entry = ENTRY % (commit_id, commit_message, author, pubDate)

            ## Write FEED and sleep to avoid race condition
            try:
                write_feed(entry, fpath)
            except IOError as e:
                ## Avoid race condition during file write
                time.sleep(2)
                try:
                    ## Try writing to feed again after 2 secs
                    write_feed(entry, fpath)
                except IOError as e:
                    print("Error writing feed", e)

            ## Limit feed length to 200
            try:
                limit_feed_length(fpath, length)
            except Exception as e:
                print("Error limiting feed size", e)
    return
