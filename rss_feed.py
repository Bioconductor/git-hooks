import subprocess
import datetime
# import re
from os.path import basename, abspath
from xml.etree.ElementTree import parse, fromstring
import logging


ENTRY="""
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
            commit_id, author, email, timestamp = commit.split("|")
            #pubDate = datetime.datetime.fromtimestamp(
            #            float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = subprocess.check_output(["git", "log" ,
                                                  "--pretty=format:%B",
                                                  "-n", "1", commit_id])
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


def indent_xml(elem, level=0):
    """
    Recursive function to indent xml entry in RSS feed.
    """
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        # Recurse (aka leap of faith)
        for elem in elem:
            indent_xml(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


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
