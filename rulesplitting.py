'''
Rule Splitting, Uploading to ES
'''

from elasticsearch import Elasticsearch
es = Elasticsearch() #put the aws line here


def splitRule():
    ...
    return rulechunks


def ruletoES(rulechunks, idstart):
    for i, chunk in range(idstart, idstart+len(rulechunks)), rulechunks:
        res = es.index(index=chunk["name"], id=i, body=doc)
        