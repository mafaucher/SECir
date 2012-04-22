#!/usr/bin/env python

"""secdoc.py

Class for parsed SEC documents
"""
import csv

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

# Dictionary template (currently not required)
""" 
class CompanyDict(dict):
    def __init__(self, *args, **kw):
        super(CompanyDict, self).__init__(*args, **kw)
        self.itemlist = super(CompanyDict, self).keys()
    def __setitem__(self, key, value):
         # TODO: what should happen to the order if
         #       the key is already in the dict
        self.itemlist.append(key)
        super(odict,self).__setitem__(key, value)
    def __iter__(self):
        return iter(self.itemlist)
    def keys(self):
        return self.itemlist
    def values(self):
        return [self[key] for key in self]  
    def itervalues(self):
        return (self[key] for key in self)    

def findByCik(newCik, companyList):
    for company in companyList:
        if company.cik == newCik:
            return company
    return None
"""

# Company class (merged with Doc class)
""" 
class Company:
    def __init__(self, companyname, companycik):
        self.docs       = []
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.cik == other.cik
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
"""
