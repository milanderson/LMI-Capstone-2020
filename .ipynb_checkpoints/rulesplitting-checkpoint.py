'''
Rule Splitting, Uploading to ES
'''
from elasticsearch import Elasticsearch
es = Elasticsearch() #put the aws url in here


def splitRule():
    ...
    #return rulechunks


def ruletoES_lists(rulechunks, idnum):
    for chunk in rulechunks:
        res = es.index(index=chunk.key, id=idnum, body=chunk.value)
        idnum += 1
    print(f"Last id uploaded: {idnum-1}")


def ruletoES_dicts(rulechunks, idnum):
    for chunk in rulechunks:
        for key, value in chunk.items():
            res = es.index(index=key, id=idnum, body=value)
            idnum += 1
    print(f"Last id uploaded: {idnum-1}")

