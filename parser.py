"""
parser.py

Module used to parse SEC forms
"""

import codecs, csv, htmlentitydefs, os, re, string, sys

class Doc:
	def __init__(self, originalname, companyname, companycik,
			     doctype, docfilingdate, docreportdate):
		self.compname   = companyname
		self.compcik    = companycik
		self.srcname    = originalname
		self.type       = doctype
		self.filingdate = docfilingdate
		self.reportdate = docreportdate
		self.docname    = str(self.compcik)+"-"+str(self.filingdate)+".txt"

	def write(self, wfile):
		writer = csv.writer(wfile, delimiter='|')
		writer.writerow([self.compname, str(self.compcik), self.type,
			            str(self.filingdate), str(self.reportdate),
			            self.srcname, self.docname])

# DIRECTORIES AND FILES

# Files to parse 
FILING_LIST = "filingslist.csv"                 # Spreadsheet with header data
INCLUDE     = "include.txt"                     # List of files to include for parsing
EXCLUDE     = "exclude.txt"                     # List of files to exclude for parsing
UNPARSED    = "unparsed.txt"                    # Log of unparseable files

DIR_MEDIA   = os.path.join(os.path.abspath(os.path.curdir), 'files')
DIR_INPUT   = os.path.join(DIR_MEDIA, 'input')  # Directory for original forms
DIR_TEMP    = os.path.join(DIR_MEDIA, 'temp')   # Temporary directory for partial parsing
DIR_OUTPUT  = os.path.join(DIR_MEDIA, 'output') # Directory for parsed text

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
# First pass version
ITEM9_PATTERN   = re.compile(r'\n\s*(?:ITEM\D{0,5}9.{0,15}?management.{0,2}\s*discussion\s*)(?:.{0,3}?\s*analysis\s*of\s*financial\s*condition\s*.{0,3}\s*results\s*of\s*operations\s*)?(?!\n\s*ITEM\D{0,5}9.{0,10}?management.{0,2}\s*discussion\s*)(.*?)(?=\s*\n\s*ITEM\D{0,5}10)',
		flags=(re.DOTALL|re.IGNORECASE))
# Second pass version
ITEM9P2_PATTERN = re.compile(r'\n\s*(?:ITEM\D{0,5}9.{0,15}?management.{0,2}\s*discussion\s*)(?:.{0,3}?\s*analysis\s*of\s*financial\s*condition\s*.{0,3}\s*results\s*of\s*operations\s*)?(.*)',
		flags=(re.DOTALL|re.IGNORECASE))

# Item 5 (2001-...)
# First pass version
ITEM5_PATTERN   = re.compile(r'\n\s*(?:ITEM\D{0,5}5.{0,15}?operating\s*)(?:.{0,3}?\s*financial\s*review\s*.{0,3}?\s*prospects\s*)?(?!\n\s*ITEM\D{0,5}5.{0,10}?operating\s*)(.*?)(?=\s*\n\s*ITEM\D{0,5}6)',
		flags=(re.DOTALL|re.IGNORECASE))
# Second pass version
ITEM5P2_PATTERN = re.compile(r'\n\s*(?:ITEM\D{0,5}5.{0,15}?operating\s*)(?:.{0,3}?\s*financial\s*review\s*.{0,3}?\s*prospects\s*)?(.*)',
		flags=(re.DOTALL|re.IGNORECASE))

# SEC-XML tags
PAGE_PATTERN = re.compile(r'\s*\S*\s*<PAGE>\s*',
		flags=(re.DOTALL|re.IGNORECASE))
TABLE_PATTERN = re.compile(r'<TABLE>.*?</TABLE>',
		flags=(re.DOTALL|re.IGNORECASE))
TAG_PATTERN = re.compile(r'<.*?>')

# HTML tags
P_PATTERN = re.compile(r'<P', flags=(re.IGNORECASE))

# Paragraph
PARAG_PATTERN = re.compile(r'\s*$')

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
#
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
#
# @return The document without markup.
def strip_markup(text):
	text = PAGE_PATTERN.sub('\r\n', text)
	text = TABLE_PATTERN.sub('', text)
	text = TAG_PATTERN.sub('', text)
	return text

# PARSER METHODS

##
# Finds and returns the first instance of a pattern in a string.
# 
# @param pattern The pattern to match.
# @param string The string to find first instance.
#
# @return matched text.
def findOnce(pattern, string):
	match = pattern.search(string)
	if match: return match.group()
	return None

##
# Parse SEC-HEADER.
# 
# @param docName The name of document to parse.
#
# @return Doc object.
def parseHeader(docName):
	# Extract Header content
	with open(os.path.join(DIR_INPUT, docName+'.txt'), 'r') as rfile:
		xml = rfile.read()
	header = findOnce(HEAD_PATTERN, xml)
	# Parse Doc attributes
	doc = Doc(docName+'.txt',
			str(findOnce(COMP_NAME_PATTERN,   header)).strip(),
			str(findOnce(COMP_CIK_PATTERN,    header)).strip(),
			str(findOnce(DOC_TYPE_PATTERN,    header)).strip(),
			str(findOnce(FILING_DATE_PATTERN, header)).strip(),
			str(findOnce(REPORT_DATE_PATTERN, header)).strip())
	return doc

