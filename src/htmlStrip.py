#!/usr/bin/env python

"""htmlStrip.py

Script to remove HTML tags
"""

import parser

FILE = "2008/0001193125-08-060572"


##
# Parse the Text content (currently only Item 5/9)
#
# @param docName The name of the form to parse.
#
# @return content for this form or None
def htmlStrip():
    # Extract Header content
    parser.makeDir(parser.DIR_FORM+'/'+FILE)
    with open(parser.DIR_FORM+'/'+FILE+'.txt', 'r') as rfile:
        xml = rfile.read()
    # Get the TEXT content
    content = parser.findOnce(parser.TEXT_PATTERN, xml)
    html = parser.findOnce(parser.HTML_PATTERN, content)
    if html: # Strip HTML content
        parser.makeDIr(FILE)
        with open(FILE+'_plaintext.txt', 'w') as wfile:
            wfile.write(strip_html(content).encode('UTF-8'))
    return None

def main(argv=None):
    parseText()
    
if __name__ == '__main__':
    sys.exit(main())
