#!/usr/bin/env python

"""parser.py

Module used to parse SEC forms
"""

import re, os, sys, lxml.html, codecs, htmlentitydefs
import secdoc



# DIRECTORIES AND FILES

DIR_FORM = "/home/maf/Media/doc"    # Directory for original forms
DIR_TEXT = "/home/maf/Media/text"   # Directory for parsed text
FILING_LIST = "/home/maf/Projects/SECir/filingslist.csv"



# PATTERNS

# XML sections
HEAD_PATTERN = re.compile(r'(?<=<SEC-HEADER>)(.*?)(?=</SEC-HEADER>)',
        flags=(re.DOTALL|re.IGNORECASE))
TEXT_PATTERN = re.compile(r'(?<=<TYPE>20)(?:.*?TEXT>)(.*?)(?=</TEXT>)',
        flags=(re.DOTALL|re.IGNORECASE))

# SEC-DOC header attributes
COMP_NAME_PATTERN   = re.compile(r'(?<=COMPANY CONFORMED NAME:)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
COMP_CIK_PATTERN    = re.compile(r'(?<=CENTRAL INDEX KEY:)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
DOC_TYPE_PATTERN    = re.compile(r'(?<=FORM TYPE:)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
REPORT_DATE_PATTERN = re.compile(r'(?<=CONFORMED PERIOD OF REPORT:)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))
FILING_DATE_PATTERN = re.compile(r'(?<=FILED AS OF DATE:)(.*?)(?=\r?\n)',
        flags=(re.IGNORECASE))

# TEXT content type 
HTML_PATTERN = re.compile(r'(?<=<html>)(.*?)(?=</html>)',
        flags=(re.DOTALL|re.IGNORECASE))
IMG_PATTERN  = re.compile(r'(?<=<TYPE>GRAPHIC)(?:.*?TEXT>)(.*?)(?=</TEXT>)',
        flags=(re.DOTALL|re.IGNORECASE))
PDF_PATTERN  = re.compile(r'(?<=<PDF>)(.*?)(?=</PDF>)',
        flags=(re.DOTALL|re.IGNORECASE))

# Item 9 (...-2000)
#ITEM9_PATTERN = re.compile(r'\n\s*(?:ITEM\s*9.{0,10}?management.{0,2}\s*discussion\s*.{0,3}?\s*analysis\s*of\s*financial\s*condition\s*.{0,3}\s*results\s*of\s*operations)(.*?)(?=\s*\n\s*ITEM\s*10.{0,10}?directors\s*.{0,3}?\s*officers)',
ITEM9_PATTERN = re.compile(r'\n\s*(?:ITEM\s*9.{0,10}?management.{0,2}\s*discussion\s*)(?:.{0,3}?\s*analysis\s*of\s*financial\s*condition\s*.{0,3}\s*results\s*of\s*operations)?(.*?)(?=\s*\n\s*ITEM\s*10.{0,10}?directors)',
        flags=(re.DOTALL|re.IGNORECASE))

# Item 5 (2001-...)
#ITEM5_PATTERN = re.compile(r'\n\s*(?:ITEM\s*5.{0,10}?operating\s*.{0,3}?\s*financial\s*review\s*.{0,3}?\s*prospects\s*.{0,3}?\s*\n\s*)(.*?)(?=\s*\n\s*ITEM\s*6.{0,10}?directors,?\s*.{0,3}?\s*senior\s*management,?\s*.{0,3}\s*employees)',
ITEM5_PATTERN = re.compile(r'\n\s*(?:ITEM\s*5.{0,10}?operating\s*)(?:.{0,3}?\s*financial\s*review\s*.{0,3}?\s*prospects\s*.{0,3}?\s*\n\s*)?(.*?)(?=\s*\n\s*ITEM\s*6.{0,10}?directors)',
        flags=(re.DOTALL|re.IGNORECASE))
NA_PATTERN = re.compile(r'^\s*(Not Applicable\.?)\s*$',
        flags=(re.DOTALL|re.IGNORECASE))
NONE_PATTERN = re.compile(r'^\s*$',
        flags=(re.DOTALL|re.IGNORECASE))

# Currently removes 3 lines ending with the line that contains <PAGE>
PAGE_PATTERN = re.compile(r'\r\n.*?\r\n.*?\r\n.*?<PAGE>.*?\r\n',
        flags=(re.IGNORECASE))
TABLE_PATTERN = re.compile(r'<TABLE>.*?</TABLE>',
        flags=(re.DOTALL|re.IGNORECASE))



# HELPER METHODS

##
# Create directory for new file
# 
# @param filename Name of the new file
def makeDir(filename):
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

##
# Removes HTML markup from a text string.
#
# @param text The HTML source.
# @return The plain text.  If the HTML source contains non-ASCII
#     entities or character references, this is a Unicode string.
def strip_html(text):
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        if text[:2] == "&#":
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        elif text[:1] == "&":
            import htmlentitydefs
            entity = htmlentitydefs.entitydefs.get(text[1:-1])
            if entity:
                if entity[:2] == "&#":
                    try:
                        return unichr(int(entity[2:-1]))
                    except ValueError:
                        pass
                else:
                    return unicode(entity, "iso-8859-1")
        return text # leave as is
    return re.sub("(?s)<[^>]*>|&#?\w+;", fixup, text)

##
# Removes XML markup from a document.
#
# @param text The document with markup.
# @return The document without markup.
def strip_markup(text):
    text = PAGE_PATTERN.sub('', text)
    text = TABLE_PATTERN.sub('', text)
    return text

##
# Finds and returns the first instance of a pattern in a string.
# 
# @param pattern The pattern to match.
# @param string The string to find first instance.
# @return matched text.
def findOnce(pattern, string, verbose=False):
    match = pattern.search(string)
    if match:
        return match.group()
    else:
        if verbose:
            print "could not match", pattern.pattern
        return None



# PARSER METHODS

##
# Parse SEC-HEADER.
# 
# @param docName The name of document to parse.
# @return Doc object.
def parseHeader(docName, verbose=False):
    # Extract Header content
    with open(DIR_FORM+'/'+docName+'.txt', 'r') as rfile:
        xml = rfile.read()
    header = findOnce(HEAD_PATTERN, xml, verbose=verbose)
    # Parse Doc attributes
    doc = secdoc.Doc(docName+'.txt',
            str(findOnce(COMP_NAME_PATTERN,   header, verbose=verbose)).strip(),
            str(findOnce(COMP_CIK_PATTERN,    header, verbose=verbose)).strip(),
            str(findOnce(DOC_TYPE_PATTERN,    header, verbose=verbose)).strip(),
            str(findOnce(FILING_DATE_PATTERN, header, verbose=verbose)).strip(),
            str(findOnce(REPORT_DATE_PATTERN, header, verbose=verbose)).strip())
    return doc

##
# Find item in a parsed form.
# 
# @param itemPattern Compiled RE for item content
# @param form The content of the form to parse.
# @param docName The name of the document if available (for testing).
# @return matched text or None if no item 5 is found.
def parseItem(itemPattern, form, docName="", verbose=True):
    allMatch = itemPattern.findall(form)
    for match in allMatch:
        if not NONE_PATTERN.findall(match) and not NA_PATTERN.findall(match) and len(match.split()) > 100:
            return match
    if verbose:
        print docName, ": No Item"
    return None

##
# Parse the Text content (currently only Item 5/9)
#
# @param docName The name of the form to parse.
# @return content for this form or None
def parseText(docName, verbose=False):
    # Extract Header content
    with open(DIR_FORM+'/'+docName+'.txt', 'r') as rfile:
        xml = rfile.read()
    # Default parse strategy for plain text content
    content = findOnce(TEXT_PATTERN, xml,     verbose=verbose)
    if not content:
        return None
    html = findOnce(HTML_PATTERN, content, verbose=verbose)
    if html: # Strip HTML content
        content = strip_html(content).encode('UTF-8')
    else: # Strip XML tags
        content = strip_markup(content)
    # Get item depending on year of filing
    if int(os.path.dirname(docName)) <= 2000:
        content = parseItem(ITEM9_PATTERN, content, docName)
    else:
        content = parseItem(ITEM5_PATTERN, content, docName)
    if content and not NONE_PATTERN.findall(content):
        return content
    return None

##
# Get the list of document names in DIR_FORM
# 
# @return docNames List of document names in the form:
# "1997/0000950151-97-000162"
def getFormList(verbose=False):
    docNames = []
    for r, dirs, f in os.walk(DIR_FORM):
        for dir in dirs:
            for root, d, files in os.walk(DIR_FORM+'/'+dir):
                for name in files:
                    docNames.append(dir+'/'+name[0:-4])
    return sorted(docNames)

##
# Parse all forms
# 
# @return writes CSV file for form list
# @return writes parsed text content (currently only Item 5)
def parseForms(verbose=False):
    docNames = getFormList(verbose)
    makeDir(FILING_LIST)
    with open(FILING_LIST, 'wb') as formlist:
        for docName in docNames:
            form = parseHeader(docName, verbose)
            content = parseText(docName, verbose=verbose)
            if content is not None:
                form.write(formlist)
                filename = DIR_TEXT+'/'+form.docname
                makeDir(filename)
                with codecs.open(filename, 'w', "utf-8") as wfile:
                    wfile.write(unicode(content, 'utf-8'))
                if verbose:
                    print "PARSED", docName
            else:
                print "IGNORE", docName

# MAIN METHOD

def main(argv=None):
    parseForms(verbose=False)
    
if __name__ == '__main__':
    sys.exit(main())
