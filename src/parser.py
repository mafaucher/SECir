#!/usr/bin/env python

"""parser.py

Module used to parse SEC forms
"""

from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
import re, os.path, sys, lxml.html, codecs
import secdoc

# Document directories
DIR_FORM = "/home/maf/Media/doc/2004"
DIR_HTML = "/home/maf/Media/html"
DIR_TEXT = "/home/maf/Media/text"

SELF_CLOSING_TAGS = ['acceptance-datetime', 'type',
                     'sequence', 'filename', 'description']

# Matches the XML sections
HEAD_PATTERN = re.compile(r'(?<=<SEC-HEADER>)(.*?)(?=</SEC-HEADER>)',
        flags=(re.DOTALL|re.IGNORECASE))
TEXT_PATTERN = re.compile(r'(?<=<TYPE>20)(?:.*?TEXT>)(.*?)(?=</TEXT>)',
        flags=(re.DOTALL|re.IGNORECASE))

# Matches document attributes of the header
COMP_NAME_PATTERN   = re.compile(r'(?<=COMPANY CONFORMED NAME:)(?:\s*)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
COMP_CIK_PATTERN    = re.compile(r'(?<=CENTRAL INDEX KEY:)(?:\s*)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
DOC_TYPE_PATTERN    = re.compile(r'(?<=FORM TYPE:)(?:\s*)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
REPORT_DATE_PATTERN = re.compile(r'(?<=CONFORMED PERIOD OF REPORT:)(?:\s*)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
FILING_DATE_PATTERN = re.compile(r'(?<=FILED AS OF DATE:)(?:\s*)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))

# Matches types of content
HTML_PATTERN = re.compile(r'(?<=<html>)(.*?)(?=</html>)',
        flags=(re.DOTALL|re.IGNORECASE))
IMG_PATTERN  = re.compile(r'(?<=<TYPE>GRAPHIC)(?:.*?TEXT>)(.*?)(?=</TEXT>)',
        flags=(re.DOTALL|re.IGNORECASE))
PDF_PATTERN  = re.compile(r'(?<=<PDF>)(.*?)(?=</PDF>)',
        flags=(re.DOTALL|re.IGNORECASE))

# Matches sections of the form text
ITEM5_PATTERN = re.compile(r'(?:ITEM\s*?5)(?:\s*?.\s*?.\s*?)(?:Operating\s+)(?:\w{0,3})?(?:\s+Financial\s+Review\s+and\s+Prospects\s*?[\.|-]?\s*?\n)(.*?)(?=ITEM\s*?6\s*?.\s*?.\s*?Directors,?\s+)(?:\w{0,3})?(\s+Senior\s+Management,?\s+and\s+Employees)',
        flags=(re.DOTALL|re.IGNORECASE))
NA_PATTERN = re.compile(r'^\s*(Not Applicable\.?)\s*$', flags=(re.DOTALL|re.IGNORECASE))
NONE_PATTERN = re.compile(r'^\s*$', flags=(re.DOTALL|re.IGNORECASE))

# Methods to count words
def ors(l): return r"|".join([re.escape(c) for c in l])
def retext(text, chars, sub): return re.compile(ors(chars)).sub(sub, text)
def countWords(text):
    text = retext(text, [" ", "\n"], u" ")
    text = retext(text.strip(), [], u"")
    words = text and len(re.compile(r"[ ]+").split(text)) or 0
    return words

# Finds and returns the first instance of a pattern in a string
def findOnce(pattern, string, verbose=False):
    match = pattern.search(string)
    if match:
        return match.group()
    else:
        if verbose:
            print "could not match", pattern.pattern
        return None

# Parse SEC-HEADER and return Company and Doc objects
def parseHeader(docName, verbose=False):
    # Extract Header content
    with open(DIR_FORM+'/'+docName+'.txt', 'r') as rfile:
        xml = rfile.read()
    header     = findOnce(HEAD_PATTERN, xml, verbose=verbose)
    filer = secdoc.Company(findOnce(COMP_NAME_PATTERN, header, verbose=verbose),
                           findOnce(COMP_CIK_PATTERN, header, verbose=verbose))
    form = secdoc.Doc(docName, findOnce(DOC_TYPE_PATTERN, header, verbose=verbose),
                           findOnce(REPORT_DATE_PATTERN, header, verbose=verbose),
                           findOnce(FILING_DATE_PATTERN, header, verbose=verbose))
    return (filer, form)

# Parse ITEM 5 of the form of return None if absent of 'Not Applicable'
def parseItem5(form, docName="", verbose=True):
    allMatch = ITEM5_PATTERN.findall(form)
    for match in allMatch:
        if not NONE_PATTERN.findall(match) and not NA_PATTERN.findall(match) and countWords(match) > 100:
            return match
    if verbose:
        print docName, ": No Item 5"
    return None

# Parse a 20-F form and extract text content
def parseText(docName, verbose=False):
    # Extract Header content
    with open(DIR_FORM+'/'+docName+'.txt', 'r') as rfile:
        xml = rfile.read()
    # Default parse strategy for plain text content
    wfilename = DIR_TEXT+'/'+docName+'.txt'
    content = findOnce(TEXT_PATTERN, xml, verbose=verbose)
    html = findOnce(HTML_PATTERN, content, verbose=verbose)
    if html: # Alternate parse strategy for HTML content
        wfilename = DIR_HTML+'/'+docName+'.html'
        content = html
    else: # Plain text document only
        content = parseItem5(content, docName=docName)
    # Write content to file
    if content and not NONE_PATTERN.findall(content):
        with open(wfilename, 'w') as wfile:
            wfile.write(content)

# Get list of form document names
def getFormList(verbose=False):
    docNames = []
    for root, dirs, files in os.walk(DIR_FORM):
        for name in files:
            # Truncate '.txt' off filename
            docNames.append(name[0:-4]) 
    return sorted(docNames)

# Parse all forms
def parseForms(verbose=False):
    docNames = getFormList(verbose=verbose)
    filers = []
    for docName in docNames:
        filer, form = parseHeader(docName, verbose=verbose)
        f = secdoc.findByCik(filer.cik, filers)
        if f is None:
            filers.append(filer)
            f = secdoc.findByCik(filer.cik, filers)
        f.docs.append(form)
        parseText(docName, verbose=verbose)
        if verbose:
            print "parsed", docName
    return filers

def main(argv=None):
    filers = parseForms(verbose=False)
    print len(filers)
    
if __name__ == '__main__':
    sys.exit(main())
