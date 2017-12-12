import subprocess
import datetime
import re
from os.path import basename, abspath
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


def limit_feed_length(fh, length):
    """ This is run everytime the feed reaches limit"""
    doc = parse(fh)
    root = doc.getroot()
    # Get all RSS item
    channel_root = root.find("channel")
    items = channel_root.findall("item")
    # check length
    if len(items) > length:
        extra_items = items[length:]
        for item in extra_items:
            channel_root.remove(item)
    fh.seek(0)
    fh.truncate()
    doc.write(fh)
    fh.write("\n")
    return


def write_feed(entry, fh):
    """Write feed to the beginning of the file"""
    text = fh.read()
    text = re.sub(r'<copyright />\n',
                  '<copyright />\n' + entry,
                  text)
    fh.seek(0)
    fh.write(text)
    fh.flush()
    return


def rss_feed(oldrev, newrev, refname, fh, length):
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

            entry = ENTRY % (package_name,
                             commit_msg,
                             author,
                             pubDate,
                             commit_id)
            # Write FEED and sleep to avoid race condition
            try:
                write_feed(entry, fh)
            except IOError as e:
                logging.error("Error writing feed", e)
            try:
                limit_feed_length(fh, length)
            except Exception as e:
                logging.error("Error limiting feed size", e)
    return