##
# Find item in a parsed form.
# 
# @param itemPattern Compiled RE for item content
# @param pass2Pattern Compile RE for second pass
# @param form The content of the form to parse.
# @param docName The name of the document if available (for testing).
#
# @return matched text or None if no item is found.
def parseItem(itemPattern, pass2Pattern, form, docName=""):
	allMatch = itemPattern.findall(form)
	for match in allMatch:
		# Match as long as second pass still matches
		pass2 = findOnce(pass2Pattern, match)
		while pass2 and pass2 != match:
			match = pass2
			pass2 = findOnce(pass2Pattern, match)
		if pass2 and len(pass2.split()) > 100:
			return pass2
		if match and len(match.split()) > 100:
			return match
	return None

##
# Parse the Text content (currently only Item 5/9)
#
# @param docName The name of the form to parse.
#
# @return content for this form or None
def parseText(docName):
	# Extract Header content
	with open(os.path.join(DIR_INPUT, docName+'.txt'), 'r') as rfile:
		xml = rfile.read()
	# Get the TEXT content
	content = findOnce(TEXT_PATTERN, xml)
	if not content:
		return None
	html = findOnce(HTML_PATTERN, content)
	if html: # Strip HTML content
		content = P_PATTERN.sub("\r\n<P", content)
		content = strip_html(content).encode('UTF-8').replace("\xc2\xa0", " ")
	# Get desired item
	item = parseItem(ITEM5_PATTERN, ITEM5P2_PATTERN, content, docName)
	if not item:
		item = parseItem(ITEM9_PATTERN, ITEM9P2_PATTERN, content, docName)
	if item:
		item = strip_markup(item)
		return item
	# Log unparsed documents
	with open(UNPARSED, 'a') as log:
		log.write(docName+".txt\n")
	return None

def paragraphs(file, separator=None):
	if not callable(separator):
		def separator(line): return PARAG_PATTERN.match(line)
	paragraph = []
	for line in file:
		if separator(line):
			if paragraph:
				yield ''.join(paragraph)
				paragraph = []
		else:
			paragraph.append(line)
	if paragraph: yield ''.join(paragraph)

def paragFilter(content):
	return content.rstrip()[-1] in string.punctuation

def parseParagraphs(docNames):
	makeDir(DIR_OUTPUT)
	listlen = len(docNames)
	done = 0
	lastint = 0
	current = 0.0
	for docName in docNames:
		form = parseHeader(docName)
		print form.srcname, "->", form.docname
		content = parseText(docName)
		tempFile = os.path.join(DIR_TEMP, form.docname)
		textFile = os.path.join(DIR_OUTPUT, form.docname)
		if content is not None:
			# Add form to formlist
			with open(FILING_LIST, 'ab') as formlist:
				form.write(formlist)
			# Write phase 1 parsing in tempFile
			makeDir(tempFile)
			with codecs.open(tempFile, 'w', "utf-8") as wfile:
				wfile.write(unicode(content, "utf-8"))
			# Write phase 2 parsing in textFile
			with open(textFile, 'w') as wfile:
				wfile.write("\r\n".join(filter(paragFilter, paragraphs(open(tempFile)))))
		current += 1.0
		done = int(100*(current/listlen))
		if done != lastint:
			lastint = done
			print "COMPLETED:", str(done), '%'

##
# Get the list of document names in INCLUDE
# 
# @return docNames List of document names in the form:
#       "1997/0000950151-97-000162"
def getDocList(listFile):
	docNames = []
	for line in open(listFile, 'r'):
		docNames.append(os.path.splitext(line.strip())[0])
	return docNames

##
# Get the list of all documents in DIR_INPUT
# 
# @return docNames List of document names in the form:
#       "1997/0000950151-97-000162"
def getAllList():
	docNames = []
	for r, dirs, f in os.walk(DIR_INPUT):
		for dir in dirs:
			for root, d, files in os.walk(os.path.join(DIR_INPUT, dir)):
				for name in files:
					docNames.append(os.join(dir, os.path.splitext(name)[0]))
	return docNames

##
# Get the list of documents in INCLUDE - EXCLUDE
#
# @return docNames List of document names in the form:
#       "1997/0000950151-97-000162"
def getFormList():
	docNames = getDocList(INCLUDE) if os.path.exists(INCLUDE) else getAllList()
	exclude = getDocList(EXCLUDE) if os.path.exists(EXCLUDE) else []
	docNames = list(set(docNames) - set(exclude))
	return sorted(docNames)

# MAIN METHOD

def main(argv=None):
	docNames = getFormList()
	parseParagraphs(docNames)

if __name__ == '__main__':
	sys.exit(main())
