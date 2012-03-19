#!/usr/bin/env python

"""parser.py

Module used to parse source documents
"""

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
import re, os.path, sys, lxml.html, codecs

DIR_ORIGINAL = "/home/maf/Media/2004"
DIR_HTML = "/home/maf/Media/2004/html"
DIR_TEXT = "/home/maf/Media/2004/text"
SELF_CLOSING_TAGS = ['acceptance-datetime', 'type',
                     'sequence', 'filename', 'description']
# TODO: Add greedy whitespace to avoid empty docs
HTML_PATTERN = re.compile(r'(?<=<TYPE>20-F)(?:.*?html>)(.*?)(?=</html>)', 
        flags=(re.DOTALL|re.IGNORECASE))
TEXT_PATTERN = re.compile(r'(?<=<TYPE>20-F)(?:.*?TEXT>)(.*?)(?=</TEXT>)',
        flags=(re.DOTALL|re.IGNORECASE))
IMG_PATTERN = re.compile(r'(?<=<TYPE>GRAPHIC)(?:.*?TEXT>)(.*?)(?=</TEXT>)',
        flags=(re.DOTALL|re.IGNORECASE))
PDF_PATTERN = re.compile(r'(?<=<PDF>)(.*?)(?=</PDF>)',
        flags=(re.DOTALL|re.IGNORECASE))

# Remove binary data and return parse tree or None if the document could not be parsed
def parse(docname):
    rf = open(DIR_ORIGINAL+'/'+docname+'.txt', 'r')
    try:
        xml = rf.read()
        # Remove binary data and generate parse tree
        xml = re.sub(IMG_PATTERN, '', xml)
        xml = re.sub(PDF_PATTERN, '', xml)
        doc = BeautifulStoneSoup(xml, selfClosingTags=SELF_CLOSING_TAGS,
                convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        return doc
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, e:
        print "Parse error in", docname, ":", e.__str__()
        return None
    finally:
        rf.close()

# Output text content to file
def parseText(docname):
    rf = open(DIR_ORIGINAL+'/'+docname+'.txt', 'r')
    wf = open(DIR_HTML+'/'+docname+'.html', 'w')
    try:
        xml = rf.read()
        docs = re.findall(HTML_PATTERN, xml)
        if not docs: # Alternate file format
            docs = re.findall(TEXT_PATTERN, xml)
            if not docs: return None
            wf.close()
            wf = open(DIR_TEXT+'/'+docname+'.txt', 'w')
        wf.write(''.join(docs))
        """
        if not docs return
        html = []
        for doc in docs:
            html.append(BeautifulSoup(doc, convertEntities=BeautifulSoup.HTML_ENTITIES))
        wf = codecs.open(DIR_HTML+'/'+docname, 'w', html[0].originalEncoding)
        for doc in html:
            wf.write(''.join(doc.findAll(text=True)))
        """
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, e:
        print "Parse error in", docname, ":", e.__str__()
        return None
    finally:
        rf.close()
        wf.close()


# FAILED ATTEMPT: beautifulSoup does not properly detect encoding
"""
def parseText(docname):
    rf = open(DIR_ORIGINAL+'/'+docname, 'r')
    try:
        xml = rf.read()
        # Remove binary data and generate parse tree
        xml = re.sub(IMG_PATTERN, '', xml)
        xml = re.sub(PDF_PATTERN, '', xml)
        doc = BeautifulStoneSoup(xml, selfClosingTags=SELF_CLOSING_TAGS,
                convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        wf = codecs.open(DIR_HTML+'/'+docname, 'w', doc.originalEncoding)
        print doc.originalEncoding
        wf.write(''.join(doc.findAll(text=True)))
        #print ''.join(doc.findAll(text=True))
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception, e:
        print docname
        raise
        print "Parse error in", docname, ":", e.__str__()
        return None
    finally:
        rf.close()
        
        try:
            l = len(d.contents[1])
            s = ""
            for i in range(3, l, 2): # Location of <DOCUMENT>s
                #if (d.contents[1].contents[i].contents[2] is u'20-F\r\n'): # NOT TESTED (verifies if 20-F form)
                if (len(d.contents[1].contents[i] >= 10)): # Removes binary <DOCUMENT>s
                    s += 
            # write s to file DESTINATION/name
"""        
    
# Get list of source documents
def getSourceList():
    docnames = []
    for root, dirs, files in os.walk(DIR_ORIGINAL):
        for name in files:
            docnames.append(name[0:-4]) # Truncate '.txt' off filename
    return sorted(docnames)

# Parse documents in source directory and write 
def parseSource():
    docs = []
    docnames = getSourceList()
    for name in docnames:
        d = parse(name)
        if (d):
            docs.append(d)
    return docs

def parseTextSource():
    docnames = getSourceList()
    for name in docnames:
        parseText(name)

def main(argv=None):
    parseTextSource()
    
if __name__ == '__main__':
    sys.exit(main())
