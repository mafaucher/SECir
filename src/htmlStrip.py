#!/usr/bin/env python

"""htmlStrip.py

Script to remove HTML tags. This is used to make the HTML text readeable, it is
NOT used in the extraction algorithm.
"""

import parser
import os, sys

FILE = "2009/0001362310-09-007787"
DIR_FILE = os.path.join(parser.DIR_FORM, FILE))

##
# Parse the Text content (currently only Item 5/9)
#
# @param docName The name of the form to parse.
#
# @return content for this form or None
def htmlStrip():
    # Extract Header content
    parser.makeDir(DIR_FILE)
	with open(os.path.join(parser.DIR_FORM, FILE+'.txt'), 'r') as rfile:
        xml = rfile.read()
    # Get the TEXT content
    content = parser.findOnce(parser.TEXT_PATTERN, xml)
    html = parser.findOnce(parser.HTML_PATTERN, content)
    if html: # Strip HTML content
        parser.makeDir(os.path.join(os.path.curdir), FILE)
        with open(os.path.join(os.path.curdir), FILE+'_plaintext.txt'), 'w') as wfile:
            wfile.write(parser.strip_html(content).encode('UTF-8'))
    return None

def main(argv=None):
    htmlStrip()
    
if __name__ == '__main__':
    sys.exit(main())
