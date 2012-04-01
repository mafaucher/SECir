#!/usr/bin/env python

"""secdoc.py

Class for parsed SEC documents
"""

import csv

class Company:
    def __init__(self, companyname, companycik):
        self.name = companyname
        self.cik  = companycik
        self.docs = []

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.cik == other.cik
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class Doc:
    def __init__(self, docname, doctype, docfiledate, docreportdate):
        self.name       = docname
        self.type       = doctype
        self.reportdate = docreportdate
        self.filedate   = docfiledate
            
def findByCik(newCik, companyList):
    for company in companyList:
        if company.cik == newCik:
            return company
    return None
