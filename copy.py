"""
copy.py

Used to copy a large number of files using include.txt and exclude.txt as filters
"""

import os, shutil, sys

# DIRECTORIES AND FILES

# Files to parse 
INCLUDE     = "include.txt"                     # List of files to include for parsing
EXCLUDE     = "exclude.txt"                     # List of files to exclude for parsing

DIR_MEDIA   = os.path.join(os.path.abspath(os.path.curdir), 'files')
DIR_INPUT   = os.path.join(DIR_MEDIA, 'input')  # Directory for original forms
DIR_OUTPUT  = os.path.join(DIR_MEDIA, 'output') # Directory for parsed text

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
# Get the list of document names in listFile
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
					docNames.append(os.path.join(dir, os.path.splitext(name)[0]))
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
	makeDir(DIR_OUTPUT)
	for docName in docNames:
		makeDir(os.path.join(DIR_OUTPUT, docName+".txt"))
		shutil.copy(os.path.join(DIR_INPUT, docName+".txt"), os.path.join(DIR_OUTPUT, docName+".txt"))

if __name__ == '__main__':
	sys.exit(main())
