#!/usr/bin/env python

"""parser.py

Module used to read files into BeautifulSoup parse tree
"""

from BeautifulSoup import BeautifulStoneSoup
import re, os.path, sys

SOURCE = "/home/maf/Media/2004"

SELF_CLOSING_TAGS = ['acceptance-datetime', 'type',
                     'sequence', 'filename', 'description']

IMG_PATTERN = re.compile(r'(?<=<TYPE>GRAPHIC)(?:.*?TEXT>)(.*)(?=</TEXT>)',
        flags=(re.DOTALL|re.IGNORECASE))

PDF_PATTERN = re.compile(r'(?<=<PDF>)(.*)(?=</PDF>)',
        flags=(re.DOTALL|re.IGNORECASE))

# Remove binary data and return parse tree or None if the document could not be parsed
def parse(docname):
    try:
        xml = open(docname, 'rb').read()
        xml = re.sub(IMG_PATTERN, '', xml)
        xml = re.sub(PDF_PATTERN, '', xml)
        doc = BeautifulStoneSoup(xml, selfClosingTags=SELF_CLOSING_TAGS)
        return doc
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, e:
        print "Parse error in", docname, ":", e.__str__()
        return None

# Parse documents in SOURCE and return list of parse trees
def parseSource():
    docnames = []
    docs = []
    for root, dirs, files in os.walk(SOURCE):
        for name in files:
            docnames.append(root+"/"+name)
    sorted(docnames)
    for name in docnames:
        d = parse(name)
        if (d):
            docs.append(d)
    return docs
