'''
Rule Splitting, Uploading to ES
'''
from elasticsearch import Elasticsearch
es = Elasticsearch() #put the aws url in here


def splitRule():
    ...
    return rulechunks


def ruletoES(rulechunks, i):
    for chunk in rulechunks:
        res = es.index(index=chunk["name"], id=i, body=chunk)
        i += 1
    return i