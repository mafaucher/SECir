# SECir

## Requirements

- Python 2.7

## Parser for Public SEC Filings

parser.py will process the files contained in **"./files/input/"**, and output the
desired section to **"./files/output/"**. Additionally, the following information
about each filing will be extracted from the header in **"filingslist.csv"**:

- Company name
- CIK (Central Index Key), a unique company ID used by the SEC
- The document type (generally 20-F)
- The filing date
- The reporting date
- The original file name
- The new file name (CIK+"-"+filing\_date+".txt")

The parser will read a text document named **"include.txt"**, if this document is not
present it will include all files in "./files/input/" by
default. It will then read another text document named **"exclude.txt"**, if this
document is not present it will exclude no files by default. Files which could
not be parsed are logged in **"unparsed.txt"**.

To run the parser, simply call the script from the current directory:

> python parser.py

*NOTE: The content of of "./files/output/", "filingslist.csv" and "unparsed.txt" will
not be erased, so these files should be removed manually if the user wishes to
start from a "clean" state.*

## Copy Files Without Processing

copy.py allows to copy files from "./files/input/" to "./files/output/", using
the include and exclude lists described above, without parsing the content of
the files.
